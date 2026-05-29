"""
招聘数据 CSV 导入 MySQL 数据库
功能：
1. 数据库连接测试
2. CSV 数据预览
3. 自动创建表结构
4. 批量导入数据
5. 导入结果验证
"""
import streamlit as st
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, 'config', '.env'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.data_pipeline.db_manager import DatabaseManager

# 页面配置
st.set_page_config(
    page_title="招聘数据导入MySQL",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 Session State
if 'db_config' not in st.session_state:
    st.session_state.db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "recruitment_db"),
        "charset": "utf8mb4"
    }

if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

if 'db_manager' not in st.session_state:
    st.session_state.db_manager = None

# 侧边栏
st.sidebar.title("📊 数据导入")
st.sidebar.info("将 CSV 招聘数据导入 MySQL 数据库")

st.sidebar.divider()
st.sidebar.subheader("⚙️ 数据库配置")

# 数据库配置表单
with st.sidebar.form("db_config_form"):
    host = st.text_input("主机地址", value=st.session_state.db_config["host"])
    port = st.number_input("端口", value=st.session_state.db_config["port"])
    user = st.text_input("用户名", value=st.session_state.db_config["user"])
    password = st.text_input("密码", type="password", value=st.session_state.db_config["password"])
    database = st.text_input("数据库名", value=st.session_state.db_config["database"])
    
    submitted = st.form_submit_button("更新配置", use_container_width=True)
    
    if submitted:
        st.session_state.db_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": "utf8mb4"
        }
        st.success("✅ 配置已更新")

# 主页面
st.title("📊 招聘数据 CSV 导入 MySQL 数据库")
st.write("支持批量导入 15000+ 条招聘数据，自动建表、分批插入、进度显示")

# 步骤指示器
st.markdown("---")
st.markdown("### 📋 导入步骤")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.info("**步骤 1**：连接数据库")
with col2:
    st.info("**步骤 2**：加载 CSV 数据")
with col3:
    st.info("**步骤 3**：创建表结构")
with col4:
    st.info("**步骤 4**：批量导入")

st.markdown("---")

# 步骤 1：连接数据库
st.subheader("🔌 步骤 1：连接数据库")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 测试连接", type="primary", use_container_width=True):
        with st.spinner("正在连接数据库..."):
            db = DatabaseManager(st.session_state.db_config)
            conn = db.connect()
            
            if conn:
                st.success("🎉 数据库连接成功！")
                st.session_state.db_manager = db
                
                # 显示数据库信息
                cursor = conn.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()
                
                st.info(f"数据库版本：MySQL {version}")
                conn.close()
            else:
                st.error("❌ 数据库连接失败，请检查配置")

with col2:
    if st.button("🗄️ 创建数据库", use_container_width=True):
        with st.spinner("正在创建数据库..."):
            db = DatabaseManager(st.session_state.db_config)
            if db.create_database():
                st.success(f"✅ 数据库 {st.session_state.db_config['database']} 创建成功")
            else:
                st.error("❌ 数据库创建失败")

# 步骤 2：加载 CSV 数据
st.subheader("📂 步骤 2：加载 CSV 数据")

csv_path = os.path.join(ROOT, 'data', 'processed', 'cleaned_recruitment_data(1).csv')

if os.path.exists(csv_path):
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 加载 CSV 数据", type="primary", use_container_width=True):
            with st.spinner("正在加载数据..."):
                df = pd.read_csv(csv_path, encoding='utf-8')
                st.session_state.csv_data = df
                st.success(f"✅ 数据加载完成：{len(df)} 行 × {len(df.columns)} 列")
    
    with col2:
        if st.session_state.csv_data is not None:
            st.success("✅ 数据已加载")
        else:
            st.warning("⚠️ 尚未加载数据")
    
    # 显示数据预览
    if st.session_state.csv_data is not None:
        st.markdown("---")
        st.write("**数据预览：**")
        st.dataframe(st.session_state.csv_data.head(10), use_container_width=True)
        
        # 显示数据统计
        st.markdown("---")
        st.write("**数据统计：**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总记录数", len(st.session_state.csv_data))
        with col2:
            st.metric("字段数", len(st.session_state.csv_data.columns))
        with col3:
            st.metric("平均月薪", f"¥{st.session_state.csv_data['平均月薪'].mean():.0f}")
        with col4:
            st.metric("企业数量", st.session_state.csv_data['企业名称'].nunique())
else:
    st.warning(f"⚠️ 未找到 CSV 文件：{csv_path}")
    st.info("请确保数据文件存在于正确路径")

# 步骤 3：创建表结构
st.subheader("🏗️ 步骤 3：创建表结构")

if st.session_state.db_manager is None:
    st.warning("⚠️ 请先连接数据库")
