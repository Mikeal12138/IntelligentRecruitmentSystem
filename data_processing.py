import pandas as pd
import numpy as np
import re
import os

RAW_DATA_PATH = r'c:\Users\13309\Desktop\大实验\test1.csv'
PROCESSED_DIR = r'c:\Users\13309\Desktop\大实验\IntelligentRecruitmentSystem\data'
os.makedirs(PROCESSED_DIR, exist_ok=True)

CLEANED_DATA_PATH = os.path.join(PROCESSED_DIR, 'cleaned_recruitment_data.csv')
ANALYSIS_REPORT_PATH = os.path.join(PROCESSED_DIR, 'analysis_report.txt')

# ============================================================
# 1. 数据读取
# ============================================================
print("=" * 60)
print("1. 数据读取")
print("=" * 60)

df = pd.read_csv(RAW_DATA_PATH, encoding='utf-8')
print(f"原始数据集形状: {df.shape}")
print(f"列数: {len(df.columns)}")

# ============================================================
# 2. 数据清洗
# ============================================================
print("\n" + "=" * 60)
print("2. 数据清洗")
print("=" * 60)

# --- 2.1 删除完全空值的列 ---
cols_to_drop = []
for col in df.columns:
    if df[col].isna().all():
        cols_to_drop.append(col)
df_clean = df.drop(columns=cols_to_drop)
print(f"\n[2.1] 删除完全空值的列: {cols_to_drop}")
print(f"删除后形状: {df_clean.shape}")

# --- 2.2 删除全空的行 ---
before_drop_all_na = len(df_clean)
df_clean = df_clean.dropna(how='all')
print(f"\n[2.2] 删除全部为空的行: {before_drop_all_na - len(df_clean)} 行")

# --- 2.3 删除重复行 ---
before_drop_dup = len(df_clean)
df_clean = df_clean.drop_duplicates()
print(f"\n[2.3] 删除重复行: {before_drop_dup - len(df_clean)} 行")
print(f"去重后形状: {df_clean.shape}")

# --- 2.4 清洗列名 ---
df_clean.columns = [col.strip() for col in df_clean.columns]

# --- 2.5 清洗职位描述 - 去除HTML标签 ---
def clean_html(text):
    if pd.isna(text) or not isinstance(text, str):
        return text
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

df_clean['职位描述'] = df_clean['职位描述'].apply(clean_html)
print(f"\n[2.5] 职位描述HTML标签清洗完成")

# --- 2.6 清洗来源列 - 去除广告水印 ---
def clean_source(text):
    if pd.isna(text) or not isinstance(text, str):
        return text
    text = re.sub(r'[（(]?来源[：:].*|.*马克数据网.*|.*macrodatas\.cn.*|.*微信公众号.*|.*搜索.*数据.*', '', text)
    text = re.sub(r'[（(]?更多数据[，,].*', '', text)
    text = text.strip()
    return text

df_clean['来源'] = df_clean['来源'].apply(clean_source)
ad_keywords = ['马克数据网', 'macrodatas', '搜索马', '微信公众号']
df_clean.loc[df_clean['来源'].isin(ad_keywords), '来源'] = '智联招聘'
print(f"[2.6] 来源列清洗完成")

# --- 2.7 清洗企业名称 - 去除尾部广告标记 ---
def clean_company_name(text):
    if pd.isna(text) or not isinstance(text, str):
        return text
    text = re.sub(r'[（(]微信.*', '', text)
    text = re.sub(r'[（(]更多.*', '', text)
    text = re.sub(r'\s*（来自.*', '', text)
    text = text.strip()
    return text

df_clean['企业名称'] = df_clean['企业名称'].apply(clean_company_name)

