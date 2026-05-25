import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 无 GUI 环境
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA


class MLVisualizer:
    def __init__(self, output_dir='models/figures'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_style('whitegrid')
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

    def _save(self, filename):
        path = os.path.join(self.output_dir, filename)
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  [Viz] 图表已保存: {path}")

    def plot_clustering_pca(self, X, labels, title='KMeans 聚类结果 (PCA降维)', filename='clustering_pca.png'):
        """PCA 降维 + 聚类散点图"""
        # 如果 X 是稀疏矩阵，先转稠密
        if hasattr(X, 'toarray'):
            X_dense = X.toarray()
        else:
            X_dense = X

        # 采样以加速 PCA（最多 5000 条）
        n = len(X_dense)
        if n > 5000:
            idx = np.random.RandomState(42).choice(n, 5000, replace=False)
            X_plot = X_dense[idx]
            y_plot = labels[idx]
        else:
            X_plot = X_dense
            y_plot = labels

        pca = PCA(n_components=2, random_state=42)
        X_2d = pca.fit_transform(X_plot)

        fig, ax = plt.subplots(figsize=(10, 7))
        unique_labels = np.unique(y_plot)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

        for k, color in zip(unique_labels, colors):
            mask = y_plot == k
            ax.scatter(X_2d[mask, 0], X_2d[mask, 1], c=[color], label=f'簇 {k}',
                       s=15, alpha=0.6, edgecolors='none')

        ax.set_xlabel(f'PCA1 ({pca.explained_variance_ratio_[0]:.1%})')
        ax.set_ylabel(f'PCA2 ({pca.explained_variance_ratio_[1]:.1%})')
        ax.set_title(title, fontsize=14)
        ax.legend(markerscale=3, fontsize=9)
        self._save(filename)

    def plot_confusion_matrix(self, y_true, y_pred, class_names=None,
                              title='混淆矩阵', filename='confusion_matrix.png'):
        """混淆矩阵热力图"""
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_true, y_pred)

        fig, ax = plt.subplots(figsize=(10, 8))
        labels = class_names or [str(i) for i in range(cm.shape[0])]
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=labels, yticklabels=labels, ax=ax,
                    cbar_kws={'label': '样本数'})
        ax.set_xlabel('预测标签', fontsize=12)
        ax.set_ylabel('真实标签', fontsize=12)
        ax.set_title(title, fontsize=14)
        self._save(filename)

    def plot_training_curves(self, history, title='训练曲线', filename='training_curves.png'):
        """训练 Loss / Accuracy 曲线"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        epochs = range(1, len(history['train_loss']) + 1)
        ax1.plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
        ax1.plot(epochs, history['val_loss'], 'r-', label='Val Loss', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_title('Loss 曲线')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(epochs, history['train_acc'], 'b-', label='Train Acc', linewidth=2)
        ax2.plot(epochs, history['val_acc'], 'r-', label='Val Acc', linewidth=2)
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.set_title('Accuracy 曲线')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        fig.suptitle(title, fontsize=14, y=1.02)
        self._save(filename)

    def plot_elbow_curve(self, k_results, filename='elbow_curve.png'):
        """KMeans 肘部曲线 + 轮廓系数"""
        ks = sorted(k_results.keys())
        inertias = [k_results[k]['inertia'] for k in ks]
        silhouettes = [k_results[k]['silhouette'] for k in ks]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        ax1.plot(ks, inertias, 'bo-', linewidth=2, markersize=8)
        ax1.set_xlabel('K 值')
        ax1.set_ylabel('Inertia')
        ax1.set_title('肘部法则')
        ax1.grid(True, alpha=0.3)

        ax2.plot(ks, silhouettes, 'ro-', linewidth=2, markersize=8)
        ax2.set_xlabel('K 值')
        ax2.set_ylabel('轮廓系数')
        ax2.set_title('轮廓系数 vs K')
        best_k = ks[np.argmax(silhouettes)]
        ax2.axvline(best_k, color='green', linestyle='--', label=f'最优 K={best_k}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        self._save(filename)

    def plot_feature_importance(self, feature_names, weights, top_k=20,
                                title='Top 特征权重', filename='top_features.png'):
        """TF-IDF 特征重要性排序"""
        indices = np.argsort(np.abs(weights))[::-1][:top_k]
        names = [feature_names[i] for i in indices]
        vals = [weights[i] for i in indices]

        fig, ax = plt.subplots(figsize=(10, 7))
        y_pos = range(len(names))
        ax.barh(y_pos, vals, color='steelblue')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(names)
        ax.invert_yaxis()
        ax.set_xlabel('权重')
        ax.set_title(title)
        self._save(filename)
