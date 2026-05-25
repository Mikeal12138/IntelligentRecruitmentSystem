import os
import jieba
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


# 内置默认停用词（与 stopwords.txt 互补）
_DEFAULT_STOPWORDS = {
    '的', '了', '是', '在', '和', '有', '为', '与', '及', '其', '对', '以',
    '于', '等', '能', '可', '也', '就', '都', '这', '那', '被', '到', '要',
    '将', '会', '从', '而', '但', '如', '如果', '因为', '所以', '当', '时',
    '中', '上', '下', '里', '外', '过', '还', '个', '之', '已', '者', '人',
    '公司', '企业', '我们', '相关', '经验', '熟悉', '具备', '一定', '了解',
    '掌握', '优先', '以上', '以下', '具有', '从事', '负责', '参与', '提供',
    '进行', '使用', '工作', '要求', '任职', '资格', '条件', '岗位', '职责',
    '待遇', '福利', '薪资', '工资', '保险', '公积金', '年假', '年终奖',
    '晋升', '培训', '发展', '机会', '团队', '部门', '业务', '产品', '服务',
    '技术', '专业', '基础', '能力', '素质', '良好', '优秀', '熟练', '精通',
    '开发', '设计', '管理', '支持', '维护', '运营', '分析', '研究', '优化',
    '完成', '实现', '解决', '处理', '执行', '推动', '协调', '沟通', '合作',
    '配合', '协助', '汇报', '总结', '计划', '组织', '安排', '监督', '检查',
    '评估', '考核', '标准', '规范', '流程', '制度', '体系', '平台', '系统',
    '工具', '软件', '硬件', '网络', '数据', '信息', '资源', '项目', '任务',
    '目标', '结果', '绩效', '指标', '方案', '策略', '方向', '思路', '方法',
    '方式', '手段', '技巧', '技能', '知识', '背景', '学历', '学位', '毕业',
    '学校', '专业', '本科', '硕士', '博士', '大专', '高中', '中专', '年',
    '月', '日', '左右', '大约', '约', '类', '型', '式', '级', '度', '量',
    '种', '面议', '待遇从优', '薪酬面议', '薪资面议', '五险一金', '双休',
    '带薪年假', '节日福利', '定期体检', '免费', '补助', '奖金', '全勤',
    '工龄', '股票', '期权', '弹性', '打卡', '扁平', '氛围', '等优先',
    '等相关', '等相关经验', '等岗位', '等工作', '以及', '或者', '并且',
    '同时', '另外', '此外', '其中', '包括', '包含', '无', '无需', '不限',
    '不限经验', '不限专业', '不限学历',
}


class NLPProcessor:
    def __init__(self, max_features=5000, ngram_range=(1, 2)):
        self.stopwords = set(_DEFAULT_STOPWORDS)
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            token_pattern=None,  # 使用自定义 tokenizer
            tokenizer=self._tokenizer,
            lowercase=False,
        )
        self._is_fitted = False

    def _tokenizer(self, text):
        """内部 token 化: jieba 分词 + 去停用词 + 过滤单字"""
        tokens = jieba.lcut(text)
        return [t for t in tokens if t not in self.stopwords and len(t) > 1]

    def load_stopwords(self, filepath: str):
        """从外部文件加载停用词表（追加到内置集合）"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        self.stopwords.add(word)
            print(f"  [NLP] 从 {filepath} 加载了额外停用词")
        else:
            print(f"  [NLP] 停用词文件不存在: {filepath}，使用内置停用词")

    def tokenize(self, text: str) -> list:
        """对单条文本分词 + 去停用词"""
        return self._tokenizer(text)

    def remove_stopwords(self, tokens: list) -> list:
        """从 token 列表中移除停用词"""
        return [t for t in tokens if t not in self.stopwords and len(t) > 1]

    def vectorize(self, texts: list):
        """将文本列表转换为 TF-IDF 矩阵"""
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts: list):
        """训练期: 拟合 vectorizer 并返回 TF-IDF 矩阵"""
        matrix = self.vectorizer.fit_transform(texts)
        self._is_fitted = True
        vocab_size = len(self.vectorizer.vocabulary_)
        print(f"  [NLP] TF-IDF 拟合完成: {len(texts)} 条文本, {vocab_size} 维特征")
        return matrix

    def transform(self, texts: list):
        """推理期: 使用已拟合的 vectorizer 转换新文本"""
        if not self._is_fitted:
            raise RuntimeError("Vectorizer 尚未拟合，请先调用 fit_transform()")
        return self.vectorizer.transform(texts)

    def get_feature_names(self):
        """返回 TF-IDF 特征名列表"""
        if not self._is_fitted:
            raise RuntimeError("Vectorizer 尚未拟合")
        return self.vectorizer.get_feature_names_out()

    def save(self, filepath: str):
        """保存 vectorizer 和 stopwords 到 pickle 文件"""
        data = {
            'vectorizer': self.vectorizer,
            'stopwords': self.stopwords,
            'is_fitted': self._is_fitted,
        }
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"  [NLP] 模型已保存至 {filepath}")

    def load(self, filepath: str):
        """从 pickle 文件加载 vectorizer 和 stopwords"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.vectorizer = data['vectorizer']
        self.stopwords = data['stopwords']
        self._is_fitted = data['is_fitted']
        print(f"  [NLP] 模型已从 {filepath} 加载")
