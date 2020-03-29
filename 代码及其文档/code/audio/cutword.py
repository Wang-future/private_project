# -*-coding:utf-8 -*-

import jieba.analyse
import jieba
import os

raw_data_path = './data/voice_data/'

cut_data_path = './data/voice_cutdata/'

stop_word_path = './data/voice_cutdata/stopwords.txt'


def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'rb').readlines()]
    return stopwords


def cut_word(raw_data_path, cut_data_path):
    data_file_list = os.listdir(raw_data_path)

    corpus = ''

    temp = 0

    for file in data_file_list:
        with open(raw_data_path + file, 'rb') as f:
            print(temp + 1)
            temp += 1
            document = f.read()
            document_cut = jieba.cut(document, cut_all=False)
            # print('/'.join(document_cut))
            result = ' '.join(document_cut)
            corpus += result

    with open(cut_data_path + 'corpus.txt', 'w+', encoding='utf-8') as f:

        f.write(corpus)  # 读取的方式和写入的方式要一致

    stopwords = stopwordslist(stop_word_path)  # 这里加载停用词的路径

    with open(cut_data_path + 'corpus.txt', 'r', encoding='utf-8') as f:

        document_cut = f.read()
        outstr = ''

        for word in document_cut:

            if word not in stopwords:
                if word != '\t':
                    outstr += word

                    outstr += " "

    with open(cut_data_path + 'corpus1.txt', 'w+', encoding='utf-8') as f:

        f.write(outstr)  # 读取的方式和写入的方式要一致


if __name__ == "__main__":
    cut_word(raw_data_path, cut_data_path)


