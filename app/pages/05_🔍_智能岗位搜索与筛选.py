"""
智能岗位搜索与筛选页面
功能：
1. 自然语言搜索
2. 多维度智能筛选
3. 相似岗位推荐
4. 岗位收藏与对比
"""
import os
import sys
import streamlit as st
import pandas as pd

# 项目根目录（app 的上一级）
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ml_engine.search_service import JobSearchService

# 页面配置
st.set_page_config(
    page_title="智能岗位搜索与筛选",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化搜索服务
@st.cache_resource
def init_search_service():
    # 优先使用数据库，data_path 作为备选
    data_path = os.path.join(ROOT, 'data', 'processed', 'cleaned_recruitment_data(1).csv')
    model_dir = os.path.join(ROOT, 'models')
    return JobSearchService(data_path=data_path, model_dir=model_dir, use_database=True)

# 初始化 Session State
if 'search_service' not in st.session_state:
    st.session_state.search_service = init_search_service()
if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'compare_list' not in st.session_state:
    st.session_state.compare_list = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = pd.DataFrame()
if 'search_conditions' not in st.session_state:
    st.session_state.search_conditions = {}
if 'has_searched' not in st.session_state:
    st.session_state.has_searched = False  # 标记是否执行过搜索

search_service = st.session_state.search_service

# 侧边栏
st.sidebar.title("🔍 智能岗位搜索")
st.sidebar.info(f"已收录 {len(search_service.df)} 条岗位数据")

st.sidebar.divider()
st.sidebar.subheader("收藏夹")
if st.session_state.favorites:
    for idx in st.session_state.favorites:
        if idx < len(search_service.df):
            job_title = search_service.df.iloc[idx]['招聘岗位']
            company = search_service.df.iloc[idx]['企业名称']
            st.sidebar.write(f"⭐ {job_title} - {company}")
else:
    st.sidebar.write("暂无收藏")

st.sidebar.divider()
st.sidebar.subheader("对比列表")
if st.session_state.compare_list:
    for idx in st.session_state.compare_list:
        if idx < len(search_service.df):
            job_title = search_service.df.iloc[idx]['招聘岗位']
            company = search_service.df.iloc[idx]['企业名称']
            st.sidebar.write(f"📊 {job_title} - {company}")
else:
    st.sidebar.write("暂无对比")

# 主页面
st.title("🔍 智能岗位搜索与筛选")
st.write("支持自然语言查询和多维度智能筛选")

# 标签页
tab1, tab2, tab3 = st.tabs(["🎯 智能搜索", "🔖 收藏夹", "📊 岗位对比"])

with tab1:
    # 自然语言搜索
    st.subheader("💬 自然语言搜索")
    st.write("例如：我想找福州的Java开发工作，月薪1万以上")
    
    query = st.text_input(
        "输入您的求职需求",
        placeholder="描述您想找的工作，包括地点、薪资、技能要求等...",
        key="query_input"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔍 搜索", type="primary", use_container_width=True):
            if query:
                results, conditions = search_service.search_by_query(query)
                st.session_state.search_results = results
                st.session_state.search_conditions = conditions
                st.session_state.has_searched = True  # 标记已搜索
                st.success(f"找到 {len(results)} 个匹配的岗位")
            else:
                st.warning("请输入搜索内容")
    
    # 显示搜索条件
    if st.session_state.search_conditions:
        st.subheader("📋 识别的搜索条件")
        cols = st.columns(4)
        conditions = st.session_state.search_conditions
        with cols[0]:
            if conditions.get('location'):
                st.info(f"📍 地点: {conditions['location']}")
        with cols[1]:
            if conditions.get('min_salary') or conditions.get('max_salary'):
                min_s = conditions.get('min_salary', '不限')
                max_s = conditions.get('max_salary', '不限')
                st.info(f"💰 薪资: {min_s}K-{max_s}K")
        with cols[2]:
            if conditions.get('experience'):
                st.info(f"💼 经验: {conditions['experience']}")
        with cols[3]:
            if conditions.get('education'):
                st.info(f"🎓 学历: {conditions['education']}")
    
    st.divider()
    
    # 高级筛选器
    with st.expander("🛠️ 高级筛选器"):
        st.subheader("多维度筛选")
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            cities = ["全部"] + search_service.get_unique_values('工作城市')
            selected_city = st.selectbox("工作城市", cities, key="filter_city")
        
        with filter_col2:
            experiences = ["全部"] + search_service.get_unique_values('要求经验')
            selected_experience = st.selectbox("工作经验", experiences, key="filter_exp")
        
        with filter_col3:
            educations = ["全部"] + search_service.get_unique_values('学历要求')
            selected_education = st.selectbox("学历要求", educations, key="filter_edu")
        
        with filter_col4:
            company_types = ["全部"] + search_service.get_unique_values('行业类型')
            selected_company_type = st.selectbox("行业类型", company_types, key="filter_type")
        
        filter_col5, filter_col6 = st.columns(2)
        with filter_col5:
            min_salary = st.slider("最低月薪 (K)", 0, 50, 0, key="filter_min_salary")
        with filter_col6:
            max_salary = st.slider("最高月薪 (K)", 0, 100, 100, key="filter_max_salary")
        
        if st.button("应用筛选", type="primary"):
            filters = {
                'location': selected_city if selected_city != "全部" else None,
                'experience': selected_experience if selected_experience != "全部" else None,
                'education': selected_education if selected_education != "全部" else None,
                'company_type': selected_company_type if selected_company_type != "全部" else None,
                'min_salary': min_salary if min_salary > 0 else None,
                'max_salary': max_salary if max_salary < 100 else None,
            }
            results = search_service.search_by_keywords([], filters)
            st.session_state.search_results = results
            st.session_state.has_searched = True  # 标记已筛选
            st.success(f"筛选到 {len(results)} 个岗位")
    
    st.divider()
    
    # 显示搜索结果（仅在用户主动搜索后显示）
    if st.session_state.has_searched and not st.session_state.search_results.empty:
        st.subheader(f"📄 搜索结果 ({len(st.session_state.search_results)} 条)")
        
        for idx, row in st.session_state.search_results.iterrows():
            # 使用原始索引
            orig_idx = row.name if hasattr(row, 'name') else idx
            
            with st.expander(
                f"**{row['招聘岗位']}** - {row['企业名称']} "
                f"{'| 💰' + str(row['平均月薪']) + 'K' if pd.notna(row.get('平均月薪')) else ''}"
                f"{'| 📍' + str(row['工作城市']) if pd.notna(row.get('工作城市')) else ''}"
                f"{'| ⭐ 匹配度: ' + str(round(row.get('similarity_score', 0)*100, 1)) + '%' if 'similarity_score' in row else ''}"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**💰 薪资：** {row.get('最低月薪', '面议')} - {row.get('最高月薪', '面议')} K")
                    st.write(f"**📍 地点：** {row.get('工作城市', '未指定')}")
                    st.write(f"**💼 经验：** {row.get('要求经验', '不限')}")
                    st.write(f"**🎓 学历：** {row.get('学历要求', '不限')}")
                with col2:
                    st.write(f"**🏢 企业规模：** {row.get('企业规模', '未指定')}")
                    st.write(f"**🏭 行业：** {row.get('行业类型', '未指定')}")
                    st.write(f"**📅 发布日期：** {row.get('招聘发布日期', '未指定')}")
                    st.write(f"**🏷️ 招聘类别：** {row.get('招聘类别', '未指定')}")
                
                st.divider()
                st.subheader("📝 职位描述")
                st.write(row.get('职位描述', '暂无描述'))
                
                if pd.notna(row.get('年终奖估算')):
                    st.subheader("🎁 福利待遇")
                    st.write(f"年终奖估算：{row['年终奖估算']} 元")
                
                st.divider()
                action_col1, action_col2, action_col3 = st.columns(3)
                with action_col1:
                    if st.button(f"⭐ 收藏", key=f"fav_{orig_idx}"):
                        if orig_idx not in st.session_state.favorites:
                            st.session_state.favorites.append(orig_idx)
                            st.success("已添加到收藏夹")
                        else:
                            st.info("已在收藏夹中")
                with action_col2:
                    if st.button(f"📊 加入对比", key=f"cmp_{orig_idx}"):
                        if orig_idx not in st.session_state.compare_list:
                            if len(st.session_state.compare_list) < 4:
                                st.session_state.compare_list.append(orig_idx)
                                st.success("已添加到对比列表")
                            else:
                                st.warning("最多对比4个岗位")
                        else:
                            st.info("已在对比列表中")
                with action_col3:
                    if st.button(f"🔍 相似岗位", key=f"sim_{orig_idx}"):
                        similar = search_service.get_similar_jobs(orig_idx, top_n=5)
                        if not similar.empty:
                            st.session_state.search_results = similar
                            st.session_state.has_searched = True  # 标记已搜索
                            st.success("已找到相似岗位")
    
    else:
        if st.session_state.has_searched:
            st.info("未找到匹配的岗位，请尝试调整搜索条件")
        else:
            st.info("💡 请输入搜索条件开始搜索，例如：我想找福州的Java开发工作，月薪1万以上")

with tab2:
    st.subheader("⭐ 我的收藏夹")
    
    if st.session_state.favorites:
        if st.button("🗑️ 清空收藏夹"):
            st.session_state.favorites = []
            st.rerun()
        
        for idx in st.session_state.favorites:
            if idx < len(search_service.df):
                row = search_service.df.iloc[idx]
                with st.expander(
                    f"**{row['招聘岗位']}** - {row['企业名称']} "
                    f"| 💰 {row.get('最低月薪', '面议')}-{row.get('最高月薪', '面议')}K"
                    f"| 📍 {row.get('工作城市', '未指定')}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**经验：** {row.get('要求经验', '不限')}")
                        st.write(f"**学历：** {row.get('学历要求', '不限')}")
                    with col2:
                        st.write(f"**企业规模：** {row.get('企业规模', '未指定')}")
                        st.write(f"**行业：** {row.get('行业类型', '未指定')}")
                    
                    st.write(f"**职位描述：** {row.get('职位描述', '暂无描述')}")
                    
                    if st.button(f"移除", key=f"remove_fav_{idx}"):
                        st.session_state.favorites.remove(idx)
                        st.rerun()
    else:
        st.info("暂无收藏的岗位，快去搜索并收藏心仪的岗位吧！")

with tab3:
    st.subheader("📊 岗位对比")
    
    if st.session_state.compare_list:
        if len(st.session_state.compare_list) > 1:
            if st.button("🗑️ 清空对比列表"):
                st.session_state.compare_list = []
                st.rerun()
            
            # 构建对比表格
            compare_data = []
            for idx in st.session_state.compare_list:
                if idx < len(search_service.df):
                    row = search_service.df.iloc[idx]
                    compare_data.append({
                        '岗位': row['招聘岗位'],
                        '企业': row['企业名称'],
                        '城市': row.get('工作城市', '未指定'),
                        '最低月薪(K)': row.get('最低月薪', '面议'),
                        '最高月薪(K)': row.get('最高月薪', '面议'),
                        '平均月薪(K)': row.get('平均月薪', '面议'),
                        '经验要求': row.get('要求经验', '不限'),
                        '学历要求': row.get('学历要求', '不限'),
                        '企业规模': row.get('企业规模', '未指定'),
                        '行业类型': row.get('行业类型', '未指定'),
                        '年终奖估算': row.get('年终奖估算', '面议'),
                        '招聘类别': row.get('招聘类别', '未指定'),
                    })
            
            compare_df = pd.DataFrame(compare_data)
            st.table(compare_df)
            
            st.divider()
            st.subheader("📝 详细对比")
            
            for idx in st.session_state.compare_list:
                if idx < len(search_service.df):
                    row = search_service.df.iloc[idx]
                    st.write(f"**{row['招聘岗位']} - {row['企业名称']}**")
                    st.write(f"职位描述：{row.get('职位描述', '暂无描述')}")
                    st.divider()
            
            # 移除按钮
            st.subheader("管理对比列表")
            remove_cols = st.columns(len(st.session_state.compare_list))
            for i, idx in enumerate(st.session_state.compare_list):
                with remove_cols[i]:
                    if idx < len(search_service.df):
                        row = search_service.df.iloc[idx]
                        if st.button(f"移除: {row['招聘岗位'][:10]}...", key=f"remove_cmp_{idx}"):
                            st.session_state.compare_list.remove(idx)
                            st.rerun()
        else:
            st.warning("请至少添加2个岗位进行对比")
    else:
        st.info("暂无对比的岗位，请搜索岗位并添加到对比列表")
