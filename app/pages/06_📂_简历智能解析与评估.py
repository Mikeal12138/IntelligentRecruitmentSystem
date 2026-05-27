"""
个人简历智能解析与评估页面
功能：
1. 支持 PDF、Word、TXT 格式上传
2. 自动提取简历信息
3. 生成评分报告
4. 提供优化建议
"""
import os
import sys
import streamlit as st
import pandas as pd
import tempfile
import json
from dotenv import load_dotenv

# 加载 .env 文件
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT, '.env'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.llm_service.resume_parser import ResumeParser

# 页面配置
st.set_page_config(
    page_title="简历智能解析与评估",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化解析器
@st.cache_resource
def init_parser():
    api_key = os.getenv("LLM_API_KEY")
    if api_key:
        print("[ResumeParser] 已从环境变量加载 API Key")
    else:
        print("[ResumeParser] 警告：未找到环境变量 LLM_API_KEY")
    return ResumeParser(api_key=api_key)

# 初始化 Session State
if 'parser' not in st.session_state:
    try:
        st.session_state.parser = init_parser()
    except Exception as e:
        st.error(f"初始化失败：{str(e)}")
        st.stop()

if 'parse_result' not in st.session_state:
    st.session_state.parse_result = None

parser = st.session_state.parser

# 侧边栏
st.sidebar.title("📄 简历解析")
st.sidebar.info("支持 PDF、Word、TXT 格式")

if not parser.client:
    st.sidebar.error("⚠️ 未找到 LLM_API_KEY 环境变量")
    st.sidebar.info("请在 .env 文件中配置 LLM_API_KEY")

# 主页面
st.title("📄 个人简历智能解析与评估")
st.write("上传简历，自动提取信息并生成评估报告")

# 标签页
tab1, tab2, tab3 = st.tabs(["📤 上传简历", " 评估报告", "💡 改进建议"])

with tab1:
    st.subheader(" 上传您的简历")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "选择简历文件",
        type=['pdf', 'docx', 'doc', 'txt'],
        help="支持 PDF、Word、TXT 格式"
    )
    
    if uploaded_file:
        # 显示文件信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📄 文件名：{uploaded_file.name}")
        with col2:
            st.info(f"📦 大小：{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.info(f"📋 类型：{uploaded_file.type}")
        
        # 解析按钮
        if st.button("🔍 开始解析", type="primary", use_container_width=True):
            if not parser.client:
                st.error("请先配置 LLM API Key")
            else:
                with st.spinner("正在解析简历，请稍候..."):
                    # 保存临时文件
                    with tempfile.NamedTemporaryFile(
                        delete=False, 
                        suffix=os.path.splitext(uploaded_file.name)[1]
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    try:
                        # 解析和评估
                        result = parser.parse_and_evaluate(tmp_path)
                        st.session_state.parse_result = result
                        st.success("✅ 简历解析完成！")
                    except Exception as e:
                        st.error(f"❌ 解析失败：{str(e)}")
                    finally:
                        # 删除临时文件
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
    
    # 显示解析结果
    if st.session_state.parse_result:
        result = st.session_state.parse_result
        
        # 检查是否是错误结果
        if 'error' in result:
            st.error(f"❌ 解析失败：{result['error']}")
        elif 'parsed_data' not in result:
            st.error("❌ 解析结果格式异常")
        else:
            parsed = result['parsed_data']
            
            st.divider()
            st.subheader(" 解析结果")
            
            # 基本信息
            st.write("### 👤 基本信息")
            info_col1, info_col2, info_col3 = st.columns(3)
            with info_col1:
                st.write(f"**姓名：** {parsed.get('name', '未提取')}")
                st.write(f"**电话：** {parsed.get('phone', '未提取')}")
            with info_col2:
                st.write(f"**邮箱：** {parsed.get('email', '未提取')}")
                st.write(f"**工作年限：** {parsed.get('years_of_experience', '未提取')} 年")
            with info_col3:
                st.write(f"**最高学历：** {parsed.get('highest_degree', '未提取')}")
            
            st.divider()
            
            # 教育背景
            if parsed.get('education'):
                st.write("### 🎓 教育背景")
                for edu in parsed['education']:
                    if isinstance(edu, dict):
                        st.write(f"- **{edu.get('school', '未知')}** | {edu.get('degree', '未知')} | {edu.get('major', '未知')}")
                    else:
                        st.write(f"- {edu}")
            
            st.divider()
            
            # 工作经历
            if parsed.get('work_experience'):
                st.write("### 💼 工作经历")
                for work in parsed['work_experience']:
                    if isinstance(work, dict):
                        with st.expander(f"**{work.get('position', '未知')}** - {work.get('company', '未知')}"):
                            st.write(f"**时长：** {work.get('duration', '未知')}")
                            st.write(f"**描述：** {work.get('description', '无')}")
                    else:
                        st.write(f"- {work}")
            
            st.divider()
            
            # 项目经验
            if parsed.get('projects'):
                st.write("### 🚀 项目经验")
                for proj in parsed['projects']:
                    if isinstance(proj, dict):
                        with st.expander(f"**{proj.get('name', '未知项目')}**"):
                            st.write(f"**角色：** {proj.get('role', '未知')}")
                            st.write(f"**描述：** {proj.get('description', '无')}")
                    else:
                        st.write(f"- {proj}")
            
            st.divider()
            
            # 技能列表
            if parsed.get('skills'):
                st.write("### 🛠️ 技能列表")
                skills = parsed['skills']
                if isinstance(skills, list):
                    for skill in skills:
                        st.write(f"• {skill}")
                else:
                    st.write(skills)
            
            st.divider()
            
            # 证书
            if parsed.get('certificates'):
                st.write("### 🏆 证书资质")
                certs = parsed['certificates']
                if isinstance(certs, list):
                    for cert in certs:
                        st.write(f"• {cert}")
                else:
                    st.write(certs)

with tab2:
    st.subheader("📊 简历评估报告")
    
    if not st.session_state.parse_result:
        st.info("请先在「上传简历」标签页上传并解析简历")
    else:
        result = st.session_state.parse_result
        score_report = result.get('score_report', {})
        
        if not score_report:
            st.warning("暂无评估数据")
        else:
            # 总分展示
            st.write("### 🎯 总体评分")
            overall_score = score_report.get('overall_score', 0)
            
            # 用进度条展示总分
            st.progress(overall_score / 100)
            st.metric("总分", f"{overall_score}/100")
            
            st.divider()
            
            # 详细评分
            st.write("### 📈 详细评分")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                completeness = score_report.get('completeness_score', 0)
                st.metric("完整性", f"{completeness}/40")
                st.progress(completeness / 40)
                st.caption("基本信息、教育背景、工作经历等完整度")
            
            with col2:
                match = score_report.get('match_score', 0)
                st.metric("匹配度", f"{match}/30")
                st.progress(match / 30)
                st.caption("技能与市场需求的匹配程度")
            
            with col3:
                competitive = score_report.get('competitiveness_score', 0)
                st.metric("竞争力", f"{competitive}/30")
                st.progress(competitive / 30)
                st.caption("学历、经验、项目等综合竞争力")
            
            st.divider()
            
            # 优势
            st.write("### ✅ 优势分析")
            strengths = score_report.get('strengths', [])
            if strengths:
                for strength in strengths:
                    st.success(f"✓ {strength}")
            else:
                st.info("暂无明显优势")
            
            st.divider()
            
            # 不足
            st.write("### ⚠️ 不足之处")
            weaknesses = score_report.get('weaknesses', [])
            if weaknesses:
                for weakness in weaknesses:
                    st.warning(f"✗ {weakness}")
            else:
                st.success("未发现明显不足")
            
            st.divider()
            
            # 技能匹配详情
            matched_skills = score_report.get('matched_skills', [])
            if matched_skills:
                st.write("### 🎯 匹配的技能")
                for skill in matched_skills:
                    st.write(f"• {skill}")

with tab3:
    st.subheader("💡 简历改进建议")
    
    if not st.session_state.parse_result:
        st.info("请先在「上传简历」标签页上传并解析简历")
    else:
        result = st.session_state.parse_result
        improvement = result.get('improvement_report', '')
        
        if improvement:
            st.write(improvement)
        else:
            st.info("暂无改进建议")
            
            # 显示基础建议
            score_report = result.get('score_report', {})
            suggestions = score_report.get('suggestions', [])
            
            if suggestions:
                st.write("### 📝 基础建议")
                for suggestion in suggestions:
                    st.info(f"• {suggestion}")