# --- 2.8 标准化学历要求 ---
edu_mapping = {
    '本科': '本科',
    '硕士': '硕士',
    '大专': '大专',
    '博士': '博士',
    '不限': '学历不限',
    '学历不限': '学历不限',
    '中专': '中专',
    '中技': '中技',
    '高中': '高中',
    '初中及以下': '初中及以下',
}
def standardize_education(text):
    if pd.isna(text) or not isinstance(text, str):
        return '学历不限'
    text = text.strip()
    if text in edu_mapping:
        return edu_mapping[text]
    if '及以上' in text or '以上' in text:
        for key in ['博士', '硕士', '本科', '大专']:
            if key in text:
                return key
    if '不限' in text:
        return '学历不限'
    return text

df_clean['学历要求'] = df_clean['学历要求'].apply(standardize_education)

edu_order = ['初中及以下', '高中', '中专', '中技', '大专', '本科', '硕士', '博士', '学历不限']
df_clean['学历要求_排序'] = df_clean['学历要求'].apply(
    lambda x: edu_order.index(x) if x in edu_order else 99
)
print(f"\n[2.8] 学历要求标准化完成")
print(f"学历分布:\n{df_clean['学历要求'].value_counts()}")

# --- 2.9 标准化经验要求 ---
exp_mapping = {
    '经验不限': '经验不限',
    '不限': '经验不限',
    '1年以下': '1年以下',
    '1年以下经验': '1年以下',
    '应届毕业生': '1年以下',
    '1年以上经验': '1-3年',
}
def standardize_experience(text):
    if pd.isna(text) or not isinstance(text, str):
        return '经验不限'
    text = text.strip()
    if text in exp_mapping:
        return exp_mapping[text]
    year_patterns = [
        ('10年以上', r'10年以上'),
        ('5-10年', r'5[-~]10年|5年以上'),
        ('3-5年', r'3[-~]5年'),
        ('1-3年', r'1[-~]3年|1年以上|2年以上'),
        ('1年以下', r'1年以下'),
    ]
    for label, pattern in year_patterns:
        if re.search(pattern, text):
            return label
    if re.search(r'\d+', text):
        nums = list(map(int, re.findall(r'\d+', text)))
        max_year = max(nums)
        if max_year >= 10:
            return '5-10年'
        elif max_year >= 5:
            return '5-10年'
        elif max_year >= 3:
            return '3-5年'
        elif max_year >= 1:
            return '1-3年'
        else:
            return '1年以下'
    return '经验不限'

df_clean['要求经验'] = df_clean['要求经验'].apply(standardize_experience)

exp_order = ['1年以下', '1-3年', '3-5年', '5-10年', '10年以上', '经验不限']
df_clean['要求经验_排序'] = df_clean['要求经验'].apply(
    lambda x: exp_order.index(x) if x in exp_order else 99
)
print(f"\n[2.9] 经验要求标准化完成")
print(f"经验分布:\n{df_clean['要求经验'].value_counts()}")

# --- 2.10 处理薪资 - 填充缺失值 & 计算平均薪资 ---
salary_cols = ['最低月薪', '最高月薪']
for col in salary_cols:
    median_val = df_clean[col].median()
    df_clean[col] = df_clean[col].fillna(median_val)

df_clean['平均月薪'] = (df_clean['最低月薪'] + df_clean['最高月薪']) / 2
df_clean['薪资浮动'] = (df_clean['最高月薪'] - df_clean['最低月薪'])
print(f"\n[2.10] 薪资缺失值填充完成")
print(f"薪资浮动均值: {df_clean['薪资浮动'].mean():.0f}")
print(f"平均月薪均值: {df_clean['平均月薪'].mean():.0f}")

# --- 2.11 工作城市清洗（修复截断问题）---
def clean_city(text):
    """
    清洗城市名称，保留完整城市名
    - 仅去除末尾的'市'后缀（如'北京市'→'北京'）
    - 保留'城'、'县'等在中间的城市名（如'盐城'、'防城港'不变）
    - 处理省级后缀如'省'、'自治区'等
    """
    if pd.isna(text) or not isinstance(text, str):
        return '其他'
    text = text.strip()
    # 只去除末尾的'市'，不去除中间的'市'或'城'
    if text.endswith('市') and len(text) > 1:
        text = text[:-1]
    # 去除'省'、'自治区'等后缀（仅当在末尾时）
    text = re.sub(r'(省|自治区|特别行政区)$', '', text)
    return text

