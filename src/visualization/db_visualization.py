"""
数据库可视化服务
功能：
1. 从数据库加载数据用于可视化
2. 支持实时数据查询
3. 与Streamlit前端集成
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.data_pipeline.db_manager import DatabaseManager


class DatabaseVisualization:
    """数据库可视化服务"""
    
    def __init__(self, use_database=True):
        self.use_database = use_database
        self.db_manager = None
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """加载数据（优先数据库，备选CSV）"""
        # 优先从数据库加载
        if self.use_database:
            self.df = self._load_from_database()
        
        # 如果数据库加载失败，从CSV加载
        if self.df is None or self.df.empty:
            self.df = self._load_from_csv()
    
    def _load_from_database(self):
        """从数据库加载数据"""
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.connect()
            
            if self.db_manager.connection and self.db_manager.connection.is_connected():
                query = "SELECT * FROM recruitment_data"
                df = pd.read_sql(query, self.db_manager.connection)
                print(f"[DBViz] 从数据库加载 {len(df)} 条数据")
                return df
            else:
                print("[DBViz] 数据库连接失败")
                return None
        except Exception as e:
            print(f"[DBViz] 数据库加载失败：{e}")
            return None
    
    def _load_from_csv(self):
        """从CSV加载数据"""
        csv_paths = [
            os.path.join(ROOT_DIR, 'data', 'processed', 'cleaned_recruitment_data(1).csv'),
            os.path.join(ROOT_DIR, 'data', 'cleaned_recruitment_data.csv'),
        ]
        
        for csv_path in csv_paths:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
                print(f"[DBViz] 从CSV加载 {len(df)} 条数据")
                return df
        
        print("[DBViz] 未找到CSV文件")
        return pd.DataFrame()
    
    def get_data(self):
        """获取数据集"""
        return self.df
    
    def get_data_source(self):
        """获取数据源类型"""
        if self.db_manager and self.db_manager.connection and self.db_manager.connection.is_connected():
            return "MySQL 数据库"
        else:
            return "CSV 文件"
    
    def query_custom(self, sql):
        """执行自定义SQL查询"""
        if self.db_manager and self.db_manager.connection and self.db_manager.connection.is_connected():
            return pd.read_sql(sql, self.db_manager.connection)
        return pd.DataFrame()
    
    def close(self):
        """关闭数据库连接"""
        if self.db_manager:
            self.db_manager.disconnect()
