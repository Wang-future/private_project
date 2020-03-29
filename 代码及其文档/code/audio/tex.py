
from gensim.models import word2vec
import jieba
import numpy as np
from scipy.linalg import norm

class voiceModel():
    def __init__(self):
        self.model = word2vec.Word2Vec.load('voice.model')

    def sentence_vector(self, s):
        words = jieba.lcut(s)
        v = np.zeros(100)
        for word in words:
            v += self.model.wv[word]
        v /= len(words)
        return v

    def vector_similarity(self, s1, s2):
        v1, v2 = self.sentence_vector(s1), self.sentence_vector(s2)
        return np.dot(v1, v2) / (norm(v1) * norm(v2))
if __name__ == "__main__":
    mvoiceModel = voiceModel()
    senten1 = "我要关闭"
    senten2 = "我要部署"
    print(mvoiceModel.vector_similarity(senten1,senten2))
