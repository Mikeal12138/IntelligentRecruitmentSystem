import sqlite3
import hashlib
import os

# 获取数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'users.db')

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db_with_test_user():
    """初始化数据库并添加测试用户"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 添加测试用户（如果不存在）
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            ('test', 'test@example.com', hash_password('123456'))
        )
        print("测试用户创建成功")
    except sqlite3.IntegrityError:
        print("测试用户已存在")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db_with_test_user()
    print(f"数据库文件: {DB_PATH}")
