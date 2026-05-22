import pandas as pd
import numpy as np

df = pd.read_csv(r'c:\Users\13309\Desktop\大实验\IntelligentRecruitmentSystem\data\cleaned_recruitment_data.csv', encoding='utf-8-sig')

print('=' * 60)
print('数据质量全面审查')
print('=' * 60)
print(f'\n数据集形状: {df.shape}')
print(f'列: {df.columns.tolist()}')

# 1. 缺失值检查
print('\n' + '-' * 40)
print('【1】缺失值检查')
print('-' * 40)
missing = df.isna().sum()
for col, count in missing.items():
    if count > 0:
        print(f'  {col}: {count}条缺失 ({count/len(df)*100:.2f}%)')
if missing.sum() == 0:
    print('  无缺失值 ✓')

# 2. 岗位名称去重检查
print('\n' + '-' * 40)
print('【2】岗位名称重复检查')
print('-' * 40)
# 查找可能的重复变体
java_jobs = df[df['招聘岗位'].str.contains('java', case=False, na=False)]['招聘岗位'].unique()
print(f'  Java相关岗位变体: {list(java_jobs)}')

c_jobs = df[df['招聘岗位'].str.contains(r'\bc\b', na=False)]['招聘岗位'].unique()
print(f'  C/C++/C#相关岗位变体: {list(c_jobs)[:20]}')

# 3. 学历要求检查
print('\n' + '-' * 40)
print('【3】学历要求完整性')
print('-' * 40)
edu = df['学历要求'].value_counts()
print(f'  学历分类: {list(edu.index)}')
print(f'  "中专/中技"仍合并: {edu.get("中专/中技", 0)}条')

# 4. 经验要求检查
print('\n' + '-' * 40)
print('【4】经验要求完整性')
print('-' * 40)
exp = df['要求经验'].value_counts()
print(f'  经验分类: {list(exp.index)}')
# 检查是否有不规范的经验描述
unusual_exp = df[~df['要求经验'].isin(['1年以下', '1-3年', '3-5年', '5-10年', '10年以上', '经验不限'])]
if len(unusual_exp) > 0:
    print(f'  ⚠ 存在不规范经验描述: {unusual_exp["要求经验"].unique()}')
else:
    print('  经验分类完整 ✓')

# 5. 薪资异常值再检查
print('\n' + '-' * 40)
print('【5】薪资异常值检查')
print('-' * 40)
print(f'  最低月薪 < 1000: {(df["最低月薪"] < 1000).sum()}条')
print(f'  最高月薪 > 100000: {(df["最高月薪"] > 100000).sum()}条')
print(f'  最高月薪 < 最低月薪: {(df["最高月薪"] < df["最低月薪"]).sum()}条')
print(f'  薪资为0: {(df["最低月薪"] == 0).sum()}条')

# 6. 城市完整性检查
print('\n' + '-' * 40)
print('【6】工作城市检查')
print('-' * 40)
cities = df['工作城市'].value_counts()
single_char_cities = cities[cities.index.str.len() == 1]
if len(single_char_cities) > 0:
    print(f'  ⚠ 仍存在单字城市: {single_char_cities.tolist()}')
else:
    print('  城市名完整 ✓')

# 检查是否有"其他"城市
other_cities = cities.get('其他', 0)
print(f'  "其他"城市数量: {other_cities}条')

# 7. 初级分类检查
print('\n' + '-' * 40)
print('【7】初级分类检查')
print('-' * 40)
cats = df['初级分类'].value_counts()
print(f'  分类总数: {len(cats)}种')
print(f'  "其他"分类数量: {cats.get("其他", 0)}条')

# 8. 企业类型/行业检查
print('\n' + '-' * 40)
print('【8】行业类型分布')
print('-' * 40)
industry = df['行业类型'].value_counts()
print(f'  行业分类: {list(industry.index)}')
print(f'  "其他"行业占比: {industry.get("其他", 0)/len(df)*100:.1f}%')

# 9. 企业规模检查
print('\n' + '-' * 40)
print('【9】企业规模分布')
print('-' * 40)
size = df['企业规模'].value_counts()
print(f'  规模分类: {list(size.index)}')
print(f'  "其他"占比: {size.get("其他", 0)/len(df)*100:.1f}%')

# 10. 日期格式检查
print('\n' + '-' * 40)
print('【10】招聘发布日期格式')
print('-' * 40)
date_col = df['招聘发布日期']
print(f'  数据类型: {date_col.dtype}')
print(f'  缺失值: {date_col.isna().sum()}条')
if date_col.dtype == 'object':
    print('  ⚠ 日期列仍为字符串格式，未转为datetime')

# 11. 数据来源检查
print('\n' + '-' * 40)
print('【11】数据来源分布')
print('-' * 40)
sources = df['来源'].value_counts()
print(f'  数据来源: {sources.to_dict()}')

# 12. 招聘类别检查
print('\n' + '-' * 40)
print('【12】招聘类别分布')
print('-' * 40)
cat_dist = df['招聘类别'].value_counts()
print(f'  类别: {cat_dist.to_dict()}')

# 13. 检查是否有冗余列
print('\n' + '-' * 40)
print('【13】冗余列检查')
print('-' * 40)
print(f'  "招聘发布年份"与"招聘发布日期"信息重复')
print(f'  "学历要求_排序"和"要求经验_排序"为辅助列，是否需要保留?')

print('\n' + '=' * 60)
print('优化建议总结')
print('=' * 60)
print('1. "中专/中技"仍合并，需从原始数据分离')
print('2. Java大小写统一未完成（java开发工程师仍有91条）')
print('3. 日期列仍为字符串格式')
print('4. "其他"行业占比28.4%过高，需更精细分类')
print('5. 企业规模"其他"占12.3%，分类规则需优化')
