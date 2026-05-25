"""
智能招聘推荐系统 - 机器学习训练入口
用法: python train_models.py
"""
import os
import sys

# 项目根目录
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import yaml
from src.ml_engine.trainer import TrainingPipeline


def load_config(path='config/config.yaml'):
    """加载 YAML 配置"""
    full_path = os.path.join(ROOT, path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        print(f"[Config] 已加载配置文件: {full_path}")
        return cfg
    print(f"[Config] 配置文件不存在: {full_path}，使用默认配置")
    return {}


def main():
    cfg = load_config()

    # 数据路径
    data_path = os.path.join(
        ROOT,
        cfg.get('data', {}).get('processed_path', 'data/processed'),
        'cleaned_recruitment_data(1).csv',
    )

    if not os.path.exists(data_path):
        print(f"[Error] 数据文件不存在: {data_path}")
        sys.exit(1)

    model_dir = os.path.join(ROOT, cfg.get('models', {}).get('model_path', 'models'))

    # 构建训练配置
    train_config = {
        # NLP
        'nlp_max_features': cfg.get('nlp', {}).get('max_features', 5000),
        'nlp_ngram_range': cfg.get('nlp', {}).get('ngram_range', [1, 2]),
        'stopwords_path': os.path.join(ROOT, cfg.get('nlp', {}).get('stopwords_path', '')),
        # KMeans
        'kmeans_n_clusters': cfg.get('hyperparameters', {}).get('kmeans', {}).get('n_clusters', 8),
        'kmeans_random_state': cfg.get('hyperparameters', {}).get('kmeans', {}).get('random_state', 42),
        'kmeans_max_iter': cfg.get('hyperparameters', {}).get('kmeans', {}).get('max_iter', 300),
        # Neural Network
        'nn_hidden_size': cfg.get('hyperparameters', {}).get('neural_network', {}).get('hidden_size', 128),
        'nn_learning_rate': cfg.get('hyperparameters', {}).get('neural_network', {}).get('learning_rate', 0.001),
    }

    print("\n" + "=" * 60)
    print("配置摘要:")
    for k, v in train_config.items():
        print(f"  {k}: {v}")
    print("=" * 60)

    pipeline = TrainingPipeline(
        data_path=data_path,
        model_dir=model_dir,
        config=train_config,
    )

    # 执行完整训练
    pipeline.run_all(
        auto_k=True,                    # 自动搜索最优 K
        salary_epochs=cfg.get('hyperparameters', {}).get('neural_network', {}).get('epochs', 100),
        category_epochs=50,
    )


if __name__ == '__main__':
    main()
