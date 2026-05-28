"""
薪资谈判助手页面
功能：
1. 市场薪资查询
2. 薪资谈判策略生成
3. 谈判话术生成
4. 福利待遇分析
"""
import os
import sys
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# 加载 .env 文件
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, '.env'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.llm_service.salary_negotiator import SalaryNegotiator

# 页面配置
st.set_page_config(
    page_title="薪资谈判助手",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化薪资谈判器
@st.cache_resource
def init_negotiator():
    api_key = os.getenv("LLM_API_KEY")
    return SalaryNegotiator(api_key=api_key)

# 初始化 Session State
if 'negotiator' not in st.session_state:
    try:
        st.session_state.negotiator = init_negotiator()
    except Exception as e:
        st.error(f"初始化失败：{str(e)}")
        st.stop()

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

negotiator = st.session_state.negotiator

# 侧边栏
st.sidebar.title(" 薪资谈判助手")
st.sidebar.info("帮助您获得更好的薪资待遇")

if not negotiator.client:
    st.sidebar.warning("⚠️ 未配置 API Key")

# 主页面
st.title(" 薪资谈判助手")
st.write("基于市场数据，帮您制定最优薪资谈判策略")

# 标签页
tab1, tab2, tab3, tab4 = st.tabs([" 市场薪资查询", " 谈判策略", " 福利分析", " 准备清单"])

with tab1:
    st.subheader(" 市场薪资查询")
    st.write("输入岗位信息，查询市场薪资范围")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        position = st.text_input("岗位名称", placeholder="如：Java 开发工程师")
    with col2:
        cities = ["全部"] + sorted(negotiator.df['工作城市'].dropna().unique().tolist()) if not negotiator.df.empty else ["全部"]
        city = st.selectbox("工作城市", cities)
    with col3:
        experiences = ["全部"] + sorted(negotiator.df['要求经验'].dropna().unique().tolist()) if not negotiator.df.empty else ["全部"]
        experience = st.selectbox("工作经验", experiences)
    
    col4, col5 = st.columns(2)
    with col4:
        industries = ["全部"] + sorted(negotiator.df['行业类型'].dropna().unique().tolist()) if not negotiator.df.empty else ["全部"]
        industry = st.selectbox("行业类型", industries)
    
    if st.button("🔍 查询薪资", type="primary", use_container_width=True):
        if position:
            with st.spinner("正在查询市场薪资数据..."):
                result = negotiator.query_market_salary(
                    position=position,
                    city=city if city != "全部" else None,
                    experience=experience if experience != "全部" else None,
                    industry=industry if industry != "全部" else None,
                )
                st.session_state.market_query_result = result
        else:
            st.warning("请输入岗位名称")
    
    # 显示查询结果
    if 'market_query_result' in st.session_state:
        result = st.session_state.market_query_result
        
        if 'error' in result:
            st.error(result['error'])
        else:
            st.success(f"找到 {result['sample_size']} 条相关数据")
            
            st.divider()
            st.subheader("📊 薪资统计")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if result.get('min_salary'):
                    st.metric("最低薪资", f"{result['min_salary']:.0f} 元")
            with col2:
                if result.get('max_salary'):
                    st.metric("最高薪资", f"{result['max_salary']:.0f} 元")
            with col3:
                if result.get('avg_salary'):
                    st.metric("平均薪资", f"{result['avg_salary']:.0f} 元")
            with col4:
                if result.get('median_salary'):
                    st.metric("中位数薪资", f"{result['median_salary']:.0f} 元")
            
            st.divider()
            
            # 薪资区间分布
            st.subheader(" 薪资区间分布")
            col1, col2 = st.columns(2)
            with col1:
                if result.get('percentile_25') and result.get('percentile_75'):
                    st.info(f"25% 分位：{result['percentile_25']:.0f} 元")
                    st.info(f"75% 分位：{result['percentile_75']:.0f} 元")
                    st.info(f"中间 50% 薪资范围：{result['percentile_25']:.0f} - {result['percentile_75']:.0f} 元")
            
            # 按经验分组
            if result.get('by_experience'):
                st.subheader(" 按经验分组")
                exp_df = pd.DataFrame(result['by_experience'])
                st.dataframe(exp_df, use_container_width=True)
            
            # 按城市分组
            if result.get('by_city'):
                st.subheader("️ 按城市分组 (Top 10)")
                city_df = pd.DataFrame(result['by_city'])
                st.dataframe(city_df, use_container_width=True)

with tab2:
    st.subheader("💼 薪资谈判策略")
    st.write("输入您的情况，生成专属谈判策略和话术")
    
    col1, col2 = st.columns(2)
    with col1:
        position = st.text_input("目标岗位", placeholder="如：Java 开发工程师", key="neg_position")
        company_name = st.text_input("公司名称", placeholder="如：腾讯", key="neg_company")
        experience = st.text_input("工作经验", placeholder="如：3 年", key="neg_exp")
    with col2:
        offer_salary = st.number_input("公司 Offer 薪资 (元/月)", min_value=0, value=10000, key="neg_offer")
        target_salary = st.number_input("期望薪资 (元/月)", min_value=0, value=15000, key="neg_target")
        city = st.selectbox("工作城市", ["全国"] + sorted(negotiator.df['工作城市'].dropna().unique().tolist()) if not negotiator.df.empty else ["全国"], key="neg_city")
    
    col3, col4 = st.columns(2)
    with col3:
        company_size = st.selectbox("公司规模", ["未知", "大型企业", "中型企业", "小型企业", "初创公司"], key="neg_size")
    with col4:
        industry = st.selectbox("行业类型", ["未知"] + sorted(negotiator.df['行业类型'].dropna().unique().tolist()) if not negotiator.df.empty else ["未知"], key="neg_industry")
    
    if st.button("📋 生成谈判策略", type="primary", use_container_width=True):
        if position and company_name and experience:
            # 先查询市场薪资
            market_data = negotiator.query_market_salary(
                position=position,
                city=city if city != "全国" else None,
                industry=industry if industry != "未知" else None,
            )
            
            with st.spinner("正在生成谈判策略..."):
                strategy = negotiator.generate_negotiation_strategy(
                    position=position,
                    company_name=company_name,
                    experience=experience,
                    offer_salary=offer_salary,
                    target_salary=target_salary,
                    market_min=market_data.get('min_salary'),
                    market_max=market_data.get('max_salary'),
                    company_size=company_size if company_size != "未知" else None,
                    industry=industry if industry != "未知" else None,
                )
                st.session_state.strategy_result = strategy
        else:
            st.warning("请填写完整的岗位、公司和经验信息")
    
    # 显示策略结果
    if 'strategy_result' in st.session_state:
        st.divider()
        st.subheader("📋 谈判策略")
        st.write(st.session_state.strategy_result)

with tab3:
    st.subheader("🎁 福利待遇分析")
    st.write("分析目标岗位的常见福利待遇")
    
    col1, col2 = st.columns(2)
    with col1:
        position = st.text_input("岗位名称", placeholder="如：Java 开发工程师", key="ben_position")
    with col2:
        industry = st.selectbox("行业类型", ["全部"] + sorted(negotiator.df['行业类型'].dropna().unique().tolist()) if not negotiator.df.empty else ["全部"], key="ben_industry")
    
    if st.button(" 分析福利", type="primary", use_container_width=True):
        if position:
            with st.spinner("正在分析福利待遇..."):
                result = negotiator.analyze_benefits(
                    offer_salary=0,
                    position=position,
                    industry=industry if industry != "全部" else None,
                )
                st.session_state.benefits_result = result
        else:
            st.warning("请输入岗位名称")
    
    # 显示福利分析结果
    if 'benefits_result' in st.session_state:
        result = st.session_state.benefits_result
        
        if 'error' in result:
            st.error(result['error'])
        else:
            st.success(f"基于 {result['sample_size']} 条数据分析")
            
            st.divider()
            st.subheader("💰 年终奖情况")
            col1, col2 = st.columns(2)
            with col1:
                if result.get('avg_bonus'):
                    st.metric("平均年终奖", f"{result['avg_bonus']:.0f} 元")
            with col2:
                if result.get('max_bonus'):
                    st.metric("最高年终奖", f"{result['max_bonus']:.0f} 元")
            
            st.divider()
            st.subheader("🎁 常见福利待遇")
            benefits = result.get('common_benefits', [])
            cols = st.columns(2)
            for i, benefit in enumerate(benefits):
                with cols[i % 2]:
                    st.write(f"✅ {benefit}")
            
            st.divider()
            st.subheader("💡 谈判建议")
            st.info("除了基本工资，您可以尝试争取以下福利：")
            st.write("- **年终奖**：询问年终奖发放标准和比例")
            st.write("- **股票/期权**：了解公司是否有股权激励计划")
            st.write("- **培训预算**：争取年度培训费用报销")
            st.write("- **灵活办公**：协商远程办公或弹性工作时间")
            st.write("- **额外假期**：争取更多带薪年假")
            st.write("- **交通/餐补**：询问是否有相关补贴")

with tab4:
    st.subheader("📋 谈判前准备清单")
    st.write("做好充分准备，提高谈判成功率")
    
    checklist = negotiator.get_preparation_checklist()
    
    for i, item in enumerate(checklist):
        st.checkbox(item, key=f"check_{i}")
    
    st.divider()
    st.subheader("⚠️ 谈判注意事项")
    
    notes = [
        "保持自信和专业的态度，不要显得急躁或不满",
        "用数据和事实支持你的薪资要求",
        "不要只谈薪资，也要关注职业发展机会",
        "如果对方无法满足薪资要求，尝试争取其他福利",
        "不要在第一次报价时就接受，适当协商",
        "设定底线，如果差距太大做好放弃的准备",
        "谈判结束后，要求书面确认所有达成的协议",
    ]
    
    for note in notes:
        st.warning(f"⚠️ {note}")