df_clean['工作城市'] = df_clean['工作城市'].apply(clean_city)
print(f"\n[2.11] 工作城市清洗完成")

# --- 2.12 处理日期列 ---
df_clean['招聘发布日期'] = pd.to_datetime(df_clean['招聘发布日期'], errors='coerce')
df_clean['招聘发布年份'] = df_clean['招聘发布年份'].fillna(2024).astype(int)

# --- 2.13 处理招聘类别 ---
df_clean['招聘类别'] = df_clean['招聘类别'].fillna('全职')

# --- 2.14 初级分类缺失值填充 ---
missing_cat_count = df_clean['初级分类'].isna().sum()
if missing_cat_count > 0:
    df_clean['初级分类'] = df_clean['初级分类'].fillna('其他')
    print(f"\n[2.14] 初级分类缺失值填充: {missing_cat_count} 条 → '其他'")

# --- 2.15 岗位名称统一标准化 ---
def normalize_job_title(text):
    """统一岗位名称大小写和格式"""
    if pd.isna(text) or not isinstance(text, str):
        return text
    text = text.strip()
    # Java 统一大写（不使用\b，因为中文字符间无单词边界）
    text = re.sub(r'java', 'Java', text, flags=re.IGNORECASE)
    # C++ 统一格式
    text = re.sub(r'c\+\+', 'C++', text, flags=re.IGNORECASE)
    # C# 统一格式
    text = re.sub(r'c#', 'C#', text, flags=re.IGNORECASE)
    # AI/Ai 统一大写
    text = re.sub(r'(?<![a-zA-Z])ai(?![a-zA-Z])', 'AI', text, flags=re.IGNORECASE)
    # IoT 统一大写
    text = re.sub(r'iot', 'IoT', text, flags=re.IGNORECASE)
    # Web 统一首字母大写
    text = re.sub(r'web', 'Web', text, flags=re.IGNORECASE)
    # HTML 统一大写
    text = re.sub(r'html', 'HTML', text, flags=re.IGNORECASE)
    # SQL 统一大写
    text = re.sub(r'sql', 'SQL', text, flags=re.IGNORECASE)
    # 去除多余空格和特殊字符
    text = re.sub(r'\s+', '', text)
    # 去除职位编号等后缀
    text = re.sub(r'[（(]职位编号[^）)]*[）)]', '', text)
    text = text.strip()
    return text

df_clean['招聘岗位'] = df_clean['招聘岗位'].apply(normalize_job_title)
print(f"\n[2.15] 岗位名称标准化完成")

# --- 2.16 薪资异常值处理 ---
# 最高月薪 > 100000 的视为异常，用中位数替换
high_salary_mask = df_clean['最高月薪'] > 100000
high_salary_count = high_salary_mask.sum()
if high_salary_count > 0:
    median_salary = df_clean.loc[~high_salary_mask, '最高月薪'].median()
    df_clean.loc[high_salary_mask, '最高月薪'] = median_salary
    # 重新计算平均月薪和薪资浮动
    df_clean.loc[high_salary_mask, '平均月薪'] = (
        df_clean.loc[high_salary_mask, '最低月薪'] + median_salary
    ) / 2
    df_clean.loc[high_salary_mask, '薪资浮动'] = (
        median_salary - df_clean.loc[high_salary_mask, '最低月薪']
    )
    print(f"\n[2.16] 薪资异常值处理: {high_salary_count} 条最高月薪>100000的记录已修正")

