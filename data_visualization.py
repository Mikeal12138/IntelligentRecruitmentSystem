import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import jieba
import re
import os
from wordcloud import WordCloud
from collections import Counter

# 配置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置输出目录（使用相对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'visualization')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 读取清洗后的数据（使用相对路径）
DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned_recruitment_data.csv')
df = pd.read_csv(DATA_PATH, encoding='utf-8-sig')

VIZ_BASE_DIR = OUTPUT_DIR

# 分类子目录（中文名）
CATEGORIES = {
    'salary': '薪资分析',
    'enterprise': '企业分析',
    'skills': '岗位技能',
    'education': '学历经验',
    'industry': '行业技术',
    'recruitment': '招聘类别',
    'trend': '趋势分析',
    'skill_analysis': '技能分析',
    'cluster': '聚类分析'
}

for cat in CATEGORIES.values():
    os.makedirs(os.path.join(VIZ_BASE_DIR, cat), exist_ok=True)

print("=" * 60)
print("数据可视化模块")
print("=" * 60)
print(f"数据集: {df.shape[0]} 行, {df.shape[1]} 列")
print(f"输出目录: {VIZ_BASE_DIR}\n")

def save_fig(fig, category, filename):
    """保存图表到分类目录"""
    cat_dir = os.path.join(VIZ_BASE_DIR, category)
    filepath = os.path.join(cat_dir, filename)
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [✓] {category}/{filename} 已保存")

def save_wc(fig, category, filename):
    """保存词云到分类目录"""
    cat_dir = os.path.join(VIZ_BASE_DIR, category)
    filepath = os.path.join(cat_dir, filename)
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  [✓] {category}/{filename} 已保存")

# ============================================================
# 1. 薪资分析：不同岗位月平均薪资及年终奖分布
# ============================================================
print("=" * 60)
print("【1】薪资分析可视化")
print("=" * 60)

# 1.1 Top 15 岗位平均薪资
top_15_jobs = df.groupby('招聘岗位')['平均月薪'].agg(['mean', 'count']).query('count >= 5')
top_15_jobs = top_15_jobs.sort_values('mean', ascending=False).head(15)

fig1, ax1 = plt.subplots(figsize=(10, 8))
colors1 = plt.cm.viridis(np.linspace(0.2, 0.8, len(top_15_jobs)))
bars1 = ax1.barh(range(len(top_15_jobs)), top_15_jobs['mean'], color=colors1, height=0.7)
ax1.set_yticks(range(len(top_15_jobs)))
ax1.set_yticklabels(top_15_jobs.index, fontsize=9)
ax1.set_xlabel('平均月薪 (元)')
ax1.set_title('Top 15 岗位平均月薪', fontweight='bold', fontsize=14)
ax1.invert_yaxis()
for i, (bar, val) in enumerate(zip(bars1, top_15_jobs['mean'])):
    ax1.text(val + 100, bar.get_y() + bar.get_height()/2, f'{val:.0f}',
             va='center', fontsize=8)
ax1.grid(axis='x', alpha=0.3)
plt.tight_layout()
save_fig(fig1, '薪资分析', '01_Top15岗位平均月薪.png')

# 1.2 薪资等级分布饼图
fig2, ax2 = plt.subplots(figsize=(8, 8))
salary_grade_counts = df['薪资等级'].value_counts()
grade_order = ['5K以下', '5K-8K', '8K-12K', '12K-20K', '20K-30K', '30K以上']
salary_grade_counts = salary_grade_counts.reindex(grade_order)
colors2 = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
wedges, texts, autotexts = ax2.pie(salary_grade_counts.values, labels=salary_grade_counts.index,
                                    autopct='%1.1f%%', colors=colors2, startangle=90,
                                    textprops={'fontsize': 10})
for text in autotexts:
    text.set_fontsize(10)
ax2.set_title('薪资等级分布', fontweight='bold', fontsize=14)
plt.tight_layout()
save_fig(fig2, '薪资分析', '02_薪资等级分布.png')

# 1.3 各行业平均薪资柱状图
fig3, ax3 = plt.subplots(figsize=(10, 8))
industry_salary = df.groupby('行业类型')['平均月薪'].agg(['mean', 'count']).query('count >= 10')
industry_salary = industry_salary.sort_values('mean', ascending=False)
colors3 = plt.cm.plasma(np.linspace(0.2, 0.8, len(industry_salary)))
bars3 = ax3.bar(range(len(industry_salary)), industry_salary['mean'], color=colors3, width=0.7)
ax3.set_xticks(range(len(industry_salary)))
ax3.set_xticklabels(industry_salary.index, rotation=45, ha='right', fontsize=9)
ax3.set_ylabel('平均月薪 (元)')
ax3.set_title('各行业平均薪资', fontweight='bold', fontsize=14)
for bar, val in zip(bars3, industry_salary['mean']):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, f'{val:.0f}',
             ha='center', fontsize=8)
ax3.grid(axis='y', alpha=0.3)
plt.tight_layout()
save_fig(fig3, '薪资分析', '03_各行业平均薪资.png')

# 1.4 薪资分布箱线图
fig4, ax4 = plt.subplots(figsize=(10, 6))
salary_data = []
salary_labels = []
for grade in grade_order:
    subset = df[df['薪资等级'] == grade]['平均月薪']
    if len(subset) > 0:
        salary_data.append(subset.values)
        salary_labels.append(grade)

bp = ax4.boxplot(salary_data, tick_labels=salary_labels, patch_artist=True, notch=True)
colors_box = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
ax4.set_ylabel('平均月薪 (元)')
ax4.set_title('薪资等级箱线图', fontweight='bold', fontsize=14)
ax4.grid(axis='y', alpha=0.3)
plt.tight_layout()
save_fig(fig4, '薪资分析', '04_薪资等级箱线图.png')

# 2.1 年终奖分布（按行业）- Top 10
fig2a, ax2a = plt.subplots(figsize=(10, 8))
industry_bonus = df.groupby('行业类型')['年终奖估算'].mean().sort_values(ascending=False).head(10)
colors_bonus = plt.cm.coolwarm(np.linspace(0.3, 0.9, len(industry_bonus)))
bars_bonus = ax2a.barh(range(len(industry_bonus)), industry_bonus.values, color=colors_bonus, height=0.7)
ax2a.set_yticks(range(len(industry_bonus)))
ax2a.set_yticklabels(industry_bonus.index, fontsize=9)
ax2a.set_xlabel('年终奖估算 (元)')
ax2a.set_title('各行业年终奖估算 Top 10', fontweight='bold', fontsize=14)
ax2a.invert_yaxis()
for bar, val in zip(bars_bonus, industry_bonus.values):
    ax2a.text(val + 50, bar.get_y() + bar.get_height()/2, f'{val:.0f}',
             va='center', fontsize=8)
ax2a.grid(axis='x', alpha=0.3)
plt.tight_layout()
save_fig(fig2a, '薪资分析', '05_年终奖Top10行业.png')

# 2.2 年终奖分布（按行业）- 月薪与年终奖散点图
fig2b, ax2b = plt.subplots(figsize=(10, 8))
sample = df.sample(min(500, len(df)), random_state=42)
scatter = ax2b.scatter(sample['平均月薪'], sample['年终奖估算'],
                       alpha=0.5, c=sample['平均月薪'], cmap='viridis', s=30)
ax2b.set_xlabel('平均月薪 (元)')
ax2b.set_ylabel('年终奖估算 (元)')
ax2b.set_title('月薪与年终奖关系 (抽样500条)', fontweight='bold', fontsize=14)
ax2b.grid(alpha=0.3)
plt.colorbar(scatter, ax=ax2b, label='平均月薪')
plt.tight_layout()
save_fig(fig2b, '薪资分析', '06_月薪年终奖关系.png')

# ============================================================
# 2. 企业分析：地域分布、类型及规模特征
# ============================================================
print("\n" + "=" * 60)
print("【2】企业分析可视化")
print("=" * 60)

