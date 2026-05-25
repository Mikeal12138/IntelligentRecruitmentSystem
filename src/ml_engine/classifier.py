import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split


class _NeuralNet(nn.Module):
    """深层神经网络: 多层 Linear + BatchNorm + ReLU + Dropout"""
    def __init__(self, input_size, hidden_size, num_classes, dropout=0.3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.BatchNorm1d(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.BatchNorm1d(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_classes),
        )

    def forward(self, x):
        return self.network(x)


class NeuralClassifier:
    def __init__(self, input_size, hidden_size=128, num_classes=10,
                 learning_rate=0.001, dropout=0.3, device=None):
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = torch.device(device)
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_classes = num_classes
        self.lr = learning_rate
        self.dropout = dropout

        self.model = _NeuralNet(input_size, hidden_size, num_classes, dropout)
        self.model.to(self.device)
        self._label_encoder = None  # 外部设置
        self._is_trained = False

    def _to_tensor(self, X):
        if isinstance(X, np.ndarray):
            return torch.FloatTensor(X)
        # 支持 scipy sparse matrix
        if hasattr(X, 'toarray'):
            return torch.FloatTensor(X.toarray())
        return torch.FloatTensor(X)

    def train(self, X, y, epochs=100, batch_size=128, val_ratio=0.2,
              patience=15, verbose=True):
        """
        训练神经网络
        X: 特征矩阵 (numpy array 或 scipy sparse)
        y: 标签 (整数数组)
        返回: 训练历史记录 dict
        """
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=val_ratio, random_state=42, stratify=y
        )

        X_train_t = self._to_tensor(X_train).to(self.device)
        X_val_t = self._to_tensor(X_val).to(self.device)
        y_train_t = torch.LongTensor(y_train).to(self.device)
        y_val_t = torch.LongTensor(y_val).to(self.device)

        train_ds = TensorDataset(X_train_t, y_train_t)
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.5)

        history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
        best_val_acc = 0
        best_state = None
        wait = 0

        for epoch in range(epochs):
            # Training
            self.model.train()
            total_loss = 0
            correct = 0
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item() * len(batch_y)
                correct += (outputs.argmax(1) == batch_y).sum().item()

            train_loss = total_loss / len(X_train)
            train_acc = correct / len(X_train)

            # Validation
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val_t)
                val_loss = criterion(val_outputs, y_val_t).item()
                val_correct = (val_outputs.argmax(1) == y_val_t).sum().item()
            val_acc = val_correct / len(X_val)

            scheduler.step()
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['train_acc'].append(train_acc)
            history['val_acc'].append(val_acc)

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_state = {k: v.clone() for k, v in self.model.state_dict().items()}
                wait = 0
            else:
                wait += 1

            if verbose and (epoch % 10 == 0 or epoch == epochs - 1):
                print(f"  [NN] Epoch {epoch:3d} | train_loss={train_loss:.4f} train_acc={train_acc:.4f} | val_loss={val_loss:.4f} val_acc={val_acc:.4f}")

            if wait >= patience:
                if verbose:
                    print(f"  [NN] Early stopping at epoch {epoch}, best val_acc={best_val_acc:.4f}")
                break

        # 恢复最优模型
        if best_state is not None:
            self.model.load_state_dict(best_state)
        self._is_trained = True
        return history

    def predict(self, X, return_proba=False):
        """
        预测类别
        return_proba=True 时返回 (类别, 概率分布)
        """
        if not self._is_trained:
            raise RuntimeError("模型尚未训练，请先调用 train()")

        self.model.eval()
        X_t = self._to_tensor(X).to(self.device)
        with torch.no_grad():
            outputs = self.model(X_t)
            probs = torch.softmax(outputs, dim=1)
            preds = probs.argmax(1).cpu().numpy()

        if return_proba:
            return preds, probs.cpu().numpy()
        return preds

    def save(self, filepath: str):
        """保存模型权重和元数据"""
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        checkpoint = {
            'state_dict': self.model.state_dict(),
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'num_classes': self.num_classes,
            'lr': self.lr,
            'dropout': self.dropout,
        }
        torch.save(checkpoint, filepath)
        print(f"  [NN] 模型已保存至 {filepath}")

    def load(self, filepath: str, device=None):
        """加载模型权重和元数据"""
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = torch.device(device)

        checkpoint = torch.load(filepath, map_location=self.device, weights_only=True)
        self.input_size = checkpoint['input_size']
        self.hidden_size = checkpoint['hidden_size']
        self.num_classes = checkpoint['num_classes']
        self.lr = checkpoint['lr']
        self.dropout = checkpoint['dropout']

        self.model = _NeuralNet(self.input_size, self.hidden_size, self.num_classes, self.dropout)
        self.model.load_state_dict(checkpoint['state_dict'])
        self.model.to(self.device)
        self._is_trained = True
        print(f"  [NN] 模型已从 {filepath} 加载 (device={self.device})")
