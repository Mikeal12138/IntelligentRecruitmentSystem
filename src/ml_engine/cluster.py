import pickle
import numpy as np
from scipy.sparse import issparse
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score


class ClusterEngine:
    def __init__(self, n_clusters=8, random_state=42, max_iter=300):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.max_iter = max_iter
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            max_iter=max_iter,
            n_init=10,
        )
        self._is_fitted = False
        self._labels = None

    def fit(self, X):
        """拟合 KMeans 模型"""
        self.model.fit(X)
        self._is_fitted = True
        self._labels = self.model.labels_
        print(f"  [KMeans] 拟合完成: k={self.n_clusters}, inertia={self.model.inertia_:.1f}")
        return self

    def predict(self, X):
        """预测样本所属簇"""
        if not self._is_fitted:
            raise RuntimeError("模型尚未拟合，请先调用 fit()")
        return self.model.predict(X)

    def fit_predict(self, X):
        """拟合并返回簇标签"""
        self.fit(X)
        return self._labels

    def evaluate(self, X):
        """评估聚类质量: 轮廓系数 + Calinski-Harabasz 指数"""
        if not self._is_fitted:
            raise RuntimeError("模型尚未拟合")
        n_samples = X.shape[0] if hasattr(X, 'shape') else len(X)
        sil = silhouette_score(X, self._labels, sample_size=min(5000, n_samples))
        X_dense = X.toarray() if issparse(X) else X
        ch = calinski_harabasz_score(X_dense, self._labels)
        print(f"  [KMeans] 轮廓系数: {sil:.4f}")
        print(f"  [KMeans] Calinski-Harabasz: {ch:.1f}")
        return {'silhouette': sil, 'calinski_harabasz': ch}

    def get_cluster_info(self):
        """返回每个簇的信息: 样本数、占比、中心坐标"""
        if not self._is_fitted:
            raise RuntimeError("模型尚未拟合")
        info = {}
        total = len(self._labels)
        for k in range(self.n_clusters):
            mask = self._labels == k
            info[k] = {
                'count': int(mask.sum()),
                'ratio': float(mask.sum() / total),
                'center': self.model.cluster_centers_[k].tolist(),
            }
        return info

    def auto_select_k(self, X, k_range=range(3, 16)):
        """自动搜索最优 k 值（基于轮廓系数）"""
        n_samples = X.shape[0] if hasattr(X, 'shape') else len(X)
        best_k = self.n_clusters
        best_score = -1
        results = {}
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=self.random_state, max_iter=self.max_iter, n_init=10)
            labels = km.fit_predict(X)
            sil = silhouette_score(X, labels, sample_size=min(5000, n_samples))
            results[k] = {'silhouette': sil, 'inertia': km.inertia_}
            print(f"  [KMeans] k={k}: silhouette={sil:.4f}, inertia={km.inertia_:.1f}")
            if sil > best_score:
                best_score = sil
                best_k = k
        # 使用最优 k 重新拟合
        self.n_clusters = best_k
        self.model = KMeans(
            n_clusters=best_k,
            random_state=self.random_state,
            max_iter=self.max_iter,
            n_init=10,
        )
        self.fit(X)
        print(f"  [KMeans] 最优 k={best_k} (silhouette={best_score:.4f})")
        return best_k, results

    def save(self, filepath: str):
        """保存模型"""
        import os
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"  [KMeans] 模型已保存至 {filepath}")

    def load(self, filepath: str):
        """加载模型"""
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        self._is_fitted = True
        self._labels = self.model.labels_
        self.n_clusters = self.model.n_clusters
        print(f"  [KMeans] 模型已从 {filepath} 加载")