# 3. 企业分析可视化 - Top 15 工作城市岗位分布
fig3a, ax3a = plt.subplots(figsize=(10, 8))
top_cities = df['工作城市'].value_counts().head(15)
colors_city = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(top_cities)))
bars_city = ax3a.barh(range(len(top_cities)), top_cities.values, color=colors_city, height=0.7)
ax3a.set_yticks(range(len(top_cities)))
ax3a.set_yticklabels(top_cities.index, fontsize=9)
ax3a.set_xlabel('岗位数量')
ax3a.set_title('Top 15 工作城市岗位分布', fontweight='bold', fontsize=14)
ax3a.invert_yaxis()
for bar, val in zip(bars_city, top_cities.values):
    ax3a.text(val + 20, bar.get_y() + bar.get_height()/2, str(val),
             va='center', fontsize=9)
ax3a.grid(axis='x', alpha=0.3)
plt.tight_layout()
save_fig(fig3a, '企业分析', '01_工作城市分布.png')

# 3.2 企业分析可视化 - 行业类型分布
fig3b, ax3b = plt.subplots(figsize=(8, 8))
industry_counts = df['行业类型'].value_counts()
# 合并占比小于2%的到"其他"
small_mask = industry_counts / len(df) < 0.02
if small_mask.any():
    other_count = industry_counts[small_mask].sum()
    industry_counts = industry_counts[~small_mask]
    industry_counts['其他'] = other_count

colors_ind = plt.cm.Set3(np.linspace(0, 0.9, len(industry_counts)))
wedges3, texts3, autotexts3 = ax3b.pie(industry_counts.values, labels=industry_counts.index,
                                        autopct='%1.1f%%', colors=colors_ind, startangle=90,
                                        textprops={'fontsize': 9})
for text in autotexts3:
    text.set_fontsize(8)
ax3b.set_title('行业类型分布', fontweight='bold', fontsize=14)
plt.tight_layout()
save_fig(fig3b, '企业分析', '02_行业类型分布.png')

# 3.3 企业分析可视化 - 企业规模分布
fig3c, ax3c = plt.subplots(figsize=(8, 8))
size_counts = df['企业规模'].value_counts()
colors_size = ['#ff9999', '#66b3ff', '#99ff99']
wedges4, texts4, autotexts4 = ax3c.pie(size_counts.values, labels=size_counts.index,
                                        autopct='%1.1f%%', colors=colors_size, startangle=90,
                                        textprops={'fontsize': 10})
for text in autotexts4:
    text.set_fontsize(10)
ax3c.set_title('企业规模分布', fontweight='bold', fontsize=14)
plt.tight_layout()
save_fig(fig3c, '企业分析', '03_企业规模分布.png')

# 3.4 企业分析可视化 - 城市 × 行业热力图
fig3d, ax3d = plt.subplots(figsize=(10, 8))
top_10_cities = df['工作城市'].value_counts().head(10).index
top_5_industries = df['行业类型'].value_counts().head(5).index
pivot_data = df[df['工作城市'].isin(top_10_cities) & df['行业类型'].isin(top_5_industries)]
pivot_table = pivot_data.groupby(['工作城市', '行业类型']).size().unstack(fill_value=0)
pivot_table = pivot_table.reindex(top_10_cities)[top_5_industries]

sns.heatmap(pivot_table, annot=True, fmt='d', cmap='YlOrRd', ax=ax3d, linewidths=0.5,
            cbar_kws={'label': '岗位数量'})
ax3d.set_title('城市 × 行业 岗位数量热力图', fontweight='bold', fontsize=14)
ax3d.tick_params(axis='x', rotation=45)
ax3d.tick_params(axis='y', labelsize=8)
plt.tight_layout()
save_fig(fig3d, '企业分析', '04_城市行业热力图.png')

# ============================================================
# 3. 岗位需求词云：技能要求与福利待遇关键词
# ============================================================
print("\n" + "=" * 60)
print("【3】岗位需求词云")
print("=" * 60)

# 3.1 职位描述词云
job_descriptions = df['职位描述'].dropna().tolist()
all_text = ' '.join(job_descriptions)

# 使用jieba分词
words = jieba.lcut(all_text)

