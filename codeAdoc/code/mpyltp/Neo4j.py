#!/usr/bin/env python
# -*- coding:utf-8 -*-

from py2neo import Graph,Node,Relationship,cypher
 

class MKB():
    def __init__(self, _ip, _port, _username, _password):
        self.ip = _ip
        self.port = _port
        self.username = _username
        self.password = _password
        self.label = 'NODE'
        # connect
        self.mGraph = Graph('http://' + self.ip + ':' + self.port,username=self.username, password=self.password)

    def addNode(self,_label, _dict):
        dicStr = ''
        for item in _dict:
            dicStr += item 
            dicStr += ':\'' + _dict[item] + '\','
        dicStr = dicStr[:len(dicStr)-1]
        match_str = 'create (e:' + _label + ' {' + dicStr +'});'
        print(match_str)
        return self.mGraph.run(match_str).data()

    
    def addSPO(self, s, p, o):
        sdict = {}
        odict = {}
        sdict['value'] = s
        odict['value'] = o
        self.addNode(self.label, sdict)
        self.addNode(self.label, odict)
        match_str = 'MATCH (a:' + self.label + '),(b:' + self.label + ') WHERE a.value = \'' + s +'\' AND b.value = \'' + o + '\' CREATE (a)-[r:' + p + ']->(b);'
        print(match_str)
        return self.mGraph.run(match_str).data()

    def prGraph(self):
        print(self.mGraph)

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = '7474'
    username = 'neo4j'
    password = 'wang654321.'
    mKB = MKB(ip, port, username, password)
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
    mKB.addSPO('我', '想', '红苹果')
    # print(data)