# 最低月薪 < 1000 的视为异常
low_salary_mask = df_clean['最低月薪'] < 1000
low_salary_count = low_salary_mask.sum()
if low_salary_count > 0:
    df_clean.loc[low_salary_mask, '最低月薪'] = df_clean.loc[low_salary_mask, '最高月薪'] * 0.5
    df_clean.loc[low_salary_mask, '平均月薪'] = (
        df_clean.loc[low_salary_mask, '最低月薪'] + df_clean.loc[low_salary_mask, '最高月薪']
    ) / 2
    df_clean.loc[low_salary_mask, '薪资浮动'] = (
        df_clean.loc[low_salary_mask, '最高月薪'] - df_clean.loc[low_salary_mask, '最低月薪']
    )
    print(f"[2.16] 薪资异常值处理: {low_salary_count} 条最低月薪<1000的记录已修正")

# 修复最高月薪 < 最低月薪 的异常记录
swap_mask = df_clean['最高月薪'] < df_clean['最低月薪']
swap_count = swap_mask.sum()
if swap_count > 0:
    # 交换最高和最低薪资
    df_clean.loc[swap_mask, ['最低月薪', '最高月薪']] = df_clean.loc[swap_mask, ['最高月薪', '最低月薪']].values
    # 重新计算平均月薪和薪资浮动
    df_clean.loc[swap_mask, '平均月薪'] = (
        df_clean.loc[swap_mask, '最低月薪'] + df_clean.loc[swap_mask, '最高月薪']
    ) / 2
    df_clean.loc[swap_mask, '薪资浮动'] = (
        df_clean.loc[swap_mask, '最高月薪'] - df_clean.loc[swap_mask, '最低月薪']
    )
    print(f"[2.16] 薪资异常值处理: {swap_count} 条最高<最低薪的记录已交换修正")

# --- 2.17 薪资分级 ---
def salary_grade(avg_salary):
    """根据平均月薪划分薪资等级"""
    if pd.isna(avg_salary):
        return '未知'
    if avg_salary < 5000:
        return '5K以下'
    elif avg_salary < 8000:
        return '5K-8K'
    elif avg_salary < 12000:
        return '8K-12K'
    elif avg_salary < 20000:
        return '12K-20K'
    elif avg_salary < 30000:
        return '20K-30K'
    else:
        return '30K以上'

df_clean['薪资等级'] = df_clean['平均月薪'].apply(salary_grade)

# --- 2.18 企业规模分类（基于企业名称）---
def classify_company_size(name):
    """根据企业名称关键词推断企业规模"""
    if pd.isna(name) or not isinstance(name, str):
        return '未知'
    name = name.strip()
    large_keywords = ['集团', '股份', '有限公司', '科技', '技术']
    medium_keywords = ['有限', '公司']
    if any(kw in name for kw in large_keywords):
        return '大中型企业'
    elif any(kw in name for kw in medium_keywords):
        return '中小型企业'
    return '其他'

df_clean['企业规模'] = df_clean['企业名称'].apply(classify_company_size)

