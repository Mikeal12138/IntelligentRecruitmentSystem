import jieba
from sklearn.feature_extraction.text import TfidfVectorizer


class NLPProcessor:
    def __init__(self):
        self.stopwords = set()
        self.vectorizer = TfidfVectorizer()
    
    def load_stopwords(self, filepath: str):
        pass
    
    def tokenize(self, text: str) -> list:
        pass
    
    def remove_stopwords(self, tokens: list) -> list:
        pass
    
    def vectorize(self, texts: list):
        pass
