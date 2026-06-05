import pandas as pd
import os

# 数据文件路径
DATA_PATH = r'c:\Users\13309\Desktop\大实验\IntelligentRecruitmentSystem\data\cleaned_recruitment_data.csv'

print("=" * 60)
print("删除指定列脚本")
print("=" * 60)

# 读取数据
print("\n1. 读取数据...")
df = pd.read_csv(DATA_PATH)
print(f"原始列数: {len(df.columns)}")
print(f"原始数据形状: {df.shape}")
print(f"列名: {list(df.columns)}")

# 要删除的列
cols_to_drop = ['招聘发布年份', '来源', '招聘发布日期']

# 检查列是否存在
existing_cols = [col for col in cols_to_drop if col in df.columns]
non_existing = [col for col in cols_to_drop if col not in df.columns]

if existing_cols:
    print(f"\n2. 找到待删除列: {existing_cols}")
    if non_existing:
        print(f"   以下列不存在: {non_existing}")
    
    # 删除列
    df_clean = df.drop(columns=existing_cols)
    print(f"\n3. 删除后列数: {len(df_clean.columns)}")
    print(f"删除后数据形状: {df_clean.shape}")
    print(f"剩余列名: {list(df_clean.columns)}")
    
    # 保存到临时文件
    TEMP_PATH = DATA_PATH.replace('.csv', '_temp.csv')
    df_clean.to_csv(TEMP_PATH, index=False, encoding='utf-8-sig')
    print(f"\n4. 临时文件已保存至: {TEMP_PATH}")
    
    # 尝试替换原文件
    try:
        # 先删除原文件
        if os.path.exists(DATA_PATH):
            os.remove(DATA_PATH)
        # 重命名临时文件
        os.rename(TEMP_PATH, DATA_PATH)
        print(f"5. 原文件已替换完成！")
    except PermissionError:
        print(f"\n️ 原文件被占用，无法替换！")
        print(f"请手动操作：")
        print(f"1. 关闭所有打开该文件的程序（如 Excel）")
        print(f"2. 将 {TEMP_PATH} 重命名为 cleaned_recruitment_data.csv")
        print(f"3. 或者将 TEMP_PATH 的内容复制到原文件")
    print("\n处理完成！")
else:
    print(f"\n未找到待删除的列: {cols_to_drop}")
    print("当前列名:", list(df.columns))
