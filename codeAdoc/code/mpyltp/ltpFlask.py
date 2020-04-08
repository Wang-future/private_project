#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify,request
from Spo import *
from Neo4j import MKB
import requests
import chardet
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
    
app = Flask(__name__)

g_LtpParser = LtpParser()
g_mLtpParser = CPyltp('./model/cws.model', './model/pos.model', './model/ner.model', './model/parser.model', './model/pisrl.model', g_LtpParser)
g_tripleExtractor = TripleExtractor(g_LtpParser)
g_mKB = MKB('47.115.55.90', '7474', 'neo4j', 'wang654321.')

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
    ret_words = g_mLtpParser.segmentor(sentence.encode('utf-8'))
    ret_postaggerList = g_mLtpParser.postagger(sentence.encode('utf-8'))
    # print('ret_postaggerStr:')
    # print(ret_postaggerList)
    ret_dict = {}
    ret_dict['ret_code'] = 0
    ret_dict['ret_words'] = ' '.join(ret_words)
    ret_dict['ret_postaggerStr'] = ' '.join(ret_postaggerList)
    return ret_dict

@app.route('/extractSPO',methods=['GET','POST'])
def extractSPO():
    sentence = request.json.get('ask')
    print(' get sentence to extract spo:' + sentence)
    spos = g_tripleExtractor.triple_main(sentence)
    ansList = []
    if len(spos) == 0:
        return jsonify({'ansList' : spos, 'ret_code':1})
    for item in spos:
        s = item[0]
        p = item[1]
        temList = g_mKB.searchBaseSP(s,p)
        ansList.extend(temList)
    return jsonify({'ansList' : ansList, 'ret_code':0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5017)
    # ret_postaggerStr = g_mLtpParser.postagger("部署")
    # ret_dict = {}
    # ret_dict['ret_code'] = 0
    # ret_dict['ret_postaggerStr'] = ret_postaggerStr


