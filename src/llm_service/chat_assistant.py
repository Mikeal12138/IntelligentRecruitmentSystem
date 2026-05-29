"""
智能求职助手 - 对话 AI 核心服务
功能：
1. 用户档案管理和上下文记忆
2. 简历优化对话
3. 面试模拟对话
4. 岗位匹配推荐
5. 求职规划和心理支持
6. 多轮对话和指代消解
"""
import os
import sys
import re
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))


class UserProfile:
    """用户求职档案"""
    def __init__(self):
        self.basic_info = {
            'name': None,
            'phone': None,
            'email': None,
            'education': None,
            'graduation_year': None,
            'major': None,
        }
        self.work_info = {
            'years_of_experience': None,
            'current_position': None,
            'current_company': None,
            'skills': [],
            'projects': [],
            'certificates': [],
        }
        self.job_intention = {
            'target_position': None,
            'target_industry': None,
            'target_city': None,
            'expected_salary': None,
            'preferred_company_size': None,
            'preferred_work_mode': None,
        }
        self.job_progress = {
            'applied_jobs': [],
            'interviews': [],
            'offers': [],
            'status': 'seeking',
        }
        self.preferences = {
            'communication_style': 'professional',
            'decision_factors': [],
            'feedback_history': [],
        }
        self.conversation_history = []
    
    def to_dict(self) -> Dict:
        return {
            'basic_info': self.basic_info,
            'work_info': self.work_info,
            'job_intention': self.job_intention,
            'job_progress': self.job_progress,
            'preferences': self.preferences,
            'conversation_count': len(self.conversation_history),
        }
    
    def update_from_conversation(self, user_message: str):
        """从对话中自动提取和更新用户信息"""
        # 提取姓名
        name_match = re.search(r'我叫 ([\u4e00-\u9fa5]{2,4})', user_message)
        if name_match:
            self.basic_info['name'] = name_match.group(1)
        
        # 提取学历
        edu_match = re.search(r'([\u4e00-\u9fa5]{2,4})学历', user_message)
        if edu_match:
            self.basic_info['education'] = edu_match.group(1)
        
        # 提取工作年限
        years_match = re.search(r'(\d+)[年]+?(?:工作)?经验', user_message)
        if years_match:
            self.work_info['years_of_experience'] = int(years_match.group(1))
        
        # 提取目标岗位
        target_match = re.search(r'想找[\u4e00-\u9fa5]*?([\u4e00-\u9fa5]+(?:开发 | 工程师 | 经理 | 总监 | 专员))', user_message)
        if target_match:
            self.job_intention['target_position'] = target_match.group(1)
        
        # 提取目标城市
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '南京', '武汉', '西安', '厦门']
        for city in cities:
            if city in user_message and '城市' in user_message or '去' in user_message:
                self.job_intention['target_city'] = city
                break
        
        # 提取期望薪资
        salary_match = re.search(r'期望.*?(\d+)[kK]?', user_message)
        if salary_match:
            self.job_intention['expected_salary'] = int(salary_match.group(1))


