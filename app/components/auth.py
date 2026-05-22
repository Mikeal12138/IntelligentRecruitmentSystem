import streamlit as st


def login_form():
    with st.form("login_form"):
        st.subheader("用户登录")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("登录")
        
        if submitted:
            return username, password
    return None, None


def register_form():
    with st.form("register_form"):
        st.subheader("用户注册")
        username = st.text_input("用户名")
        email = st.text_input("邮箱")
        password = st.text_input("密码", type="password")
        confirm_password = st.text_input("确认密码", type="password")
        submitted = st.form_submit_button("注册")
        
        if submitted:
            return username, email, password, confirm_password
    return None, None, None, None
