"""
面试辅助与评估页面
功能：
1. 生成面试题库（结合岗位要求）
2. AI实时记录面试语音转文字并提炼要点
3. 面试表现评分
"""
import os
import sys
import streamlit as st
from dotenv import load_dotenv

# 加载 .env 文件
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, '.env'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.llm_service.interview_assistant import InterviewAssistant

# 页面配置
st.set_page_config(
    page_title="面试辅助与评估",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化面试助手
@st.cache_resource
def init_assistant():
    api_key = os.getenv("LLM_API_KEY")
    return InterviewAssistant(api_key=api_key)

# 初始化 Session State
if 'interviewer' not in st.session_state:
    try:
        st.session_state.interviewer = init_assistant()
    except Exception as e:
        st.error(f"初始化失败：{str(e)}")
        st.stop()

if 'questions' not in st.session_state:
    st.session_state.questions = ""

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = ""

if 'score_result' not in st.session_state:
    st.session_state.score_result = ""

if 'follow_up_questions' not in st.session_state:
    st.session_state.follow_up_questions = ""

interviewer = st.session_state.interviewer

# 侧边栏
st.sidebar.title("🤝 面试辅助与评估")
st.sidebar.info("帮助您进行高效的面试评估")

if not interviewer.client:
    st.sidebar.warning("⚠️ 未配置 API Key，部分功能受限")

# 主页面
st.title("🤝 面试辅助与评估")
st.write("基于AI的面试题库生成、记录分析与评分系统")

# 标签页
tab1, tab2, tab3 = st.tabs(["📝 生成面试题库", "🎙️ 面试记录分析", "📊 面试评分"])

with tab1:
    st.subheader("📝 生成面试题库")
    st.write("根据岗位要求生成针对性的面试题目")
    
    col1, col2 = st.columns(2)
    with col1:
        position = st.text_input("岗位名称", placeholder="如：Java开发工程师", key="q_position")
        experience = st.selectbox("经验要求", ["不限", "应届毕业生", "1-3年", "3-5年", "5-10年", "10年以上"], key="q_exp")
    with col2:
        question_count = st.slider("题目数量", min_value=3, max_value=10, value=5, key="q_count")
        skills = st.text_input("技能要求（逗号分隔）", placeholder="如：Java, Spring Boot, MySQL", key="q_skills")
    
    if st.button("🚀 生成面试题", type="primary", use_container_width=True):
        if position:
            skill_list = [s.strip() for s in skills.split(",")] if skills else None
            
            with st.spinner("正在生成面试题..."):
                questions = interviewer.generate_questions(
                    position=position,
                    experience=experience,
                    skill_requirements=skill_list,
                    question_count=question_count
                )
                st.session_state.questions = questions
        else:
            st.warning("请输入岗位名称")
    
    # 显示生成的题目
    if st.session_state.questions:
        st.divider()
        st.subheader("📋 面试题库")
        st.markdown(st.session_state.questions)

with tab2:
    st.subheader("🎙️ 面试记录分析")
    st.write("记录面试内容，AI自动提炼要点")
    
    # 面试记录输入
    transcript = st.text_area("面试记录（语音转文字）", 
                              placeholder="请粘贴面试语音转文字记录...\n\n示例：\n面试官：请介绍一下你做过的项目？\n候选人：我在XX公司做过XX项目，主要负责XX模块...",
                              height=200,
                              key="transcript_input")
    
    col1, col2 = st.columns(2)
    with col1:
        position = st.text_input("面试岗位", placeholder="如：前端开发工程师", key="analysis_position")
    
    # 分析按钮
    if st.button("🔍 分析面试记录", type="primary", use_container_width=True):
        if transcript and position:
            with st.spinner("正在分析面试记录..."):
                analysis = interviewer.analyze_interview_transcript(
                    transcript=transcript,
                    position=position
                )
                st.session_state.analysis_result = analysis
                st.session_state.transcript = transcript
        else:
            st.warning("请填写面试记录和岗位信息")
    
    # 显示分析结果
    if st.session_state.analysis_result:
        st.divider()
        st.subheader("📊 面试分析报告")
        st.markdown(st.session_state.analysis_result)
        
        # 生成追问问题
        if st.button("💬 生成追问问题", key="follow_up_btn"):
            with st.spinner("正在生成追问问题..."):
                follow_up = interviewer.generate_follow_up_questions(
                    transcript=st.session_state.transcript,
                    position=position if position else "未知岗位",
                    count=3
                )
                st.session_state.follow_up_questions = follow_up
        
        if st.session_state.follow_up_questions:
            st.divider()
            st.subheader("💬 追问问题")
            st.markdown(st.session_state.follow_up_questions)

with tab3:
    st.subheader("📊 面试评分")
    st.write("对面试表现进行综合评分")
    
    # 面试记录输入
    score_transcript = st.text_area("面试记录", 
                                    placeholder="请粘贴面试记录...",
                                    height=200,
                                    key="score_transcript")
    
    col1, col2 = st.columns(2)
    with col1:
        score_position = st.text_input("面试岗位", placeholder="如：Python开发工程师", key="score_position")
    
    # 评分按钮
    if st.button("✅ 开始评分", type="primary", use_container_width=True):
        if score_transcript and score_position:
            with st.spinner("正在评分..."):
                score = interviewer.score_interview(
                    transcript=score_transcript,
                    position=score_position
                )
                st.session_state.score_result = score
        else:
            st.warning("请填写面试记录和岗位信息")
    
    # 显示评分结果
    if st.session_state.score_result:
        st.divider()
        st.subheader("📈 面试评分报告")
        st.markdown(st.session_state.score_result)

# 页脚
st.divider()
st.info("💡 提示：配置API Key后可获得更准确的面试题生成和评分结果")
