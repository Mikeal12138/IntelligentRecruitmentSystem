"""
训练主流程: 特征工程 + KMeans聚类 + 神经网络分类
"""
import os
import sys
import time
import pickle
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# 将项目根目录加入路径
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.data_pipeline.nlp_processor import NLPProcessor
from src.ml_engine.cluster import ClusterEngine
from src.ml_engine.classifier import NeuralClassifier
from src.ml_engine.visualizer import MLVisualizer


class TrainingPipeline:
    def __init__(self, data_path, model_dir='models', config=None):
        self.data_path = data_path
        self.model_dir = model_dir
        self.figures_dir = os.path.join(model_dir, 'figures')
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)

        self.config = config or {}
        self.nlp = NLPProcessor(
            max_features=self.config.get('nlp_max_features', 5000),
            ngram_range=tuple(self.config.get('nlp_ngram_range', [1, 2])),
        )
        self.visualizer = MLVisualizer(output_dir=self.figures_dir)

        # 用于推理时复用
        self.numeric_scaler = StandardScaler()
        self.label_encoders = {}

    def load_data(self):
        print("\n" + "=" * 60)
        print("Step 1: 加载数据")
        print("=" * 60)
        df = pd.read_csv(self.data_path)
        print(f"  [Data] 加载 {len(df)} 条记录, {len(df.columns)} 列")
        self.df = df
        return df

    def prepare_text_features(self):
        print("\n" + "=" * 60)
        print("Step 2: NLP 文本特征工程")
        print("=" * 60)

        # 拼接职位名称 + 职位描述
        df = self.df
        texts = (df['招聘岗位'].astype(str) + ' ' + df['职位描述'].astype(str)).tolist()
        print(f"  [NLP] 拼接文本: 招聘岗位 + 职位描述, 共 {len(texts)} 条")

        # 加载停用词
        sw_path = self.config.get('stopwords_path', 'data/text_features/stopwords.txt')
        self.nlp.load_stopwords(sw_path)

        # TF-IDF 向量化
        tfidf_matrix = self.nlp.fit_transform(texts)
        self.tfidf_matrix = tfidf_matrix

        # 保存 NLP 模型
        self.nlp.save(os.path.join(self.model_dir, 'tfidf_vectorizer.pkl'))
        return tfidf_matrix

    def prepare_numeric_features(self, feature_cols=None):
        print("\n" + "=" * 60)
        print("Step 3: 数值特征工程")
        print("=" * 60)

        if feature_cols is None:
            feature_cols = ['最低月薪', '最高月薪', '要求经验_排序', '学历要求_排序', '薪资浮动', '年终奖估算']

        df = self.df
        numeric_data = df[feature_cols].values.astype(np.float32)
        self.numeric_scaled = self.numeric_scaler.fit_transform(numeric_data)

        # 保存 scaler
        scaler_path = os.path.join(self.model_dir, 'feature_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump({
                'scaler': self.numeric_scaler,
                'feature_cols': feature_cols,
            }, f)
        print(f"  [Numeric] 数值特征 {len(feature_cols)} 维, 已标准化并保存至 {scaler_path}")
        return self.numeric_scaled

    def build_combined_features(self):
        print("\n" + "=" * 60)
        print("Step 4: 组合特征")
        print("=" * 60)

        combined = hstack([self.tfidf_matrix, self.numeric_scaled])
        print(f"  [Features] 组合特征维度: {combined.shape} (TF-IDF + 数值)")
        self.combined_features = combined
        return combined

    def run_clustering(self, auto_k=True, k_range=range(3, 16)):
        print("\n" + "=" * 60)
        print("Step 5: KMeans 聚类分析")
        print("=" * 60)

        engine = ClusterEngine(
            n_clusters=self.config.get('kmeans_n_clusters', 8),
            random_state=self.config.get('kmeans_random_state', 42),
            max_iter=self.config.get('kmeans_max_iter', 300),
        )

        if auto_k:
            best_k, results = engine.auto_select_k(self.combined_features, k_range=k_range)
            # 绘制肘部曲线
            self.visualizer.plot_elbow_curve(results, filename='elbow_curve.png')
        else:
            engine.fit(self.combined_features)

        # 评估
        eval_result = engine.evaluate(self.combined_features)

        # 获取簇信息
        cluster_info = engine.get_cluster_info()
        for k, info in cluster_info.items():
            print(f"  [KMeans] 簇 {k}: {info['count']} 条 ({info['ratio']:.1%})")

        # 保存模型
        engine.save(os.path.join(self.model_dir, 'kmeans_model.pkl'))

        # 可视化: PCA 散点图
        labels = engine.model.labels_
        self.visualizer.plot_clustering_pca(
            self.combined_features, labels,
            title=f'KMeans 聚类结果 (k={engine.n_clusters})',
            filename='clustering_pca.png',
        )

        # 将簇标签加入 DataFrame
        self.df['cluster_label'] = labels

        self.cluster_engine = engine
        return engine, labels

    def run_salary_classification(self, epochs=100, batch_size=128):
        print("\n" + "=" * 60)
        print("Step 6: 薪资等级分类 (神经网络)")
        print("=" * 60)

        # 编码标签
        le = LabelEncoder()
        y = le.fit_transform(self.df['薪资等级'])
        self.label_encoders['salary'] = le
        class_names = le.classes_.tolist()
        num_classes = len(class_names)
        print(f"  [NN-Salary] 类别: {class_names}")
        print(f"  [NN-Salary] 类别分布: {dict(zip(class_names, np.bincount(y)))}")

        # 划分训练/测试集
        X_train, X_test, y_train, y_test = train_test_split(
            self.combined_features, y, test_size=0.2, random_state=42, stratify=y
        )

        input_size = X_train.shape[1]
        hidden_size = self.config.get('nn_hidden_size', 128)

        clf = NeuralClassifier(
            input_size=input_size,
            hidden_size=hidden_size,
            num_classes=num_classes,
            learning_rate=self.config.get('nn_learning_rate', 0.001),
            dropout=0.3,
        )
        print(f"  [NN-Salary] 输入维度={input_size}, 隐藏层={hidden_size}, 类别={num_classes}")

        history = clf.train(X_train, y_train, epochs=epochs, batch_size=batch_size,
                           patience=15, verbose=True)

        # 测试集评估
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"\n  [NN-Salary] 测试集准确率: {acc:.4f}")
        print(f"  [NN-Salary] 分类报告:")
        report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)
        print(classification_report(y_test, y_pred, target_names=class_names))

        # 保存模型
        clf.save(os.path.join(self.model_dir, 'nn_salary_classifier.pt'))

        # 保存 label encoder
        with open(os.path.join(self.model_dir, 'salary_label_encoder.pkl'), 'wb') as f:
            pickle.dump(le, f)

        # 可视化
        self.visualizer.plot_confusion_matrix(
            y_test, y_pred, class_names=class_names,
            title='薪资等级分类 - 混淆矩阵',
            filename='salary_confusion_matrix.png',
        )
        self.visualizer.plot_training_curves(
            history, title='薪资分类训练曲线',
            filename='salary_training_curves.png',
        )

        self.salary_classifier = clf
        return clf, acc, report

    def run_category_classification(self, epochs=50, batch_size=128):
        print("\n" + "=" * 60)
        print("Step 7: 招聘类别分类 (神经网络)")
        print("=" * 60)

        le = LabelEncoder()
        y = le.fit_transform(self.df['招聘类别'])
        self.label_encoders['category'] = le
        class_names = le.classes_.tolist()
        num_classes = len(class_names)
        print(f"  [NN-Category] 类别: {class_names}")
        print(f"  [NN-Category] 类别分布: {dict(zip(class_names, np.bincount(y)))}")

        X_train, X_test, y_train, y_test = train_test_split(
            self.combined_features, y, test_size=0.2, random_state=42, stratify=y
        )

        input_size = X_train.shape[1]
        hidden_size = self.config.get('nn_hidden_size', 128)

        clf = NeuralClassifier(
            input_size=input_size,
            hidden_size=hidden_size,
            num_classes=num_classes,
            learning_rate=self.config.get('nn_learning_rate', 0.001),
            dropout=0.3,
        )
        print(f"  [NN-Category] 输入维度={input_size}, 隐藏层={hidden_size}, 类别={num_classes}")

        history = clf.train(X_train, y_train, epochs=epochs, batch_size=batch_size,
                           patience=10, verbose=True)

        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"\n  [NN-Category] 测试集准确率: {acc:.4f}")
        print(classification_report(y_test, y_pred, target_names=class_names))

        clf.save(os.path.join(self.model_dir, 'nn_category_classifier.pt'))

        with open(os.path.join(self.model_dir, 'category_label_encoder.pkl'), 'wb') as f:
            pickle.dump(le, f)

        self.visualizer.plot_confusion_matrix(
            y_test, y_pred, class_names=class_names,
            title='招聘类别分类 - 混淆矩阵',
            filename='category_confusion_matrix.png',
        )
        self.visualizer.plot_training_curves(
            history, title='招聘类别分类训练曲线',
            filename='category_training_curves.png',
        )

        self.category_classifier = clf
        return clf, acc

    def save_pipeline_artifacts(self):
        print("\n" + "=" * 60)
        print("Step 8: 保存管线元数据")
        print("=" * 60)

        # 保存带簇标签的数据
        output_csv = os.path.join(os.path.dirname(self.data_path), 'jobs_with_clusters.csv')
        self.df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"  [Save] 带簇标签的数据已保存: {output_csv}")

        # 保存 label encoders
        le_path = os.path.join(self.model_dir, 'label_encoders.pkl')
        with open(le_path, 'wb') as f:
            pickle.dump(self.label_encoders, f)
        print(f"  [Save] Label Encoders 已保存: {le_path}")

    def run_all(self, auto_k=True, salary_epochs=100, category_epochs=50):
        start = time.time()
        print("\n" + "#" * 60)
        print("#  智能招聘推荐系统 - 机器学习训练管线")
        print("#" * 60)

        self.load_data()
        self.prepare_text_features()
        self.prepare_numeric_features()
        self.build_combined_features()
        self.run_clustering(auto_k=auto_k)
        self.run_salary_classification(epochs=salary_epochs)
        self.run_category_classification(epochs=category_epochs)
        self.save_pipeline_artifacts()

        elapsed = time.time() - start
        print("\n" + "#" * 60)
        print(f"#  训练完成! 总耗时: {elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
        print(f"#  模型文件: {self.model_dir}/")
        print(f"#  可视化: {self.figures_dir}/")
        print("#" * 60)
