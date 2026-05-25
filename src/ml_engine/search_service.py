"""
智能岗位搜索与筛选服务
功能：
1. 自然语言查询解析
2. 多维度智能筛选
3. 基于余弦相似度的岗位匹配
4. 岗位收藏与对比
"""
import os
import re
import pickle
import numpy as np
import pandas as pd
from scipy.sparse import issparse
from sklearn.metrics.pairwise import cosine_similarity


class JobSearchService:
    def __init__(self, data_path, model_dir='models'):
        self.data_path = data_path
        self.model_dir = model_dir
        self.df = None
        self.tfidf_matrix = None
        self.vectorizer = None
        self.stopwords = set()
        self._load_models()
        self._load_data()
    
    def _load_models(self):
        tfidf_path = os.path.join(self.model_dir, 'tfidf_vectorizer.pkl')
        if os.path.exists(tfidf_path):
            with open(tfidf_path, 'rb') as f:
                data = pickle.load(f)
            self.vectorizer = data['vectorizer']
            self.stopwords = data.get('stopwords', set())
            print(f"[Search] 已加载 TF-IDF 模型: {tfidf_path}")
        else:
            print(f"[Search] 警告: TF-IDF 模型不存在: {tfidf_path}")
    
    def _load_data(self):
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path, encoding='utf-8')
            print(f"[Search] 已加载 {len(self.df)} 条岗位数据")
            self._build_tfidf_matrix()
        else:
            print(f"[Search] 警告: 数据文件不存在: {self.data_path}")
            self.df = pd.DataFrame()
    
    def _build_tfidf_matrix(self):
        if self.df.empty or self.vectorizer is None:
            return
        texts = (self.df['招聘岗位'].astype(str) + ' ' + self.df['职位描述'].astype(str)).tolist()
        self.tfidf_matrix = self.vectorizer.transform(texts)
        print(f"[Search] TF-IDF 矩阵构建完成: {self.tfidf_matrix.shape}")
    
    def parse_query(self, query_text):
        """
        解析自然语言查询，提取筛选条件
        返回: {
            'keywords': [关键词列表],
            'location': 城市或None,
            'min_salary': 最低薪资或None,
            'max_salary': 最高薪资或None,
            'experience': 经验要求或None,
            'education': 学历要求或None,
            'company_type': 公司类型或None,
        }
        """
        conditions = {
            'keywords': [],
            'location': None,
            'min_salary': None,
            'max_salary': None,
            'experience': None,
            'education': None,
            'company_type': None,
        }
        
        text = query_text.lower()
        
        # 城市字典（常见城市）
        cities = [
            '北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '重庆', '武汉', '西安',
            '天津', '苏州', '长沙', '青岛', '大连', '厦门', '福州', '济南', '郑州', '合肥',
            '南昌', '昆明', '贵阳', '南宁', '海口', '三亚', '拉萨', '西宁', '银川', '乌鲁木齐',
            '哈尔滨', '长春', '沈阳', '呼和浩特', '太原', '石家庄'
        ]
        
        # 提取城市
        for city in cities:
            if city in text:
                conditions['location'] = city
                break
        
        # 经验要求
        exp_patterns = [
            (r'(\d+)[年]+以上', 'experience', lambda m: f'{m.group(1)}年以上'),
            (r'(\d+)-(\d+)[年]+', 'experience', lambda m: f'{m.group(1)}-{m.group(2)}年'),
            (r'应届', 'experience', lambda m: '应届毕业生'),
            (r'不限经验', 'experience', lambda m: '不限'),
            (r'1年以内', 'experience', lambda m: '1年以内'),
        ]
        for pattern, key, func in exp_patterns:
            match = re.search(pattern, text)
            if match:
                conditions[key] = func(match)
                break
        
        # 学历要求
        edu_keywords = {
            '博士': '博士',
            '硕士': '硕士',
            '本科': '本科',
            '大专': '大专',
            '中专': '中专',
            '高中': '高中',
            '不限学历': '不限',
        }
        for keyword, value in edu_keywords.items():
            if keyword in text:
                conditions['education'] = value
                break
        
        # 薪资提取（如 "1万以上"、"15k-25k"、"月薪20k以上"）
        salary_patterns = [
            (r'(\d+)k?[-~至到](\d+)k?', lambda m: (int(m.group(1)), int(m.group(2)))),
            (r'(\d+)万?[-~至到](\d+)万?', lambda m: (int(m.group(1))*10, int(m.group(2))*10)),
            (r'(\d+)k?以上', lambda m: (int(m.group(1)), None)),
            (r'(\d+)万?以上', lambda m: (int(m.group(1))*10, None)),
            (r'(\d+)k?以下', lambda m: (None, int(m.group(1)))),
            (r'(\d+)万?以下', lambda m: (None, int(m.group(1))*10)),
        ]
        for pattern, func in salary_patterns:
            match = re.search(pattern, text)
            if match:
                min_sal, max_sal = func(match)
                conditions['min_salary'] = min_sal
                conditions['max_salary'] = max_sal
                break
        
        # 公司类型
        company_types = ['互联网', 'IT', '金融', '教育', '医疗', '制造', '电商', '游戏', '房地产', '咨询']
        for ctype in company_types:
            if ctype in text:
                conditions['company_type'] = ctype
                break
        
        # 提取关键词（去除条件后的文本）
        # 移除已识别的条件词汇
        keywords_text = text
        if conditions['location']:
            keywords_text = keywords_text.replace(conditions['location'], '')
        if conditions['experience']:
            keywords_text = keywords_text.replace(conditions['experience'], '')
        if conditions['education']:
            keywords_text = keywords_text.replace(conditions['education'], '')
        
        # 移除常见停用词和功能性词汇
        filter_words = ['我想找', '我要找', '想找', '寻找', '工作', '岗位', '职位', 
                       '月薪', '薪资', '工资', '不需要', '需要', '不加班', '加班', '最好']
        for word in filter_words:
            keywords_text = keywords_text.replace(word, '')
        
        # 分词（简单按标点和空格分割）
        keywords = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', keywords_text)
        keywords = [kw for kw in keywords if len(kw) > 1 and kw not in self.stopwords]
        conditions['keywords'] = keywords
        
        return conditions
    
    def search_by_query(self, query_text, top_n=50):
        """
        执行智能搜索：
        1. 解析查询条件
        2. 计算余弦相似度
        3. 应用筛选条件
        4. 返回排序后的结果
        """
        if self.df.empty or self.tfidf_matrix is None:
            return pd.DataFrame(), {}
        
        # 解析查询
        conditions = self.parse_query(query_text)
        
        # 计算查询文本与所有岗位的余弦相似度
        query_text_for_vector = ' '.join(conditions['keywords'] + ([query_text] if not conditions['keywords'] else []))
        query_vector = self.vectorizer.transform([query_text_for_vector])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # 创建带相似度的副本
        result_df = self.df.copy()
        result_df['similarity_score'] = similarities
        
        # 应用筛选条件
        filtered = result_df.copy()
        
        if conditions['location']:
            filtered = filtered[filtered['工作城市'] == conditions['location']]
        
        if conditions['min_salary'] is not None:
            filtered = filtered[filtered['最高月薪'] >= conditions['min_salary']]
        
        if conditions['max_salary'] is not None:
            filtered = filtered[filtered['最低月薪'] <= conditions['max_salary']]
        
        if conditions['experience']:
            filtered = filtered[filtered['要求经验'].str.contains(conditions['experience'], na=False)]
        
        if conditions['education']:
            filtered = filtered[filtered['学历要求'] == conditions['education']]
        
        if conditions['company_type']:
            filtered = filtered[filtered['行业类型'].str.contains(conditions['company_type'], na=False)]
        
        # 按相似度排序
        filtered = filtered.sort_values('similarity_score', ascending=False)
        
        # 返回前 top_n 条
        return filtered.head(top_n), conditions
    
    def search_by_keywords(self, keywords, filters=None):
        """
        传统关键词搜索 + 多条件筛选
        """
        if self.df.empty:
            return pd.DataFrame()
        
        result_df = self.df.copy()
        
        # 关键词搜索
        if keywords:
            mask = pd.Series([False] * len(result_df), index=result_df.index)
            for kw in keywords:
                mask |= result_df['招聘岗位'].str.contains(kw, case=False, na=False)
                mask |= result_df['企业名称'].str.contains(kw, case=False, na=False)
                mask |= result_df['职位描述'].str.contains(kw, case=False, na=False)
            result_df = result_df[mask]
        
        # 应用筛选条件
        if filters:
            if filters.get('location'):
                result_df = result_df[result_df['工作城市'] == filters['location']]
            if filters.get('min_salary') is not None:
                result_df = result_df[result_df['最高月薪'] >= filters['min_salary']]
            if filters.get('max_salary') is not None:
                result_df = result_df[result_df['最低月薪'] <= filters['max_salary']]
            if filters.get('experience'):
                result_df = result_df[result_df['要求经验'] == filters['experience']]
            if filters.get('education'):
                result_df = result_df[result_df['学历要求'] == filters['education']]
            if filters.get('company_type'):
                result_df = result_df[result_df['行业类型'].str.contains(filters['company_type'], na=False)]
            if filters.get('company_size'):
                result_df = result_df[result_df['企业规模'] == filters['company_size']]
        
        return result_df
    
    def get_similar_jobs(self, job_index, top_n=10):
        """
        基于内容相似度推荐与指定岗位相似的其他机会
        """
        if self.tfidf_matrix is None or job_index >= len(self.df):
            return pd.DataFrame()
        
        job_vector = self.tfidf_matrix[job_index]
        similarities = cosine_similarity(job_vector, self.tfidf_matrix).flatten()
        
        result_df = self.df.copy()
        result_df['similarity_score'] = similarities
        
        # 排除自身，按相似度排序
        result_df = result_df[result_df.index != job_index]
        result_df = result_df.sort_values('similarity_score', ascending=False)
        
        return result_df.head(top_n)
    
    def get_unique_values(self, column):
        """获取某列的唯一值列表"""
        if self.df.empty or column not in self.df.columns:
            return []
        return sorted(self.df[column].dropna().unique().tolist())
