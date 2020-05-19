# -*- coding: utf-8 -*-

from gensim.models import word2vec
import logging

##训练word2vec模型

# 获取日志信息
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

# 加载分词后的文本，使用的是Text8Corpus类
sentences = word2vec.Text8Corpus(r'./data/manMachCutData/manMach.txt')

# 训练模型，部分参数如下
model = word2vec.Word2Vec(sentences, size=100, alpha=0.025, hs=1, min_count=1, window=2)

model.save(u'manMach.model')
# 对应的加载方式
# model2 = word2vec.Word2Vec.load('搜狗新闻.model')

# 以一种c语言可以解析的形式存储词向量
# model.save_word2vec_format(u"书评.model.bin", binary=True)
# 对应的加载方式
# model_3 =word2vec.Word2Vec.load_word2vec_format("text8.model.bin",binary=True)






