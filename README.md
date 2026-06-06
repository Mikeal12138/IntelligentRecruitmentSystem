# IntelligentRecruitmentSystem 智能招聘系统

> 基于人工智能和机器学习的智能招聘分析与求职辅助平台

## 项目简介

IntelligentRecruitmentSystem 是一个综合性智能招聘系统，结合了机器学习、自然语言处理和大语言模型技术，为求职者和招聘方提供全流程的智能化服务。系统基于 15000+ 条真实招聘数据，包含数据可视化分析、岗位智能匹配、简历智能解析、薪资谈判辅助、面试辅助评估、劳动法律咨询等核心功能模块。

## 核心功能

### 1. 数据可视化大屏
- 多维度数据可视化（薪资分析、企业分析、学历经验、行业技术等）
- 薪资等级分布与行业薪资对比
- 城市分布与城市-行业热力图
- 支持按分类筛选图表

### 2. 岗位词云与需求分析
- 岗位技能需求词云
- 招聘职位关键词词云
- 行业技术热点词云
- 福利待遇关键词词云

### 3. 智能求职助手（AI 对话）
- 多轮对话记忆，自动构建用户求职档案
- 简历优化：基于目标岗位定制优化建议
- 面试模拟：支持 HR 面、技术面等多种类型
- 岗位推荐：基于 15000+ 条数据的智能匹配
- 职业规划与心理支持

### 4. 智能岗位搜索与筛选
- 自然语言搜索：用日常语言描述求职需求
- 智能条件提取：自动识别薪资、地点、经验、学历等条件
- 基于 TF-IDF 和余弦相似度的岗位匹配推荐
- 岗位收藏与多维度对比

### 5. 简历智能解析与评估
- 支持 PDF、Word、TXT 多格式上传
- 自动提取姓名、联系方式、教育背景、工作经历、技能等
- 完整性、匹配度、竞争力三维评分
- 基于大模型的详细优化建议

### 6. 薪资谈判助手
- 按岗位、城市、经验查询市场薪资范围
- 基于公司类型和岗位级别的定制谈判策略
- 多场景谈判话术模板
- 可争取的额外福利待遇分析

### 7. 面试辅助与评估
- 面试问题预测与准备
- 模拟面试与实时评估
- 面试表现分析与改进建议

### 8. 劳动法律咨询
- 劳动法相关问题智能问答
- 权益保障建议

### 9. 招聘数据导入数据库
- 支持 CSV 数据批量导入 MySQL 数据库

## 技术架构

### 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | Python 3.9+ |
| **Web 框架** | Streamlit |
| **机器学习** | Scikit-learn, PyTorch |
| **NLP** | Jieba, TF-IDF |
| **大模型** | OpenAI 兼容 API（通义千问） |
| **数据库** | MySQL, SQLite |
| **数据处理** | Pandas, NumPy |
| **可视化** | Matplotlib, Seaborn, Plotly, WordCloud |
| **PDF 解析** | pdfplumber, PyPDF2, pdfminer |

### 项目结构

