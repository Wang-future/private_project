#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify,request
from Spo import CPyltp
import requests
import chardet
app = Flask(__name__)

g_mLtpParser = CPyltp('./model/cws.model', './model/pos.model', './model/ner.model', './model/parser.model', './model/pisrl.model')

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
    ret_postaggerList = g_mLtpParser.postagger(ret_words)
    # print('ret_postaggerStr:')
    # print(ret_postaggerList)
    ret_dict = {}
    ret_dict['ret_code'] = 0
    ret_dict['ret_words'] = ' '.join(ret_words)
    ret_dict['ret_postaggerStr'] = ' '.join(ret_postaggerList)
    return ret_dict
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5017)
    # ret_postaggerStr = g_mLtpParser.postagger("部署")
    # ret_dict = {}
    # ret_dict['ret_code'] = 0
    # ret_dict['ret_postaggerStr'] = ret_postaggerStr


