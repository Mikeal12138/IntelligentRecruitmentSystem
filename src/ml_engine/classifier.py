import torch
import torch.nn as nn


class NeuralClassifier:
    def __init__(self, input_size, hidden_size, num_classes):
        self.model = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, num_classes)
        )
    
    def train(self, X, y, epochs=100):
        pass
    
    def predict(self, X):
        pass
    
    def save(self, filepath: str):
        pass
    
    def load(self, filepath: str):
        pass
