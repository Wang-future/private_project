#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify,request
import requests
import json
from mVoiceModel import voiceModel
app = Flask(__name__)

# global
g_classifyList = []
g_classUrlList = []
g_voiceModel = voiceModel()
#get class and their interface
with open('classify.txt', mode='r',encoding='UTF-8') as f:
    print('read conf:')
    txt = f.readlines()
    for item in txt:
        index = item.rfind(':')
        temStrClass = item[:index]
        temStrUrl = item[index+1:len(item)]
        temStrUrl = "".join(temStrUrl.split())# 用于去掉换行符
        print(temStrClass + ' , ' + temStrUrl)
        g_classifyList.append(temStrClass)
        g_classUrlList.append(temStrUrl)
    print('end read conf:')

@app.route('/voiceSend',methods=['GET','POST'])
def voiceSend():
    # input
    seqId = request.json.get("seqId")
    message = request.json.get('message')
    print('seqId:' + seqId + ', message:' + message)
    #output
    ret_code = 0
    ret_info = ''

    #获取分类
    simList = []
    maxIndex = 0
    maxSim = 0
    for i in range(len(g_classifyList)):
        temSim = g_voiceModel.vector_similarity(message, g_classifyList[i])
        if temSim > maxSim:
            maxSim = temSim
            maxIndex = i
    print(message + ' 分类为:' + g_classUrlList[maxIndex])
    ret_info = message + ' 分类为:' + g_classUrlList[maxIndex]
    # 辨别出实体
    url = 'http://172.17.0.1:5017/postagger'
    data = {"seqId": seqId, "sentence": message}
    res = requests.post(url=url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    print("res：")
    print(res)
    ret_code = json.loads(res.text).get('ret_code')
    ret_postaggerList = json.loads(res.text).get('ret_postaggerStr').strip(' ').split(' ')
    ret_words = json.loads(res.text).get('ret_words').strip(' ').split(' ')
    print('ret_code:' + str(ret_code))
    print(ret_postaggerList)
    extaList = []
    for index in range(len(ret_postaggerList)):
        if ret_postaggerList[index] == 'ws':
            extaList.append(ret_words[index])
    # 调用完成操作
    strDel = '调用url为：'+g_classUrlList[maxIndex] + ', 参数为:'
    for index in range(len(extaList)):
        strDel += (extaList[index] + ', ')
    print(strDel)
    print("ret_code:" + str(ret_code) + ', ret_info:'+ret_info)
    ret_dict = {}
    ret_dict['ret_code'] = ret_code
    ret_dict['ret_info'] = ret_info
    return ret_dict

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5016)


