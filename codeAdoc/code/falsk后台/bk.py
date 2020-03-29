#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, jsonify,request
import time
app = Flask(__name__)

# 辅助函数
def todayDate():
    return time.strftime("%Y-%m-%d",time.localtime(time.time()))

# 小程序相关接口
@app.route('/getOpenid',methods=['GET'])
def getOpenid():
    # url一定要拼接，不可用传参方式
    url = "https://api.weixin.qq.com/sns/jscode2session"
    appid = "wxf97cbaa326d3510b"
    secret = "75080e518deceb0d0526a00286482a0e"
    jscode = request.args.get("code") #获取get请求参数
    murl = url + "?appid=" + appid + "&secret=" + secret + "&js_code=" + jscode + "&grant_type=authorization_code"
    r = requests.get(murl)
    print(r.json())
    openid = r.json()['openid']
    return openid


@app.route('/addArticle',methods=['POST'])
def index():
    print('hfl')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5015)
