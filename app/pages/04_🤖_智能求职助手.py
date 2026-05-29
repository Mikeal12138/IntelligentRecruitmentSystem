"""
智能求职助手 - 对话 AI 前端页面
功能：
1. 多轮对话交互
2. 简历优化对话
3. 面试模拟对话
4. 岗位推荐
5. 职业规划
6. 心理支持
7. 用户档案管理
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

from src.llm_service.chat_assistant import ChatAssistant

# 页面配置
st.set_page_config(
    page_title="智能求职助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化助手
@st.cache_resource
def init_assistant():
    api_key = os.getenv("LLM_API_KEY")
    return ChatAssistant(api_key=api_key)

# 初始化 Session State
if 'assistant' not in st.session_state:
    try:
        st.session_state.assistant = init_assistant()
    except Exception as e:
        st.error(f"初始化失败：{str(e)}")
        st.stop()

if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是职引助手，你的专属求职顾问。\n\n我可以帮助你：\n• 优化简历\n• 准备面试\n• 推荐岗位\n• 职业规划\n• 心理支持\n\n有什么我可以帮你的吗？"}
    ]

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'interview_mode' not in st.session_state:
    st.session_state.interview_mode = False
    st.session_state.interview_questions = []
    st.session_state.current_question = 0

if 'show_profile' not in st.session_state:
    st.session_state.show_profile = False

assistant = st.session_state.assistant

# 侧边栏
st.sidebar.title("🤖 职引助手")
st.sidebar.info("你的专属求职顾问")

if not assistant.client:
    st.sidebar.warning("⚠️ 未配置 API Key")

st.sidebar.divider()

# 功能选择
selected_function = st.sidebar.selectbox(
    "🎯 选择功能",
    ["💬 自由对话", "📄 简历优化", " 面试模拟", "💼 岗位推荐", "📊 职业规划", "💝 心理支持"],
    key="function_select"
)

# 显示用户档案
if st.sidebar.button(" 查看我的档案"):
    st.session_state.show_profile = not st.session_state.show_profile

if st.session_state.show_profile:
    st.sidebar.divider()
    st.sidebar.subheader("我的档案")
    profile = assistant.user_profile.to_dict()
    
    st.sidebar.write("**基本信息**")
    for k, v in profile['basic_info'].items():
        if v:
            st.sidebar.write(f"• {k}: {v}")
    
    st.sidebar.write("**工作信息**")
    for k, v in profile['work_info'].items():
        if v and v != []:
            st.sidebar.write(f"• {k}: {v}")
    
    st.sidebar.write("**求职意向**")
    for k, v in profile['job_intention'].items():
        if v:
            st.sidebar.write(f"• {k}: {v}")
    
    if st.sidebar.button("🗑️ 清空档案"):
        assistant.user_profile = type(assistant.user_profile)()
        st.rerun()

# 主页面
st.title("🤖 智能求职助手")
st.write("全流程陪伴式求职专属顾问")

# 功能模式处理
if selected_function == "📄 简历优化":
    st.subheader("📄 简历优化")
    st.write("粘贴或上传你的简历内容，我将为你提供优化建议")
    
    resume_text = st.text_area("粘贴简历内容", height=200, placeholder="在此粘贴你的简历内容...")
    target_job = st.text_input("目标岗位（可选）", placeholder="如：Java 开发工程师")
    
    if st.button("🔍 开始优化", type="primary"):
        if resume_text:
            with st.spinner("正在分析简历..."):
                result = assistant.optimize_resume(resume_text, target_job)
                st.markdown(result)
        else:
            st.warning("请先粘贴简历内容")

elif selected_function == "🎤 面试模拟":
    st.subheader("🎤 面试模拟")
    st.write("选择面试类型和目标岗位，开始模拟面试")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        job_title = st.text_input("目标岗位", placeholder="如：Java 开发工程师")
    with col2:
        interview_type = st.selectbox("面试类型", ["general", "hr", "technical"])
    with col3:
        if st.button(" 开始模拟", type="primary"):
            if job_title:
                result = assistant.simulate_interview(job_title, interview_type)
                st.session_state.interview_mode = True
                st.session_state.interview_questions = result['questions']
                st.session_state.current_question = 0
                st.rerun()
    
    if st.session_state.interview_mode and st.session_state.interview_questions:
        questions = st.session_state.interview_questions
        current = st.session_state.current_question
        
        if current < len(questions):
            q = questions[current]
            st.divider()
            st.write(f"**问题 {current + 1}/{len(questions)}**")
            st.info(q['question'])
            
            answer = st.text_area("你的回答", height=100, key=f"answer_{current}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 提交回答"):
                    if answer:
                        with st.spinner("正在评估..."):
                            feedback = assistant.evaluate_answer(q['question'], answer, job_title)
                            st.session_state.feedback = feedback
                    else:
                        st.warning("请先输入回答")
            
            with col2:
                if st.button("➡️ 下一题"):
                    st.session_state.current_question += 1
                    st.rerun()
            
            if 'feedback' in st.session_state:
                st.divider()
                st.subheader("📝 评估反馈")
                st.markdown(st.session_state.feedback)
        else:
            st.success("🎉 模拟面试完成！你做得很好！")
            if st.button("🔄 重新开始"):
                st.session_state.interview_mode = False
                st.session_state.interview_questions = []
                st.session_state.current_question = 0
                st.rerun()

elif selected_function == "💼 岗位推荐":
    st.subheader("💼 智能岗位推荐")
    st.write("告诉我你的求职需求，我会为你推荐合适的岗位")
    
    # 自然语言输入
    user_query = st.text_area(
        "描述你的求职需求",
        height=120,
        placeholder="例如：我想找北京地区的 Java 开发工作，期望薪资 15k-20k，有 3 年经验，本科学历..."
    )
    
    st.divider()
    st.write("**或者使用快速筛选：**")
    col1, col2, col3 = st.columns(3)
    with col1:
        position = st.text_input("岗位关键词", placeholder="如：Java", key="quick_position")
    with col2:
        city = st.text_input("工作城市", placeholder="如：北京", key="quick_city")
    with col3:
        experience = st.text_input("工作经验", placeholder="如：3 年", key="quick_experience")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 智能推荐", type="primary", use_container_width=True):
            if user_query:
                with st.spinner("正在为您智能匹配岗位..."):
                    recommendations = assistant.recommend_jobs(user_query=user_query, top_n=10)
                    st.session_state.job_recommendations = recommendations
            else:
                st.warning("请先描述你的求职需求")
    
    with col2:
        if st.button("🔎 快速筛选", use_container_width=True):
            filters = {}
            if position:
                filters['position'] = position
            if city:
                filters['city'] = city
            if experience:
                filters['experience'] = experience
            
            if filters:
                with st.spinner("正在搜索岗位..."):
                    recommendations = assistant.recommend_jobs(filters=filters, top_n=10)
                    st.session_state.job_recommendations = recommendations
            else:
                st.warning("请至少填写一个筛选条件")
    
    # 显示推荐结果
    if st.session_state.get('job_recommendations'):
        recommendations = st.session_state.job_recommendations
        
        if recommendations:
            st.divider()
            st.success(f"✅ 找到 {len(recommendations)} 个匹配岗位")
            
            for i, rec in enumerate(recommendations):
                match_score = rec.get('match_score', 0)
                with st.expander(
                    f"💼 {rec['position']} - {rec['company']} (匹配度：{match_score}%)",
                    expanded=(i == 0)
                ):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**📍 城市：** {rec['city']}")
                        st.write(f"**🎓 学历：** {rec['education']}")
                    with col2:
                        st.write(f"**💼 经验：** {rec['experience']}")
                        st.write(f"**🏭 行业：** {rec.get('industry', '未知')}")
                    with col3:
                        st.write(f"**💰 薪资：** {rec['salary_range']}")
                        st.write(f"**📊 规模：** {rec.get('company_size', '未知')}")
                    
                    # 显示匹配原因
                    if rec.get('match_reasons'):
                        st.divider()
                        st.write("**✅ 匹配亮点：**")
                        for reason in rec['match_reasons']:
                            st.success(f"✓ {reason}")
                    
                    # 显示职位描述
                    if rec.get('job_desc'):
                        st.divider()
                        st.write("**📋 职位描述：**")
                        job_desc = rec['job_desc']
                        if len(job_desc) > 400:
                            job_desc = job_desc[:400] + "..."
                        st.write(job_desc)
                    
                    # 发布日期
                    if rec.get('publish_date'):
                        st.caption(f"发布日期：{rec['publish_date']}")
        else:
            st.warning("未找到匹配岗位，请调整你的需求描述或筛选条件")

elif selected_function == "📊 职业规划":
    st.subheader("📊 职业规划")
    st.write("告诉我你的情况，我帮你制定职业发展计划")
    
    current_situation = st.text_area("描述你的当前情况", height=150, placeholder="如：我是应届毕业生，计算机专业，想找前端开发工作...")
    
    if st.button(" 生成规划", type="primary"):
        if current_situation:
            with st.spinner("正在生成职业规划..."):
                plan = assistant.career_planning(current_situation)
                st.markdown(plan)
        else:
            st.warning("请描述你的当前情况")

elif selected_function == "💝 心理支持":
    st.subheader("💝 心理支持")
    st.write("求职路上遇到困难？我会在这里支持你")
    
    user_feeling = st.text_area("说说你的感受", height=150, placeholder="如：最近投了很多简历都没有回复，感觉很焦虑...")
    
    if st.button("💌 获取支持", type="primary"):
        if user_feeling:
            with st.spinner("正在准备回复..."):
                support = assistant.emotional_support(user_feeling)
                st.markdown(support)
        else:
            st.warning("请说说你的感受")

# 聊天历史显示
st.divider()
st.subheader("💬 对话记录")

# 显示消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 输入框
if prompt := st.chat_input("告诉我你的想法..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # 获取助手回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            response = assistant.chat(prompt, st.session_state.conversation_history)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.conversation_history.append({"role": "assistant", "content": response})

# 清空对话
if st.sidebar.button("🗑️ 清空对话"):
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我是职引助手，你的专属求职顾问。\n\n有什么我可以帮你的吗？"}
    ]
    st.session_state.conversation_history = []
    st.rerun()
