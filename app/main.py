import streamlit as st


def main():
    st.set_page_config(
        page_title="智能招聘系统",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("欢迎使用智能招聘系统")
    st.markdown("---")
    
    st.sidebar.title("导航菜单")
    
    st.write("请选择左侧菜单开始使用系统功能。")


if __name__ == "__main__":
    main()