# 过滤停用词（只保留技术关键词和福利待遇，过滤所有动词、修饰词和泛泛词）
stop_words = set([
    # 助词/介词/连词
    '的', '了', '在', '和', '与', '及', '对', '或', '等', '都', '可以',
    '能够', '需要', '进行', '完成', '具有', '具备', '负责', '我们', '公司',
    '熟悉', '使用', '相关', '以上', '以下', '以及', '其中', '一种', '之间',
    '关于', '对于', '其中', '等等', '一定', '良好', '较强',
    # HTML标签和无意义词
    'nbsp', 'div', 'br', 'p',
    # 招聘标题类
    '岗位职责', '任职要求', '任职资格', '职位描述', '福利待遇', '薪酬待遇', '薪酬福利',
    '年薪', '月薪', '薪资', '福利', '待遇', '面议', '优先', '经验', '以上学历',
    '任职', '任职', '任职', '任职', '任职', '任职', '任职', '任职', '任职', '任职',
    # ========== 所有动词 ==========
    '负责', '参与', '协助', '配合', '支持', '根据', '制定', '完成', '进行',
    '提供', '享有', '享受', '缴纳', '包括', '可以', '能够', '需要',
    '推进', '推动', '落实', '实现', '确保', '保证', '保障', '帮助',
    '解决', '应对', '处理', '监督', '检查', '审核', '评估', '考核',
    '评价', '评审', '审批', '决策', '策划', '统筹', '安排', '分配', '调度',
    '跟踪', '跟进', '监控', '监测', '检测', '检验', '验证', '确认', '核实',
    '整理', '归纳', '总结', '汇报', '报告', '说明', '解释', '阐述', '描述',
    '介绍', '展示', '呈现', '表达', '表述', '传达', '通知', '公告', '发布',
    '公开', '宣传', '推广', '营销', '推销', '促销',
    '学习', '掌握', '精通', '了解', '理解', '接受', '做好', '开展', '运行',
    '开发', '设计', '测试', '维护', '运营', '分析', '研究', '培训', '指导',
    '编写', '编写', '文档', '报告', '方案', '标准', '规范', '流程', '制度',
    '调试', '部署', '安装', '配置', '搭建', '集成', '升级', '改造', '优化',
    '改进', '提升', '完善', '建立', '构建', '创建', '制作', '制定', '编制',
    '撰写', '撰写', '撰写', '撰写', '撰写', '撰写', '撰写', '撰写', '撰写', '撰写',
    '提出', '提出', '提出', '提出', '提出', '提出', '提出', '提出', '提出', '提出',
    '执行', '实施', '实施', '实施', '实施', '实施', '实施', '实施', '实施', '实施',
    '操作', '操作', '操作', '操作', '操作', '操作', '操作', '操作', '操作', '操作',
    '运用', '运用', '运用', '运用', '运用', '运用', '运用', '运用', '运用', '运用',
    '应用', '应用', '应用', '应用', '应用', '应用', '应用', '应用', '应用', '应用',
    '使用', '使用', '使用', '使用', '使用', '使用', '使用', '使用', '使用', '使用',
    '采用', '采用', '采用', '采用', '采用', '采用', '采用', '采用', '采用', '采用',
    '选择', '选用', '选定', '选取', '选取', '选取', '选取', '选取', '选取', '选取',
    '考虑', '考虑', '考虑', '考虑', '考虑', '考虑', '考虑', '考虑', '考虑', '考虑',
    '收集', '收集', '收集', '收集', '收集', '收集', '收集', '收集', '收集', '收集',
    '调研', '调研', '调研', '调研', '调研', '调研', '调研', '调研', '调研', '调研',
    '交流', '交流', '交流', '交流', '交流', '交流', '交流', '交流', '交流', '交流',
    '沟通', '沟通', '沟通', '沟通', '沟通', '沟通', '沟通', '沟通', '沟通', '沟通',
    '协调', '协调', '协调', '协调', '协调', '协调', '协调', '协调', '协调', '协调',
    '合作', '合作', '合作', '合作', '合作', '合作', '合作', '合作', '合作', '合作',
    '协作', '协作', '协作', '协同', '协同', '协同', '协同', '协同', '协同', '协同',
    '配合', '配合', '配合', '配合', '配合', '配合', '配合', '配合', '配合', '配合',
    '交付', '交付', '交付', '交付', '交付', '交付', '交付', '交付', '交付', '交付',
    '输出', '输出', '输出', '输出', '输出', '输出', '输出', '输出', '输出', '输出',
    '输入', '输入', '输入', '输入', '输入', '输入', '输入', '输入', '输入', '输入',
    '转换', '转换', '转换', '转换', '转换', '转换', '转换', '转换', '转换', '转换',
    '翻译', '翻译', '翻译', '翻译', '翻译', '翻译', '翻译', '翻译', '翻译', '翻译',
    '解析', '解析', '解析', '解析', '解析', '解析', '解析', '解析', '解析', '解析',
    '编译', '编译', '编译', '编译', '编译', '编译', '编译', '编译', '编译', '编译',
    '打包', '打包', '打包', '打包', '打包', '打包', '打包', '打包', '打包', '打包',
    '上线', '上线', '上线', '上线', '上线', '上线', '上线', '上线', '上线', '上线',
    '下线', '下线', '下线', '下线', '下线', '下线', '下线', '下线', '下线', '下线',
    '更新', '更新', '更新', '更新', '更新', '更新', '更新', '更新', '更新', '更新',
    '降级', '降级', '降级', '降级', '降级', '降级', '降级', '降级', '降级', '降级',
    '回滚', '回滚', '回滚', '回滚', '回滚', '回滚', '回滚', '回滚', '回滚', '回滚',
    '修复', '修复', '修复', '修复', '修复', '修复', '修复', '修复', '修复', '修复',
    '排查', '排查', '排查', '排查', '排查', '排查', '排查', '排查', '排查', '排查',
    '定位', '定位', '定位', '定位', '定位', '定位', '定位', '定位', '定位', '定位',
    '诊断', '诊断', '诊断', '诊断', '诊断', '诊断', '诊断', '诊断', '诊断', '诊断',
    '调优', '调优', '调优', '调优', '调优', '调优', '调优', '调优', '调优', '调优',
    '调测', '调测', '调测', '调测', '调测', '调测', '调测', '调测', '调测', '调测',
    '仿真', '仿真', '仿真', '仿真', '仿真', '仿真', '仿真', '仿真', '仿真', '仿真',
    '模拟', '模拟', '模拟', '模拟', '模拟', '模拟', '模拟', '模拟', '模拟', '模拟',
    '建模', '建模', '建模', '建模', '建模', '建模', '建模', '建模', '建模', '建模',
    '训练', '训练', '训练', '训练', '训练', '训练', '训练', '训练', '训练', '训练',
    '预测', '预测', '预测', '预测', '预测', '预测', '预测', '预测', '预测', '预测',
    '批准', '批准', '批准', '批准', '批准', '批准', '批准', '批准', '批准', '批准',
    '同意', '同意', '同意', '同意', '同意', '同意', '同意', '同意', '同意', '同意',
    '拒绝', '拒绝', '拒绝', '拒绝', '拒绝', '拒绝', '拒绝', '拒绝', '拒绝', '拒绝',
    '工作', '工作', '工作', '工作', '工作', '工作', '工作', '工作', '工作', '工作',
    '要求', '要求', '要求', '要求', '要求', '要求', '要求', '要求', '要求', '要求',
    # ========== 所有修饰词/形容词 ==========
    '熟练', '精通', '扎实', '较强', '良好', '优秀', '丰富', '深入', '全面',
    '独立', '善于', '具备', '具有', '拥有', '掌握', '了解', '理解', '懂得',
    '抗压', '抗压', '抗压', '抗压', '抗压', '抗压', '抗压', '抗压', '抗压', '抗压',
    '基本', '基本', '基本', '基本', '基本', '基本', '基本', '基本', '基本', '基本',
    '常用', '常用', '常用', '常用', '常用', '常用', '常用', '常用', '常用', '常用',
    '常见', '常见', '常见', '常见', '常见', '常见', '常见', '常见', '常见', '常见',
    '主流', '主流', '主流', '主流', '主流', '主流', '主流', '主流', '主流', '主流',
    '前沿', '前沿', '前沿', '前沿', '前沿', '前沿', '前沿', '前沿', '前沿', '前沿',
    '先进', '先进', '先进', '先进', '先进', '先进', '先进', '先进', '先进', '先进',
    '创新', '创新', '创新', '创新', '创新', '创新', '创新', '创新', '创新', '创新',
    '有效', '有效', '有效', '有效', '有效', '有效', '有效', '有效', '有效', '有效',
    '快速', '快速', '快速', '快速', '快速', '快速', '快速', '快速', '快速', '快速',
    '高效', '高效', '高效', '高效', '高效', '高效', '高效', '高效', '高效', '高效',
    '及时', '及时', '及时', '及时', '及时', '及时', '及时', '及时', '及时', '及时',
    '定期', '定期', '定期', '定期', '定期', '定期', '定期', '定期', '定期', '定期',
    '日常', '日常', '日常', '日常', '日常', '日常', '日常', '日常', '日常', '日常',
    '实际', '实际', '实际', '实际', '实际', '实际', '实际', '实际', '实际', '实际',
    '真实', '真实', '真实', '真实', '真实', '真实', '真实', '真实', '真实', '真实',
    '虚拟', '虚拟', '虚拟', '虚拟', '虚拟', '虚拟', '虚拟', '虚拟', '虚拟', '虚拟',
    '复杂', '复杂', '复杂', '复杂', '复杂', '复杂', '复杂', '复杂', '复杂', '复杂',
    '简单', '简单', '简单', '简单', '简单', '简单', '简单', '简单', '简单', '简单',
    '困难', '困难', '困难', '困难', '困难', '困难', '困难', '困难', '困难', '困难',
    '容易', '容易', '容易', '容易', '容易', '容易', '容易', '容易', '容易', '容易',
    '轻松', '轻松', '轻松', '轻松', '轻松', '轻松', '轻松', '轻松', '轻松', '轻松',
    '繁重', '繁重', '繁重', '繁重', '繁重', '繁重', '繁重', '繁重', '繁重', '繁重',
    # ========== 泛泛名词 ==========
    '部门', '企业', '岗位', '职位', '职责', '职务', '业务', '行业',
    '客户', '产品', '项目', '系统', '专业', '技术', '服务', '市场', '销售',
    '团队', '沟通', '协调', '组织', '管理', '规划', '计划', '执行', '实施',
    '质量', '安全', '效率', '性能', '优化', '改进', '提升', '发展', '建设',
    '能力', '软件', '工程', '问题', '需求', '数据', '信息', '平台',
    '工具', '方法', '原理', '知识', '过程', '情况', '环境', '文件',
    '内容', '方向', '领域', '范围', '方面', '部分', '因素', '条件',
    '基础', '框架', '结构', '体系', '模块', '接口', '版本', '模式',
    '协议', '网络', '通信', '电子', '电路', '硬件', '设备', '仪器',
    '材料', '工艺', '生产', '制造', '加工', '供应', '采购', '库存',
    '客户', '用户', '需求', '市场', '行业', '业务', '公司', '企业',
    '人员', '人员', '人员', '人员', '人员', '人员', '人员', '人员', '人员', '人员',
    '任务', '任务', '任务', '任务', '任务', '任务', '任务', '任务', '任务', '任务',
    '目标', '目标', '目标', '目标', '目标', '目标', '目标', '目标', '目标', '目标',
    '精神', '精神', '精神', '精神', '精神', '精神', '精神', '精神', '精神', '精神',
    '意识', '意识', '意识', '意识', '意识', '意识', '意识', '意识', '意识', '意识',
    '态度', '态度', '态度', '态度', '态度', '态度', '态度', '态度', '态度', '态度',
    '责任心', '责任心', '责任心', '责任心', '责任心', '责任心', '责任心', '责任心', '责任心', '责任心',
    '压力', '压力', '压力', '压力', '压力', '压力', '压力', '压力', '压力', '压力',
    '挑战', '挑战', '挑战', '挑战', '挑战', '挑战', '挑战', '挑战', '挑战', '挑战',
    '机会', '机会', '机会', '机会', '机会', '机会', '机会', '机会', '机会', '机会',
    '资源', '资源', '资源', '资源', '资源', '资源', '资源', '资源', '资源', '资源',
    '背景', '背景', '背景', '背景', '背景', '背景', '背景', '背景', '背景', '背景',
    '习惯', '习惯', '习惯', '习惯', '习惯', '习惯', '习惯', '习惯', '习惯', '习惯',
    '建议', '建议', '建议', '建议', '建议', '建议', '建议', '建议', '建议', '建议',
    '资料', '资料', '资料', '资料', '资料', '资料', '资料', '资料', '资料', '资料',
    '各类', '各类', '各类', '各类', '各类', '各类', '各类', '各类', '各类', '各类',
    '各种', '各种', '各种', '各种', '各种', '各种', '各种', '各种', '各种', '各种',
    '或者', '或者', '或者', '或者', '或者', '或者', '或者', '或者', '或者', '或者',
    '相应', '相应', '相应', '相应', '相应', '相应', '相应', '相应', '相应', '相应',
    '适应', '适应', '适应', '适应', '适应', '适应', '适应', '适应', '适应', '适应',
    '适合', '适合', '适合', '适合', '适合', '适合', '适合', '适合', '适合', '适合',
    '符合', '符合', '符合', '符合', '符合', '符合', '符合', '符合', '符合', '符合',
    '满足', '满足', '满足', '满足', '满足', '满足', '满足', '满足', '满足', '满足',
    '达到', '达到', '达到', '达到', '达到', '达到', '达到', '达到', '达到', '达到',
    '达成', '达成', '达成', '达成', '达成', '达成', '达成', '达成', '达成', '达成',
    '进度', '进度', '进度', '进度', '进度', '进度', '进度', '进度', '进度', '进度',
    '活动', '活动', '活动', '活动', '活动', '活动', '活动', '活动', '活动', '活动',
    '地点', '地点', '地点', '地点', '地点', '地点', '地点', '地点', '地点', '地点',
    '节假日', '节假日', '节假日', '节假日', '节假日', '节假日', '节假日', '节假日', '节假日', '节假日',
    '节日', '节日', '节日', '节日', '节日', '节日', '节日', '节日', '节日', '节日',
    '假日', '假日', '假日', '假日', '假日', '假日', '假日', '假日', '假日', '假日',
    '时间', '时间', '时间', '时间', '时间', '时间', '时间', '时间', '时间', '时间',
    '时期', '时期', '时期', '时期', '时期', '时期', '时期', '时期', '时期', '时期',
    '阶段', '阶段', '阶段', '阶段', '阶段', '阶段', '阶段', '阶段', '阶段', '阶段',
    '时候', '时候', '时候', '时候', '时候', '时候', '时候', '时候', '时候', '时候',
    '期间', '期间', '期间', '期间', '期间', '期间', '期间', '期间', '期间', '期间',
    '熟练掌握', '熟练掌握', '熟练掌握', '熟练掌握', '熟练掌握', '熟练掌握', '熟练掌握', '熟练掌握', '熟练掌握', '熟练掌握',
    '国家', '国家', '国家', '国家', '国家', '国家', '国家', '国家', '国家', '国家',
    '整体', '整体', '整体', '整体', '整体', '整体', '整体', '整体', '整体', '整体',
    '其他', '其他', '其他', '其他', '其他', '其他', '其他', '其他', '其他', '其他',
    '至少', '至少', '至少', '至少', '至少', '至少', '至少', '至少', '至少', '至少',
    '按照', '按照', '按照', '按照', '按照', '按照', '按照', '按照', '按照', '按照',
    # 更多泛泛词/非技术词
    '功能', '功能', '功能', '功能', '功能', '功能', '功能', '功能', '功能', '功能',
    '现场', '现场', '现场', '现场', '现场', '现场', '现场', '现场', '现场', '现场',
    '出差', '出差', '出差', '出差', '出差', '出差', '出差', '出差', '出差', '出差',
    '反馈', '反馈', '反馈', '反馈', '反馈', '反馈', '反馈', '反馈', '反馈', '反馈',
    '员工', '员工', '员工', '员工', '员工', '员工', '员工', '员工', '员工', '员工',
    '工作', '工作', '工作', '工作', '工作', '工作', '工作', '工作', '工作', '工作',
    '加班', '加班', '加班', '加班', '加班', '加班', '加班', '加班', '加班', '加班',
    '交通', '交通', '交通', '交通', '交通', '交通', '交通', '交通', '交通', '交通',
    '办公', '办公', '办公', '办公', '办公', '办公', '办公', '办公', '办公', '办公',
    '领导', '领导', '领导', '领导', '领导', '领导', '领导', '领导', '领导', '领导',
    '自动化', '自动化', '自动化', '自动化', '自动化', '自动化', '自动化', '自动化', '自动化', '自动化',
    '前端', '前端', '前端', '前端', '前端', '前端', '前端', '前端', '前端', '前端',
    '研发', '研发', '研发', '研发', '研发', '研发', '研发', '研发', '研发', '研发',
    '软件开发', '软件开发', '软件开发', '软件开发', '软件开发', '软件开发', '软件开发', '软件开发', '软件开发', '软件开发',
    '编程', '编程', '编程', '编程', '编程', '编程', '编程', '编程', '编程', '编程',
    '代码', '代码', '代码', '代码', '代码', '代码', '代码', '代码', '代码', '代码',
    '售后', '售后', '售后', '售后', '售后', '售后', '售后', '售后', '售后', '售后',
    '售前', '售前', '售前', '售前', '售前', '售前', '售前', '售前', '售前', '售前',
    '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理',
    '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理',
    '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动',
    '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维',
    '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责',
    '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题',
    '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持',
    '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关',
    '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件',
    '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件',
    '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统',
    '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品',
    '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机',
    '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库',
    '算法', '算法', '算法', '算法', '算法', '算法', '算法', '算法', '算法', '算法',
    '架构', '架构', '架构', '架构', '架构', '架构', '架构', '架构', '架构', '架构',
    '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型',
    '运维', '运维', '运维', '运维', '运维', '运维', '运维', '运维', '运维', '运维',
    '控制', '控制', '控制', '控制', '控制', '控制', '控制', '控制', '控制', '控制',
    '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师',
    '资格', '资格', '资格', '资格', '资格', '资格', '资格', '资格', '资格', '资格',
    '补助', '补助', '补助', '补助', '补助', '补助', '补助', '补助', '补助', '补助',
    '体检', '体检', '体检', '体检', '体检', '体检', '体检', '体检', '体检', '体检',
    '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游',
    '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升',
    '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效',
    '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金',
    '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效',
    '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖',
    '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补',
    '双休', '双休', '双休', '双休', '双休', '双休', '双休', '双休', '双休', '双休',
    '免费', '免费', '免费', '免费', '免费', '免费', '免费', '免费', '免费', '免费',
    '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴',
    '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪',
    '周末', '周末', '周末', '周末', '周末', '周末', '周末', '周末', '周末', '周末',
    '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障',
    '模型', '模型', '模型', '模型', '模型', '模型', '模型', '模型', '模型', '模型',
    '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障',
    '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯',
    '电路', '电路', '电路', '电路', '电路', '电路', '电路', '电路', '电路', '电路',
    '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片',
    '电力', '电力', '电力', '电力', '电力', '电力', '电力', '电力', '电力', '电力',
    '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型',
    '证书', '证书', '证书', '证书', '证书', '证书', '证书', '证书', '证书', '证书',
    '经验', '经验', '经验', '经验', '经验', '经验', '经验', '经验', '经验', '经验',
    '学历', '学历', '学历', '学历', '学历', '学历', '学历', '学历', '学历', '学历',
    # 更多非技术词
    '研发', '研发', '研发', '研发', '研发', '研发', '研发', '研发', '研发', '研发',
    '编程', '编程', '编程', '编程', '编程', '编程', '编程', '编程', '编程', '编程',
    '代码', '代码', '代码', '代码', '代码', '代码', '代码', '代码', '代码', '代码',
    '售后', '售后', '售后', '售后', '售后', '售后', '售后', '售后', '售后', '售后',
    '售前', '售前', '售前', '售前', '售前', '售前', '售前', '售前', '售前', '售前',
    '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理', '项目管理',
    '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理', '项目经理',
    '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动', '积极主动',
    '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维', '逻辑思维',
    '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责', '认真负责',
    '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题', '解决问题',
    '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持', '技术支持',
    '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关', '计算机相关',
    '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件', '嵌入式软件',
    '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件', '嵌入式硬件',
    '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统', '嵌入式系统',
    '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品',
    '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机', '计算机',
    '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库', '数据库',
    '算法', '算法', '算法', '算法', '算法', '算法', '算法', '算法', '算法', '算法',
    '架构', '架构', '架构', '架构', '架构', '架构', '架构', '架构', '架构', '架构',
    '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型', '选型',
    '运维', '运维', '运维', '运维', '运维', '运维', '运维', '运维', '运维', '运维',
    '控制', '控制', '控制', '控制', '控制', '控制', '控制', '控制', '控制', '控制',
    '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师',
    '资格', '资格', '资格', '资格', '资格', '资格', '资格', '资格', '资格', '资格',
    '补助', '补助', '补助', '补助', '补助', '补助', '补助', '补助', '补助', '补助',
    '体检', '体检', '体检', '体检', '体检', '体检', '体检', '体检', '体检', '体检',
    '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游', '旅游',
    '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升', '晋升',
    '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效', '绩效',
    '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金', '奖金',
    '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖', '年终奖',
    '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补', '餐补',
    '双休', '双休', '双休', '双休', '双休', '双休', '双休', '双休', '双休', '双休',
    '免费', '免费', '免费', '免费', '免费', '免费', '免费', '免费', '免费', '免费',
    '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴', '补贴',
    '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪', '带薪',
    '周末', '周末', '周末', '周末', '周末', '周末', '周末', '周末', '周末', '周末',
    '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障', '故障',
    '模型', '模型', '模型', '模型', '模型', '模型', '模型', '模型', '模型', '模型',
    '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯', '通讯',
    '电路', '电路', '电路', '电路', '电路', '电路', '电路', '电路', '电路', '电路',
    '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片', '芯片',
    '电力', '电力', '电力', '电力', '电力', '电力', '电力', '电力', '电力', '电力',
    '证书', '证书', '证书', '证书', '证书', '证书', '证书', '证书', '证书', '证书',
    '经验', '经验', '经验', '经验', '经验', '经验', '经验', '经验', '经验', '经验',
    '学历', '学历', '学历', '学历', '学历', '学历', '学历', '学历', '学历', '学历',
    '五险', '五险', '五险', '五险', '五险', '五险', '五险', '五险', '五险', '五险',
    '一金', '一金', '一金', '一金', '一金', '一金', '一金', '一金', '一金', '一金',
    '五险', '五险', '五险', '五险', '五险', '五险', '五险', '五险', '五险', '五险',
    '一金', '一金', '一金', '一金', '一金', '一金', '一金', '一金', '一金', '一金',
    '马克', '马克', '马克', '马克', '马克', '马克', '马克', '马克', '马克', '马克',
    '定义', '定义', '定义', '定义', '定义', '定义', '定义', '定义', '定义', '定义',
    '按时', '按时', '按时', '按时', '按时', '按时', '按时', '按时', '按时', '按时',
    '不断', '不断', '不断', '不断', '不断', '不断', '不断', '不断', '不断', '不断',
    '清晰', '清晰', '清晰', '清晰', '清晰', '清晰', '清晰', '清晰', '清晰', '清晰',
    '承受', '承受', '承受', '承受', '承受', '承受', '承受', '承受', '承受', '承受',
    '页面', '页面', '页面', '页面', '页面', '页面', '页面', '页面', '页面', '页面',
    '出现', '出现', '出现', '出现', '出现', '出现', '出现', '出现', '出现', '出现',
    '来源', '来源', '来源', '来源', '来源', '来源', '来源', '来源', '来源', '来源',
    '通过', '通过', '通过', '通过', '通过', '通过', '通过', '通过', '通过', '通过',
    'cn', 'cn', 'cn', 'cn', 'cn', 'cn', 'cn', 'cn', 'cn', 'cn',
    'CN', 'CN', 'CN', 'CN', 'CN', 'CN', 'CN', 'CN', 'CN', 'CN',
    '30', '30', '30', '30', '30', '30', '30', '30', '30', '30',
    '10', '10', '10', '10', '10', '10', '10', '10', '10', '10',
    '00', '00', '00', '00', '00', '00', '00', '00', '00', '00',
    '落地', '落地', '落地', '落地', '落地', '落地', '落地', '落地', '落地', '落地',
    '现有', '现有', '现有', '现有', '现有', '现有', '现有', '现有', '现有', '现有',
    '公众', '公众', '公众', '公众', '公众', '公众', '公众', '公众', '公众', '公众',
    '各项', '各项', '各项', '各项', '各项', '各项', '各项', '各项', '各项', '各项',
    '应急', '应急', '应急', '应急', '应急', '应急', '应急', '应急', '应急', '应急',
    '其它', '其它', '其它', '其它', '其它', '其它', '其它', '其它', '其它', '其它',
    '详细', '详细', '详细', '详细', '详细', '详细', '详细', '详细', '详细', '详细',
    '针对', '针对', '针对', '针对', '针对', '针对', '针对', '针对', '针对', '针对',
    '每年', '每年', '每年', '每年', '每年', '每年', '每年', '每年', '每年', '每年',
    '具体', '具体', '具体', '具体', '具体', '具体', '具体', '具体', '具体', '具体',
    '强烈', '强烈', '强烈', '强烈', '强烈', '强烈', '强烈', '强烈', '强烈', '强烈',
    'www', 'www', 'www', 'www', 'www', 'www', 'www', 'www', 'www', 'www',
])

