import streamlit as st
import os

# 获取项目根目录和可视化目录
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(APP_DIR)
VIZ_DIR = os.path.join(ROOT_DIR, 'visualization')

def display_category(category_name, folder_path, images):
    """显示一个分类下的所有图表"""
    if os.path.exists(folder_path):
        with st.expander(f"{category_name}", expanded=True):
            st.markdown(f"### {category_name}")
            
            # 每行显示2张图
            for i in range(0, len(images), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        img_name, title = images[i + j]
                        img_path = os.path.join(folder_path, img_name)
                        with col:
                            with st.container(border=True):
                                st.subheader(title)
                                if os.path.exists(img_path):
                                    st.image(img_path)
                                else:
                                    st.warning(f"图片未找到: {img_name}")

def main():
    st.set_page_config(page_title="数据可视化大屏", page_icon="📊", layout="wide")
    st.title("📊 数据可视化大屏")
    
    # ========== 图表分类筛选 ==========
    st.sidebar.header("🔍 图表筛选")
    categories = {
        "全部": ["薪资分析", "企业分析", "岗位技能", "学历经验", "行业技术", "技能分析", "聚类分析", "招聘类别"],
        "💰 薪资分析": ["薪资分析"],
        "🏢 企业分析": ["企业分析"],
        "🛠️ 岗位技能": ["岗位技能"],
        "🎓 学历经验": ["学历经验"],
        "🔥 行业技术": ["行业技术"],
        "🔍 技能分析": ["技能分析"],
        "🎯 聚类分析": ["聚类分析"],
        "📋 招聘类别": ["招聘类别"]
    }
    
    selected_category = st.sidebar.radio(
        "选择图表分类",
        list(categories.keys()),
        index=0
    )
    
    show_categories = categories[selected_category]
    
    # ========== 薪资分析 ==========
    if "薪资分析" in show_categories:
        display_category(" 薪资分析", 
                        os.path.join(VIZ_DIR, '薪资分析'),
                        [
                            ('01_Top15岗位平均月薪.png', 'Top 15 岗位平均月薪'),
                            ('02_薪资等级分布.png', '薪资等级分布'),
                            ('03_各行业平均薪资.png', '各行业平均薪资'),
                            ('04_薪资等级箱线图.png', '薪资等级箱线图'),
                            ('05_年终奖Top10行业.png', '年终奖 Top 10 行业'),
                            ('06_月薪年终奖关系.png', '月薪与年终奖关系')
                        ])
    
    # ========== 企业分析 ==========
    if "企业分析" in show_categories:
        display_category("🏢 企业分析",
                        os.path.join(VIZ_DIR, '企业分析'),
                        [
                            ('01_工作城市分布.png', '工作城市分布'),
                            ('02_行业类型分布.png', '行业类型分布'),
                            ('03_企业规模分布.png', '企业规模分布'),
                            ('04_城市行业热力图.png', '城市 × 行业热力图')
                        ])
    
    # ========== 岗位技能（排除已展示的词云） ==========
    if "岗位技能" in show_categories:
        display_category("🛠️ 岗位技能",
                        os.path.join(VIZ_DIR, '岗位技能'),
                        [
                            ('02_技能关键词Top20.png', '技能关键词 Top 20')
                        ])
    
    # ========== 学历经验 ==========
    if "学历经验" in show_categories:
        display_category("🎓 学历经验",
                        os.path.join(VIZ_DIR, '学历经验'),
                        [
                            ('01_学历要求分布.png', '学历要求分布'),
                            ('02_经验要求分布.png', '经验要求分布'),
                            ('03_学历vs薪资.png', '学历 vs 薪资'),
                            ('04_经验vs薪资.png', '经验 vs 薪资')
                        ])
    
    # ========== 行业技术（排除已展示的词云） ==========
    if "行业技术" in show_categories:
        display_category("🔥 行业技术",
                        os.path.join(VIZ_DIR, '行业技术'),
                        [
                            ('01_各行业岗位数量分布.png', '各行业岗位数量分布'),
                            ('02_技术关键词热度.png', '技术关键词热度')
                        ])
    
    # ========== 技能分析 ==========
    if "技能分析" in show_categories:
        display_category("🔍 技能分析",
                        os.path.join(VIZ_DIR, '技能分析'),
                        [
                            ('02_岗位技能热力图.png', '岗位-技能出现频率热力图')
                        ])
    
    # ========== 聚类分析 ==========
    if "聚类分析" in show_categories:
        display_category("🎯 聚类分析",
                        os.path.join(VIZ_DIR, '聚类分析'),
                        [
                            ('03_岗位描述聚类降维.png', '岗位描述聚类降维')
                        ])
    
    # ========== 招聘类别 ==========
    if "招聘类别" in show_categories:
        display_category("📋 招聘类别",
                        os.path.join(VIZ_DIR, '招聘类别'),
                        [
                            ('01_招聘类别分布.png', '招聘类别分布')
                        ])


if __name__ == "__main__":
    main()