class ChatAssistant:
    """智能求职助手 - 对话 AI"""
    def __init__(self, api_key=None, model="qwen3.6-plus", base_url=None, data_path=None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.client = None
        if self.api_key and self.api_key != "your_api_key_here":
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        
        # 用户档案
        self.user_profile = UserProfile()
        
        # 对话模式
        self.current_mode = 'general'
        self.mode_context = {}
        
        # 加载岗位数据
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'processed', 'cleaned_recruitment_data(1).csv'
            )
        self.job_data = None
        if os.path.exists(data_path):
            self.job_data = pd.read_csv(data_path, encoding='utf-8')
        
        print(f"[ChatAssistant] 初始化完成，模型：{self.model}")
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        profile = self.user_profile.to_dict()
        
        prompt = f"""
你是"职引助手"，一个专业的全流程陪伴式求职顾问。

## 你的角色
- 专业的求职顾问，拥有丰富的招聘行业经验
- 温暖的倾听者，能理解求职者的压力和焦虑
- 实用的建议者，提供具体可操作的建议
- 诚实的评估者，客观分析用户的优势和不足

## 用户档案
{json.dumps(profile, ensure_ascii=False, indent=2)}

## 对话原则
1. 友好专业：使用亲切但不失专业的语气
2. 具体实用：避免空泛建议，提供具体可操作的方案
3. 个性化：根据用户档案提供定制化建议
4. 共情理解：当用户表达焦虑或沮丧时，先共情再给建议
5. 引导互动：适时提出问题，引导用户更多信息
6. 记住上下文：引用之前对话中提到的信息

## 可用功能
你可以帮助用户：
- 简历优化和评估
- 面试准备和模拟
- 岗位匹配和推荐
- 薪资谈判指导
- 职业规划建议
- 求职心理支持
- 求职流程答疑

## 当前对话模式：{self.current_mode}
"""
        return prompt
    
    def chat(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """处理用户对话"""
        if not self.client:
            return "抱歉，服务暂未配置 API Key，无法进行对话。"
        
        # 更新用户档案
        self.user_profile.update_from_conversation(user_message)
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        # 添加对话历史（最多保留 10 轮）
        if conversation_history:
            for msg in conversation_history[-20:]:
                messages.append(msg)
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"对话服务暂时不可用，请稍后重试。错误：{safe_error}"
    
    def optimize_resume(self, resume_text: str, target_job: str = None) -> str:
        """简历优化对话"""
        self.current_mode = 'resume_optimization'
        
        prompt = f"""
请作为专业简历顾问，对用户提供的简历进行优化建议。

## 用户简历内容
{resume_text}

## 目标岗位（如有）
{target_job or '未指定'}

请提供：
1. 简历整体评分（0-100 分）和总体评价
2. 主要问题指出（内容、结构、表达等方面）
3. 逐段优化建议
4. 针对目标岗位的定制化建议（如有）
5. 具体修改示例

请用友好的语气，像面对面指导一样与用户交流。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的简历优化顾问，擅长帮助用户提升简历质量。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"简历优化服务暂时不可用：{safe_error}"
    
    def simulate_interview(self, job_title: str, interview_type: str = "general") -> Dict:
        """面试模拟"""
        self.current_mode = 'interview_simulation'
        
        # 生成面试问题
        questions = self._generate_interview_questions(job_title, interview_type)
        
        return {
            'mode': 'interview_simulation',
            'job_title': job_title,
            'interview_type': interview_type,
            'questions': questions,
            'current_question_index': 0,
            'feedback': [],
        }
    
    def _generate_interview_questions(self, job_title: str, interview_type: str) -> List[Dict]:
        """生成面试问题"""
        questions = []
        
        # 根据面试类型生成问题
        if interview_type == "hr":
            questions = [
                {"question": "请做一个简短的自我介绍", "type": "self_intro"},
                {"question": "你为什么选择我们公司？", "type": "motivation"},
                {"question": "你的职业规划是什么？", "type": "career_plan"},
                {"question": "你最大的优点和缺点是什么？", "type": "strengths_weaknesses"},
                {"question": "你期望的薪资是多少？", "type": "salary"},
            ]
        elif interview_type == "technical":
            questions = [
                {"question": f"请介绍一下你最近做的与{job_title}相关的项目", "type": "project"},
                {"question": "你在项目中遇到的最大技术挑战是什么？如何解决的？", "type": "challenge"},
                {"question": "你熟悉哪些技术栈？最擅长哪个？", "type": "skills"},
                {"question": "如果遇到一个不熟悉的技术问题，你会怎么处理？", "type": "problem_solving"},
            ]
        else:
            questions = [
                {"question": "请做一个简短的自我介绍", "type": "self_intro"},
                {"question": "你为什么想应聘这个岗位？", "type": "motivation"},
                {"question": "你觉得自己最大的优势是什么？", "type": "strengths"},
                {"question": "你期望的薪资是多少？", "type": "salary"},
                {"question": "你有什么问题想问我们？", "type": "questions"},
            ]
        
        return questions
    
    def evaluate_answer(self, question: str, user_answer: str, job_title: str = None) -> str:
        """评估面试回答"""
        prompt = f"""
请评估以下面试回答：

## 面试问题
{question}

## 候选人回答
{user_answer}

## 目标岗位
{job_title or '未指定'}

请从以下维度进行评估：
1. 内容完整性（0-10 分）
2. 逻辑清晰度（0-10 分）
3. 表达流畅度（0-10 分）
4. 专业匹配度（0-10 分）
5. 总体评价

并给出：
- 回答中的亮点
- 需要改进的地方
- 更优回答示例

请用鼓励性的语气，像面试官给反馈一样。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的面试评估官，擅长评估候选人的面试表现并提供建设性反馈。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"评估服务暂时不可用：{safe_error}"
    
    def recommend_jobs(self, filters: Dict = None) -> List[Dict]:
        """岗位推荐"""
        if self.job_data is None or self.job_data.empty:
            return []
        
        filtered = self.job_data.copy()
        
        # 应用筛选条件
        if filters:
            if filters.get('position'):
                filtered = filtered[filtered['招聘岗位'].str.contains(filters['position'], case=False, na=False)]
            if filters.get('city'):
                filtered = filtered[filtered['工作城市'] == filters['city']]
            if filters.get('min_salary'):
                filtered = filtered[filtered['最高月薪'] >= filters['min_salary']]
            if filters.get('max_salary'):
                filtered = filtered[filtered['最低月薪'] <= filters['max_salary']]
            if filters.get('experience'):
                filtered = filtered[filtered['要求经验'].str.contains(filters['experience'], na=False)]
        
        # 按平均月薪排序
        if '平均月薪' in filtered.columns:
            filtered = filtered.sort_values('平均月薪', ascending=False)
        
        # 返回前 10 条
        result = filtered.head(10)
        
        recommendations = []
        for _, row in result.iterrows():
            rec = {
                'position': row.get('招聘岗位', ''),
                'company': row.get('企业名称', ''),
                'city': row.get('工作城市', ''),
                'salary_range': f"{row.get('最低月薪', 0):.0f}-{row.get('最高月薪', 0):.0f} 元",
                'experience': row.get('要求经验', ''),
                'education': row.get('学历要求', ''),
            }
            recommendations.append(rec)
        
        return recommendations
    
    def career_planning(self, current_situation: str) -> str:
        """职业规划建议"""
        prompt = f"""
请作为职业规划师，根据以下用户情况提供职业发展建议：

## 用户当前情况
{current_situation}

请提供：
1. 职业方向评估
2. 短期目标建议（3-6 个月）
3. 中期目标建议（1-2 年）
4. 需要提升的技能
5. 推荐的学习资源

请用温暖的语气，像一位经验丰富的导师一样给建议。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的职业规划师，擅长帮助用户制定切实可行的职业发展计划。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"职业规划服务暂时不可用：{safe_error}"
    
    def emotional_support(self, user_message: str) -> str:
        """情绪支持和心理疏导"""
        prompt = f"""
用户正在求职过程中，表达了以下情绪和想法：

"{user_message}"

请作为一位温暖的朋友和专业的心理咨询师：
1. 先表达理解和共情
2. 肯定用户的感受和经历
3. 提供积极的角度和建议
4. 给出实用的应对方法
5. 鼓励用户继续前进

语气要温暖、真诚、有力量，避免空洞的鸡汤。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位温暖的朋友和专业的心理咨询师，擅长帮助求职者缓解压力和焦虑。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"心理支持服务暂时不可用：{safe_error}"