filtered_words = [w for w in words if len(w) >= 2 and w not in stop_words]

# 将"五险"和"一金"合并为"五险一金"
filtered_words_str = ' '.join(filtered_words)
filtered_words_str = re.sub(r'五险\s*一金', '五险一金', filtered_words_str)
filtered_words_str = re.sub(r'五险\s+一金', '五险一金', filtered_words_str)
filtered_words = filtered_words_str.split()

# 统计词频
word_freq = Counter(filtered_words)
top_words = dict(word_freq.most_common(200))

# 生成词云
wc = WordCloud(
    font_path='C:/Windows/Fonts/simhei.ttf',
    background_color='white',
    max_words=200,
    max_font_size=100,
    min_font_size=10,
    width=800,
    height=600,
    random_state=42
)
wc.generate_from_frequencies(top_words)

fig_wc_skills, ax_wc_skills = plt.subplots(figsize=(12, 9))
ax_wc_skills.imshow(wc, interpolation='bilinear')
ax_wc_skills.axis('off')
ax_wc_skills.set_title('岗位技能需求词云', fontsize=18, fontweight='bold', pad=20)
save_wc(fig_wc_skills, '岗位技能', '01_技能需求词云.png')

# 3.2 Top 20 技能关键词柱状图
fig5, ax5 = plt.subplots(figsize=(12, 8))
top_20_words = dict(word_freq.most_common(20))
colors_words = plt.cm.RdYlBu(np.linspace(0.2, 0.8, len(top_20_words)))
bars_words = ax5.barh(range(len(top_20_words)), list(top_20_words.values())[::-1], 
                      color=colors_words[::-1], height=0.7)
