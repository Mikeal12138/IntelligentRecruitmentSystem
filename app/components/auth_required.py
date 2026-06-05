import streamlit as st
import sys
import os

# 添加上级目录到路径
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(APP_DIR)

from components.auth import init_auth_state, show_auth_page

def auth_required(func):
    """页面认证装饰器"""
    def wrapper(*args, **kwargs):
        init_auth_state()
        
        # 检查登录状态
        if not st.session_state.get('logged_in', False):
            show_auth_page()
            st.stop()
        
        return func(*args, **kwargs)
    
    return wrapper

def check_auth():
    """检查认证状态，未登录则显示登录页面"""
    init_auth_state()
    
    if not st.session_state.get('logged_in', False):
        show_auth_page()
        st.stop()
