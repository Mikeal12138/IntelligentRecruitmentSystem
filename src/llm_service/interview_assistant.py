"""
面试辅助与评估服务
功能：
1. 生成面试题库（结合岗位要求）
2. AI实时记录面试语音转文字并提炼要点
3. 面试表现评分
"""
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class InterviewAssistant:
    """面试辅助助手"""
    
    def __init__(self, api_key=None, model="qwen3.6-plus", base_url=None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.client = None
        
        if self.api_key and self.api_key != "your_api_key_here":
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
    
    def generate_questions(self, position, experience=None, skill_requirements=None, question_count=5):
        """
        根据岗位要求生成面试题库
        
        参数：
        - position: 岗位名称
        - experience: 工作经验要求（可选）
        - skill_requirements: 技能要求列表（可选）
        - question_count: 生成题目数量
        
        返回：
        - 包含问题和参考答案的列表
        """
        if not self.client:
            return self._generate_default_questions(position, question_count)
        
        skills_text = ", ".join(skill_requirements) if skill_requirements else "未指定"
        
        prompt = f"""
作为一名资深面试官，请为以下岗位生成面试题：

岗位信息：
- 岗位名称：{position}
- 经验要求：{experience or '不限'}
- 技能要求：{skills_text}

请生成 {question_count} 道面试题，涵盖以下类型：
1. 技术基础题
2. 项目经验题
3. 问题解决题
4. 行为面试题

每道题请提供：
- 题目类型
- 问题描述
- 考察要点
- 参考答案要点

输出格式：
1. 【类型】问题描述
   - 考察要点：xxx
   - 参考答案要点：xxx

请用中文输出，语言专业但易于理解。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的技术面试官，擅长设计高质量的面试问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"生成面试题时出错：{str(e)}\n\n{self._generate_default_questions(position, question_count)}"
    
    def _generate_default_questions(self, position, count):
        """生成默认面试题（备用）"""
        questions = [
            {
                "type": "技术基础",
                "question": f"请介绍一下{position}岗位所需的核心技术栈？",
                "focus": "考察候选人对岗位技术要求的理解",
                "answer": "根据岗位需求，核心技术栈通常包括：..."
            },
            {
                "type": "项目经验",
                "question": f"请描述一个你在{position}相关项目中遇到的最大挑战？",
                "focus": "考察候选人的问题解决能力和项目经验",
                "answer": "在XX项目中，我遇到了XX问题，通过XX方法解决..."
            },
            {
                "type": "技术深度",
                "question": f"请深入讲解{position}相关的一个核心技术原理？",
                "focus": "考察候选人的技术深度和理解能力",
                "answer": "以XX技术为例，其核心原理是..."
            },
            {
                "type": "行为面试",
                "question": "你如何处理工作中的压力和挑战？",
                "focus": "考察候选人的抗压能力和应对策略",
                "answer": "我通常会通过XX方式来管理压力..."
            },
            {
                "type": "团队协作",
                "question": "请描述一次成功的团队合作经历？",
                "focus": "考察候选人的团队协作能力",
                "answer": "在XX项目中，我与团队成员通过XX方式..."
            }
        ]
        
        result = ""
        for i, q in enumerate(questions[:count], 1):
            result += f"{i}. 【{q['type']}】{q['question']}\n"
            result += f"   - 考察要点：{q['focus']}\n"
            result += f"   - 参考答案要点：{q['answer']}\n\n"
        
        return result
    
    def analyze_interview_transcript(self, transcript, position):
        """
        分析面试记录，提炼要点
        
        参数：
        - transcript: 面试语音转文字记录
        - position: 面试岗位
        
        返回：
        - 分析报告，包含要点提炼和评估
        """
        if not self.client:
            return self._default_analyze_transcript(transcript, position)
        
        prompt = f"""
作为一名专业的面试评估专家，请分析以下面试记录：

面试岗位：{position}

面试记录：
{transcript}

请从以下维度进行分析：
1. 技术能力评估：候选人的技术知识掌握程度
2. 项目经验：候选人描述的项目经历是否充分
3. 沟通能力：表达是否清晰、逻辑是否严谨
4. 问题解决能力：面对问题时的思考方式
5. 文化匹配度：是否适合团队文化

请提供详细的分析报告，包括优点和改进建议。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的面试评估专家，擅长分析面试表现。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"分析面试记录时出错：{str(e)}\n\n{self._default_analyze_transcript(transcript, position)}"
    
    def _default_analyze_transcript(self, transcript, position):
        """默认分析面试记录（备用）"""
        analysis = f"""
## 面试分析报告

### 面试岗位
{position}

### 面试记录要点
{transcript[:200]}...

### 评估维度

**1. 技术能力评估**
- 需要进一步了解候选人的技术深度

**2. 项目经验**
- 需要更多具体项目案例

**3. 沟通能力**
- 表达清晰度待评估

**4. 问题解决能力**
- 需要更多实例验证

**5. 文化匹配度**
- 需要进一步了解

### 综合建议
建议继续深入提问以全面评估候选人能力。
"""
        return analysis
    
    def score_interview(self, transcript, position, criteria=None):
        """
        对面试表现进行评分
        
        参数：
        - transcript: 面试记录
        - position: 面试岗位
        - criteria: 评分标准（可选）
        
        返回：
        - 评分报告，包含各项得分和综合评价
        """
        if not self.client:
            return self._default_score_interview(transcript, position)
        
        prompt = f"""
作为一名专业的面试评估专家，请为以下面试表现评分：

面试岗位：{position}

面试记录：
{transcript}

请按照以下标准评分（每项满分10分）：
1. 技术能力：技术知识掌握程度和深度
2. 项目经验：项目经历的丰富度和相关性
3. 沟通表达：表达清晰度和逻辑性
4. 问题解决：分析和解决问题的能力
5. 团队协作：团队合作和沟通能力

请提供：
- 各项得分和简要理由
- 综合评分
- 录用建议（强烈推荐/推荐/观望/不推荐）
- 改进建议（如适用）
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的面试评估专家，擅长给出客观公正的评分。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"评分时出错：{str(e)}\n\n{self._default_score_interview(transcript, position)}"
    
    def _default_score_interview(self, transcript, position):
        """默认评分（备用）"""
        report = f"""
## 面试评分报告

### 面试岗位
{position}

### 评分详情

| 维度 | 得分 | 评价 |
|------|------|------|
| 技术能力 | 7/10 | 具备基本技术能力，需进一步考察深度 |
| 项目经验 | 6/10 | 有一定项目经验，需更多细节验证 |
| 沟通表达 | 7/10 | 表达较为清晰，逻辑基本连贯 |
| 问题解决 | 6/10 | 问题分析能力有待提高 |
| 团队协作 | 7/10 | 团队合作意识良好 |

### 综合评分
**6.8/10**

### 录用建议
**推荐**

### 改进建议
- 建议进一步考察技术深度
- 建议了解更多项目细节
- 可考虑安排二面深入评估
"""
        return report
    
    def generate_follow_up_questions(self, transcript, position, count=3):
        """
        根据面试记录生成追问问题
        
        参数：
        - transcript: 已有面试记录
        - position: 面试岗位
        - count: 追问数量
        
        返回：
        - 追问问题列表
        """
        if not self.client:
            return self._default_follow_up_questions(position, count)
        
        prompt = f"""
根据以下面试记录，生成 {count} 个针对性的追问问题：

面试岗位：{position}

面试记录：
{transcript}

请分析候选人的回答，找出需要深入了解的地方，生成追问问题。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的面试官，擅长根据候选人回答提出深入的追问。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"生成追问时出错：{str(e)}\n\n{self._default_follow_up_questions(position, count)}"
    
    def _default_follow_up_questions(self, position, count):
        """默认追问问题（备用）"""
        questions = [
            f"你在{position}相关项目中遇到的最大挑战是什么？如何解决的？",
            f"请详细描述你在{position}工作中最有成就感的一个项目？",
            f"你认为作为{position}，最重要的三项能力是什么？你如何提升这些能力？",
            f"请举例说明你如何学习新技术并应用到实际工作中？",
            f"你对我们公司了解多少？为什么想来这里工作？"
        ]
        
        result = ""
        for i, q in enumerate(questions[:count], 1):
            result += f"{i}. {q}\n"
        
        return result