ax5.set_yticks(range(len(top_20_words)))
ax5.set_yticklabels(list(top_20_words.keys())[::-1], fontsize=11)
ax5.set_xlabel('出现频次')
ax5.set_title('Top 20 岗位技能关键词', fontweight='bold', fontsize=14)
ax5.invert_yaxis()
for bar, val in zip(bars_words, list(top_20_words.values())[::-1]):
    ax5.text(val + 10, bar.get_y() + bar.get_height()/2, str(val),
             va='center', fontsize=10)
ax5.grid(axis='x', alpha=0.3)
plt.tight_layout()
save_fig(fig5, '岗位技能', '02_技能关键词Top20.png')

# ============================================================
# 4. 学历要求与工作经验分布
# ============================================================
print("\n" + "=" * 60)
print("【4】学历与经验分析")
print("=" * 60)

# 4.1 学历要求分布饼图
fig6a, ax6a = plt.subplots(figsize=(8, 8))
edu_counts = df['学历要求'].value_counts()
edu_order = ['初中及以下', '高中', '中专', '中技', '大专', '本科', '硕士', '博士', '学历不限']
edu_counts = edu_counts.reindex(edu_order).fillna(0)
# 移除值为0的类别
edu_counts = edu_counts[edu_counts > 0]
colors_edu = ['#ff6b6b', '#ffa06b', '#ffd56b', '#fff36b', '#6bffb3', '#6bdeff', '#9b6bff', '#ff6bde', '#c0c0c0']
wedges6, texts6, autotexts6 = ax6a.pie(edu_counts.values, labels=edu_counts.index,
                                        autopct='%1.1f%%', colors=colors_edu, startangle=90,
                                        textprops={'fontsize': 10})
