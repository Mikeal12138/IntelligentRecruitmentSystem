import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import os

# 导入认证模块
from components.auth import init_auth_state, show_auth_page, logout

# 初始化认证状态
init_auth_state()

# 检查登录状态
if not st.session_state.get('logged_in', False):
    st.set_page_config(
        page_title="登录 - 智能招聘助手", 
        page_icon="💼", 
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    st.title(" 智能招聘助手")
    st.markdown("### 欢迎使用智能招聘系统")
    st.caption("基于AI的智能招聘分析与推荐平台")
    st.divider()
    
    show_auth_page()
    st.stop()

# 页面配置（已登录状态）
st.set_page_config(
    page_title="智能招聘助手",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 获取项目根目录
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(APP_DIR)

# 全局数据加载（使用缓存，只加载一次）
@st.cache_data(ttl=3600)
def load_data():
    """加载招聘数据"""
    try:
        csv_path = os.path.join(ROOT_DIR, 'data', 'cleaned_recruitment_data.csv')
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df
    except FileNotFoundError:
        st.warning("未找到数据文件，使用示例数据")
        return create_sample_data()
    except Exception as e:
        st.error(f"数据加载失败：{str(e)}")
        return create_sample_data()

def create_sample_data():
    """创建示例数据"""
    data = {
        'job_title': ['Java开发工程师', 'Python开发工程师', '前端开发工程师', '产品经理', '数据分析师'],
        'company_name': ['腾讯', '阿里巴巴', '字节跳动', '美团', '京东'],
        'location': ['北京', '上海', '杭州', '深圳', '广州'],
        'min_salary': [15000, 18000, 12000, 20000, 15000],
        'max_salary': [25000, 30000, 20000, 35000, 25000],
        'avg_salary': [20000, 24000, 16000, 27500, 20000],
        'experience': ['3-5年', '3-5年', '1-3年', '5-10年', '3-5年'],
        'education': ['本科', '本科', '本科', '本科', '硕士'],
        'company_size': ['1000-5000人', '10000人以上', '10000人以上', '10000人以上', '10000人以上'],
        'industry': ['互联网', '互联网', '互联网', '互联网', '互联网'],
        'job_description': ['负责Java后端开发，熟悉Spring Boot框架',
                          '负责Python后端开发，熟悉Django/Flask',
                          '负责前端开发，熟悉Vue/React',
                          '负责产品设计和需求分析',
                          '负责数据分析和可视化']
    }
    return pd.DataFrame(data)

# 加载数据
df = load_data()

# 字段映射（CSV中文列名 -> 代码使用的列名）
COLUMN_MAP = {
    '企业名称': 'company_name',
    '招聘岗位': 'job_title',
    '工作城市': 'location',
    '最低月薪': 'min_salary',
    '最高月薪': 'max_salary',
    '职位描述': 'job_description',
    '学历要求': 'education',
    '要求经验': 'experience',
    '平均月薪': 'avg_salary',
    '企业规模': 'company_size',
    '行业类型': 'industry',
    '薪资等级': 'salary_level',
    '年终奖估算': 'year_end_bonus'
}

# 重命名列名
df = df.rename(columns=COLUMN_MAP)

# 侧边栏导航
st.sidebar.title(" 智能招聘助手")

# 显示用户信息和登出按钮
if st.session_state.get('user'):
    st.sidebar.write(f"👤 当前用户：{st.session_state['user']['username']}")
    if st.sidebar.button("🔓 退出登录"):
        logout()

st.sidebar.divider()
st.sidebar.info(f"系统已收录 {len(df)} 条招聘数据")

# 页面内容 - 直接显示首页内容
st.title("🏠 欢迎使用智能招聘助手")
st.markdown("### 📊 基于15000+条招聘数据的智能分析与推荐系统")

st.divider()

# 显示数据集基本信息
st.subheader("📈 数据集基本信息")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总岗位数", f"{len(df):,}")
with col2:
    st.metric("平均薪资", f"¥{df['avg_salary'].mean():,.0f}")
with col3:
    st.metric("覆盖城市数", df['location'].nunique())
with col4:
    st.metric("企业数量", df['company_name'].nunique())

st.divider()

# 数据集详细统计
st.subheader("📊 数据统计详情")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🏢 企业规模分布**")
    company_size_dist = df['company_size'].value_counts().head(5)
    for size, count in company_size_dist.items():
        st.write(f"• {size}: {count} 个岗位")

with col2:
    st.markdown("**🎓 学历要求分布**")
    education_dist = df['education'].value_counts()
    for edu, count in education_dist.items():
        st.write(f"• {edu}: {count} 个岗位")

st.divider()

# 项目功能介绍
st.subheader("🚀 系统功能模块")

features = [
    ("📊 数据可视化大屏", "多维度数据可视化，包括薪资分析、企业分析、技能词云等"),
    ("☁️ 岗位词云与需求", "展示岗位描述与招聘职位中的核心关键词"),
    (" 智能求职助手", "基于AI的求职建议与岗位推荐"),
    ("🔍 智能岗位搜索与筛选", "多维度搜索筛选，快速找到匹配岗位"),
    ("📂 简历智能解析与评估", "AI解析简历内容，评估匹配度"),
    ("💰 薪资谈判助手", "智能薪资分析与谈判策略建议"),
    ("🤝 面试辅助与评估", "面试问题预测与模拟面试评估"),
    ("📊 招聘数据导入数据库", "支持CSV数据批量导入MySQL数据库")
]

for icon_name, description in features:
    st.markdown(f"**{icon_name}**: {description}")

st.divider()

# 热门岗位TOP10
st.subheader(" 热门岗位 TOP 10")

top_jobs = df.groupby('job_title').size().sort_values(ascending=False).head(10)
fig = px.bar(
    x=top_jobs.values,
    y=top_jobs.index,
    orientation='h',
    labels={'x': '岗位数量', 'y': '岗位名称'},
    color=top_jobs.values,
    color_continuous_scale='Blues'
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# 薪资分布
st.subheader(" 薪资分布概览")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("最低薪资", f"¥{df['min_salary'].min():,}")
with col2:
    st.metric("25%分位", f"¥{df['avg_salary'].quantile(0.25):,.0f}")
with col3:
    st.metric("中位数", f"¥{df['avg_salary'].median():,.0f}")
with col4:
    st.metric("75%分位", f"¥{df['avg_salary'].quantile(0.75):,.0f}")
with col5:
    st.metric("最高薪资", f"¥{df['max_salary'].max():,}")
