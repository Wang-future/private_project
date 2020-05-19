#!/usr/bin/env python
# -*- coding:utf-8 -*-
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class MKB():
    def __init__(self, _ip, _port, _username, _password):
        self.ip = _ip
        self.port = _port
        self.username = _username
        self.password = _password
        self.label = 'NODE'
        # connect
        self.mGraph = Graph('http://' + self.ip + ':' + self.port,username=self.username, password=self.password)
        self.matcher = NodeMatcher(self.mGraph)

    def nodeExist(self, _value):
        m = self.matcher.match(self.label, value = _value).first()
        print(m)
        if m is None:
            return False
        else:
            return True
    def test(self):
        node1 = Node('NODE',value = '服务平台算法部署步骤')
        node2 = Node('NODE',value = '如已经存在服务，则先通过关闭该服务,然后在部署新服务')
        mnodes = []
        mnodes.append(node1)
        mnodes.append(node2)
        ret = self.mGraph.match(nodes=mnodes, r_type=None, limit=None) #找到所有的relationships
        # for item in ret:
        #     print item
        print(len(ret))

    def addNode(self, _label, _dict):
        dicStr = ''
        for item in _dict:
            dicStr += item 
            dicStr += ':\'' + _dict[item] + '\','
        dicStr = dicStr[:len(dicStr)-1]
        if self.nodeExist(_dict['value']):
            return True
        else:
            match_str = 'create (e:' + _label + ' {' + dicStr +'});'
            print(match_str)
            return self.mGraph.run(match_str).data()

    
    def addSPO(self, s, p, o):
        print('in addSPO!')
        sdict = {}
        odict = {}
        sdict['value'] = s
        odict['value'] = o
        self.addNode(self.label, sdict)
        self.addNode(self.label, odict)
        match_str = 'MATCH (a:' + self.label + '),(b:' + self.label + ') WHERE a.value = \'' + s +'\' AND b.value = \'' + o + '\' CREATE (a)-[r:' + p + ']->(b);'
        print(match_str)
        return self.mGraph.run(match_str).data()

    def searchBaseSP(self, s, p):
        match_str = 'MATCH (a:' + self.label + ')-[r:' + p +']->(O)' ' WHERE a.value = \'' + s +'\'' + ' RETURN O.value'
        print(match_str)
        oList = self.mGraph.run(match_str).data()
        ansStr = []
        for item in oList:
            print(type(item))
            print(item.keys())
            for i,result in item.items():
                ansStr.append(str(result))
                # print('searchBaseSP return o:'+  ' ' + str(item).encode('utf-8').decode('utf-8'))
        return ansStr

    def prGraph(self):
        print(self.mGraph)

if __name__ == '__main__':
    ip = '47.115.55.90'
    port = '7474'
    username = 'neo4j'
    password = 'wang654321.'
    mKB = MKB(ip, port, username, password)
    mKB.test()
    # mKB.searchBaseSP('我', '想')
    # name = 'wang'
    # label = 'Person'
    # mKB.addNode(label,name)
    # mKB.prGraph()
    # graph = Graph('http://localhost:7474',username='neo4j',password='wang654321.')
    # test_node_1 = Node(label='Person',name='皇帝')
    # graph.create(test_node_1)
    # print(test_node_1)
    # macth_str = 'create (e:Person {name: \'huang\'});'
    #解析一：
    # mdic = {}
    # mdic['name'] = 'fei'
    # mdic['new'] = 'hello'
    # label = 'Person'
    # mKB.addNode(label, mdic)
    # mKB.addSPO('我', '想', '红苹果')
    # print(data)

    #测试是否存在某个节点
    # if mKB.nodeExist('NODE',"服务平台算法部署步骤"):
    #     print("服务平台算法部署步骤 节点 存在")
    # else:
    #     print("服务平台算法部署步骤 节点 不存在")

    
