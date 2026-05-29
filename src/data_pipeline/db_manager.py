"""
MySQL 数据库管理模块
功能：
1. 数据库连接管理
2. 自动创建表结构
3. 批量导入 CSV 数据
4. 数据查询和验证
"""
import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class DatabaseManager:
    """MySQL 数据库管理器"""
    
    def __init__(self, config: Dict = None):
        """初始化数据库配置"""
        if config is None:
            self.config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", 3306)),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
                "database": os.getenv("DB_NAME", "recruitment_db"),
                "charset": "utf8mb4"
            }
        else:
            self.config = config
        
        self.connection = None
        self.table_name = "recruitment_data"
    
    def connect(self) -> Optional[mysql.connector.MySQLConnection]:
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print(f"[DB] 成功连接到数据库：{self.config['database']}")
                return self.connection
        except Error as e:
            print(f"[DB] 连接失败：{e}")
            return None
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[DB] 数据库连接已关闭")
    
    def create_database(self, db_name: str = None) -> bool:
        """创建数据库（如果不存在）"""
        db_name = db_name or self.config['database']
        
        try:
            # 先连接到 MySQL（不指定数据库）
            temp_config = self.config.copy()
            temp_config.pop('database')
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {db_name} "
                f"DEFAULT CHARACTER SET utf8mb4 "
                f"COLLATE utf8mb4_unicode_ci"
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"[DB] 数据库 {db_name} 创建成功（或已存在）")
            return True
        except Error as e:
            print(f"[DB] 创建数据库失败：{e}")
            return False
    
    def create_table(self, table_name: str = None) -> bool:
        """创建招聘数据表"""
        table_name = table_name or self.table_name
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
            企业名称 VARCHAR(255) COMMENT '企业名称',
            招聘岗位 VARCHAR(255) COMMENT '招聘岗位',
            工作城市 VARCHAR(100) COMMENT '工作城市',
            最低月薪 DECIMAL(10,2) COMMENT '最低月薪',
            最高月薪 DECIMAL(10,2) COMMENT '最高月薪',
            职位描述 TEXT COMMENT '职位描述',
            学历要求 VARCHAR(50) COMMENT '学历要求',
            要求经验 VARCHAR(50) COMMENT '要求经验',
            招聘类别 VARCHAR(50) COMMENT '招聘类别',
            初级分类 VARCHAR(100) COMMENT '初级分类',
            招聘发布日期 VARCHAR(50) COMMENT '招聘发布日期',
            招聘发布年份 INT COMMENT '招聘发布年份',
            来源 VARCHAR(100) COMMENT '数据来源',
            学历要求_排序 INT COMMENT '学历要求排序',
            要求经验_排序 INT COMMENT '要求经验排序',
            平均月薪 DECIMAL(10,2) COMMENT '平均月薪',
            薪资浮动 DECIMAL(10,2) COMMENT '薪资浮动',
            薪资等级 VARCHAR(50) COMMENT '薪资等级',
            企业规模 VARCHAR(100) COMMENT '企业规模',
            行业类型 VARCHAR(100) COMMENT '行业类型',
            年终奖估算 DECIMAL(10,2) COMMENT '年终奖估算',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '数据导入时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='招聘数据总表';
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
            cursor.close()
            print(f"[DB] 表 {table_name} 创建成功（或已存在）")
            return True
        except Error as e:
            print(f"[DB] 建表失败：{e}")
            return False
    
    def batch_insert(self, df: pd.DataFrame, batch_size: int = 1000, 
                     progress_callback=None) -> int:
        """批量插入数据"""
        if df.empty:
            print("[DB] 数据为空，跳过插入")
            return 0
        
        # 准备插入的列（排除 create_time）
        insert_columns = [col for col in df.columns]
        placeholders = ", ".join(["%s"] * len(insert_columns))
        insert_sql = f"""
            INSERT INTO {self.table_name} ({', '.join(insert_columns)}) 
            VALUES ({placeholders})
        """
        
        total_rows = len(df)
        success_count = 0
        
        try:
            cursor = self.connection.cursor()
            
            # 分批次插入
            for i in range(0, total_rows, batch_size):
                batch_data = df.iloc[i:i+batch_size].values.tolist()
                cursor.executemany(insert_sql, batch_data)
                self.connection.commit()
                success_count += len(batch_data)
                
                # 更新进度
                if progress_callback:
                    progress_callback(success_count, total_rows)
                else:
                    print(f"[DB] 导入进度：{success_count}/{total_rows} ({success_count/total_rows*100:.1f}%)")
            
            cursor.close()
            print(f"[DB] 成功导入 {success_count} 条数据")
            return success_count
            
        except Error as e:
            self.connection.rollback()
            print(f"[DB] 数据导入失败：{e}")
            return 0
    
    def get_record_count(self) -> int:
        """获取表中的记录数"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error as e:
            print(f"[DB] 查询记录数失败：{e}")
            return 0
    
    def query_data(self, limit: int = 10, offset: int = 0) -> pd.DataFrame:
        """查询数据"""
        try:
            query_sql = f"""
                SELECT * FROM {self.table_name} 
                ORDER BY id DESC 
                LIMIT {limit} OFFSET {offset}
            """
            df = pd.read_sql(query_sql, self.connection)
            return df
        except Error as e:
            print(f"[DB] 查询失败：{e}")
            return pd.DataFrame()
    
    def clear_table(self) -> bool:
        """清空表数据"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name}")
            self.connection.commit()
            cursor.close()
            print(f"[DB] 表 {self.table_name} 已清空")
            return True
        except Error as e:
            print(f"[DB] 清空表失败：{e}")
            return False
    
    def drop_table(self) -> bool:
        """删除表"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
            self.connection.commit()
            cursor.close()
            print(f"[DB] 表 {self.table_name} 已删除")
            return True
        except Error as e:
            print(f"[DB] 删除表失败：{e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