# --- 2.19 企业类型分类（基于初级分类）---
industry_mapping = {
    # IT互联网大类
    '计算机软件': 'IT互联网',
    '互联网': 'IT互联网',
    'IT服务': 'IT互联网',
    '计算机硬件': 'IT互联网',
    '人工智能': 'IT互联网',
    '云计算/大数据': 'IT互联网',
    '物联网': 'IT互联网',
    '运营商/增值服务': 'IT互联网',
    '网络/信息安全': 'IT互联网',
    '电子商务': 'IT互联网',
    '企业服务': 'IT互联网',
    '区块链': 'IT互联网',
    '新零售': 'IT互联网',
    '新媒体': 'IT互联网',
    '游戏': 'IT互联网',
    '在线生活服务（O2O）': 'IT互联网',
    '在线医疗': 'IT互联网',
    '在线教育': 'IT互联网',
    '互联网金融/小额贷款': 'IT互联网',
    # 电子硬件大类
    '电子/半导体/集成电路': '电子硬件',
    '通信/网络设备': '电子硬件',
    '智能硬件': '电子硬件',
    '消费电子产品': '电子硬件',
    '光电子行业': '电子硬件',
    '机器人': '电子硬件',
    # 制造业大类
    '仪器仪表制造': '制造业',
    '电气机械/电力设备': '制造业',
    '专用设备制造': '制造业',
    '汽车研发/制造': '制造业',
    '工业自动化': '制造业',
    '电子设备制造': '制造业',
    '船舶/航空/航天/火车制造': '制造业',
    '金属制品业': '制造业',
    '通用设备制造': '制造业',
    '汽车零部件': '制造业',
    '文体/办公设备制造': '制造业',
    '家具制造': '制造业',
    '新能源汽车': '制造业',
    '新材料': '制造业',
    '军工制造': '制造业',
    '汽车智能互联': '制造业',
    # 制造业-化工材料
    '化工': '制造业',
    '化学原料/化学制品': '制造业',
    '化学纤维制造业': '制造业',
    '橡胶和塑料制品': '制造业',
    '非金属矿物制品业': '制造业',
    '钢铁/有色金属冶炼及加工': '制造业',
    '纺织业/服饰产品加工制造': '制造业',
    # 制造业-其他
    '印刷/包装/造纸': '制造业',
    '农副产品加工制造': '制造业',
    '日化产品制造': '制造业',
    '食品/饮料': '制造业',
    '烟草/酒业': '制造业',
    '玩具/礼品': '制造业',
    '家具/家居/家电': '制造业',
    '智能硬件': '电子硬件',
    '耐用消费品': '制造业',
    '快速消费品': '制造业',
    '服装/纺织/皮革': '制造业',
    # 医药健康大类
    '医药制造': '医药健康',
    '医疗设备/器械': '医药健康',
    '生物工程': '医药健康',
    '医药批发/零售': '医药健康',
    '卫生服务': '医药健康',
    '医疗检测': '医药健康',
    '医院': '医药健康',
    '医美/健康服务': '医药健康',
    # 能源化工
    '新能源': '能源化工',
    '电力/水利/热力/燃气': '能源化工',
    '石油/石化': '能源化工',
    '矿产/采掘': '能源化工',
    # 金融大类
    '金融': '金融',
    '保险': '金融',
    '银行': '金融',
    '证券/期货': '金融',
    '基金': '金融',
    '信托': '金融',
    '投资/融资': '金融',
    '互联网金融/小额贷款': '金融',
    '租赁/拍卖/典当/担保': '金融',
    '汽车金融': '金融',
    # 房地产建筑
    '房地产开发': '房地产建筑',
    '工程施工': '房地产建筑',
    '建筑设备安装': '房地产建筑',
    '建材': '房地产建筑',
    '建筑设计': '房地产建筑',
    '装饰装修': '房地产建筑',
    '物业管理': '房地产建筑',
    '房地产中介': '房地产建筑',
    '工程技术与设计服务': '房地产建筑',
    '建筑工程检测': '房地产建筑',
    '土地与公共设施管理': '房地产建筑',
    # 教育大类
    '培训/辅导服务': '教育',
    '学校/学历教育': '教育',
    '在线教育': '教育',
    # 零售贸易
    '零售/批发': '零售贸易',
    '贸易/进出口': '零售贸易',
    '电子商务': '零售贸易',
    '汽车4S店/经销商': '零售贸易',
    # 物流交通
    '货运/物流/仓储': '物流交通',
    '客运服务': '物流交通',
    '邮政/快递': '物流交通',
    '火车站/港口/汽车站/路政': '物流交通',
    # 生活服务
    '餐饮服务': '生活服务',
    '酒店/民宿': '生活服务',
    '旅游服务': '生活服务',
    '回收/维修': '生活服务',
    '租赁服务': '生活服务',
    # 专业服务
    '咨询服务': '专业服务',
    '检测/认证': '专业服务',
    '专业技术服务': '专业服务',
    '人力资源服务': '专业服务',
    '财务/审计/税务': '专业服务',
    '专利/商标/知识产权': '专业服务',
    '翻译服务': '专业服务',
    '商业代理服务': '专业服务',
    # 文化传媒
    '广告/营销': '文化传媒',
    '新闻/出版': '文化传媒',
    '广播/影视': '文化传媒',
    '文化艺术/娱乐': '文化传媒',
    '会议/展览': '文化传媒',
    '体育': '文化传媒',
    '景区/商业/市场等综合管理': '文化传媒',
    # 科研学术
    '学术/科研': '科研学术',
    '科学技术推广': '科研学术',
    # 环保
    '环保': '环保',
    # 农林牧渔
    '农/林/牧/渔': '农林牧渔',
    # 政府公共事业
    '政府/公共事业': '政府公共事业',
    '社团/组织/社会保障': '政府公共事业',
    # 其他
    '办公用品/设备': '零售贸易',
    '珠宝/首饰': '零售贸易',
    '汽车后市场': '零售贸易',
    '智能家居': '电子硬件',
}

