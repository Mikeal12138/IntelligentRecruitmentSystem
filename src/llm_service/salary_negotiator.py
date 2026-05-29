"""
薪资谈判助手服务
功能：
1. 市场薪资查询和统计分析
2. 薪资谈判策略生成
3. 谈判话术生成
4. 福利待遇分析
"""
import os
import sys
import re
import json
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))


class SalaryNegotiator:
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
            print(f"[SalaryNegotiator] 初始化成功，API Base: {self.base_url}")
        
        # 加载招聘数据
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'processed', 'cleaned_recruitment_data(1).csv'
            )
        
        self.df = None
        if os.path.exists(data_path):
            try:
                self.df = pd.read_csv(data_path, encoding='utf-8')
                print(f"[SalaryNegotiator] 成功加载 {len(self.df)} 条招聘数据")
            except Exception as e:
                print(f"[SalaryNegotiator] 加载数据失败：{str(e)}")
    
    def query_market_salary(self, position: str, city: str = None, 
                           experience: str = None, industry: str = None) -> Dict:
        """查询市场薪资范围"""
        if self.df is None or self.df.empty:
            return {"error": "未加载招聘数据"}
        
        # 筛选数据
        filtered = self.df.copy()
        
        # 按岗位名称筛选（模糊匹配，支持部分关键词）
        if position:
            # 提取岗位关键词
            keywords = []
            if 'Java' in position or 'java' in position.lower():
                keywords.append('Java')
            if 'Python' in position or 'python' in position.lower():
                keywords.append('Python')
            if '前端' in position:
                keywords.append('前端')
            if '后端' in position:
                keywords.append('后端')
            if '开发' in position:
                keywords.append('开发')
            if '工程师' in position:
                keywords.append('工程师')
            if '产品经理' in position:
                keywords.append('产品经理')
            if '数据分析' in position:
                keywords.append('数据分析')
            
            # 如果没有提取到关键词，使用原始输入
            if not keywords:
                keywords = [position]
            
            # 构建筛选条件：只要包含任一关键词即可
            mask = filtered['招聘岗位'].notna()
            for keyword in keywords:
                mask = mask | filtered['招聘岗位'].str.contains(keyword, case=False, na=False)
            filtered = filtered[mask]
        
        # 按城市筛选
        if city and city != "全部":
            filtered = filtered[filtered['工作城市'] == city]
        
        # 按经验筛选
        if experience and experience != "全部":
            filtered = filtered[filtered['要求经验'] == experience]
        
        # 按行业筛选
        if industry and industry != "全部":
            filtered = filtered[filtered['行业类型'] == industry]
        
        # 检查是否有数据
        if filtered.empty or '平均月薪' not in filtered.columns:
            return {"error": "未找到匹配的薪资数据", "sample_size": 0}
        
        # 计算统计信息
        salary_data = filtered['平均月薪'].dropna()
        
        if salary_data.empty:
            return {"error": "薪资数据为空", "sample_size": 0}
        
        result = {
            'sample_size': len(salary_data),
            'min_salary': float(salary_data.min()),
            'max_salary': float(salary_data.max()),
            'avg_salary': float(salary_data.mean()),
            'median_salary': float(salary_data.median()),
            'percentile_25': float(salary_data.quantile(0.25)),
            'percentile_75': float(salary_data.quantile(0.75)),
        }
        
        # 按经验分组统计
        if '要求经验' in filtered.columns and '平均月薪' in filtered.columns:
            by_experience = filtered.groupby('要求经验')['平均月薪'].agg(['mean', 'count'])
            by_experience = by_experience.reset_index()
            by_experience.columns = ['经验要求', '平均薪资', '样本数']
            result['by_experience'] = by_experience.to_dict('records')
        
        # 按城市分组统计
        if '工作城市' in filtered.columns and '平均月薪' in filtered.columns:
            by_city = filtered.groupby('工作城市')['平均月薪'].agg(['mean', 'count'])
            by_city = by_city.reset_index()
            by_city.columns = ['城市', '平均薪资', '样本数']
            by_city = by_city.sort_values('样本数', ascending=False).head(10)
            result['by_city'] = by_city.to_dict('records')
        
        return result
    
    def generate_negotiation_strategy(self, position: str, company_name: str,
                                     experience: str, offer_salary: float,
                                     target_salary: float, market_min: float = None,
                                     market_max: float = None, company_size: str = None,
                                     industry: str = None) -> str:
        """生成薪资谈判策略"""
        if not self.client:
            return "未配置 API Key，无法生成谈判策略"
        
        # 计算薪资差距
        gap = target_salary - offer_salary
        gap_percent = (gap / offer_salary) * 100 if offer_salary > 0 else 0
        
        # 构建市场薪资信息
        market_info = ""
        if market_min and market_max:
            market_info = f"""
市场薪资参考：
- 市场最低：{market_min:.0f} 元/月
- 市场最高：{market_max:.0f} 元/月
- 市场平均：{(market_min + market_max) / 2:.0f} 元/月
"""
        
        prompt = f"""
作为专业的薪资谈判顾问，请为用户制定薪资谈判策略。

## 用户情况
- 目标岗位：{position}
- 目标公司：{company_name}
- 工作经验：{experience}
{f"- 公司规模：{company_size}" if company_size else ""}
{f"- 行业类型：{industry}" if industry else ""}

## 薪资信息
- 公司 Offer：{offer_salary:.0f} 元/月
- 期望薪资：{target_salary:.0f} 元/月
- 薪资差距：{gap:.0f} 元/月（差距 {gap_percent:.1f}%）

{market_info}

请提供：
1. **谈判可行性分析**：评估期望薪资是否合理
2. **谈判策略**：具体的谈判步骤和策略
3. **话术模板**：3-5 个可以直接使用的谈判话术
4. **备选方案**：如果公司无法满足期望，可以争取的其他福利
5. **注意事项**：谈判中需要避免的误区

要求：
- 语气专业、自信但不傲慢
- 提供具体可操作的建议
- 话术要自然、真实
- 考虑中国职场文化
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的薪资谈判顾问，拥有 10 年以上 HR 和猎头经验。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"生成策略失败：{safe_error}"
    
    def analyze_benefits(self, offer_salary: float, position: str = None,
                        industry: str = None) -> Dict:
        """分析福利待遇"""
        if self.df is None or self.df.empty:
            return {"error": "未加载招聘数据"}
        
        # 筛选数据
        filtered = self.df.copy()
        
        if position:
            filtered = filtered[filtered['招聘岗位'].str.contains(position, case=False, na=False)]
        
        if industry and industry != "全部":
            filtered = filtered[filtered['行业类型'] == industry]
        
        if filtered.empty:
            return {"error": "未找到匹配数据", "sample_size": 0}
        
        # 统计年终奖
        bonus_data = {}
        if '年终奖估算' in filtered.columns:
            bonus_col = filtered['年终奖估算'].dropna()
            if not bonus_col.empty:
                bonus_data = {
                    'sample_size': len(bonus_col),
                    'avg_bonus': float(bonus_col.mean()),
                    'max_bonus': float(bonus_col.max()),
                    'min_bonus': float(bonus_col.min()),
                }
        
        # 提取常见福利关键词
        common_benefits = []
        if '职位描述' in filtered.columns:
            all_descriptions = ' '.join(filtered['职位描述'].dropna().tolist())
            
            # 常见福利关键词
            benefit_keywords = [
                '五险一金', '六险二金', '年终奖', '带薪年假', '弹性工作',
                '定期体检', '节日福利', '餐补', '交通补贴', '住房补贴',
                '通讯补贴', '股票期权', '绩效奖金', '年终双薪', '年底双薪',
                '免费班车', '员工旅游', '加班补助', '全勤奖', '工龄奖',
                '培训机会', '晋升空间', '周末双休', '下午茶', '健身房',
                '团队建设', '生日福利', '结婚礼金', '生育礼金', '子女教育',
            ]
            
            for benefit in benefit_keywords:
                if benefit in all_descriptions:
                    common_benefits.append(benefit)
        
        result = {
            'sample_size': len(filtered),
            'common_benefits': common_benefits,
        }
        
        if bonus_data:
            result.update(bonus_data)
        
        return result
    
    def generate_salary_report(self, position: str, city: str = None,
                              experience: str = None) -> str:
        """生成薪资分析报告"""
        if not self.client:
            return "未配置 API Key，无法生成报告"
        
        # 先查询市场数据
        market_data = self.query_market_salary(position, city, experience)
        
        market_info = ""
        if 'error' not in market_data:
            market_info = f"""
