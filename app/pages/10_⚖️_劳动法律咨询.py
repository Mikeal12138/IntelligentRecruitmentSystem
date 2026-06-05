"""
劳动法律咨询页面
功能：
1. 调用百炼大模型法律智能体
2. 劳动法律法规咨询
3. 就业歧视维权指导
4. 劳动合同纠纷解答
5. 流式输出支持
"""
import os
import sys
import streamlit as st
import requests
import json
from dotenv import load_dotenv

# 项目根目录
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 加载环境变量
load_dotenv(os.path.join(ROOT, '.env'))

# 页面配置
st.set_page_config(
    page_title="劳动法律咨询",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 Session State
if 'legal_messages' not in st.session_state:
    st.session_state.legal_messages = [
        {
            "role": "assistant",
            "content": "你好！我是劳动法律咨询助手，基于百炼大模型法律智能体。\n\n我可以为您解答：\n• 劳动合同相关问题\n• 就业歧视与维权\n• 工资与福利纠纷\n• 工伤与职业病\n• 解除与终止劳动合同\n• 社会保险与公积金\n\n有什么法律问题需要咨询吗？"
        }
    ]

if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# 调用法律智能体 API
def call_legal_agent(prompt: str) -> str:
    """
    调用百炼大模型法律智能体
    """
    # 从环境变量读取配置
    api_key = os.getenv("LEGAL_AGENT_API_KEY", "sk-c2442f244ff94b219e37dbd2886ebc4f")
    app_id = os.getenv("LEGAL_AGENT_APP_ID", "c097db70e75a4593877303102d76a238")
    
    url = f"https://dashscope.aliyuncs.com/api/v1/apps/{app_id}/completion"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-SSE": "enable"
    }
    
    data = {
        "input": {
            "prompt": prompt
        },
        "parameters": {}
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        # 如果响应为空
        if not response.text.strip():
            return "⚠️ API返回空响应"
        
        # 方式1: 直接JSON解析
        try:
            result = response.json()
            if 'output' in result and isinstance(result['output'], dict):
                text = result['output'].get('text', '')
                if text:
                    return text
        except:
            pass
        
        # 方式2: 解析SSE格式（每个data块是完整响应，只取最后一个）
        try:
            last_text = ""
            lines = response.text.strip().split('\n')
            
            for line in lines:
                if not line.strip():
                    continue
                
                if 'data:' in line:
                    try:
                        json_str = line.split('data:', 1)[1].strip()
                        if not json_str or json_str == '[DONE]':
                            continue
                        
                        result = json.loads(json_str)
                        if 'output' in result and isinstance(result['output'], dict):
                            text = result['output'].get('text', '')
                            if text:
                                last_text = text.replace('\\n', '\n').replace('\\r', '')
                    except:
                        continue
            
            if last_text.strip():
                return last_text.strip()
        except:
            pass
        
        # 方式3: 提取所有text字段
        try:
            import re
            text_matches = re.findall(r'"text"\s*:\s*"([^"]*)"', response.text)
            if text_matches:
                full_text = ''.join(text_matches)
                full_text = full_text.replace('\\n', '\n').replace('\\r', '')
                return full_text
        except:
            pass
        
        return "❌ 未能解析API响应"
            
    except requests.exceptions.Timeout:
        return "⏰ 请求超时，请稍后重试"
    except requests.exceptions.RequestException as e:
        return f"⚠️ 网络请求失败：{str(e)}"
    except Exception as e:
        return f"❌ 发生错误：{str(e)}"

# 侧边栏
st.sidebar.title("⚖️ 劳动法律咨询")
st.sidebar.info("基于百炼大模型法律智能体")

st.sidebar.divider()
st.sidebar.subheader("常见问题")

common_questions = [
    "试用期被无故辞退，如何维权？",
    "公司不签劳动合同怎么办？",
    "加班费应该如何计算？",
    "遭遇就业歧视如何维权？",
    "工伤赔偿流程是什么？",
    "离职时公司扣发工资怎么办？",
    "社保缴纳相关法律规定",
    "竞业限制协议是否合法？"
]

for question in common_questions:
    if st.sidebar.button(question, use_container_width=True, key=f"cq_{question[:10]}"):
        st.session_state.quick_question = question
        st.session_state.trigger_query = True

st.sidebar.divider()
if st.sidebar.button("🗑️ 清空对话", use_container_width=True):
    st.session_state.legal_messages = [
        {
            "role": "assistant",
            "content": "你好！我是劳动法律咨询助手，基于百炼大模型法律智能体。\n\n我可以为您解答：\n• 劳动合同相关问题\n• 就业歧视与维权\n• 工资与福利纠纷\n• 工伤与职业病\n• 解除与终止劳动合同\n• 社会保险与公积金\n\n有什么法律问题需要咨询吗？"
        }
    ]
    st.rerun()

# 主页面
st.title("⚖️ 劳动法律咨询")
st.write("基于百炼大模型法律智能体，为您提供专业的劳动法律咨询服务")

# 显示对话历史
for message in st.session_state.legal_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入
if prompt := st.chat_input("请输入您的劳动法律问题..."):
    # 添加用户消息
    st.session_state.legal_messages.append({"role": "user", "content": prompt})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 调用法律智能体
    with st.chat_message("assistant"):
        with st.spinner("正在咨询法律专家..."):
            response = call_legal_agent(prompt)
            st.markdown(response)
            st.session_state.legal_messages.append({"role": "assistant", "content": response})

# 处理快速提问
if st.session_state.get('trigger_query', False):
    question = st.session_state.get('quick_question', '')
    if question:
        # 添加用户消息
        st.session_state.legal_messages.append({"role": "user", "content": question})
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(question)
        
        # 调用法律智能体
        with st.chat_message("assistant"):
            with st.spinner("正在咨询法律专家..."):
                response = call_legal_agent(question)
                st.markdown(response)
                st.session_state.legal_messages.append({"role": "assistant", "content": response})
        
        # 重置触发标志
        st.session_state.trigger_query = False
        st.rerun()

# 底部说明
st.divider()
st.subheader("📌 使用说明")
st.info("""
- 本系统基于百炼大模型法律智能体，提供劳动法律咨询服务
- 支持多轮对话，可以针对具体问题深入咨询
- 点击侧边栏的常见问题可快速提问
- 法律咨询仅供参考，具体案件建议咨询专业律师
""")