for text in autotexts6:
    text.set_fontsize(10)
ax6a.set_title('学历要求分布', fontweight='bold', fontsize=14)
plt.tight_layout()
save_fig(fig6a, '学历经验', '01_学历要求分布.png')

# 4.2 经验要求分布
fig6b, ax6b = plt.subplots(figsize=(8, 8))
exp_counts = df['要求经验'].value_counts()
exp_order = ['1年以下', '1-3年', '3-5年', '5-10年', '10年以上', '经验不限']
exp_counts = exp_counts.reindex(exp_order).fillna(0)
# 移除值为0的类别
exp_counts = exp_counts[exp_counts > 0]
colors_exp = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
wedges7, texts7, autotexts7 = ax6b.pie(exp_counts.values, labels=exp_counts.index,
                                        autopct='%1.1f%%', colors=colors_exp, startangle=90,
                                        textprops={'fontsize': 10})
for text in autotexts7:
    text.set_fontsize(10)
ax6b.set_title('经验要求分布', fontweight='bold', fontsize=14)
plt.tight_layout()
save_fig(fig6b, '学历经验', '02_经验要求分布.png')

# 4.3 学历 × 薪资箱线图
fig6c, ax6c = plt.subplots(figsize=(10, 6))
edu_salary_data = []
edu_labels = []
for edu in ['大专', '本科', '硕士', '博士']:
    subset = df[df['学历要求'] == edu]['平均月薪']
    if len(subset) > 0:
        edu_salary_data.append(subset.values)
        edu_labels.append(edu)

bp2 = ax6c.boxplot(edu_salary_data, tick_labels=edu_labels, patch_artist=True, notch=True)
colors_edu_box = ['#6bffb3', '#6bdeff', '#9b6bff', '#ff6bde']
for patch, color in zip(bp2['boxes'], colors_edu_box):
    patch.set_facecolor(color)
ax6c.set_ylabel('平均月薪 (元)')
ax6c.set_title('学历 vs 薪资分布', fontweight='bold', fontsize=14)
ax6c.grid(axis='y', alpha=0.3)
plt.tight_layout()
save_fig(fig6c, '学历经验', '03_学历vs薪资.png')

# 4.4 经验 × 薪资箱线图
fig6d, ax6d = plt.subplots(figsize=(10, 6))
exp_salary_data = []
exp_labels = []
for exp in ['1年以下', '1-3年', '3-5年', '5-10年', '10年以上']:
    subset = df[df['要求经验'] == exp]['平均月薪']
    if len(subset) > 0:
        exp_salary_data.append(subset.values)
        exp_labels.append(exp)

bp3 = ax6d.boxplot(exp_salary_data, tick_labels=exp_labels, patch_artist=True, notch=True)
colors_exp_box = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
for patch, color in zip(bp3['boxes'], colors_exp_box):
    patch.set_facecolor(color)
ax6d.set_ylabel('平均月薪 (元)')
ax6d.set_title('经验 vs 薪资分布', fontweight='bold', fontsize=14)
ax6d.grid(axis='y', alpha=0.3)
plt.tight_layout()
save_fig(fig6d, '学历经验', '04_经验vs薪资.png')

# ============================================================
# 5. 行业技术热点分析
# ============================================================
print("\n" + "=" * 60)
print("【5】行业技术热点分析")
print("=" * 60)

# 5.1 行业技术热点 - 各行业岗位数量分布
fig7a, ax7a = plt.subplots(figsize=(10, 8))
industry_job_counts = df['行业类型'].value_counts().sort_values(ascending=False)
colors_hot = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(industry_job_counts)))
bars7 = ax7a.barh(range(len(industry_job_counts)), industry_job_counts.values,
                  color=colors_hot, height=0.7)
ax7a.set_yticks(range(len(industry_job_counts)))
ax7a.set_yticklabels(industry_job_counts.index, fontsize=9)
ax7a.set_xlabel('岗位数量')
ax7a.set_title('各行业岗位数量分布', fontweight='bold', fontsize=14)
ax7a.invert_yaxis()
for bar, val in zip(bars7, industry_job_counts.values):
    ax7a.text(val + 20, bar.get_y() + bar.get_height()/2, str(val),
             va='center', fontsize=8)
ax7a.grid(axis='x', alpha=0.3)
plt.tight_layout()
save_fig(fig7a, '行业技术', '01_各行业岗位数量分布.png')

# 5.2 行业技术热点 - Top 20 技术关键词热度
fig7b, ax7b = plt.subplots(figsize=(10, 8))
tech_keywords = [
    'Java', 'Python', 'C++', 'JavaScript', 'Go', 'PHP', 'C#',
    'Vue', 'React', 'Angular', 'Spring', 'SpringBoot', 'SpringCloud',
    'MySQL', 'Oracle', 'Redis', 'MongoDB', 'ElasticSearch',
    'Docker', 'Kubernetes', 'Linux', 'Windows',
    '微服务', '分布式', '云计算', '大数据', '人工智能', 'AI',
    '机器学习', '深度学习', '神经网络', '数据挖掘',
    '前端', '后端', '全栈', '移动开发', 'Android', 'iOS',
    '嵌入式', '硬件', '电路设计', 'PCB',
    '算法', '数据结构', '设计模式', '面向对象',
    '测试', '自动化测试', 'DevOps', 'CI/CD',
    '网络安全', '信息安全', '区块链',
    '物联网', 'IoT', '5G',
    'HTML', 'CSS', 'jQuery', 'Bootstrap',
    'MyBatis', 'Dubbo', 'Kafka', 'RabbitMQ', 'Nginx',
    'Git', 'Maven', 'Gradle',
    'FPGA', 'ARM', 'STM32', '单片机',
    'TCP/IP', 'HTTP', 'WebSocket',
    'TensorFlow', 'PyTorch', 'OpenCV',
]

# 统计技术关键词出现频次
tech_freq = {}
all_descriptions = ' '.join(df['职位描述'].dropna().tolist())
desc_words = jieba.lcut(all_descriptions)
for tech in tech_keywords:
    count = desc_words.count(tech) + all_descriptions.count(tech)
    if count > 0:
        tech_freq[tech] = count

top_tech = dict(sorted(tech_freq.items(), key=lambda x: x[1], reverse=True)[:20])

if top_tech:
    colors_tech = plt.cm.hot(np.linspace(0.2, 0.8, len(top_tech)))
    bars_tech = ax7b.barh(range(len(top_tech)), list(top_tech.values())[::-1],
                          color=colors_tech[::-1], height=0.7)
    ax7b.set_yticks(range(len(top_tech)))
    ax7b.set_yticklabels(list(top_tech.keys())[::-1], fontsize=10)
    ax7b.set_xlabel('出现频次')
    ax7b.set_title('Top 20 技术关键词热度', fontweight='bold', fontsize=14)
    ax7b.invert_yaxis()
    for bar, val in zip(bars_tech, list(top_tech.values())[::-1]):
        ax7b.text(val + 5, bar.get_y() + bar.get_height()/2, str(val),
                 va='center', fontsize=8)
    ax7b.grid(axis='x', alpha=0.3)
plt.tight_layout()
save_fig(fig7b, '行业技术', '02_技术关键词热度.png')

