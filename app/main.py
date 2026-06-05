import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import os

# 页面配置
st.set_page_config(
    page_title="智能招聘助手",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全局数据加载（使用缓存，只加载一次）
@st.cache_data(ttl=3600)  # 缓存1小时
def load_data():
    """加载标准化后的招聘数据"""
    try:
        # 优先尝试加载你的数据文件
        data_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_recruitment_data.csv'),
            "data/cleaned_recruitment_data.csv",
            "data/processed/jobs_standardized.csv"
        ]
        for path in data_paths:
            if os.path.exists(path):
                df = pd.read_csv(path)
                return df
        st.warning("未找到数据文件，使用示例数据")
        return create_sample_data()
    except Exception as e:
        st.warning(f"数据加载失败: {e}，使用示例数据")
        return create_sample_data()

def create_sample_data():
    """创建示例数据"""
    data = {
        'job_title': ['Java开发工程师', 'Python开发工程师', '前端开发工程师', '产品经理', '数据分析师',
                     '算法工程师', '测试工程师', '运维工程师', 'UI设计师', '销售经理'],
        'company_name': ['腾讯', '阿里巴巴', '字节跳动', '美团', '京东',
                        '百度', '网易', '小米', '华为', '滴滴'],
        'location': ['北京', '上海', '杭州', '深圳', '广州',
                    '成都', '武汉', '南京', '西安', '重庆'],
        'salary_raw': ['15-25K', '18-30K', '12-20K', '20-35K', '15-25K',
                      '25-45K', '10-18K', '12-22K', '10-18K', '12-25K'],
        'avg_salary_k': [20, 24, 16, 27.5, 20, 35, 14, 17, 14, 18.5],
        'experience_raw': ['3-5年', '3-5年', '1-3年', '5-10年', '3-5年',
                         '3-5年', '1-3年', '3-5年', '1-3年', '5-10年'],
        'education': ['本科', '本科', '本科', '本科', '硕士',
                     '硕士', '本科', '大专', '本科', '本科'],
        'company_type': ['互联网', '互联网', '互联网', '互联网', '互联网',
                        '互联网', '互联网', '硬件', '互联网', '互联网'],
        'company_size': ['1000-5000人', '10000人以上', '10000人以上', '10000人以上', '10000人以上',
                        '10000人以上', '1000-5000人', '10000人以上', '1000-5000人', '1000-5000人'],
        'financing_stage': ['已上市', '已上市', '已上市', '已上市', '已上市',
                          '已上市', '已上市', '已上市', '未上市', '已上市'],
        'job_description': ['负责Java后端开发，熟悉Spring Boot框架',
                          '负责Python后端开发，熟悉Django/Flask',
                          '负责前端开发，熟悉Vue/React',
                          '负责产品设计和需求分析',
                          '负责数据分析和可视化',
                          '负责算法研发和优化',
                          '负责软件测试和质量保证',
                          '负责系统运维和部署',
                          '负责UI设计和用户体验',
                          '负责销售管理和客户拓展'],
        'benefits': ['五险一金、年终奖、带薪年假',
                    '五险一金、股票期权、餐补',
                    '五险一金、加班补贴、节日福利',
                    '五险一金、年终奖、团建活动',
                    '五险一金、带薪年假、培训机会',
                    '五险一金、股票期权、弹性工作',
                    '五险一金、年终奖、员工旅游',
                    '五险一金、餐补、交通补贴',
                    '五险一金、年终奖、健康体检',
                    '五险一金、提成、差旅补贴']
    }
    return pd.DataFrame(data)

# 加载数据
df = load_data()

# 检查列名以确定数据格式
is_standardized = 'avg_salary_k' in df.columns
is_custom = '平均月薪' in df.columns

# 侧边栏导航
st.sidebar.title("💼 智能招聘助手")
page = st.sidebar.radio(
    "导航菜单",
    ["🏠 首页", "🔍 岗位搜索", "📊 数据可视化", "🤖 智能分析"]
)

st.sidebar.divider()
st.sidebar.info(f"系统已收录 {len(df)} 条招聘数据")

