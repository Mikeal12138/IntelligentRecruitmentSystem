"""
个人简历智能解析与评估服务
功能：
1. 支持 PDF、Word、TXT 格式简历上传
2. 自动提取个人信息、教育背景、工作经历、技能等
3. 生成简历评分报告
4. 提供优化建议
5. 基于简历信息进行岗位推荐
"""
import os
import sys
import re
import json
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

# 设置控制台编码为 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))


class ResumeParser:
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
            print(f"[ResumeParser] 初始化成功，API Base: {self.base_url}")
        self.job_skills = self._load_job_skills()
    
    def _load_job_skills(self):
        """加载市场岗位技能数据（用于匹配度计算）"""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'processed', 'cleaned_recruitment_data(1).csv'
        )
        if os.path.exists(data_path):
            df = pd.read_csv(data_path, encoding='utf-8')
            # 提取常见技能关键词
            all_text = ' '.join(df['职位描述'].dropna().tolist())
            # 简单提取技能词（实际项目可以使用更复杂的 NLP）
            skill_keywords = [
                'Python', 'Java', 'JavaScript', 'C++', 'C', 'Go', 'Rust', 'PHP',
                'Vue', 'React', 'Angular', 'Spring', 'Django', 'Flask', 'FastAPI',
                'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Docker', 'Kubernetes', 'AWS', 'Azure', '阿里云',
                '机器学习', '深度学习', '数据分析', '数据挖掘', '人工智能',
                'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
                'Git', 'Linux', 'Windows', 'MacOS',
                '项目管理', '团队协作', '沟通能力', '逻辑思维',
                'HTML', 'CSS', 'TypeScript', 'Node.js', 'Express',
                '微服务', '分布式', '高并发', '性能优化',
                'SQL', 'NoSQL', '大数据', 'Hadoop', 'Spark',
            ]
            return skill_keywords
        return []
    
    def extract_text_from_pdf(self, file_path) -> str:
        """从 PDF 文件提取文本"""
        text = ""
        errors = []
        
        # 方法 1：尝试 pdfplumber
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        safe_text = page_text.encode('utf-8', errors='replace').decode('utf-8')
                        text += safe_text + "\n"
            if text.strip():
                print(f"[PDF] pdfplumber 提取成功，共 {len(text)} 字符")
                return text
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            errors.append(f"pdfplumber: {safe_error}")
            print(f"[PDF] pdfplumber 提取失败: {safe_error}")
        
        # 方法 2：尝试 PyPDF2
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        safe_text = page_text.encode('utf-8', errors='replace').decode('utf-8')
                        text += safe_text + "\n"
            if text.strip():
                print(f"[PDF] PyPDF2 提取成功，共 {len(text)} 字符")
                return text
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            errors.append(f"PyPDF2: {safe_error}")
            print(f"[PDF] PyPDF2 提取失败: {safe_error}")
        
        # 方法 3：尝试 pdfminer
        try:
            from pdfminer.high_level import extract_text as pdfminer_extract
            text = pdfminer_extract(file_path)
            if text.strip():
                safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
                print(f"[PDF] pdfminer 提取成功，共 {len(safe_text)} 字符")
                return safe_text
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            errors.append(f"pdfminer: {safe_error}")
            print(f"[PDF] pdfminer 提取失败: {safe_error}")
        
        # 如果所有方法都失败，尝试使用 fitz (PyMuPDF)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                page_text = page.get_text()
                if page_text:
                    safe_text = page_text.encode('utf-8', errors='replace').decode('utf-8')
                    text += safe_text + "\n"
            doc.close()
            if text.strip():
                print(f"[PDF] PyMuPDF 提取成功，共 {len(text)} 字符")
                return text
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            errors.append(f"PyMuPDF: {safe_error}")
            print(f"[PDF] PyMuPDF 提取失败: {safe_error}")
        
        # 如果所有方法都失败，给出详细错误信息
        error_summary = "\n".join(errors) if errors else "未知错误"
        raise ValueError(f"无法从 PDF 中提取文本。可能的原因：\n1. PDF是扫描版或图片类型\n2. PDF格式特殊或损坏\n3. 缺少必要的解析库\n\n详细错误：\n{error_summary}")
    
    def extract_text_from_docx(self, file_path) -> str:
        """从 Word 文档提取文本"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")
    
    def extract_text_from_txt(self, file_path) -> str:
        """从 TXT 文件提取文本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def extract_text(self, file_path) -> str:
        """根据文件类型提取文本"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
    
    def parse_resume(self, resume_text: str) -> Dict:
        """使用大模型 API 解析简历"""
        if not self.client:
            raise ValueError("未配置 LLM API Key，请在环境变量中设置 LLM_API_KEY")
        
        # 如果简历文本太长，截取前 8000 字符
        if len(resume_text) > 8000:
            resume_text = resume_text[:8000] + "\n...（内容过长，已截断）"
        
        prompt = f"""