市场调研数据（基于 {market_data.get('sample_size', 0)} 条数据）：
- 薪资范围：{market_data.get('min_salary', 0):.0f} - {market_data.get('max_salary', 0):.0f} 元/月
- 平均薪资：{market_data.get('avg_salary', 0):.0f} 元/月
- 中位数薪资：{market_data.get('median_salary', 0):.0f} 元/月
- 25% 分位：{market_data.get('percentile_25', 0):.0f} 元/月
- 75% 分位：{market_data.get('percentile_75', 0):.0f} 元/月
"""
        
        prompt = f"""
作为薪资分析专家，请生成一份详细的薪资分析报告。

## 岗位信息
- 岗位名称：{position}
{f"- 工作城市：{city}" if city else ""}
{f"- 工作经验：{experience}" if experience else ""}

{market_info}

请提供：
1. **薪资水平分析**：当前市场行情和趋势
2. **影响薪资的因素**：学历、经验、技能、公司规模等
3. **薪资谈判建议**：如何在这个岗位上获得更好的薪资
4. **职业发展建议**：如何通过提升自身价值来获得更高薪资
5. **市场趋势预测**：未来 1-2 年的薪资变化趋势

要求数据详实、建议具体可操作。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的薪资分析专家，擅长市场行情分析和薪资谈判指导。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"生成报告失败：{safe_error}"
    
    def get_preparation_checklist(self) -> List[str]:
        """获取谈判前准备清单"""
        return [
            " 研究目标公司的薪资水平和福利待遇",
            " 了解该岗位的市场薪资范围（使用市场薪资查询功能）",
            " 准备你的薪资期望范围（最低可接受值和理想值）",
            " 列出你的核心优势和成就（用数据说话）",
            " 了解公司的薪酬结构（基本工资、绩效、奖金等）",
            " 准备 3-5 个可以争取的福利项目清单",
            " 练习谈判话术，保持自信和专业",
            " 设定谈判底线，做好 Walk Away 的准备",
            " 了解公司的薪资调整周期和晋升机制",
            ' 准备好回答"你为什么值这个薪资"的问题',
        ]
    
    def generate_negotiation_script(self, company_name: str, position: str,
                                   experience: str, market_min: float,
                                   market_max: float, offer_salary: float,
                                   target_salary: float) -> str:
        """生成谈判话术（使用优化后的提示词模板）"""
        if not self.client:
            return "未配置 API Key，无法生成话术"
        
        # 转换为 K 单位
        market_min_k = market_min / 1000 if market_min else 0
        market_max_k = market_max / 1000 if market_max else 0
        offer_k = offer_salary / 1000 if offer_salary else 0
        target_k = target_salary / 1000 if target_salary else 0
        
        prompt = f"""
我正在面试{company_name}的{position}岗位，我的工作经验是{experience}年，
该岗位的市场薪资范围是{market_min_k:.0f}-{market_max_k:.0f}K，公司给我的 offer 是{offer_k:.0f}K。

请帮我生成一个薪资谈判的话术，目标是争取到{target_k:.0f}K，
同时分析可以争取的其他福利待遇。

要求：
1. 话术要自然、专业、有说服力
2. 用市场数据支撑你的要求
3. 提供 3 个不同场景的话术：
   - 初次谈判（温和试探）
   - 深入谈判（数据支撑）
   - 最后通（设定底线）
4. 列出可以争取的其他福利（至少 5 项）
5. 提供谈判注意事项
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的薪资谈判顾问，拥有 10 年以上 HR 和猎头经验。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=120,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"生成话术失败：{safe_error}"
