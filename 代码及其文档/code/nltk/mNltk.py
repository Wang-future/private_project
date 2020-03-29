#!/usr/bin/env python   #设置Python解释器，告诉系统这是一个python程序
# -*- coding: UTF-8 -*-
from urllib.request import urlopen
import nltk

newfile = open('news.txt',encoding='utf-8')

text = newfile.read()  #读取文件

tokens = nltk.word_tokenize(text)  #分词

tagged = nltk.pos_tag(tokens)  #词性标注

entities = nltk.chunk.ne_chunk(tagged)  #命名实体识别

a1=str(entities) #将文件转换为字符串

file_object = open('out.txt', 'w')

file_object.write(a1)   #写入到文件中

file_object.close( )

print(entities)