请解析以下简历内容，提取关键信息并返回 JSON 格式。

简历内容：
{resume_text}

请提取以下信息并以 JSON 格式返回（如果某项信息不存在，设为 null）：
{{
  "name": "姓名",
  "phone": "电话号码",
  "email": "邮箱",
  "education": [
    {{
      "degree": "学历（如：本科、硕士、博士）",
      "school": "学校名称",
      "major": "专业",
      "graduation_year": "毕业年份"
    }}
  ],
  "work_experience": [
    {{
      "company": "公司名称",
      "position": "职位",
      "duration": "工作时长",
      "description": "工作描述"
    }}
  ],
  "projects": [
    {{
      "name": "项目名称",
      "description": "项目描述",
      "role": "担任角色"
    }}
  ],
  "skills": ["技能列表"],
  "certificates": ["证书列表"],
  "years_of_experience": "工作年限（数字）",
  "highest_degree": "最高学历"
}}

要求：
1. 只返回 JSON，不要包含其他解释文字
2. 所有字段使用中文键名
3. 数组字段如果为空返回空数组 []
4. 工作年限用数字表示
"""
        
        # 重试机制：最多重试 3 次
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[ResumeParser] 正在调用 API (尝试 {attempt + 1}/{max_retries})...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的简历解析助手，擅长从简历中提取结构化信息。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    timeout=300,  # 5 分钟超时
                )
                
                result_text = response.choices[0].message.content
                print(f"[ResumeParser] API 调用成功")
                
                # 提取 JSON
                json_match = re.search(r'\{[\s\S]*\}', result_text)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                    return parsed_data
                else:
                    return {"error": "解析失败，未能提取 JSON"}
                    
            except Exception as e:
                print(f"[ResumeParser] 尝试 {attempt + 1} 失败: {str(e)}")
                if attempt == max_retries - 1:
                    return {"error": f"解析失败（已重试 {max_retries} 次）: {str(e)}"}
                # 等待 2 秒后重试
                import time
                time.sleep(2)
    
    def evaluate_resume(self, parsed_data: Dict, target_position=None) -> Dict:
        """评估简历并生成评分报告"""
        if "error" in parsed_data:
            return parsed_data
        
        score_report = {
            'completeness_score': 0,
            'match_score': 0,
            'competitiveness_score': 0,
            'overall_score': 0,
            'strengths': [],
            'weaknesses': [],
            'suggestions': [],
        }
        
        # 1. 完整性评分（40分）
        completeness = 0
        required_fields = ['name', 'phone', 'email', 'education', 'work_experience', 'skills']
        for field in required_fields:
            if parsed_data.get(field) and parsed_data[field] not in [None, [], '']:
                completeness += 1
        
        score_report['completeness_score'] = int((completeness / len(required_fields)) * 40)
        
        # 检查具体缺失项
        if not parsed_data.get('name'):
            score_report['weaknesses'].append("缺少姓名信息")
        if not parsed_data.get('phone'):
            score_report['weaknesses'].append("缺少联系电话")
        if not parsed_data.get('email'):
            score_report['weaknesses'].append("缺少电子邮箱")
        if not parsed_data.get('education'):
            score_report['weaknesses'].append("缺少教育背景")
        if not parsed_data.get('work_experience'):
            score_report['weaknesses'].append("缺少工作经历")
        if not parsed_data.get('skills'):
            score_report['weaknesses'].append("缺少技能描述")
        
        # 2. 技能匹配度评分（30分）
        resume_skills = parsed_data.get('skills', [])
        if resume_skills and self.job_skills:
            matched_skills = []
            for skill in resume_skills:
                for market_skill in self.job_skills:
                    if market_skill.lower() in skill.lower() or skill.lower() in market_skill.lower():
                        matched_skills.append(skill)
                        break
            
            match_rate = len(matched_skills) / max(len(resume_skills), 1)
            score_report['match_score'] = int(match_rate * 30)
            score_report['matched_skills'] = matched_skills
        else:
            score_report['match_score'] = 0
        
        # 3. 竞争力评分（30分）
        competitiveness = 0
        
        # 学历加分
        degree = parsed_data.get('highest_degree', '')
        if '博士' in str(degree):
            competitiveness += 10
        elif '硕士' in str(degree):
            competitiveness += 8
        elif '本科' in str(degree):
            competitiveness += 5
        
        # 工作经验加分
        years = parsed_data.get('years_of_experience', 0)
        if isinstance(years, str):
            try:
                years = int(re.search(r'\d+', years).group())
            except:
                years = 0
        
        if years >= 10:
            competitiveness += 10
        elif years >= 5:
            competitiveness += 8
        elif years >= 3:
            competitiveness += 5
        elif years >= 1:
            competitiveness += 3
        
        # 项目经验加分
        projects = parsed_data.get('projects', [])
        if len(projects) >= 3:
            competitiveness += 10
        elif len(projects) >= 1:
            competitiveness += 5
        
        score_report['competitiveness_score'] = competitiveness
        
        # 计算总分
        score_report['overall_score'] = (
            score_report['completeness_score'] + 
            score_report['match_score'] + 
            score_report['competitiveness_score']
        )
        
        # 生成优势
        if score_report['completeness_score'] >= 30:
            score_report['strengths'].append("简历信息完整，包含关键要素")
        if score_report['match_score'] >= 20:
            score_report['strengths'].append("技能与市场需求匹配度高")
        if years >= 5:
            score_report['strengths'].append(f"拥有 {years} 年丰富工作经验")
        if degree in ['硕士', '博士']:
            score_report['strengths'].append(f"学历优势明显（{degree}）")
        if len(projects) >= 3:
            score_report['strengths'].append("项目经验丰富")
        
        # 生成建议
        if score_report['completeness_score'] < 30:
            score_report['suggestions'].append("补充完善简历基本信息，特别是联系方式和教育背景")
        if score_report['match_score'] < 15:
            score_report['suggestions'].append("提升与市场热门需求的技能匹配度，建议学习 Python、数据分析等热门技能")
        if years < 2:
            score_report['suggestions'].append("工作经验较浅，建议多积累项目经验和实习经历")
        if len(projects) < 2:
            score_report['suggestions'].append("增加项目经验描述，突出个人贡献和技术成果")
        
        return score_report
    
    def generate_improvement_report(self, parsed_data: Dict, score_report: Dict) -> str:
        """使用大模型生成详细的改进建议报告"""
        if not self.client:
            return "未配置 API，无法生成详细报告"
        
        prompt = f"""
