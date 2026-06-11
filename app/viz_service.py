"""
后端可视化服务模块 - 按需生成图表
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import jieba
import re
import os
from wordcloud import WordCloud
from collections import Counter
import matplotlib
matplotlib.use('Agg')  # 非交互式后端

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 数据路径
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'cleaned_recruitment_data.csv')

def load_data():
    """加载清洗后的数据"""
    return pd.read_csv(DATA_PATH, encoding='utf-8-sig')


# ==================== 薪资分析图表 ====================

def generate_top15_salary_chart():
    """生成 Top 15 岗位平均月薪图"""
    df = load_data()
    top_15_jobs = df.groupby('招聘岗位')['平均月薪'].agg(['mean', 'count']).query('count >= 5')
    top_15_jobs = top_15_jobs.sort_values('mean', ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(top_15_jobs)))
    bars = ax.barh(range(len(top_15_jobs)), top_15_jobs['mean'], color=colors, height=0.7)
    ax.set_yticks(range(len(top_15_jobs)))
    ax.set_yticklabels(top_15_jobs.index, fontsize=9)
    ax.set_xlabel('平均月薪 (元)')
    ax.set_title('Top 15 岗位平均月薪', fontweight='bold', fontsize=14)
    ax.invert_yaxis()
    for i, (bar, val) in enumerate(zip(bars, top_15_jobs['mean'])):
        ax.text(val + 100, bar.get_y() + bar.get_height()/2, f'{val:.0f}', va='center', fontsize=8)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    return fig


def generate_salary_grade_chart():
    """生成薪资等级分布饼图"""
    df = load_data()
    salary_grade_counts = df['薪资等级'].value_counts()
    grade_order = ['5K以下', '5K-8K', '8K-12K', '12K-20K', '20K-30K', '30K以上']
    salary_grade_counts = salary_grade_counts.reindex(grade_order)
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(salary_grade_counts.values, labels=salary_grade_counts.index,
                                       autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 10})
    for text in autotexts:
        text.set_fontsize(10)
    ax.set_title('薪资等级分布', fontweight='bold', fontsize=14)
    plt.tight_layout()
    return fig


def generate_industry_salary_chart():
    """生成各行业平均薪资柱状图"""
    df = load_data()
    industry_salary = df.groupby('行业类型')['平均月薪'].mean().sort_values(ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(industry_salary)))
    bars = ax.bar(range(len(industry_salary)), industry_salary.values, color=colors)
    ax.set_xticks(range(len(industry_salary)))
    ax.set_xticklabels(industry_salary.index, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('平均月薪 (元)')
    ax.set_title('各行业平均薪资', fontweight='bold', fontsize=14)
    for bar, val in zip(bars, industry_salary.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, f'{val:.0f}', ha='center', fontsize=8)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return fig


def generate_salary_boxplot():
    """生成薪资等级箱线图"""
    df = load_data()
    grade_order = ['5K以下', '5K-8K', '8K-12K', '12K-20K', '20K-30K', '30K以上']
    salary_data = [df[df['薪资等级'] == g]['平均月薪'].dropna().values for g in grade_order]
    salary_data = [s for s in salary_data if len(s) > 0]
    valid_grades = [g for g, s in zip(grade_order, salary_data) if len(s) > 0]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(salary_data, tick_labels=valid_grades, patch_artist=True, notch=True)
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
    for patch, color in zip(bp['boxes'], colors[:len(salary_data)]):
        patch.set_facecolor(color)
    ax.set_ylabel('平均月薪 (元)')
    ax.set_title('薪资等级箱线图', fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return fig


def generate_bonus_chart():
    """生成年终奖 Top 10 行业图"""
    df = load_data()
    industry_bonus = df.groupby('行业类型')['年终奖估算'].mean().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.coolwarm(np.linspace(0.3, 0.9, len(industry_bonus)))
    bars = ax.barh(range(len(industry_bonus)), industry_bonus.values, color=colors, height=0.7)
    ax.set_yticks(range(len(industry_bonus)))
    ax.set_yticklabels(industry_bonus.index, fontsize=9)
    ax.set_xlabel('年终奖估算 (元)')
    ax.set_title('各行业年终奖估算 Top 10', fontweight='bold', fontsize=14)
    ax.invert_yaxis()
    for bar, val in zip(bars, industry_bonus.values):
        ax.text(val + 50, bar.get_y() + bar.get_height()/2, f'{val:.0f}', va='center', fontsize=8)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    return fig


def generate_salary_scatter():
    """生成月薪与年终奖关系散点图"""
    df = load_data()
    sample = df.sample(min(500, len(df)), random_state=42)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(sample['平均月薪'], sample['年终奖估算'], alpha=0.5, c=sample['平均月薪'], cmap='viridis', s=30)
    ax.set_xlabel('平均月薪 (元)')
    ax.set_ylabel('年终奖估算 (元)')
    ax.set_title('月薪与年终奖关系 (抽样500条)', fontweight='bold', fontsize=14)
    ax.grid(alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='平均月薪')
    plt.tight_layout()
    return fig


# ==================== 企业分析图表 ====================

def generate_city_chart():
    """生成工作城市分布图"""
    df = load_data()
    top_cities = df['工作城市'].value_counts().head(15)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(top_cities)))
    bars = ax.barh(range(len(top_cities)), top_cities.values, color=colors, height=0.7)
    ax.set_yticks(range(len(top_cities)))
    ax.set_yticklabels(top_cities.index, fontsize=9)
    ax.set_xlabel('岗位数量')
    ax.set_title('Top 15 工作城市岗位分布', fontweight='bold', fontsize=14)
    ax.invert_yaxis()
    for bar, val in zip(bars, top_cities.values):
        ax.text(val + 20, bar.get_y() + bar.get_height()/2, str(val), va='center', fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    return fig


def generate_industry_chart():
    """生成行业类型分布饼图"""
    df = load_data()
    industry_counts = df['行业类型'].value_counts()
    small_mask = industry_counts / len(df) < 0.02
    if small_mask.any():
        other_count = industry_counts[small_mask].sum()
        industry_counts = industry_counts[~small_mask]
        industry_counts['其他'] = other_count
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set3(np.linspace(0, 0.9, len(industry_counts)))
    wedges, texts, autotexts = ax.pie(industry_counts.values, labels=industry_counts.index,
                                       autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 9})
    for text in autotexts:
        text.set_fontsize(8)
    ax.set_title('行业类型分布', fontweight='bold', fontsize=14)
    plt.tight_layout()
    return fig


def generate_company_size_chart():
    """生成企业规模分布饼图"""
    df = load_data()
    size_counts = df['企业规模'].value_counts()
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(size_counts.values, labels=size_counts.index,
                                       autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 10})
    for text in autotexts:
        text.set_fontsize(10)
    ax.set_title('企业规模分布', fontweight='bold', fontsize=14)
    plt.tight_layout()
    return fig


def generate_city_industry_heatmap():
    """生成城市 × 行业热力图"""
    import seaborn as sns
    df = load_data()
    top_10_cities = df['工作城市'].value_counts().head(10).index
    top_5_industries = df['行业类型'].value_counts().head(5).index
    pivot_data = df[df['工作城市'].isin(top_10_cities) & df['行业类型'].isin(top_5_industries)]
    pivot_table = pivot_data.groupby(['工作城市', '行业类型']).size().unstack(fill_value=0)
    pivot_table = pivot_table.reindex(top_10_cities)[top_5_industries]
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlOrRd', ax=ax, linewidths=0.5, cbar_kws={'label': '岗位数量'})
    ax.set_title('城市 × 行业 岗位数量热力图', fontweight='bold', fontsize=14)
    ax.tick_params(axis='x', rotation=45)
    ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout()
    return fig


# ==================== 学历经验图表 ====================

def generate_education_chart():
    """生成学历要求分布饼图"""
    df = load_data()
    edu_counts = df['学历要求'].value_counts()
    edu_order = ['初中及以下', '高中', '中专', '中技', '大专', '本科', '硕士', '博士', '学历不限']
    edu_counts = edu_counts.reindex(edu_order).fillna(0)
    edu_counts = edu_counts[edu_counts > 0]
    colors = ['#ff6b6b', '#ffa06b', '#ffd56b', '#fff36b', '#6bffb3', '#6bdeff', '#9b6bff', '#ff6bde', '#c0c0c0']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(edu_counts.values, labels=edu_counts.index,
                                       autopct='%1.1f%%', colors=colors[:len(edu_counts)], startangle=90, textprops={'fontsize': 10})
    for text in autotexts:
        text.set_fontsize(10)
    ax.set_title('学历要求分布', fontweight='bold', fontsize=14)
    plt.tight_layout()
    return fig


def generate_experience_chart():
    """生成经验要求分布饼图"""
    df = load_data()
    exp_counts = df['要求经验'].value_counts()
    exp_order = ['1年以下', '1-3年', '3-5年', '5-10年', '10年以上', '经验不限']
    exp_counts = exp_counts.reindex(exp_order).fillna(0)
    exp_counts = exp_counts[exp_counts > 0]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(exp_counts.values, labels=exp_counts.index,
                                       autopct='%1.1f%%', colors=colors[:len(exp_counts)], startangle=90, textprops={'fontsize': 10})
    for text in autotexts:
        text.set_fontsize(10)
    ax.set_title('经验要求分布', fontweight='bold', fontsize=14)
    plt.tight_layout()
    return fig


def generate_edu_salary_boxplot():
    """生成学历 vs 薪资箱线图"""
    df = load_data()
    edu_salary_data = []
    edu_labels = []
    for edu in ['大专', '本科', '硕士', '博士']:
        subset = df[df['学历要求'] == edu]['平均月薪']
        if len(subset) > 0:
            edu_salary_data.append(subset.values)
            edu_labels.append(edu)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(edu_salary_data, tick_labels=edu_labels, patch_artist=True, notch=True)
    colors = ['#6bffb3', '#6bdeff', '#9b6bff', '#ff6bde']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    ax.set_ylabel('平均月薪 (元)')
    ax.set_title('学历 vs 薪资分布', fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return fig


def generate_exp_salary_boxplot():
    """生成经验 vs 薪资箱线图"""
    df = load_data()
    exp_salary_data = []
    exp_labels = []
    for exp in ['1年以下', '1-3年', '3-5年', '5-10年', '10年以上']:
        subset = df[df['要求经验'] == exp]['平均月薪']
        if len(subset) > 0:
            exp_salary_data.append(subset.values)
            exp_labels.append(exp)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(exp_salary_data, tick_labels=exp_labels, patch_artist=True, notch=True)
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    ax.set_ylabel('平均月薪 (元)')
    ax.set_title('经验 vs 薪资分布', fontweight='bold', fontsize=14)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return fig


# ==================== 岗位技能词云 ====================

def generate_skill_wordcloud():
    """生成岗位技能需求词云（仅IT相关行业）"""
    df = load_data()
    # 过滤IT相关行业
    it_industries = ['IT互联网', '电子硬件', '云计算/大数据', '人工智能', '物联网', '通信/网络设备']
    df_it = df[df['行业类型'].isin(it_industries)]
    
    text = ' '.join(df_it['职位描述'].dropna().tolist())
    words = jieba.lcut(text)
    
    stop_words = {
        '能力', '要求', '工作', '职位', '职位', '专业', '根据', '制定', '协助', '配合', '参与',
        '负责', '熟悉', '掌握', '了解', '具备', '具有', '相关', '经验', '以上', '以下',
        '良好', '优秀', '团队', '沟通', '协调', '合作', '精神', '责任心', '意识',
        '独立', '完成', '执行', '实施', '进行', '开展', '推动', '促进', '提升', '优化',
        '编写', '编写', '编写', '测试', '维护', '支持', '协助', '配合',
        '项目', '产品', '系统', '软件', '硬件', '数据', '技术', '业务',
        '分析', '设计', '开发', '管理', '运营', '服务', '客户', '用户',
        '来源', '通过', 'cn', 'CN', '30', '10', '00', '马克', '定义', '按时',
        '不断', '清晰', '承受', '页面', '出现', '落地', '现有', '公众', '各项',
        '应急', '其它', '详细', '针对', '每年', '具体', '强烈', 'www',
        '熟练掌握', '国家', '整体', '其他', '至少', '按照',
    }
    
    general_words = {'软件', '工程', '问题', '需求', '数据', '信息', '平台', '工具', '方法', '原理',
                     '知识', '过程', '情况', '环境', '文件', '内容', '方向', '领域', '范围', '方面',
                     '部分', '因素', '条件', '基础', '框架', '结构', '体系', '模块', '接口', '版本',
                     '模式', '协议', '网络', '通信', '电子', '电路', '硬件', '设备', '仪器', '材料',
                     '工艺', '生产', '制造', '加工', '供应', '采购', '库存', '研发', '编程', '代码',
                     '产品经理', '项目管理', '本科', '大专', '硕士', '自动化', '前端', '软件开发',
                     '五险', '一金'}
    stop_words.update(general_words)
    
    filtered_words = [w for w in words if len(w) >= 2 and w not in stop_words]
    word_freq = Counter(filtered_words)
    top_words = dict(word_freq.most_common(150))
    
    # 合并五险一金
    if '五险' in top_words and '一金' in top_words:
        combined = top_words.get('五险', 0) + top_words.get('一金', 0)
        top_words['五险一金'] = combined
        top_words.pop('五险', None)
        top_words.pop('一金', None)
    
    fig, ax = plt.subplots(figsize=(12, 9))
    wc = WordCloud(font_path='C:/Windows/Fonts/simhei.ttf', background_color='white',
                   max_words=150, max_font_size=100, min_font_size=14, width=800, height=600, random_state=42)
    wc.generate_from_frequencies(top_words)
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('岗位技能需求词云', fontsize=18, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig


def generate_benefit_wordcloud():
    """生成福利待遇词云（仅IT相关行业）"""
    df = load_data()
    # 过滤IT相关行业
    it_industries = ['IT互联网', '电子硬件', '云计算/大数据', '人工智能', '物联网', '通信/网络设备']
    df_it = df[df['行业类型'].isin(it_industries)]
    
    benefit_keywords = [
        '五险一金', '年终奖', '带薪年假', '绩效奖金', '全勤奖', '交通补助', '餐补', '房补',
        '通讯补贴', '加班补助', '高温补贴', '节日福利', '生日福利', '定期体检', '员工旅游',
        '免费班车', '免费食宿', '包吃住', '包住', '包吃', '双休', '周末双休', '单休',
        '弹性工作', '不加班', '加班费', '股票期权', '股权', '分红', '提成', '培训', '晋升',
        '发展空间', '职业规划', '导师', '下午茶', '零食', '健身房', '团建', '旅游',
        '补充医疗保险', '补充公积金', '企业年金', '产假', '陪产假', '育儿假', '婚假', '丧假',
        '六险二金', '补充商业保险', '早九晚六', '朝九晚五', '不打卡', '扁平管理', '氛围好',
        '团队', '技术氛围', '餐补', '车补', '话补', '住房补贴', '13薪', '14薪', '15薪',
        '16薪', '年终奖', '项目奖金', '季度奖金', '半年奖', '年度奖金', '免费体检', '年度体检',
        '带薪休假', '年假', '调休', '弹性工作制', '远程办公', '居家办公',
    ]
    
    all_descriptions = ' '.join(df_it['职位描述'].dropna().tolist())
    benefit_freq = {}
    for kw in benefit_keywords:
        count = all_descriptions.count(kw)
        if count > 0:
            benefit_freq[kw] = count
    
    fig, ax = plt.subplots(figsize=(12, 9))
    wc = WordCloud(font_path='C:/Windows/Fonts/simhei.ttf', background_color='white',
                   max_words=200, max_font_size=120, min_font_size=12, width=800, height=600,
                   random_state=42, prefer_horizontal=0.6, scale=4, relative_scaling=0.3, collocations=True)
    wc.generate_from_frequencies(benefit_freq)
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('福利待遇关键词词云', fontsize=18, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig


# ==================== 行业技术图表 ====================

def generate_tech_trend():
    """生成技术方向月度趋势图"""
    df = load_data()
    tech_trend_keywords = ['Java', 'Python', 'C++', 'JavaScript', 'Go', '前端', '后端', '嵌入式', '算法', '测试']
    
    df['招聘发布日期'] = pd.to_datetime(df['招聘发布日期'], errors='coerce')
    df['招聘年月'] = df['招聘发布日期'].dt.to_period('M')
    month_counts = df['招聘年月'].value_counts()
    valid_months = month_counts[month_counts >= 10].index.tolist()
    valid_months = sorted(valid_months)
    
    if valid_months:
        months = valid_months
        df_valid = df[df['招聘年月'].isin(months)]
        all_descriptions_trend = df_valid.groupby('招聘年月')['职位描述'].apply(lambda x: ' '.join(x.dropna().tolist()))
        
        trend_data = {}
        for tech in tech_trend_keywords:
            tech_counts = []
            for month in months:
                if month in all_descriptions_trend.index:
                    text = str(all_descriptions_trend[month])
                    count = text.count(tech)
                    tech_counts.append(count)
                else:
                    tech_counts.append(0)
            trend_data[tech] = tech_counts
        
        month_labels = [str(m) for m in months]
        x_pos = range(len(months))
        
        fig, ax = plt.subplots(figsize=(14, 7))
        colors = plt.cm.tab10(np.linspace(0, 1, len(tech_trend_keywords)))
        for i, (tech, counts) in enumerate(trend_data.items()):
            ax.plot(x_pos, counts, marker='o', linewidth=2, label=tech, color=colors[i], markersize=6)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(month_labels, rotation=45, ha='right', fontsize=9)
        ax.set_xlabel('月份')
        ax.set_ylabel('出现频次')
        ax.set_title('各技术方向招聘市场月度趋势', fontweight='bold', fontsize=14)
        ax.legend(fontsize=10, ncol=2)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        df.drop(columns=['招聘年月'], inplace=True, errors='ignore')
        return fig
    return None


# ==================== 聚类分析图表 ====================

def generate_cluster_chart():
    """生成岗位描述聚类降维图"""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    import warnings
    warnings.filterwarnings('ignore')
    
    df = load_data()
    sample_size = min(1000, len(df))
    sample_df = df.sample(sample_size, random_state=42).copy()
    sample_df = sample_df.dropna(subset=['职位描述'])
    descriptions = sample_df['职位描述'].tolist()
    
    if len(descriptions) > 0:
        tfidf = TfidfVectorizer(max_features=500, stop_words=['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
        X_tfidf = tfidf.fit_transform(descriptions)
        
        n_clusters = 5
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_tfidf)
        
        pca = PCA(n_components=2, random_state=42)
        X_2d = pca.fit_transform(X_tfidf.toarray())
        
        fig, ax = plt.subplots(figsize=(12, 9))
        colors = ['#ff6b6b', '#6bdeff', '#99ff99', '#ffd56b', '#9b6bff']
        
        for i in range(n_clusters):
            mask = cluster_labels == i
            ax.scatter(X_2d[mask, 0], X_2d[mask, 1],
                      label=f'聚类 {i+1} (n={mask.sum()})', alpha=0.7, s=30, color=colors[i], edgecolors='none')
        
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
        ax.set_title('岗位描述 KMeans 聚类 (PCA 降维)', fontweight='bold', fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        return fig
    return None


# ==================== 热力图 ====================

def generate_job_skill_heatmap():
    """生成岗位-技能热力图"""
    import seaborn as sns
    df = load_data()
    top_positions = df['招聘岗位'].value_counts().head(15).index.tolist()
    heatmap_skills = ['Java', 'Python', 'C++', 'JavaScript', 'Go', 'Spring', 'MySQL',
                      'Redis', 'Linux', 'Docker', 'Vue', 'React', '算法', '测试',
                      '嵌入式', '硬件', 'PCB', 'FPGA', '前端', '后端']
    
    pos_skill_matrix = pd.DataFrame(0, index=top_positions, columns=heatmap_skills)
    for idx, row in df.iterrows():
        pos = row['招聘岗位']
        if pos in top_positions:
            desc = str(row['职位描述'])
            for skill in heatmap_skills:
                if skill in desc:
                    pos_skill_matrix.loc[pos, skill] += 1
    
    pos_skill_norm = pos_skill_matrix.div(pos_skill_matrix.sum(axis=1), axis=0) * 100
    
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(pos_skill_norm, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax,
                linewidths=0.5, cbar_kws={'label': '技能提及占比 (%)'}, annot_kws={'fontsize': 7})
    ax.set_title('岗位-技能出现频率热力图', fontweight='bold', fontsize=14)
    ax.tick_params(axis='x', rotation=45, labelsize=9)
    ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout()
    return fig


# ==================== 招聘类别 ====================

def generate_recruitment_category_chart():
    """生成招聘类别分布饼图"""
    df = load_data()
    cat_counts = df['招聘类别'].value_counts()
    colors = ['#66b3ff', '#99ff99', '#ffcc99', '#ffb3e6']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(cat_counts.values, labels=cat_counts.index,
                                       autopct='%1.1f%%', colors=colors, startangle=90, textprops={'fontsize': 10})
    for text in autotexts:
        text.set_fontsize(10)
    ax.set_title('招聘类别分布', fontweight='bold', fontsize=14)
    plt.tight_layout()
    return fig


# 导出所有图表生成函数
CHART_FUNCTIONS = {
    # 薪资分析
    'top15_salary': generate_top15_salary_chart,
    'salary_grade': generate_salary_grade_chart,
    'industry_salary': generate_industry_salary_chart,
    'salary_boxplot': generate_salary_boxplot,
    'bonus': generate_bonus_chart,
    'salary_scatter': generate_salary_scatter,
    # 企业分析
    'city': generate_city_chart,
    'industry': generate_industry_chart,
    'company_size': generate_company_size_chart,
    'city_industry_heatmap': generate_city_industry_heatmap,
    # 学历经验
    'education': generate_education_chart,
    'experience': generate_experience_chart,
    'edu_salary': generate_edu_salary_boxplot,
    'exp_salary': generate_exp_salary_boxplot,
    # 岗位技能
    'skill_wordcloud': generate_skill_wordcloud,
    'benefit_wordcloud': generate_benefit_wordcloud,
    # 行业技术
    'tech_trend': generate_tech_trend,
    # 聚类分析
    'cluster': generate_cluster_chart,
    # 技能分析
    'job_skill_heatmap': generate_job_skill_heatmap,
    # 招聘类别
    'recruitment_category': generate_recruitment_category_chart,
}
