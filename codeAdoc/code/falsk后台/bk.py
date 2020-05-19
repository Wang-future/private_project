#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify,request
import time
import redis
import requests
import json
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
    
app = Flask(__name__)

g_redis_ip = '47.115.55.90'
g_redis_port = 6379
g_redis_password = 'wang654321.'
g_redic_client=redis.Redis(host=g_redis_ip,password=g_redis_password,port=g_redis_port,db=0,decode_responses=True)
g_redic_pipe = g_redic_client.pipeline()
# 辅助函数
def todayDate():
    return time.strftime("%Y-%m-%d",time.localtime(time.time()))

def search(seqId, strAsk):
    url = 'http://172.17.0.2:5015/extractSPO'
    data = {"seqId": seqId, "ask": strAsk}
    res = requests.post(url=url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    # 提取返回的元组
    print(res.text)
    ansList = json.loads(res.text).get('ansList')
    ret_code = json.loads(res.text).get('ret_code')
    if ret_code == 1:
        return "您的问题暂时无法找到答案"
    ansStr = '你的问题候选答案如下：\n'
    print(ansList)
    for index in range(len(ansList)):
        temStr = '('+str(index+1)+')' + ansList[index]
        ansStr += temStr
    print ('ansStr:'+ansStr)
    return ansStr

def conKey(OpenId):
    return 'con_'+str(OpenId)

def insData(OpenId, sender, text):
    redisKey = conKey(OpenId)
    redisValue = sender + '_' + text
    g_redic_client.rpush(redisKey, redisValue)

def conConversation(redisList):
    retList = []
    for item in redisList:
        tmpDict = {}
        index = item.find('_')
        print(item[:index])
        print(item[index+1:])
        tmpDict['sender'] = item[:index]
        tmpDict['text'] = item[index+1:]
        retList.append(tmpDict)
    return retList

def getKeyData(OpenId):
    redisKey = conKey(OpenId)
    if not g_redic_client.exists(redisKey):
        return []
    mlist = []
    list_count = g_redic_client.llen(redisKey)
    for index in range(list_count):
        mlist.append(g_redic_client.lindex(redisKey, index))
    return conConversation(mlist)

def carryVoiceInstr(seqId, message):
    url = 'http://172.17.0.3:5016/voiceSend'
    data = {"seqId": seqId, "message": message}
    res = requests.post(url=url, data=json.dumps(data),headers={'Content-Type': 'application/json'})
    ret_code = 1
    ret_info = ' '
    print("res：")
    print(res)
    ret_code = json.loads(res.text).get('ret_code')
    ret_info = json.loads(res.text).get('ret_info')
    print('res: ret_code:' + str(ret_code) + ', ret_info:' + ret_info)

    return ret_code,ret_info
# 小程序相关接口
@app.route('/getOpenid',methods=['GET'])
def getOpenid():
    # url一定要拼接，不可用传参方式
    url = "https://api.weixin.qq.com/sns/jscode2session"
    appid = "wx1fc08f048fad7da0"
    secret = "5a01e2474b1391ff0bf14a2c98efd646"
    jscode = request.args.get("code") #获取get请求参数
    murl = url + "?appid=" + appid + "&secret=" + secret + "&js_code=" + jscode + "&grant_type=authorization_code"
    r = requests.get(murl)
    print('in getOpenid')
    print(r.json())
    openid = r.json()['openid']
    return openid

@app.route('/send',methods=['GET','POST'])
def recAsk():
    print('rec ask:')
    # input
    seqId = request.json.get("seqId")
    print(seqId)
    openId = request.json.get('openId')
    print(openId)
    message = request.json.get('message')
    print('seqId:' + seqId + ', openId:' + openId + ', message:' + message)
    # 数据库操作
    insData(openId, 'user', message)

    #output
    ret_dict = {}
    ret_dict['seqId'] = seqId
    ret_dict['ret_code'] = 0 # 0代表成功

    retDataDict = {}
    ret_messages = []
    strAnswer = search(seqId, message)
    retJson = {}
    retJson['sender'] = 'rot'
    retJson['text'] = strAnswer
    ret_messages.append(retJson)
    retDataDict['messages'] = ret_messages
    # 数据库操作
    insData(openId, 'rot', strAnswer)


    ret_dict['data'] = retDataDict
    return ret_dict

@app.route('/conversations',methods=['GET','POST'])
def getHistoryMess():
    # input
    seqId = request.json.get("seqId")
    openId = request.json.get('openId')
    print('seqId:' + seqId + ', openId:' + openId )

    # output
    ret_dict = {}
    ret_dict['seqId'] = seqId
    conversationData = getKeyData(openId)
    ret_dict['data'] = conversationData
    ret_code = 0
    if len(conversationData) == 0:
        ret_code = 1
    ret_dict['ret_code'] = ret_code
    return ret_dict

@app.route('/voiceSend',methods=['GET','POST'])
def voiceSend():
    print('rec ask:')
    # input
    seqId = request.json.get("seqId")
    print(seqId)
    openId = request.json.get('openId')
    print(openId)
    message = request.json.get('message')
    print('seqId:' + seqId + ', openId:' + openId + ', message:' + message)

    #output
    retDict = {}
    retDict['seqId'] = seqId
    retDict['ret_code'] = 0

    if message :
        carryResList = carryVoiceInstr(seqId, message)
        retDict['ret_code'] = carryResList[0]
        retDict['info'] = carryResList[1]
    else:
        retDict['ret_code'] = 0
        retDict['info'] = "你的输入为空， 执行成功"
    return retDict

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5017,ssl_context=('./zhengshu/3708790_www.iais.group.pem', './zhengshu/3708790_www.iais.group.key'))
    # redisKey ='test'
    # ret = getKeyData(redisKey)
    # print(ret)

