import streamlit as st
import sqlite3
import hashlib
import os

# 获取数据库路径
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(APP_DIR, '..', 'data', 'users.db')

def init_db():
    """初始化用户数据库"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """注册新用户"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, hash_password(password))
        )
        conn.commit()
        return True, "注册成功"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "用户名已存在"
        elif "email" in str(e):
            return False, "邮箱已被注册"
        else:
            return False, "注册失败"
    finally:
        conn.close()

def login_user(username, password):
    """用户登录验证"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user and user[3] == hash_password(password):
        return True, "登录成功", {'id': user[0], 'username': user[1], 'email': user[2]}
    return False, "用户名或密码错误", None

def init_auth_state():
    """初始化认证状态"""
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

def show_login_form():
    """显示登录表单"""
    with st.form("login_form"):
        st.subheader("🔐 用户登录")
        st.caption("请输入您的账号信息")
        
        username = st.text_input("用户名", placeholder="请输入用户名")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("登录", use_container_width=True)
        with col2:
            pass
        
        if submitted:
            if not username or not password:
                st.error("请输入用户名和密码")
                return False
            success, message, user = login_user(username, password)
            if success:
                st.session_state['user'] = user
                st.session_state['logged_in'] = True
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    return False

def show_register_form():
    """显示注册表单"""
    with st.form("register_form"):
        st.subheader("📝 用户注册")
        st.caption("创建新账号")
        
        username = st.text_input("用户名", placeholder="请输入用户名")
        email = st.text_input("邮箱", placeholder="请输入邮箱")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        
        submitted = st.form_submit_button("注册", use_container_width=True)
        
        if submitted:
            if not username or not email or not password:
                st.error("请填写所有必填字段")
                return False
            if password != confirm_password:
                st.error("两次输入的密码不一致")
                return False
            if len(password) < 6:
                st.error("密码长度至少为6位")
                return False
            success, message = register_user(username, email, password)
            if success:
                st.success(message)
                st.info("注册成功，请登录")
                return True
            else:
                st.error(message)
    return False

def show_auth_page():
    """显示登录/注册页面"""
    # 使用选项卡切换登录和注册
    tab1, tab2 = st.tabs(["🔐 登录", "📝 注册"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        if show_register_form():
            # 注册成功后自动切换到登录标签页
            st.rerun()
    
    # 测试账户提示
    st.divider()
    st.markdown("""
    ---
    ** 测试账户：**
    - 用户名：`test`
    - 密码：`123456`
    """)

def logout():
    """登出"""
    st.session_state['user'] = None
    st.session_state['logged_in'] = False
    st.rerun()
