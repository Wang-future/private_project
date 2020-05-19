#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify,request
from Spo import *
from Neo4j import MKB
from mmanMachModel import manMachModel
import requests
import chardet
import sys
import io
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
    
app = Flask(__name__)

# global
g_classifyList = []
g_manMachModel = manMachModel()
g_LtpParser = LtpParser()
g_mLtpParser = CPyltp('./model/cws.model', './model/pos.model', './model/ner.model', './model/parser.model', './model/pisrl.model', g_LtpParser)
g_tripleExtractor = TripleExtractor(g_LtpParser)
g_mKB = MKB('47.115.55.90', '7474', 'neo4j', 'wang654321.')

#get class and their interface
with io.open('classify.txt', mode='r',encoding='UTF-8') as f:
    print('read conf:')
    txt = f.readlines()
    for item in txt:
        g_classifyList.append(item)
    print('end read conf:')
    print(g_classifyList)


@app.route('/voiceSend',methods=['GET','POST'])
def voiceSend():
    # input
    seqId = request.json.get("seqId")
    message = request.json.get('message')
    print('seqId:' + seqId + ', message:' + message)

    #output
    retDict = {}
    retDict['seqId'] = seqId
    retDict['ret_code'] = 0

    if message :
        carryResList = carryVoiceInstr(message)
        retDict['ret_code'] = carryResList[0]
        retDict['info'] = carryResList[1]
    else:
        retDict['ret_code'] = 0
        retDict['info'] = "你的输入为空， 执行成功"
    return retDict
@app.route('/postagger',methods=['GET','POST'])
def postagger():
    print('in postagger')
    seqId = request.json.get("seqId")
    sentence = request.json.get('sentence')
    print("seqId:" + seqId + ', sentence:' + sentence)
    # ret_words = g_mLtpParser.segmentor(sentence.encode('utf-8'))
    ret_words, ret_postaggerList = g_mLtpParser.postagger(sentence.encode('utf-8'))
    # print('ret_postaggerStr:')
    # print(ret_postaggerList)
    ret_dict = {}
    ret_dict['ret_code'] = 0
    ret_dict['ret_words'] = ' '.join(ret_words)
    print(ret_postaggerList)
    ret_dict['ret_postaggerStr'] = ' '.join(ret_postaggerList)
    return ret_dict

@app.route('/extractSPO',methods=['GET','POST'])
def extractSPO():
    sentence = request.json.get('ask')
    print(' get sentence to extract spo:' + sentence)
    spos = g_tripleExtractor.triple_main(sentence)
    print(sentence + '\'s spos is :')
    print(spos)
    # according classify get result
    # 获取分类
    maxIndex = 0
    maxSim = 0
    for i in range(len(g_classifyList)):
        temSim = g_manMachModel.vector_similarity(sentence, g_classifyList[i])
        if temSim > maxSim:
            maxSim = temSim
            maxIndex = i
    print(sentence + ' 分类为:' + g_classifyList[maxIndex])
    newSpos = g_tripleExtractor.triple_main(g_classifyList[maxIndex])
    spos.extend(newSpos)
    print('after extend spos is :')
    print(spos)
    ansList = []
    for item in spos:
        s = item[0]
        p = item[1]
        temList = g_mKB.searchBaseSP(s,p)
        ansList.extend(temList)

    # 去重

    if len(ansList) == 0:
        return jsonify({'ansList' : ansList, 'ret_code':1})
    return jsonify({'ansList' : list(set(ansList)), 'ret_code':0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5015)
    # ret_postaggerStr = g_mLtpParser.postagger("部署")
    # ret_dict = {}
    # ret_dict['ret_code'] = 0
    # ret_dict['ret_postaggerStr'] = ret_postaggerStr


