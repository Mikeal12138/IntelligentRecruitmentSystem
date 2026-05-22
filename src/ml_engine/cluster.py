from sklearn.cluster import KMeans


class ClusterEngine:
    def __init__(self, n_clusters=8):
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
    
    def fit(self, X):
        pass
    
    def predict(self, X):
        pass
    
    def fit_predict(self, X):
        pass
