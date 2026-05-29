"""
薪资谈判助手服务
功能：
1. 市场薪资查询
2. 谈判策略生成
3. 福利待遇分析
4. 谈判准备清单
"""
import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class SalaryNegotiator:
    """薪资谈判助手"""
    
    def __init__(self, api_key=None, model="qwen3.6-plus", base_url=None):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("LLM_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.client = None
        self.df = self._load_data()
        
        if self.api_key and self.api_key != "your_api_key_here":
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
    
    def _load_data(self):
        """加载招聘数据"""
        try:
            data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   'data', 'cleaned_recruitment_data.csv')
            df = pd.read_csv(data_path)
            return df
        except Exception:
            # 返回空DataFrame作为备用
            return pd.DataFrame()
    
    def query_market_salary(self, position, city=None, experience=None, industry=None):
        """查询市场薪资"""
        result = {
            'sample_size': 0,
            'min_salary': None,
            'max_salary': None,
            'avg_salary': None,
            'median_salary': None,
            'percentile_25': None,
            'percentile_75': None,
            'by_experience': [],
            'by_city': []
        }
        
        if self.df.empty:
            return result
        
        # 筛选数据
        filtered = self.df[self.df['招聘岗位'].str.contains(position, case=False, na=False)]
        
        if city:
            filtered = filtered[filtered['工作城市'] == city]
        
        if experience:
            filtered = filtered[filtered['要求经验'].str.contains(experience, case=False, na=False)]
        
        if industry:
            filtered = filtered[filtered['行业类型'] == industry]
        
        if filtered.empty:
            return result
        
        result['sample_size'] = len(filtered)
        
        # 提取薪资信息
        salary_cols = ['最低月薪', '最高月薪', '平均月薪']
        for col in salary_cols:
            if col in filtered.columns:
                filtered[col] = pd.to_numeric(filtered[col], errors='coerce')
        
        if '平均月薪' in filtered.columns:
            salaries = filtered['平均月薪'].dropna()
            if not salaries.empty:
                result['min_salary'] = salaries.min()
                result['max_salary'] = salaries.max()
                result['avg_salary'] = salaries.mean()
                result['median_salary'] = salaries.median()
                result['percentile_25'] = salaries.quantile(0.25)
                result['percentile_75'] = salaries.quantile(0.75)
        
        # 按经验分组
        if '要求经验' in filtered.columns and '平均月薪' in filtered.columns:
            exp_groups = filtered.groupby('要求经验')['平均月薪'].agg(['mean', 'count']).reset_index()
            exp_groups.columns = ['experience', 'avg_salary', 'count']
            result['by_experience'] = exp_groups.to_dict('records')
        
        # 按城市分组
        if '工作城市' in filtered.columns and '平均月薪' in filtered.columns:
            city_groups = filtered.groupby('工作城市')['平均月薪'].agg(['mean', 'count']).reset_index()
            city_groups.columns = ['city', 'avg_salary', 'count']
            city_groups = city_groups.sort_values('count', ascending=False).head(10)
            result['by_city'] = city_groups.to_dict('records')
        
        return result
    
    def generate_negotiation_strategy(self, position, company_name, experience, 
                                      offer_salary, target_salary, market_min=None, 
                                      market_max=None, company_size=None, industry=None):
        """生成谈判策略"""
        if not self.client:
            return "⚠️ 未配置 API Key，无法生成智能谈判策略。\n\n建议：\n1. 了解市场薪资范围\n2. 准备好你的价值证明\n3. 保持专业态度进行谈判"
        
        prompt = f"""
作为一名资深的薪资谈判顾问，请为以下情况生成详细的谈判策略：

基本信息：
- 目标岗位：{position}
- 目标公司：{company_name}
- 工作经验：{experience}
- 当前Offer：{offer_salary} 元/月
- 期望薪资：{target_salary} 元/月

市场数据：
- 市场最低薪资：{market_min or '未知'} 元/月
- 市场最高薪资：{market_max or '未知'} 元/月

公司信息：
- 公司规模：{company_size or '未知'}
- 行业类型：{industry or '未知'}

请提供：
1. 市场定位分析
2. 谈判目标设定
3. 具体谈判话术
4. 应对各种情况的策略
5. 注意事项

输出格式清晰，使用中文，语言专业但易于理解。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的薪资谈判顾问，帮助求职者获得更好的薪资待遇。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"生成策略时出错：{str(e)}"
    
    def analyze_benefits(self, offer_salary, position, industry=None):
        """分析福利待遇"""
        result = {
            'sample_size': 0,
            'avg_bonus': None,
            'max_bonus': None,
            'common_benefits': []
        }
        
        if self.df.empty:
            result['common_benefits'] = [
                '五险一金', '年终奖', '带薪年假', '餐补', '交通补贴',
                '节日福利', '健康体检', '培训机会', '弹性工作', '团建活动'
            ]
            return result
        
        filtered = self.df[self.df['招聘岗位'].str.contains(position, case=False, na=False)]
        
        if industry:
            filtered = filtered[filtered['行业类型'] == industry]
        
        result['sample_size'] = len(filtered)
        
        # 常见福利列表
        result['common_benefits'] = [
            '五险一金', '年终奖', '带薪年假', '餐补', '交通补贴',
            '节日福利', '健康体检', '培训机会', '弹性工作', '团建活动'
        ]
        
        # 如果有年终奖数据
        if '年终奖估算' in filtered.columns:
            bonuses = filtered['年终奖估算'].dropna()
            if not bonuses.empty:
                try:
                    numeric_bonuses = pd.to_numeric(bonuses, errors='coerce').dropna()
                    if not numeric_bonuses.empty:
                        result['avg_bonus'] = numeric_bonuses.mean() * 1000
                        result['max_bonus'] = numeric_bonuses.max() * 1000
                except:
                    pass
        
        return result
    
    def get_preparation_checklist(self):
        """获取谈判前准备清单"""
        return [
            "✅ 了解目标岗位的市场薪资范围",
            "✅ 收集同行业同岗位薪资数据",
            "✅ 准备好自己的业绩证明和价值亮点",
            "✅ 明确自己的最低接受薪资",
            "✅ 设定理想薪资目标",
            "✅ 准备好谈判话术和开场白",
            "✅ 研究目标公司的薪资结构和福利",
            "✅ 想好备选方案和谈判底线",
            "✅ 练习谈判技巧和应对策略",
            "✅ 准备好提问清单"
        ]
