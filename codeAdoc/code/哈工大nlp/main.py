import pyltp
from pyltp import Segmentor
# 分词
def segmentor(sentence):
    cws_model_path = 'D:\application\pyltp\ltp_data_v3.4.0'
    segmentor = Segmentor()  # 初始化实例
    segmentor.load(cws_model_path)  # 加载模型
    # 使用分词外部词典
    segmentor.load_with_lexicon(cws_model_path, 'path to /segment_lexicon_6_2')  # 加载模型，第二个参数是外部词典文件路径
    words = segmentor.segment(sentence)  # 分词
    segmentor.release()  # 释放模型

if __name__ =="__main__":
    segmentor('元芳你怎么看？我就趴窗口上看呗！')  # 分句