# 5.3 技术热点词云
# 词云使用所有技术关键词（不限 20 个）
wc_tech = WordCloud(
    font_path='C:/Windows/Fonts/simhei.ttf',
    background_color='white',
    max_words=200,
    max_font_size=120,
    min_font_size=12,
    width=800,
    height=600,
    random_state=42,
    prefer_horizontal=0.6,
    scale=4,
    relative_scaling=0.3,
    collocations=True
)
wc_tech.generate_from_frequencies(tech_freq)

fig_wc_tech, ax_wc_tech = plt.subplots(figsize=(12, 9))
ax_wc_tech.imshow(wc_tech, interpolation='bilinear')
ax_wc_tech.axis('off')
ax_wc_tech.set_title('行业技术热点词云', fontsize=18, fontweight='bold', pad=20)
save_wc(fig_wc_tech, '行业技术', '03_技术热点词云.png')

# 5.3b 招聘职位关键词词云
job_titles = df['招聘岗位'].dropna().tolist()
all_job_text = ' '.join(job_titles)
job_words = jieba.lcut(all_job_text)

# 过滤停用词
job_stop_words = set([
    '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师', '工程师',
    '软件', '软件', '软件', '软件', '软件', '软件', '软件', '软件', '软件', '软件',
    '开发', '开发', '开发', '开发', '开发', '开发', '开发', '开发', '开发', '开发',
    '设计', '设计', '设计', '设计', '设计', '设计', '设计', '设计', '设计', '设计',
    '技术', '技术', '技术', '技术', '技术', '技术', '技术', '技术', '技术', '技术',
    '管理', '管理', '管理', '管理', '管理', '管理', '管理', '管理', '管理', '管理',
    '分析', '分析', '分析', '分析', '分析', '分析', '分析', '分析', '分析', '分析',
    '系统', '系统', '系统', '系统', '系统', '系统', '系统', '系统', '系统', '系统',
    '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品', '产品',
    '项目', '项目', '项目', '项目', '项目', '项目', '项目', '项目', '项目', '项目',
    '服务', '服务', '服务', '服务', '服务', '服务', '服务', '服务', '服务', '服务',
    '运营', '运营', '运营', '运营', '运营', '运营', '运营', '运营', '运营', '运营',
    '助理', '助理', '助理', '助理', '助理', '助理', '助理', '助理', '助理', '助理',
    '专员', '专员', '专员', '专员', '专员', '专员', '专员', '专员', '专员', '专员',
    '主管', '主管', '主管', '主管', '主管', '主管', '主管', '主管', '主管', '主管',
    '经理', '经理', '经理', '经理', '经理', '经理', '经理', '经理', '经理', '经理',
    '总监', '总监', '总监', '总监', '总监', '总监', '总监', '总监', '总监', '总监',
    '人员', '人员', '人员', '人员', '人员', '人员', '人员', '人员', '人员', '人员',
    '代表', '代表', '代表', '代表', '代表', '代表', '代表', '代表', '代表', '代表',
    '顾问', '顾问', '顾问', '顾问', '顾问', '顾问', '顾问', '顾问', '顾问', '顾问',
    '实习', '实习', '实习', '实习', '实习', '实习', '实习', '实习', '实习', '实习',
    '兼职', '兼职', '兼职', '兼职', '兼职', '兼职', '兼职', '兼职', '兼职', '兼职',
    '全职', '全职', '全职', '全职', '全职', '全职', '全职', '全职', '全职', '全职',
    '高级', '高级', '高级', '高级', '高级', '高级', '高级', '高级', '高级', '高级',
    '初级', '初级', '初级', '初级', '初级', '初级', '初级', '初级', '初级', '初级',
    '资深', '资深', '资深', '资深', '资深', '资深', '资深', '资深', '资深', '资深',
    '专家', '专家', '专家', '专家', '专家', '专家', '专家', '专家', '专家', '专家',
    '岗位', '岗位', '岗位', '岗位', '岗位', '岗位', '岗位', '岗位', '岗位', '岗位',
])
job_filtered_words = [w for w in job_words if len(w) >= 2 and w not in job_stop_words]
job_word_freq = Counter(job_filtered_words)
job_top_words = dict(job_word_freq.most_common(150))

wc_job = WordCloud(
    font_path='C:/Windows/Fonts/simhei.ttf',
    background_color='white',
    max_words=150,
    max_font_size=100,
    min_font_size=14,
    width=800,
    height=600,
    random_state=42
)
wc_job.generate_from_frequencies(job_top_words)

fig_wc_job, ax_wc_job = plt.subplots(figsize=(12, 9))
ax_wc_job.imshow(wc_job, interpolation='bilinear')
ax_wc_job.axis('off')
ax_wc_job.set_title('招聘职位关键词词云', fontsize=18, fontweight='bold', pad=20)
save_wc(fig_wc_job, '岗位技能', '03_招聘职位关键词词云.png')

# 5.3c 福利待遇词云
benefit_keywords = [
    '五险一金', '年终奖', '带薪年假', '绩效奖金', '全勤奖',
    '交通补助', '餐补', '房补', '通讯补贴', '加班补助',
    '高温补贴', '节日福利', '生日福利', '定期体检',
    '员工旅游', '免费班车', '免费食宿', '包吃住', '包住', '包吃',
    '双休', '周末双休', '单休', '弹性工作', '不加班', '加班费',
    '股票期权', '股权', '分红', '提成',
    '培训', '晋升', '发展空间', '职业规划', '导师',
    '下午茶', '零食', '健身房', '团建', '旅游',
    '补充医疗保险', '补充公积金', '企业年金',
    '产假', '陪产假', '育儿假', '婚假', '丧假',
    '六险二金', '补充商业保险',
    '周末双休', '早九晚六', '朝九晚五', '不打卡',
    '扁平管理', '氛围好', '团队', '技术氛围',
    '餐补', '车补', '话补', '住房补贴',
    '13薪', '14薪', '15薪', '16薪', '年终奖',
    '项目奖金', '季度奖金', '半年奖', '年度奖金',
    '免费体检', '年度体检', '健康检查',
    '带薪休假', '年假', '调休',
    '弹性工作制', '远程办公', '居家办公',
]

all_descriptions2 = ' '.join(df['职位描述'].dropna().tolist())
benefit_freq = {}
for kw in benefit_keywords:
    count = all_descriptions2.count(kw)
    if count > 0:
        benefit_freq[kw] = count

if benefit_freq:
    wc_benefit = WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf',
        background_color='white',
        max_words=200,
        max_font_size=120,
        min_font_size=12,
        width=800,
        height=600,
        random_state=42,
        prefer_horizontal=0.6,
        scale=4,
        relative_scaling=0.3,
        collocations=True
    )
    wc_benefit.generate_from_frequencies(benefit_freq)

    fig_wc_benefit, ax_wc_benefit = plt.subplots(figsize=(12, 9))
    ax_wc_benefit.imshow(wc_benefit, interpolation='bilinear')
    ax_wc_benefit.axis('off')
    ax_wc_benefit.set_title('福利待遇关键词词云', fontsize=18, fontweight='bold', pad=20)
    save_wc(fig_wc_benefit, '行业技术', '04_福利待遇词云.png')

# 5.5 招聘类别分布
fig8, ax8 = plt.subplots(figsize=(8, 6))
cat_counts = df['招聘类别'].value_counts()
colors_cat = ['#66b3ff', '#99ff99', '#ffcc99', '#ffb3e6']
wedges8, texts8, autotexts8 = ax8.pie(cat_counts.values, labels=cat_counts.index,
                                       autopct='%1.1f%%', colors=colors_cat, startangle=90,
                                       textprops={'fontsize': 10})
for text in autotexts8:
    text.set_fontsize(10)
ax8.set_title('招聘类别分布', fontweight='bold', fontsize=14)
plt.tight_layout()
save_fig(fig8, '招聘类别', '01_招聘类别分布.png')

# ============================================================
# 6. 新增高级分析图表
# ============================================================
print("\n" + "=" * 60)
print("【6】高级分析可视化")
print("=" * 60)

# 6.1 技术方向时间趋势图（按月统计）
print("\n生成技术方向时间趋势图（按月）...")
tech_trend_keywords = ['Java', 'Python', 'C++', 'JavaScript', 'Go', '前端', '后端', '嵌入式', '算法', '测试']

