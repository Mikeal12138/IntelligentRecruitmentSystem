"""
薪资谈判助手服务
功能：
1. 市场薪资查询
2. 薪资谈判策略生成
3. 谈判话术生成
4. 福利待遇分析
"""
import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))


class SalaryNegotiator:
    def __init__(self, data_path=None, api_key=None, model="qwen3.6-plus", base_url=None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.client = None
        if self.api_key and self.api_key != "your_api_key_here":
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        
        # 加载薪资数据
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'data', 'processed', 'cleaned_recruitment_data(1).csv'
            )
        self.data_path = data_path
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """加载薪资数据"""
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path, encoding='utf-8')
            print(f"[SalaryNegotiator] 已加载 {len(self.df)} 条薪资数据")
        else:
            print(f"[SalaryNegotiator] 警告：数据文件不存在 {self.data_path}")
            self.df = pd.DataFrame()
    
    def query_market_salary(self, position, city=None, experience=None, industry=None) -> Dict:
        """
        查询市场薪资范围
        返回：薪资统计数据
        """
        if self.df.empty:
            return {"error": "暂无薪资数据"}
        
        filtered = self.df.copy()
        
        # 按岗位筛选（模糊匹配）
        if position:
            mask = filtered['招聘岗位'].str.contains(position, case=False, na=False)
            filtered = filtered[mask]
        
        # 按城市筛选
        if city:
            filtered = filtered[filtered['工作城市'] == city]
        
        # 按经验筛选
        if experience:
            filtered = filtered[filtered['要求经验'].str.contains(experience, na=False)]
        
        # 按行业筛选
        if industry:
            filtered = filtered[filtered['行业类型'].str.contains(industry, na=False)]
        
        if filtered.empty:
            return {"error": f"未找到匹配的岗位数据（岗位：{position}）"}
        
        # 计算统计数据
        min_salaries = filtered['最低月薪'].dropna()
        max_salaries = filtered['最高月薪'].dropna()
        avg_salaries = filtered['平均月薪'].dropna()
        
        result = {
            'position': position,
            'city': city or '全国',
            'experience': experience or '不限',
            'industry': industry or '不限',
            'sample_size': len(filtered),
            'min_salary': float(min_salaries.min()) if not min_salaries.empty else None,
            'max_salary': float(max_salaries.max()) if not max_salaries.empty else None,
            'avg_min_salary': float(min_salaries.mean()) if not min_salaries.empty else None,
            'avg_max_salary': float(max_salaries.mean()) if not max_salaries.empty else None,
            'median_salary': float(avg_salaries.median()) if not avg_salaries.empty else None,
            'avg_salary': float(avg_salaries.mean()) if not avg_salaries.empty else None,
            'percentile_25': float(avg_salaries.quantile(0.25)) if not avg_salaries.empty else None,
            'percentile_75': float(avg_salaries.quantile(0.75)) if not avg_salaries.empty else None,
        }
        
        # 按经验分组的薪资
        if not experience:
            exp_salary = filtered.groupby('要求经验')['平均月薪'].agg(['mean', 'count']).reset_index()
            exp_salary.columns = ['经验', '平均薪资', '样本数']
            result['by_experience'] = exp_salary.to_dict('records')
        
        # 按城市分组的薪资
        if not city:
            city_salary = filtered.groupby('工作城市')['平均月薪'].agg(['mean', 'count']).reset_index()
            city_salary.columns = ['城市', '平均薪资', '样本数']
            city_salary = city_salary.sort_values('平均薪资', ascending=False).head(10)
            result['by_city'] = city_salary.to_dict('records')
        
        return result
    
    def generate_negotiation_strategy(self, position, company_name, experience, offer_salary, target_salary, 
                                     market_min=None, market_max=None, company_size=None, industry=None) -> str:
        """
        生成薪资谈判策略
        """
        if not self.client:
            return "未配置 API Key，无法生成谈判策略"
        
        # 构建市场薪资描述
        market_desc = ""
        if market_min and market_max:
            market_desc = f"该岗位市场薪资范围为 {market_min:.0f}-{market_max:.0f} 元"
        elif market_min:
            market_desc = f"该岗位市场最低薪资为 {market_min:.0f} 元"
        
        prompt = f"""
你是一位专业的薪资谈判顾问。请根据以下信息，为用户生成详细的薪资谈判策略和话术。

## 背景信息
- 目标公司：{company_name}
- 目标岗位：{position}
- 用户工作经验：{experience}
- 公司规模：{company_size or '未知'}
- 所属行业：{industry or '未知'}

## 薪资情况
- 公司 Offer：{offer_salary} 元/月
- 用户期望薪资：{target_salary} 元/月
- {market_desc}

## 请提供以下内容

### 1. 谈判可行性分析
分析从 Offer 薪资谈到目标薪资的可行性，给出成功率评估。

### 2. 谈判策略
根据公司规模和行业特点，提供具体的谈判策略：
- 如果是大公司：策略建议
- 如果是中小公司：策略建议

### 3. 谈判话术模板
提供 3 个不同场景的话术：
- 场景 A：温和协商型（适合初次谈判）
- 场景 B：据理力争型（有竞争对手 Offer 时）
- 场景 C：妥协折中型（无法达到目标时的备选方案）

### 4. 可以争取的额外福利
除了基本工资，还可以争取哪些福利待遇（如年终奖、股票期权、培训机会等）。

### 5. 谈判注意事项
列出谈判前准备清单和谈判中的注意事项。

请用专业、实用的语气回答，内容要具体可操作。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的薪资谈判顾问，擅长帮助用户在薪资谈判中获得更好的待遇。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            safe_error = str(e).encode('utf-8', errors='replace').decode('utf-8')
            return f"生成谈判策略失败：{safe_error}"
    
    def analyze_benefits(self, offer_salary, position, industry=None) -> Dict:
        """
        分析福利待遇
        """
        if self.df.empty:
            return {"error": "暂无数据"}
        
        filtered = self.df.copy()
        if position:
            filtered = filtered[filtered['招聘岗位'].str.contains(position, case=False, na=False)]
        if industry:
            filtered = filtered[filtered['行业类型'].str.contains(industry, na=False)]
        
        # 年终奖分析
        bonus_data = filtered['年终奖估算'].dropna()
        
        # 薪资等级分布
        salary_level = filtered['薪资等级'].value_counts()
        
        result = {
            'sample_size': len(filtered),
            'avg_bonus': float(bonus_data.mean()) if not bonus_data.empty else None,
            'max_bonus': float(bonus_data.max()) if not bonus_data.empty else None,
            'salary_levels': salary_level.to_dict(),
            'common_benefits': [
                '五险一金',
                '带薪年假',
                '节日福利',
                '定期体检',
                '培训机会',
                '弹性工作',
                '年终奖',
                '股票期权',
                '餐补/交通补贴',
                '加班补贴',
            ]
        }
        
        return result
    
    def get_preparation_checklist(self) -> List[str]:
        """获取谈判前准备清单"""
        return [
            "调研目标公司的薪资水平和福利待遇",
            "了解行业同岗位的市场薪资范围",
            "明确自己的最低接受薪资和理想薪资",
            "准备 2-3 个具体的加薪理由（如技能、经验、业绩）",
            "了解公司的薪酬体系和晋升机制",
            "准备竞争对手的 Offer 作为谈判筹码（如有）",
            "练习谈判话术，保持自信但不傲慢",
            "了解目标公司的业务和发展前景",
            "准备反问环节的问题（关于团队、发展等）",
            "设定谈判底线，做好 Walk away 的准备",
        ]
    
    def full_analysis(self, position, company_name, experience, offer_salary, target_salary,
                     city=None, industry=None, company_size=None) -> Dict:
        """
        完整分析：市场查询 + 策略生成 + 福利分析
        """
        # 1. 市场薪资查询
        market_data = self.query_market_salary(position, city, experience, industry)
        
        # 2. 福利待遇分析
        benefits_data = self.analyze_benefits(offer_salary, position, industry)
        
        # 3. 谈判策略生成
        market_min = market_data.get('min_salary')
        market_max = market_data.get('max_salary')
        
        strategy = self.generate_negotiation_strategy(
            position=position,
            company_name=company_name,
            experience=experience,
            offer_salary=offer_salary,
            target_salary=target_salary,
            market_min=market_min,
            market_max=market_max,
            company_size=company_size,
            industry=industry,
        )
        
        # 4. 准备清单
        checklist = self.get_preparation_checklist()
        
        return {
            'market_data': market_data,
            'benefits_data': benefits_data,
            'negotiation_strategy': strategy,
            'preparation_checklist': checklist,
        }