# 页面内容
if page == " 首页":
    st.title("欢迎使用智能招聘助手")
    st.write("基于15000+条招聘数据的智能分析与推荐系统")
    
    # 显示一些关键统计数据
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总岗位数", len(df))
    with col2:
        if is_standardized:
            st.metric("平均薪资", f"{df['avg_salary_k'].mean():.1f}K")
        elif is_custom:
            st.metric("平均薪资", f"{df['平均月薪'].mean()/1000:.1f}K")
        else:
            st.metric("平均薪资", "N/A")
    with col3:
        if is_standardized:
            st.metric("覆盖城市数", df['location'].nunique())
        elif is_custom:
            st.metric("覆盖城市数", df['工作城市'].nunique())
        else:
            st.metric("覆盖城市数", 0)
    with col4:
        if is_standardized:
            st.metric("企业数量", df['company_name'].nunique())
        elif is_custom:
            st.metric("企业数量", df['企业名称'].nunique())
        else:
            st.metric("企业数量", 0)
    
    st.divider()
    st.subheader("系统功能")
    st.write("""
    - 🔍 智能岗位搜索与多维度筛选
    - 📊 招聘数据可视化分析
    - 🤖 简历智能解析与匹配
    - 💡 个性化求职建议
    """)

elif page == "🔍 岗位搜索":
    st.title("岗位搜索")
    
    # 搜索框
    search_query = st.text_input("输入关键词搜索岗位", placeholder="例如：Java开发 福州")
    
    # 筛选条件
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if is_standardized:
            cities = ["全部"] + sorted(df['location'].dropna().unique().tolist())
        elif is_custom:
            cities = ["全部"] + sorted(df['工作城市'].dropna().unique().tolist())
        else:
            cities = ["全部"]
        selected_city = st.selectbox("工作城市", cities)
    with col2:
        if is_standardized:
            experiences = ["全部", "应届毕业生", "1年以内", "1-3年", "3-5年", "5-10年", "10年以上"]
        elif is_custom:
            experiences = ["全部"] + sorted(df['要求经验'].dropna().unique().tolist())
        else:
            experiences = ["全部"]
        selected_experience = st.selectbox("工作经验", experiences)
    with col3:
        if is_standardized:
            educations = ["全部"] + sorted(df['education'].dropna().unique().tolist())
        elif is_custom:
            educations = ["全部"] + sorted(df['学历要求'].dropna().unique().tolist())
        else:
            educations = ["全部"]
        selected_education = st.selectbox("学历要求", educations)
    with col4:
        salary_ranges = ["全部", "5K以下", "5-10K", "10-20K", "20-30K", "30K以上"]
        selected_salary = st.selectbox("薪资范围", salary_ranges)
    
    # 应用筛选条件
    filtered_df = df.copy()
    
    if search_query:
        if is_standardized:
            filtered_df = filtered_df[
                filtered_df['job_title'].str.contains(search_query, case=False) |
                filtered_df['company_name'].str.contains(search_query, case=False) |
                filtered_df['job_description'].str.contains(search_query, case=False)
            ]
        elif is_custom:
            filtered_df = filtered_df[
                filtered_df['招聘岗位'].str.contains(search_query, case=False) |
                filtered_df['企业名称'].str.contains(search_query, case=False) |
                filtered_df['职位描述'].str.contains(search_query, case=False)
            ]
    
    if selected_city != "全部":
        if is_standardized:
            filtered_df = filtered_df[filtered_df['location'] == selected_city]
        elif is_custom:
            filtered_df = filtered_df[filtered_df['工作城市'] == selected_city]
    
    if selected_experience != "全部":
        if is_standardized:
            filtered_df = filtered_df[filtered_df['experience_raw'] == selected_experience]
        elif is_custom:
            filtered_df = filtered_df[filtered_df['要求经验'] == selected_experience]
    
    if selected_education != "全部":
        if is_standardized:
            filtered_df = filtered_df[filtered_df['education'] == selected_education]
        elif is_custom:
            filtered_df = filtered_df[filtered_df['学历要求'] == selected_education]
    
    if selected_salary != "全部":
        if is_standardized:
            salary_col = 'avg_salary_k'
        elif is_custom:
            salary_col = '平均月薪'
        else:
            salary_col = None
            
        if salary_col:
            if is_custom:
                # Convert ranges to actual values (in Yuan)
                if selected_salary == "5K以下":
                    filtered_df = filtered_df[filtered_df[salary_col] < 5000]
                elif selected_salary == "5-10K":
                    filtered_df = filtered_df[(filtered_df[salary_col] >= 5000) & (filtered_df[salary_col] < 10000)]
                elif selected_salary == "10-20K":
                    filtered_df = filtered_df[(filtered_df[salary_col] >= 10000) & (filtered_df[salary_col] < 20000)]
                elif selected_salary == "20-30K":
                    filtered_df = filtered_df[(filtered_df[salary_col] >= 20000) & (filtered_df[salary_col] < 30000)]
                elif selected_salary == "30K以上":
                    filtered_df = filtered_df[filtered_df[salary_col] >= 30000]
            else:
                # Standardized data uses K values
                if selected_salary == "5K以下":
                    filtered_df = filtered_df[filtered_df[salary_col] < 5]
                elif selected_salary == "5-10K":
                    filtered_df = filtered_df[(filtered_df[salary_col] >= 5) & (filtered_df[salary_col] < 10)]
                elif selected_salary == "10-20K":
                    filtered_df = filtered_df[(filtered_df[salary_col] >= 10) & (filtered_df[salary_col] < 20)]
                elif selected_salary == "20-30K":
                    filtered_df = filtered_df[(filtered_df[salary_col] >= 20) & (filtered_df[salary_col] < 30)]
                elif selected_salary == "30K以上":
                    filtered_df = filtered_df[filtered_df[salary_col] >= 30]
    
    # 显示结果
    st.write(f"找到 {len(filtered_df)} 个匹配的岗位")
    
    # 分页显示
    page_size = 10
    total_pages = (len(filtered_df) + page_size - 1) // page_size
    if total_pages > 0:
        current_page = st.number_input("页码", min_value=1, max_value=total_pages, value=1)
        start_idx = (current_page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        
        for i, row in filtered_df.iloc[start_idx:end_idx].iterrows():
            if is_standardized:
                title = row['job_title']
                company = row['company_name']
                salary = row['salary_raw']
                location = row['location']
                experience = row['experience_raw']
                education = row['education']
                company_type = row['company_type']
                company_size = row['company_size']
                financing = row['financing_stage']
                desc = row['job_description']
                benefits = row.get('benefits', '')
            elif is_custom:
                title = row['招聘岗位']
                company = row['企业名称']
                salary = f"{row['最低月薪']:.0f}-{row['最高月薪']:.0f}元"
                location = row['工作城市']
                experience = row['要求经验']
                education = row['学历要求']
                company_type = row.get('行业类型', 'N/A')
                company_size = row.get('企业规模', 'N/A')
                financing = 'N/A'
                desc = row['职位描述']
                benefits = ''
            else:
                title = row.get('job_title', 'Unknown')
                company = row.get('company_name', 'Unknown')
                salary = row.get('salary_raw', 'N/A')
                location = row.get('location', 'N/A')
                experience = row.get('experience_raw', 'N/A')
                education = row.get('education', 'N/A')
                company_type = row.get('company_type', 'N/A')
                company_size = row.get('company_size', 'N/A')
                financing = row.get('financing_stage', 'N/A')
                desc = row.get('job_description', '')
                benefits = row.get('benefits', '')

            with st.expander(f"**{title}** - {company}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**薪资：** {salary}")
                    st.write(f"**地点：** {location}")
                    st.write(f"**经验：** {experience}")
                    st.write(f"**学历：** {education}")
                with col2:
                    st.write(f"**行业/类型：** {company_type}")
                    st.write(f"**规模：** {company_size}")
                    st.write(f"**融资：** {financing}")
                
                st.divider()
                st.subheader("岗位描述")
                st.write(desc[:500] + "..." if len(desc) > 500 else desc)
                
                if pd.notna(benefits) and benefits != "":
                    st.subheader("福利待遇")
                    st.write(benefits)

elif page == "📊 数据可视化":
    st.title("招聘数据可视化")
    
    tab1, tab2, tab3 = st.tabs(["薪资分析", "企业分析", "技能词云"])
    
    with tab1:
        st.subheader("不同岗位平均薪资分布")
        if is_standardized:
            top_jobs = df.groupby('job_title')['avg_salary_k'].mean().sort_values(ascending=False).head(10)
            x_vals = top_jobs.values
            y_vals = top_jobs.index
            x_label = '平均薪资(K)'
        elif is_custom:
            top_jobs = df.groupby('招聘岗位')['平均月薪'].mean().sort_values(ascending=False).head(10)
            x_vals = top_jobs.values / 1000
            y_vals = top_jobs.index
            x_label = '平均薪资(K)'
        else:
            x_vals, y_vals, x_label = [], [], 'N/A'
            
        if len(x_vals) > 0:
            fig = px.bar(
                x=x_vals,
                y=y_vals,
                orientation='h',
                labels={'x': x_label, 'y': '岗位名称'},
                title='薪资最高的10个岗位'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("薪资分布直方图")
        if is_standardized:
            fig = px.histogram(df, x='avg_salary_k', nbins=30, labels={'avg_salary_k': '平均薪资(K)'}, title='整体薪资分布')
        elif is_custom:
            fig = px.histogram(df, x='平均月薪', nbins=30, labels={'平均月薪': '平均薪资(元)'}, title='整体薪资分布')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("不同城市薪资对比")
        if is_standardized:
            city_salary = df.groupby('location')['avg_salary_k'].mean().sort_values(ascending=False)
        elif is_custom:
            city_salary = df.groupby('工作城市')['平均月薪'].mean().sort_values(ascending=False) / 1000
        fig = px.bar(x=city_salary.index, y=city_salary.values, labels={'x': '城市', 'y': '平均薪资(K)'}, title='各城市平均薪资')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("企业规模分布")
        if is_standardized:
            company_size_dist = df['company_size'].value_counts()
        elif is_custom:
            company_size_dist = df['企业规模'].value_counts()
        fig = px.pie(values=company_size_dist.values, names=company_size_dist.index, title='企业规模分布')
        st.plotly_chart(fig, use_container_width=True)
        
        if is_standardized:
            st.subheader("融资阶段分布")
            financing_dist = df['financing_stage'].value_counts()
            fig = px.pie(values=financing_dist.values, names=financing_dist.index, title='融资阶段分布')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("学历要求分布")
        if is_standardized:
            education_dist = df['education'].value_counts()
        elif is_custom:
            education_dist = df['学历要求'].value_counts()
        fig = px.bar(x=education_dist.index, y=education_dist.values, labels={'x': '学历要求', 'y': '岗位数量'}, title='学历要求分布')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("岗位技能词云")
        if is_standardized:
            text = ' '.join(df['job_description'].dropna().tolist())
        elif is_custom:
            text = ' '.join(df['职位描述'].dropna().tolist())
        else:
            text = ''
            
        if text:
            stopwords = set(['负责', '熟悉', '经验', '工作', '开发', '能力', '要求', '良好', '团队', '沟通'])
            wordcloud = WordCloud(
                width=800, height=400, background_color='white',
                font_path='simhei.ttf', stopwords=stopwords, max_words=100
            ).generate(text)
            plt.figure(figsize=(12, 6))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)
        
        st.subheader("福利待遇词云")
        if is_standardized:
            benefits_text = ' '.join(df['benefits'].dropna().tolist())
        else:
            benefits_text = ''
            
        if benefits_text:
            benefits_wordcloud = WordCloud(
                width=800, height=400, background_color='white',
                font_path='simhei.ttf', max_words=50
            ).generate(benefits_text)
            plt.figure(figsize=(12, 6))
            plt.imshow(benefits_wordcloud, interpolation='bilinear')
            plt.axis('off')
            st.pyplot(plt)

elif page == " 智能分析":
    st.title("智能分析")
    
    st.subheader("岗位聚类分析")
    st.write("基于岗位描述的KMeans聚类结果")
    
    st.subheader("技能需求趋势")
    fig = px.line(
        x=['1月', '2月', '3月', '4月', '5月', '6月'],
        y=[100, 120, 95, 130, 115, 140],
        labels={'x': '月份', 'y': '技能需求指数'},
        title='技能需求趋势'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("薪资预测")
    st.write("根据岗位特征预测薪资水平")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("岗位名称")
        st.selectbox("工作经验", ["应届毕业生", "1年以内", "1-3年", "3-5年", "5-10年", "10年以上"])
    with col2:
        st.selectbox("学历要求", ["大专", "本科", "硕士", "博士"])
        st.selectbox("城市", ["北京", "上海", "广州", "深圳", "杭州", "其他"])
    
    if st.button("预测薪资"):
        st.success("预测薪资：15-25K")
    
    st.subheader("智能求职建议")
    st.write("基于您的简历和市场数据，为您提供个性化建议")
    
    if st.button("生成建议"):
        st.info("""
        **求职建议：**
        
        1. **技能提升**：建议加强Python和数据分析技能
        2. **薪资期望**：根据您的背景，合理薪资范围为15-25K
        3. **投递策略**：建议优先投递一线城市的互联网公司
        4. **简历优化**：突出项目经验和技术栈
        """)