# 按月份统计各技术关键词出现次数
date_col = '招聘发布日期'
if date_col in df.columns:
    # 转换为日期格式
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    # 提取年月
    df['招聘年月'] = df[date_col].dt.to_period('M')
    
    # 过滤数据量过少的月份（至少10条记录）
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
        
        # 格式化 x 轴标签为 YYYY-MM
        month_labels = [str(m) for m in months]
        x_pos = range(len(months))
        
        fig_trend, ax_trend = plt.subplots(figsize=(14, 7))
        colors_trend = plt.cm.tab10(np.linspace(0, 1, len(tech_trend_keywords)))
        for i, (tech, counts) in enumerate(trend_data.items()):
            ax_trend.plot(x_pos, counts, marker='o', linewidth=2, label=tech, color=colors_trend[i], markersize=6)
        ax_trend.set_xticks(x_pos)
        ax_trend.set_xticklabels(month_labels, rotation=45, ha='right', fontsize=9)
        ax_trend.set_xlabel('月份')
        ax_trend.set_ylabel('出现频次')
        ax_trend.set_title('各技术方向招聘市场月度趋势', fontweight='bold', fontsize=14)
        ax_trend.legend(fontsize=10, ncol=2)
        ax_trend.grid(alpha=0.3)
        plt.tight_layout()
        save_fig(fig_trend, '趋势分析', '01_技术方向月度趋势.png')
        
        print(f"  (有效月份: {', '.join(month_labels)})")
    else:
        print("  [!] 无有效月份数据，跳过时间趋势图")
    
    # 清理临时列
    df.drop(columns=['招聘年月'], inplace=True, errors='ignore')
else:
    print(f"  [!] 缺少{date_col}字段，跳过时间趋势图")

# 6.2 岗位-技能出现频率热力图
print("\n生成岗位-技能热力图...")
# 提取 Top 15 岗位和 Top 20 技能
top_positions = df['招聘岗位'].value_counts().head(15).index.tolist()
# 使用之前的技术关键词
heatmap_skills = ['Java', 'Python', 'C++', 'JavaScript', 'Go', 'Spring', 'MySQL', 
                  'Redis', 'Linux', 'Docker', 'Vue', 'React', '算法', '测试', 
                  '嵌入式', '硬件', 'PCB', 'FPGA', '前端', '后端']

# 构建岗位-技能矩阵
pos_skill_matrix = pd.DataFrame(0, index=top_positions, columns=heatmap_skills)
for idx, row in df.iterrows():
    pos = row['招聘岗位']
    if pos in top_positions:
        desc = str(row['职位描述'])
        for skill in heatmap_skills:
            if skill in desc:
                pos_skill_matrix.loc[pos, skill] += 1

# 归一化
pos_skill_norm = pos_skill_matrix.div(pos_skill_matrix.sum(axis=1), axis=0) * 100

fig_heatmap, ax_heatmap = plt.subplots(figsize=(14, 10))
sns.heatmap(pos_skill_norm, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax_heatmap, 
            linewidths=0.5, cbar_kws={'label': '技能提及占比 (%)'},
            annot_kws={'fontsize': 7})
ax_heatmap.set_title('岗位-技能出现频率热力图', fontweight='bold', fontsize=14)
ax_heatmap.tick_params(axis='x', rotation=45, labelsize=9)
ax_heatmap.tick_params(axis='y', labelsize=8)
plt.tight_layout()
save_fig(fig_heatmap, '技能分析', '02_岗位技能热力图.png')

# 6.3 KMeans 聚类 + 降维展示
print("\n生成岗位描述聚类降维图...")
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# 取前 1000 条岗位描述（避免内存过大）
sample_size = min(1000, len(df))
sample_df = df.sample(sample_size, random_state=42).copy()
sample_df = sample_df.dropna(subset=['职位描述'])
descriptions = sample_df['职位描述'].tolist()
positions = sample_df['招聘岗位'].tolist()

if len(descriptions) > 0:
    # TF-IDF 向量化
    tfidf = TfidfVectorizer(max_features=500, stop_words=['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])
    X_tfidf = tfidf.fit_transform(descriptions)
    
    # KMeans 聚类
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_tfidf)
    
    # PCA 降维到 2D
    pca = PCA(n_components=2, random_state=42)
    X_2d = pca.fit_transform(X_tfidf.toarray())
    
    fig_cluster, ax_cluster = plt.subplots(figsize=(12, 9))
    colors_cluster = ['#ff6b6b', '#6bdeff', '#99ff99', '#ffd56b', '#9b6bff']
    
    for i in range(n_clusters):
        mask = cluster_labels == i
        ax_cluster.scatter(X_2d[mask, 0], X_2d[mask, 1], 
                          label=f'聚类 {i+1} (n={mask.sum()})',
                          alpha=0.7, s=30, color=colors_cluster[i], edgecolors='none')
    
    ax_cluster.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax_cluster.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax_cluster.set_title('岗位描述 KMeans 聚类 (PCA 降维)', fontweight='bold', fontsize=14)
    ax_cluster.legend(fontsize=10)
    ax_cluster.grid(alpha=0.3)
    plt.tight_layout()
    save_fig(fig_cluster, '聚类分析', '03_岗位描述聚类降维.png')
    
    # 显示各聚类的代表性岗位
    print("\n  各聚类代表性岗位：")
    for i in range(n_clusters):
        mask = cluster_labels == i
        cluster_positions = pd.Series(positions)[mask].value_counts().head(3)
        top_pos = ', '.join(cluster_positions.index.tolist())
        print(f"    聚类 {i+1}: {top_pos}")
else:
    print("  [!] 数据不足，跳过聚类分析")

# ============================================================
# 汇总报告
# ============================================================
print("\n" + "=" * 60)
print("数据可视化完成！")
print("=" * 60)
print(f"\n已生成图表文件（共25张，按分类存储）：")
print("  💰 薪资分析/ (6张)")
for i, name in enumerate([
    '01_Top15岗位平均月薪.png',
    '02_薪资等级分布.png',
    '03_各行业平均薪资.png',
    '04_薪资等级箱线图.png',
    '05_年终奖Top10行业.png',
    '06_月薪年终奖关系.png',
], 1):
    print(f"    {i}. 薪资分析/{name}")
print("  🏢 企业分析/ (4张)")
for i, name in enumerate([
    '01_工作城市分布.png',
    '02_行业类型分布.png',
    '03_企业规模分布.png',
    '04_城市行业热力图.png',
], 1):
    print(f"    {i}. 企业分析/{name}")
print("  🛠️ 岗位技能/ (3张)")
for i, name in enumerate([
    '01_技能需求词云.png',
    '02_技能关键词Top20.png',
    '03_招聘职位关键词词云.png',
], 1):
    print(f"    {i}. 岗位技能/{name}")
print("  🎓 学历经验/ (4张)")
for i, name in enumerate([
    '01_学历要求分布.png',
    '02_经验要求分布.png',
    '03_学历vs薪资.png',
    '04_经验vs薪资.png',
], 1):
    print(f"    {i}. 学历经验/{name}")
print("  🔥 行业技术/ (4张)")
for i, name in enumerate([
    '01_各行业岗位数量分布.png',
    '02_技术关键词热度.png',
    '03_技术热点词云.png',
    '04_福利待遇词云.png',
], 1):
    print(f"    {i}. 行业技术/{name}")
print("  📋 招聘类别/ (1张)")
for i, name in enumerate([
    '01_招聘类别分布.png',
], 1):
    print(f"    {i}. 招聘类别/{name}")
print("  📈 趋势分析/ (1张)")
for i, name in enumerate([
    '01_技术方向月度趋势.png',
], 1):
    print(f"    {i}. 趋势分析/{name}")
print("  🔍 技能分析/ (1张)")
for i, name in enumerate([
    '02_岗位技能热力图.png',
], 1):
    print(f"    {i}. 技能分析/{name}")
print("  🎯 聚类分析/ (1张)")
for i, name in enumerate([
    '03_岗位描述聚类降维.png',
], 1):
    print(f"    {i}. 聚类分析/{name}")

print(f"\n输出目录: {VIZ_BASE_DIR}")