else:
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔨 创建数据表", type="primary", use_container_width=True):
            with st.spinner("正在创建表结构..."):
                db = DatabaseManager(st.session_state.db_config)
                conn = db.connect()
                
                if conn:
                    if db.create_table():
                        st.success("✅ 表结构创建成功")
                    else:
                        st.error("❌ 表结构创建失败")
                    conn.close()
                else:
                    st.error("❌ 数据库连接失败")
    
    with col2:
        if st.button("🗑️ 清空现有数据", use_container_width=True):
            with st.spinner("正在清空数据..."):
                db = DatabaseManager(st.session_state.db_config)
                conn = db.connect()
                
                if conn:
                    if st.session_state.get('confirm_clear'):
                        if db.clear_table():
                            st.success("✅ 数据已清空")
                        conn.close()
                    else:
                        st.warning("⚠️ 请再次点击确认清空")
                        st.session_state.confirm_clear = True
                else:
                    st.error("❌ 数据库连接失败")

# 步骤 4：批量导入数据
st.subheader("📥 步骤 4：批量导入数据")

if st.session_state.db_manager is None:
    st.warning("⚠️ 请先连接数据库")
elif st.session_state.csv_data is None:
    st.warning("⚠️ 请先加载 CSV 数据")
else:
    # 导入配置
    col1, col2, col3 = st.columns(3)
    with col1:
        batch_size = st.number_input("每批导入数量", value=1000, min_value=100, max_value=5000, step=100)
    with col2:
        st.write(f"总数据量：{len(st.session_state.csv_data)} 行")
    with col3:
        estimated_batches = len(st.session_state.csv_data) // batch_size + 1
        st.write(f"预计批次：{estimated_batches}")
    
    st.markdown("---")
    
    # 导入按钮
    if st.button("🚀 开始导入数据", type="primary", use_container_width=True):
        with st.spinner("正在初始化导入..."):
            db = DatabaseManager(st.session_state.db_config)
            conn = db.connect()
            
            if conn:
                # 创建进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 定义进度回调函数
                def update_progress(current, total):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"📥 正在导入：{current}/{total} 行 ({progress*100:.1f}%)")
                
                # 批量导入
                status_text.text("📥 开始导入数据...")
                success_count = db.batch_insert(
                    st.session_state.csv_data,
                    batch_size=int(batch_size),
                    progress_callback=update_progress
                )
                
                # 导入完成
                if success_count > 0:
                    progress_bar.progress(1.0)
                    status_text.text(f"✅ 导入完成：{success_count} 行")
                    st.success(f"🎉 成功导入 {success_count} 条数据到数据库！")
                    
                    # 验证结果
                    st.markdown("---")
                    st.subheader("✅ 导入结果验证")
                    
                    total_count = db.get_record_count()
                    st.metric("数据库中总记录数", total_count)
                    
                    # 显示最新数据
                    st.write("**最新导入的数据：**")
                    latest_data = db.query_data(limit=5)
                    if not latest_data.empty:
                        st.dataframe(latest_data, use_container_width=True)
                else:
                    st.error("❌ 数据导入失败，请检查日志")
                
                conn.close()
            else:
                st.error("❌ 数据库连接失败")

# 帮助信息
st.markdown("---")
st.subheader("💡 使用说明")

with st.expander("📖 如何配置 MySQL 数据库？"):
    st.markdown("""
    1. **安装 MySQL**：从官网下载并安装 MySQL Server
    2. **启动服务**：确保 MySQL 服务正在运行（默认端口 3306）
    3. **创建数据库**：
       ```sql
       CREATE DATABASE IF NOT EXISTS recruitment_db 
       DEFAULT CHARACTER SET utf8mb4 
       COLLATE utf8mb4_unicode_ci;
       ```
    4. **配置环境变量**：在 `config/.env` 文件中填写数据库信息
    5. **安装依赖**：`pip install mysql-connector-python`
    """)

with st.expander("⚠️ 常见问题"):
    st.markdown("""
    - **连接失败**：检查 MySQL 服务是否启动、端口是否正确、用户名密码是否正确
    - **中文乱码**：确保数据库和表使用 utf8mb4 字符集
    - **导入超时**：减小每批导入数量（建议 500-1000）
    - **权限错误**：确保数据库用户有 CREATE 和 INSERT 权限
    """)

with st.expander("📊 数据字段说明"):
    st.markdown("""
    | 字段名 | 类型 | 说明 |
    |--------|------|------|
    | 企业名称 | VARCHAR(255) | 招聘企业名称 |
    | 招聘岗位 | VARCHAR(255) | 岗位名称 |
    | 工作城市 | VARCHAR(100) | 工作地点 |
    | 最低月薪 | DECIMAL(10,2) | 最低薪资（元） |
    | 最高月薪 | DECIMAL(10,2) | 最高薪资（元） |
    | 职位描述 | TEXT | 岗位要求和职责 |
    | 学历要求 | VARCHAR(50) | 最低学历要求 |
    | 要求经验 | VARCHAR(50) | 工作经验要求 |
    | ... | ... | 其他字段 |
    """)