```
IntelligentRecruitmentSystem/
├── app/                            # Streamlit 前端应用
│   ├── main.py                     # 主入口（登录 + 首页）
│   ├── viz_service.py              # 按需图表生成服务
│   ├── components/                 # 可复用组件
│   │   ├── auth.py                 # 用户认证模块
│   │   ├── auth_required.py        # 认证装饰器
│   │   └── plots.py                # 图表组件
│   └── pages/                      # 功能页面
│       ├── 01_📊_数据可视化大屏.py
│       ├── 02_☁️_岗位词云与需求.py
│       ├── 04_🤖_智能求职助手.py
│       ├── 05_🔍_智能岗位搜索与筛选.py
│       ├── 06_�_简历智能解析与评估.py
│       ├── 07_💰_薪资谈判助手.py
│       ├── 08_🤝_面试辅助与评估.py
│       ├── 09_⚖️_劳动法律咨询.py
│       └── 10_📊_招聘数据导入数据库.py
├── src/                            # 核心业务逻辑
│   ├── data_pipeline/              # 数据处理管道
│   │   ├── cleaner.py              # 数据清洗
│   │   ├── db_manager.py           # 数据库连接管理
│   │   └── nlp_processor.py        # NLP 文本处理
│   ├── llm_service/                # 大模型服务
│   │   ├── chat_api.py             # API 调用封装
│   │   ├── chat_assistant.py       # 对话助手
│   │   ├── interview_assistant.py  # 面试助手
│   │   ├── prompts.py              # Prompt 模板
│   │   ├── resume_parser.py        # 简历解析
│   │   └── salary_negotiator.py    # 薪资谈判
│   ├── ml_engine/                  # 机器学习引擎
│   │   ├── classifier.py           # 神经网络分类器
│   │   ├── cluster.py              # K-Means 聚类分析
│   │   ├── search_service.py       # TF-IDF 搜索服务
│   │   ├── trainer.py              # 模型训练流水线
│   │   └── visualizer.py           # 模型评估可视化
│   └── visualization/              # 可视化模块
│       ├── db_visualization.py     # 数据库可视化服务
│       └── visualization.py        # 图表生成
├── backend/                        # 数据库脚本
│   └── init_database.sql           # MySQL 建表 SQL
├── config/                         # 配置文件
│   └── config.yaml                 # 系统配置（模型超参数等）
├── data/                           # 数据目录
│   ├── raw/                        # 原始数据
│   ├── processed/                  # 清洗后数据
│   ├── text_features/              # 停用词等文本特征
│   ├── cleaned_recruitment_data.csv
│   ├── analysis_report.txt
│   └── users.db                    # SQLite 用户数据库
├── models/                         # 训练模型文件（.pkl）
├── visualization/                  # 生成的图表 PNG
│   ├── 薪资分析/
│   ├── 企业分析/
│   ├── 岗位技能/
│   ├── 学历经验/
│   ├── 行业技术/
│   ├── 技能分析/
│   ├── 聚类分析/
│   └── 招聘类别/
├── scripts/                        # 辅助脚本
│   ├── data_processing.py          # 数据清洗处理
│   ├── remove_columns.py           # 删除冗余列
│   ├── review_data.py              # 数据质量审查
│   └── init_users.py               # 初始化用户数据
├── data_visualization.py           # 可视化图表生成脚本
├── train_models.py                 # 模型训练入口
├── requirements.txt                # 依赖列表
├── .env.example                    # 环境变量模板
└── .gitignore
```

## 安装说明

### 环境要求

- Python 3.9+
- Anaconda（推荐）
- MySQL 8.0+（可选，支持 CSV 备选数据源）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-repo/IntelligentRecruitmentSystem.git
cd IntelligentRecruitmentSystem
```

2. **创建虚拟环境**
```bash
conda create -n pytorch python=3.9
conda activate pytorch
```

3. **安装 GPU 版 PyTorch（可选）**
```bash
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

4. **安装依赖**
```bash
pip install -r requirements.txt
```

5. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key 和数据库密码
```

### .env 配置

```env
# LLM API 配置（阿里云 DashScope）
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# MySQL 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=recruitment_db
```

## 快速开始

### 1. 初始化数据库（可选）

```bash
mysql -u root -p < backend/init_database.sql
python scripts/init_users.py
```

### 2. 训练模型

```bash
python train_models.py
```

### 3. 生成可视化图表

```bash
python data_visualization.py
```

### 4. 启动应用

```bash
cd app
streamlit run main.py
```

## 数据说明

系统基于 15000+ 条真实招聘数据进行分析，数据字段包含：

| 字段 | 说明 |
|------|------|
| 企业名称 | 招聘公司 |
| 招聘岗位 | 职位名称 |
| 工作城市 | 工作地点 |
| 最低月薪 / 最高月薪 / 平均月薪 | 薪资范围 |
| 职位描述 | 岗位详细要求 |
| 学历要求 | 最低学历门槛 |
| 要求经验 | 工作经验要求 |
| 企业规模 | 公司规模分类 |
| 行业类型 | 所属行业 |
| 薪资等级 | 薪资分级（5K以下 ~ 30K以上） |
| 年终奖估算 | 估算年终奖金额 |
| 招聘类别 | 全职/兼职等 |

## 安全说明

- API Key 和数据库密码存储在 `.env` 文件中，已添加到 `.gitignore`
- 不会上传任何敏感信息到代码仓库
- 推荐使用环境变量管理所有密钥

## 许可证

本项目仅供学习和研究使用。