def classify_industry(category):
    if pd.isna(category) or not isinstance(category, str):
        return '其他'
    # 按关键词长度降序排序，确保长关键词优先匹配
    sorted_mapping = sorted(industry_mapping.items(), key=lambda x: len(x[0]), reverse=True)
    for key, value in sorted_mapping:
        if key in category:
            return value
    return '其他'

df_clean['行业类型'] = df_clean['初级分类'].apply(classify_industry)

# --- 2.20 提取月薪区间（用于年终奖估算）---
# 假设年终奖 = 月薪 * 月数，常见为1-3个月
# 此处暂用薪资浮动作为估算依据
df_clean['年终奖估算'] = df_clean['薪资浮动'] * 0.5

print(f"\n清洗后数据集形状: {df_clean.shape}")
print(f"新增特征列: 薪资等级, 企业规模, 行业类型, 年终奖估算")

# ============================================================
# 3. 数据分析与报告
# ============================================================
print("\n" + "=" * 60)
print("3. 数据分析")
print("=" * 60)

analysis_lines = []
analysis_lines.append("=" * 60)
analysis_lines.append("招聘数据集分析报告")
analysis_lines.append("=" * 60)
analysis_lines.append(f"总样本量: {len(df_clean)}")
analysis_lines.append(f"特征列数: {len(df_clean.columns)}")
analysis_lines.append("")

# --- 一、招聘岗位分布 ---
analysis_lines.append("-" * 40)
analysis_lines.append("一、招聘岗位分布 (Top 20)")
analysis_lines.append("-" * 40)
top_jobs = df_clean['招聘岗位'].value_counts().head(20)
for job, count in top_jobs.items():
    analysis_lines.append(f"  {job}: {count}")

# --- 二、工作城市分布 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("二、工作城市分布 (Top 20)")
analysis_lines.append("-" * 40)
top_cities = df_clean['工作城市'].value_counts().head(20)
for city, count in top_cities.items():
    analysis_lines.append(f"  {city}: {count}")

# --- 三、学历要求分布 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("三、学历要求分布")
analysis_lines.append("-" * 40)
for edu, count in df_clean['学历要求'].value_counts().items():
    pct = count / len(df_clean) * 100
    analysis_lines.append(f"  {edu}: {count} ({pct:.1f}%)")

# --- 四、经验要求分布 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("四、经验要求分布")
analysis_lines.append("-" * 40)
for exp, count in df_clean['要求经验'].value_counts().items():
    pct = count / len(df_clean) * 100
    analysis_lines.append(f"  {exp}: {count} ({pct:.1f}%)")

