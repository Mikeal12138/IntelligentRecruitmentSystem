import streamlit as st
import sys
import os

# 获取项目根目录
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(APP_DIR)
VIZ_DIR = os.path.join(ROOT_DIR, 'visualization')

def main():
    st.set_page_config(page_title="岗位词云与需求", page_icon="☁️", layout="wide")
    st.title("️ 岗位词云与需求")
    
    # ========== 图表分类筛选 ==========
    st.sidebar.header(" 图表筛选")
    categories = {
        "全部": ["skill", "industry"],
        "🛠️ 岗位技能": ["skill"],
        "🔥 行业技术": ["industry"]
    }
    
    selected_category = st.sidebar.radio(
        "选择图表分类",
        list(categories.keys()),
        index=0
    )
    
    show_categories = categories[selected_category]
    
    # ========== 岗位技能词云 ==========
    if "skill" in show_categories:
        with st.expander("🛠️ 岗位技能", expanded=True):
            st.markdown("### 🛠️ 岗位技能")
            st.caption("展示岗位描述与招聘职位中的核心关键词")
            
            col1, col2 = st.columns(2)
            
            # 01_技能需求词云.png
            with col1:
                with st.container(border=True):
                    st.subheader("岗位技能需求词云")
                    st.caption("基于岗位描述提取的技能关键词云")
                    img_path = os.path.join(VIZ_DIR, '岗位技能', '01_技能需求词云.png')
                    if os.path.exists(img_path):
                        st.image(img_path, use_column_width=True)
                    else:
                        st.warning("图片未找到")
            
            # 03_招聘职位关键词词云.png
            with col2:
                with st.container(border=True):
                    st.subheader("招聘职位关键词词云")
                    st.caption("基于招聘岗位名称提取的关键词云")
                    img_path = os.path.join(VIZ_DIR, '岗位技能', '03_招聘职位关键词词云.png')
                    if os.path.exists(img_path):
                        st.image(img_path, use_column_width=True)
                    else:
                        st.warning("图片未找到")
    
    # ========== 行业技术词云 ==========
    if "industry" in show_categories:
        with st.expander(" 行业技术", expanded=True):
            st.markdown("### 🔥 行业技术")
            st.caption("展示行业技术热点与福利待遇关键词")
            
            col1, col2 = st.columns(2)
            
            # 03_技术热点词云.png
            with col1:
                with st.container(border=True):
                    st.subheader("行业技术热点词云")
                    st.caption("行业技术关键词热度分布")
                    img_path = os.path.join(VIZ_DIR, '行业技术', '03_技术热点词云.png')
                    if os.path.exists(img_path):
                        st.image(img_path, use_column_width=True)
                    else:
                        st.warning("图片未找到")
            
            # 04_福利待遇词云.png
            with col2:
                with st.container(border=True):
                    st.subheader("福利待遇关键词词云")
                    st.caption("岗位福利待遇关键词分布")
                    img_path = os.path.join(VIZ_DIR, '行业技术', '04_福利待遇词云.png')
                    if os.path.exists(img_path):
                        st.image(img_path, use_column_width=True)
                    else:
                        st.warning("图片未找到")


if __name__ == "__main__":
    main()