作为专业的职业顾问，请根据以下简历信息和评分报告，提供详细的改进建议：

简历信息：
{json.dumps(parsed_data, ensure_ascii=False, indent=2)}

评分报告：
总分：{score_report.get('overall_score', 0)}/100
优势：{', '.join(score_report.get('strengths', []))}
不足：{', '.join(score_report.get('weaknesses', []))}

请提供：
1. 简历优化建议（格式、内容、表达方式）
2. 技能提升建议（针对市场需求）
3. 职业发展建议
4. 求职策略建议

请用中文回答，格式清晰，具体可操作。
"""
        
        # 重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[ResumeParser] 正在生成改进建议 (尝试 {attempt + 1}/{max_retries})...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是专业的职业顾问，擅长分析简历并提供改进建议。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500,
                    timeout=300,  # 5 分钟超时
                )
                print(f"[ResumeParser] 改进建议生成成功")
                return response.choices[0].message.content
            except Exception as e:
                print(f"[ResumeParser] 尝试 {attempt + 1} 失败: {str(e)}")
                if attempt == max_retries - 1:
                    return f"生成报告失败（已重试 {max_retries} 次）: {str(e)}"
                import time
                time.sleep(2)
    
    def parse_and_evaluate(self, file_path) -> Dict:
        """完整流程：解析 + 评估"""
        # 1. 提取文本
        try:
            resume_text = self.extract_text(file_path)
        except Exception as e:
            error_msg = str(e)
            # 安全地打印错误信息，避免编码问题
            safe_msg = error_msg.encode('utf-8', errors='replace').decode('utf-8')
            print(f"[ResumeParser] 文本提取失败：{safe_msg}")
            return {"error": f"PDF 文本提取失败：{safe_msg}"}
        
        print(f"[ResumeParser] 提取的文本长度：{len(resume_text)} 字符")
        
        if not resume_text.strip():
            return {"error": "PDF 文本提取失败，无法获取简历内容。可能是扫描版 PDF 或格式不支持。"}
        
        # 2. 解析简历
        parsed_data = self.parse_resume(resume_text)
        
        if "error" in parsed_data:
            return parsed_data
        
        # 3. 评估简历
        score_report = self.evaluate_resume(parsed_data)
        
        # 4. 生成改进建议
        improvement_report = self.generate_improvement_report(parsed_data, score_report)
        
        return {
            'parsed_data': parsed_data,
            'score_report': score_report,
            'improvement_report': improvement_report,
        }
    
    def recommend_jobs(self, parsed_data: Dict, top_n: int = 10) -> List[Dict]:
        """基于解析的简历信息推荐合适的岗位"""
        if "error" in parsed_data:
            return []
        
        # 加载招聘数据
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'processed', 'cleaned_recruitment_data(1).csv'
        )
        
        if not os.path.exists(data_path):
            print("[ResumeParser] 警告：招聘数据文件不存在")
            return []
        
        try:
            df = pd.read_csv(data_path, encoding='utf-8')
        except Exception as e:
            print(f"[ResumeParser] 加载招聘数据失败：{str(e)}")
            return []
        
        # 提取简历关键信息
        candidate_skills = set()
        if parsed_data.get('skills'):
            for skill in parsed_data['skills']:
                if isinstance(skill, str):
                    candidate_skills.add(skill.lower())
        
        candidate_degree = parsed_data.get('highest_degree', '')
        candidate_experience = parsed_data.get('years_of_experience', 0)
        
        # 尝试将工作经验转换为数字
        if isinstance(candidate_experience, str):
            try:
                candidate_experience = int(''.join(filter(str.isdigit, candidate_experience)))
            except:
                candidate_experience = 0
        
        # 计算每个岗位的匹配度
        recommendations = []
        
        for idx, job in df.iterrows():
            score = 0
            match_reasons = []
            
            # 1. 技能匹配度（50分）
            job_desc = str(job.get('职位描述', '')).lower()
            matched_skills = []
            for skill in self.job_skills:
                if skill.lower() in candidate_skills and skill.lower() in job_desc:
                    score += 5
                    matched_skills.append(skill)
                    if len(matched_skills) >= 10:
                        break
            
            if matched_skills:
                match_reasons.append(f"技能匹配：{', '.join(matched_skills[:5])}")
            
            # 2. 学历匹配度（20分）
            job_edu = str(job.get('学历要求', ''))
            degree_score = {'博士': 5, '硕士': 4, '本科': 3, '大专': 2, '其他': 1}
            candidate_degree_level = degree_score.get(candidate_degree, 0)
            job_degree_level = degree_score.get(job_edu, 0)
            
            if candidate_degree_level >= job_degree_level:
                score += 20
                match_reasons.append(f"学历符合要求（{candidate_degree}）")
            elif candidate_degree_level >= job_degree_level - 1:
                score += 10
                match_reasons.append(f"学历基本符合（{candidate_degree}）")
            
            # 3. 经验匹配度（20分）
            job_exp = str(job.get('要求经验', ''))
            exp_score = self._parse_experience_requirement(job_exp)
            
            if candidate_experience >= exp_score:
                score += 20
                match_reasons.append(f"工作经验符合（{candidate_experience}年）")
            elif candidate_experience >= exp_score - 1:
                score += 10
                match_reasons.append(f"工作经验基本符合（{candidate_experience}年）")
            
            # 4. 薪资合理性（10分）- 根据经验匹配薪资
            job_avg_salary = job.get('平均月薪', 0)
            if pd.notna(job_avg_salary):
                expected_salary = 5000 + candidate_experience * 2000
                if job_avg_salary >= expected_salary * 0.8:
                    score += 10
            
            # 只推荐匹配度较高的岗位
            if score >= 30:
                recommendations.append({
                    'company': job.get('企业名称', '未知'),
                    'position': job.get('招聘岗位', '未知'),
                    'city': job.get('工作城市', '未知'),
                    'min_salary': job.get('最低月薪', 0),
                    'max_salary': job.get('最高月薪', 0),
                    'avg_salary': job.get('平均月薪', 0),
                    'education': job.get('学历要求', '未知'),
                    'experience': job.get('要求经验', '未知'),
                    'industry': job.get('行业类型', '未知'),
                    'company_size': job.get('企业规模', '未知'),
                    'job_desc': job.get('职位描述', ''),
                    'match_score': min(score, 100),
                    'match_reasons': match_reasons,
                    'publish_date': job.get('招聘发布日期', '未知'),
                })
        
        # 按匹配度排序
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        
        return recommendations[:top_n]
    
    def _parse_experience_requirement(self, exp_str: str) -> int:
        """解析经验要求字符串，返回最低要求年限"""
        if not exp_str or exp_str == '经验不限':
            return 0
        
        # 提取数字
        numbers = re.findall(r'\d+', exp_str)
        if numbers:
            return int(numbers[0])
        
        # 常见经验要求映射
        exp_mapping = {
            '应届生': 0,
            '在校': 0,
            '经验不限': 0,
            '1-3年': 1,
            '3-5年': 3,
            '5-10年': 5,
            '10年以上': 10,
        }
        
        for key, value in exp_mapping.items():
            if key in exp_str:
                return value
        
        return 0