# --- 五、薪资分析 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("五、薪资分析 (月薪/元)")
analysis_lines.append("-" * 40)
analysis_lines.append(f"  最低月薪均值: {df_clean['最低月薪'].mean():.0f}")
analysis_lines.append(f"  最高月薪均值: {df_clean['最高月薪'].mean():.0f}")
analysis_lines.append(f"  平均月薪均值: {df_clean['平均月薪'].mean():.0f}")
analysis_lines.append(f"  平均月薪中位数: {df_clean['平均月薪'].median():.0f}")
analysis_lines.append(f"  平均月薪标准差: {df_clean['平均月薪'].std():.0f}")
analysis_lines.append(f"  薪资浮动均值: {df_clean['薪资浮动'].mean():.0f}")

# --- 六、按城市平均薪资 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("六、按城市平均薪资 (Top 15)")
analysis_lines.append("-" * 40)
city_salary = df_clean.groupby('工作城市')['平均月薪'].agg(['mean', 'count']).query('count >= 10')
city_salary = city_salary.sort_values('mean', ascending=False).head(15)
for city, row in city_salary.iterrows():
    analysis_lines.append(f"  {city}: {row['mean']:.0f}元/月 (样本量: {int(row['count'])})")

# --- 七、按学历平均薪资 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("七、按学历平均薪资")
analysis_lines.append("-" * 40)
edu_salary = df_clean.groupby('学历要求')['平均月薪'].agg(['mean', 'count']).sort_values('mean', ascending=False)
for edu, row in edu_salary.iterrows():
    if row['count'] >= 5:
        analysis_lines.append(f"  {edu}: {row['mean']:.0f}元/月 (样本量: {int(row['count'])})")

# --- 八、招聘类别分布 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("八、招聘类别分布")
analysis_lines.append("-" * 40)
for cat, count in df_clean['招聘类别'].value_counts().items():
    pct = count / len(df_clean) * 100
    analysis_lines.append(f"  {cat}: {count} ({pct:.1f}%)")

# --- 九、初级分类分布 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("九、初级分类分布 (Top 15)")
analysis_lines.append("-" * 40)
top_categories = df_clean['初级分类'].value_counts().head(15)
for cat, count in top_categories.items():
    analysis_lines.append(f"  {cat}: {count}")

# --- 十、新增特征统计 ---
analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("十、薪资等级分布")
analysis_lines.append("-" * 40)
for grade in ['5K以下', '5K-8K', '8K-12K', '12K-20K', '20K-30K', '30K以上']:
    count = (df_clean['薪资等级'] == grade).sum()
    pct = count / len(df_clean) * 100
    analysis_lines.append(f"  {grade}: {count} ({pct:.1f}%)")

analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("十一、企业规模分布")
analysis_lines.append("-" * 40)
for size, count in df_clean['企业规模'].value_counts().items():
    pct = count / len(df_clean) * 100
    analysis_lines.append(f"  {size}: {count} ({pct:.1f}%)")

analysis_lines.append("")
analysis_lines.append("-" * 40)
analysis_lines.append("十二、行业类型分布 (Top 10)")
analysis_lines.append("-" * 40)
for industry, count in df_clean['行业类型'].value_counts().head(10).items():
    pct = count / len(df_clean) * 100
    analysis_lines.append(f"  {industry}: {count} ({pct:.1f}%)")

report_text = "\n".join(analysis_lines)
print(report_text)

# ============================================================
# 4. 保存数据
# ============================================================
print("\n" + "=" * 60)
print("4. 保存数据")
print("=" * 60)

df_clean.to_csv(CLEANED_DATA_PATH, index=False, encoding='utf-8-sig')
print(f"清洗后数据已保存至: {CLEANED_DATA_PATH}")

with open(ANALYSIS_REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report_text)
print(f"分析报告已保存至: {ANALYSIS_REPORT_PATH}")

print(f"\n处理完成！最终数据集: {df_clean.shape[0]} 行, {df_clean.shape[1]} 列")
print(f"清洗前: 15000 行")
print(f"清洗后: {df_clean.shape[0]} 行")
print(f"删除空列: {len(cols_to_drop)} 列")
print(f"新增特征: 薪资等级, 企业规模, 行业类型, 年终奖估算")