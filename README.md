# IntelligentRecruitmentSystem 智能招聘系统

> 基于人工智能和机器学习的智能招聘分析与求职辅助平台

## 📖 项目简介

IntelligentRecruitmentSystem 是一个综合性智能招聘系统，结合了机器学习、自然语言处理和大语言模型技术，为求职者和招聘方提供全流程的智能化服务。系统包含数据可视化分析、岗位智能匹配、简历智能解析、薪资谈判辅助、AI 对话助手等核心功能模块。

## 🎯 核心功能

### 1.  数据可视化大屏
- 招聘市场整体趋势分析
- 薪资分布可视化
- 行业需求统计
- 城市薪资对比
- 经验要求分布

### 2. ☁️ 岗位词云与需求分析
- 岗位技能词云生成
- 热门技能排行榜
- 行业关键词提取
- 岗位需求趋势分析

### 3. 🤖 智能求职助手（AI 对话）
- **多轮对话记忆**：自动构建用户求职档案
- **简历优化**：基于目标岗位定制优化建议
- **面试模拟**：支持 HR 面、技术面等多种类型
- **岗位推荐**：基于 15000+ 条数据的智能匹配
- **职业规划**：制定短期和长期发展计划
- **心理支持**：情绪识别与疏导

### 4. 🔍 智能岗位搜索与筛选
- **自然语言搜索**：用日常语言描述求职需求
- **智能条件提取**：自动识别薪资、地点、经验等条件
- **相似度推荐**：基于 TF-IDF 和余弦相似度的岗位推荐
- **收藏与对比**：支持岗位收藏和多维度对比

### 5. 📄 简历智能解析与评估
- **多格式支持**：PDF、Word、TXT 文件上传
- **自动信息提取**：姓名、联系方式、教育背景、工作经历、技能等
- **智能评分**：完整性、匹配度、竞争力三维评分
- **改进建议**：基于大模型的详细优化建议

### 6. 💰 薪资谈判助手
- **市场薪资查询**：按岗位、城市、经验查询薪资范围
- **谈判策略生成**：基于公司类型和岗位级别的定制策略
- **话术模板**：提供多种场景的谈判话术
- **福利分析**：分析可争取的额外福利待遇

## 🛠️ 技术架构

### 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | Python 3.9+ |
| **Web 框架** | Streamlit |
| **机器学习** | Scikit-learn, PyTorch |
| **NLP** | Jieba, TF-IDF |
| **大模型** | OpenAI 兼容 API（通义千问） |
| **数据处理** | Pandas, NumPy |
| **可视化** | Matplotlib, Seaborn, Plotly |
| **词云** | WordCloud |
| **PDF 解析** | pdfplumber, PyPDF2, pdfminer |

### 项目结构

```
IntelligentRecruitmentSystem/
├── app/                        # 前端应用
│   ├── main.py                 # 主入口
│   ├── components/             # 可复用组件
│   │   ├── auth.py             # 认证模块
│   │   └── plots.py            # 图表组件
│   ├── pages/                  # 页面模块
│   │   ├── 01_📊_数据可视化大屏.py
│   │   ├── 02_☁️_岗位词云与需求.py
│   │   ├── 04_🤖_智能求职助手.py
│   │   ├── 05_🔍_智能岗位搜索与筛选.py
│   │   ├── 06_📄_简历智能解析与评估.py
│   │   ── 07_💰_薪资谈判助手.py
│   └── utils/                  # 工具函数
├── src/                        # 后端服务
│   ├── data_pipeline/          # 数据处理管道
│   │   ├── cleaner.py          # 数据清洗
│   │   ── nlp_processor.py    # NLP 处理
│   ├── llm_service/            # 大模型服务
│   │   ├── chat_assistant.py   # 对话助手
│   │   ├── resume_parser.py    # 简历解析
│   │   └── salary_negotiator.py # 薪资谈判
│   ├── ml_engine/              # 机器学习引擎
│   │   ├── classifier.py       # 分类器
│   │   ├── cluster.py          # 聚类分析
│   │   ├── search_service.py   # 搜索服务
│   │   └── trainer.py          # 模型训练
│   └── visualization/          # 可视化模块
├── data/                       # 数据目录
│   ├── raw/                    # 原始数据
│   └── processed/              # 处理后数据
├── models/                     # 模型文件
│   └── figures/                # 模型评估图表
├── config/                     # 配置文件
│   ├── config.yaml             # 系统配置
│   └── .env.example            # 环境变量模板
├── train_models.py             # 模型训练入口
└── requirements.txt            # 依赖列表
```

## 📦 安装说明

### 环境要求

- Python 3.9+
- Anaconda（推荐）
- Windows/Linux/MacOS

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
cp config/.env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### .env 配置

```env
LLM_API_KEY=your_api_key_here
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

## 🚀 快速开始

### 启动主应用

```bash
cd app
streamlit run main.py
```

### 启动独立模块

**简历解析模块**
```bash
python start_resume_parser.py
# 访问 http://localhost:8501
```

**薪资谈判模块**
```bash
python start_salary_negotiator.py
# 访问 http://localhost:8503
```

**智能求职助手**
```bash
python start_chat_assistant.py
# 访问 http://localhost:8504
```

### 训练模型

```bash
python train_models.py
```

## 📚 模块详细说明

### 数据处理管道 (src/data_pipeline/)

- **cleaner.py**: 数据清洗、去重、缺失值处理
- **nlp_processor.py**: 文本分词、特征提取、词频统计

### 机器学习引擎 (src/ml_engine/)

- **classifier.py**: 岗位分类、薪资预测神经网络
- **cluster.py**: K-Means 聚类分析
- **search_service.py**: 基于 TF-IDF 的语义搜索
- **trainer.py**: 模型训练流水线
- **visualizer.py**: 模型评估可视化

### 大模型服务 (src/llm_service/)

- **chat_assistant.py**: 多轮对话 AI 助手
- **resume_parser.py**: 简历解析与评估
- **salary_negotiator.py**: 薪资谈判策略生成

### 可视化模块 (src/visualization/)

- 交互式图表生成
- 数据大屏渲染
- 词云生成

## 🔒 安全说明

- API Key 存储在 `.env` 文件中，已添加到 `.gitignore`
- 不会上传任何敏感信息到代码仓库
- 推荐使用环境变量管理所有密钥

## 📊 数据说明

系统基于 15000+ 条真实招聘数据进行分析和训练，数据包含：

- 企业名称
- 招聘岗位
- 工作城市
- 薪资范围（最低/最高/平均）
- 职位描述
- 学历要求
- 经验要求
- 企业规模
- 行业类型

##  贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目仅供学习和研究使用。

## 📧 联系方式

如有问题或建议，欢迎联系：

- Email: your-email@example.com
- GitHub: https://github.com/your-repo

---

**IntelligentRecruitmentSystem** - 让求职更智能，让招聘更高效
