#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
from Neo4j import MKB
import re
import sys
import json
import io
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
class LtpParser:
    def __init__(self):
        LTP_PATH = "./model"
        # 分词
        self.segmentor = Segmentor()
        print("debug:"+ os.path.join(LTP_PATH, 'cws.model'))
        self.segmentor.load(os.path.join(LTP_PATH, 'cws.model'))
        # 词性标注
        self.postagger = Postagger()
        self.postagger.load(os.path.join(LTP_PATH, 'pos.model'))
        # 依存句法
        self.parser = Parser()
        self.parser.load(os.path.join(LTP_PATH, 'parser.model'))
        # 命名实体识别
        self.recognizer = NamedEntityRecognizer()
        self.recognizer.load(os.path.join(LTP_PATH, 'ner.model'))
        # 语义角色标注
        self.labeller = SementicRoleLabeller()
        self.labeller.load(os.path.join(LTP_PATH, 'pisrl.model'))

    # 分词
    def segmentorFun(self, sentence):
        words = self.segmentor.segment(sentence)  # 分词
        return words

    def postaggerFun(self, sentence):
        words = self.segmentorFun(sentence)
        postags = self.postagger.postag(words)  # 词性标注
        return words,postags

    def format_labellerFun(self, words, postags):
        '''语义角色标注'''
        arcs = self.parser.parse(words, postags)
        roles = self.labeller.label(words, postags, arcs)
        roles_dict = {}
        for role in roles:
            # role.index代表谓词的索引
            # role.arguments 代表关于该谓词的若干语义角色
            # arg.name表示语义角色类型
            # arg.range.start表示该语义角色起始词的开始位置索引
            # arg.range.end表示该语义角色起始词的结束位置索引
            roles_dict[role.index] = {arg.name: [arg.name, arg.range.start, arg.range.end] for arg in role.arguments}
        # print(roles_dict)
        return roles_dict

    def build_parser_child_dict(self, words, postags, arcs):
        '''句法分析，为句子中的每个词语维护一个保存句法依存儿子节点的字典'''
        child_dict_list = []
        format_parser_list = []
        for index in range(len(words)):  # 循环每个词
            child_dict = dict()  # 存储的格式为{词关系（ATT）: 词}
            for arc_index in range(len(arcs)):
                # arc_index为当前词的索引，arcs[arc_index]为一个元祖（arc.head,arc.relation）
                if arcs[arc_index].head == index + 1:  # 去找到父节点为当第一个for里面索引的词，即当前词的子节点
                    if arcs[arc_index].relation in child_dict:
                        child_dict[arcs[arc_index].relation].append(arc_index)
                    else:
                        child_dict[arcs[arc_index].relation] = []
                        child_dict[arcs[arc_index].relation].append(arc_index)
            child_dict_list.append(child_dict)
        rely_id = [arc.head for arc in arcs]  # 提取依存父节点id
        relation = [arc.relation for arc in arcs]  # 提取关系依存
        heads = ['Root' if id == 0 else words[id - 1] for id in rely_id]  # 匹配依存父节点词语
        for i in range(len(words)):
            a = [relation[i], words[i], i, postags[i], heads[i], rely_id[i] - 1, postags[rely_id[i] - 1]]
            format_parser_list.append(a)
        # print("child_dict_list")
        # print(child_dict_list)
        return child_dict_list, format_parser_list

    def parser_main(self, sent):
        '''依存关系分析的主函数'''
        words = list(self.segmentor.segment(sent))
        # print('debug words:')
        # print(' '.join(words))

        postags = list(self.postagger.postag(words))
        # print('debug postags:')
        # print(postags)

        arcs = self.parser.parse(words, postags)
        # for item in arcs:
        #     print(str(item.head)+ ', relation:' + item.relation)
        # print(arcs)

        child_dict_list, format_parser_list = self.build_parser_child_dict(words, postags, arcs)
        roles_dict = self.format_labellerFun(words, postags)
        return words, postags, child_dict_list, format_parser_list, roles_dict

class CPyltp():
    def __init__(self, cws_model_path, pos_model_path, ner_model_path, parse_path, sementic_path, mLtpParser):
        self.cws_model_path = cws_model_path
        self.pos_model_path = pos_model_path
        self.ner_model_path = ner_model_path
        self.parse_path = parse_path
        self.sementic_path = sementic_path
        self.mLtpParser = mLtpParser
    # 分词
    def segmentor(self, sentence):
        return self.mLtpParser.segmentorFun(sentence)

    def postagger(self, sentence):
        
        return self.mLtpParser.postaggerFun(sentence)

    # def ner(self, sentence):
    #     recognizer = NamedEntityRecognizer() # 初始化实例
    #     recognizer.load(self.ner_model_path)  # 加载模型

    #     words = self.segmentor(sentence)
    #     postags = self.postagger(words)
    #     nertags = recognizer.recognize(words, postags)  # 命名实体识别
    #     print (' '.join(nertags))
    #     print(nertags)
    #     recognizer.release()  # 释放模型

    # def parse(self, sentence):
    #     words = self.segmentor(sentence)
    #     postags = self.postagger(words)
    #     """
    #     依存句法分析
    #     :param words:
    #     :param postags:
    #     :return:
    #     """
    #     parser = Parser()  # 初始化实例
    #     parser.load(self.parse_path)  # 加载模型
    #     arcs = parser.parse(words, postags)  # 句法分析
    #     print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
    #     for arc in arcs:
    #         print(arc)
    #         print('\n')
    #     parser.release()  # 释放模型

    # def sematic(self, sentence):
    #     labeller = SementicRoleLabeller() # 初始化实例
    #     labeller.load(self.sementic_path)  # 加载模型

    #     words = self.segmentor(sentence)
    #     postags = self.postagger(words)
    #     # arcs 使用依存句法分析的结果
    #     roles = labeller.label(words, postags, arcs)  # 语义角色标注
    #     # 打印结果
    #     for role in roles:
    #         print(role.index, "".join(["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))
    #     labeller.release()  # 释放模



class TripleExtractor:
    def __init__(self, LtpParser):
        self.parser = LtpParser
    # 对数据进行处理
    def splitData(self, data_path):
        data_file_list = os.listdir(data_path)
        corpus = ''
        sentencesList = []
        for file in data_file_list:
            with open(data_path + file, 'rb') as f:
                document = f.read()
                sentences = re.split('(。|！|\!|\.|？|\?)', document)
                if len(sentences) == 1:
                    sentencesList.append(sentences)
                    continue

                tmpSentenceList = []
                for i in range(int(len(sentences)/2)):
                    # 提取标点含句子符号
                    sentence = sentences[2*i] + sentences[2*i+1]
                    # print('debug, get sentences:' + sentence)
                    tmpSentenceList.append(sentence)

                sentencesList.extend(tmpSentenceList)
        return sentencesList


    # 对文章进行分句处理
    def split_sents(self, content):
        sentences = re.split('(。|！|\!|\.|？|\?)',content)         # 保留分割符
        if len(sentences) == 1:
            return sentences
        new_sents = []
        for i in range(int(len(sentences)/2)):
            
            sent = sentences[2*i] + sentences[2*i+1]
            new_sents.append(sent)
        return new_sents

    def semanticRoleExtra(self, words, postags, roles_dict, role_index):
        '''利用语义角色标注，直接获取主谓宾三元组，基于A0,A1,A2'''
        v = words[role_index]  # 动词
        # print("in semanticRoleExtra; v is " + v)
        role_info = roles_dict[role_index]  # 获得角色的信息
        # print ("role_info:")
        # print(role_info)
        if 'A0' in role_info.keys() and 'A1' in role_info.keys():
            s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2] + 1)
                         if postags[word_index] not in ['w', 'u', 'x'] and words[word_index]
                         ])
            o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2] + 1)
                         if postags[word_index] not in ['w', 'u', 'x'] and words[word_index]
                         ])
            if s and o:
                # print('debug svo s :' + s + ',v:'+ v.decode('utf-8').encode('utf-8') + ', o:'+o.decode('utf-8').encode('utf-8'))
                # print([s, v, o])
                return '1', [s, v, o]# 0 chage to o
        return '4', []

    def dependencyExtra(self, words, postags, child_dict_list, arcs, roles_dict):
        svos = []
        for index in range(len(postags)):
            if postags[index] == 'v':
                # print("处理的动词为："+words[index])
                child_dict = child_dict_list[index]
                # print("chile_dice")
                # print(child_dict)
                # 抽取以谓词为中心的事实三元组
                # 主谓宾关系
                if 'SBV' in child_dict and 'VOB' in child_dict:
                    r = words[index]
                    # 提取动词的动补关系
                    if 'CMP' in child_dict:
                        cmp_index = child_dict['CMP'][0]
                        # print("cmp_index is " + str(cmp_index))
                        r = r + words[cmp_index]
                    e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                    e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                    # print('debug in dependencyExtra 抽取以谓词为中心的事实三元组:' + e1 + "  " + r + "  "+e2)
                    svos.append([e1, r, e2])
                #   定语后置，动宾关系
                #  [relation[i], words[i], i, postags[i], heads[i], rely_id[i] - 1, postags[rely_id[i] - 1]]
                relation = arcs[index][0]  # 获取关系
                head = arcs[index][5]      # 获取关系的索引d
                if relation == 'ATT':      # 定中关系我们的关系 使用
                    if 'VOB' in child_dict:  # 向下的关系
                        # print("向下的关系, head is " +str(head) + ", child_dict['VOB'][0]:" + str(child_dict['VOB'][0]))
                        e1 = words[head]
                        r = words[index]
                         # 提取动词的动补关系
                        if 'CMP' in child_dict:
                            cmp_index = child_dict['CMP'][0]
                            # print("cmp_index is " + str(cmp_index))
                            r = r + words[cmp_index]
                        e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                        # print("e1:" + e1 + ", r:"+r+", e2:" + e2) 
                        # 重组关系
                        new_e1 = r + e2
                        r = e1
                        if arcs[head][0] == 'SBV':
                            relId = arcs[head][5] # 依赖的动词
                            # 获取依赖动词的vob实体作为关系
                            # print(" relId: " + str(relId))
                            tmp_child_dict = child_dict_list[relId]
                            new_e2 = self.complete_e(words, postags, child_dict_list, tmp_child_dict['VOB'][0])
                            # print("new_e1:" + new_e1 + ", r:"+r+", new_e2:" + new_e2)
                            svos.append([new_e1, r, new_e2])
        return svos

    def combineRule(self, words, postags, child_dict_list, arcs, roles_dict):
        svos = []
        # 利用语义角色提取
        for item in roles_dict:
            flag,triple = self.semanticRoleExtra(words, postags, roles_dict, item)
            if flag == '1' and triple not in svos:
                svos.append(triple)
        
        # print("\n——————————————————利用依存关系进行提取————————————————————————————————————————————————————————————\n")
        # 利用依存关系进行提取
        newSvos = self.dependencyExtra(words, postags, child_dict_list, arcs, roles_dict)
        svos.extend(newSvos)
        lastSvos = []
        for item in svos:
            if item not in lastSvos:
                lastSvos.append(item)
        return lastSvos
        



    def testruler2(self, words, postags, child_dict_list, arcs, roles_dict):
        '''基于依存结构进行关系提取'''
        svos = []
        for index in range(len(postags)):
            tmp = 1
            # 先利用语义角色进行标注，进行提取
            if index in roles_dict:
                flag, triple = self.semanticRoleExtra(words, postags, roles_dict, index)
                if flag == '1':
                    svos.append(triple)
                    tmp = 0
            if tmp == 1:  # 说明语义角色提取失败，利用依存句法进行提取
                if postags[index]:
                    child_dict = child_dict_list[index]
                    # 抽取以谓词为中心的事实三元组
                    # 主谓宾关系
                    if 'SBV' in child_dict and 'VOB' in child_dict:
                        r = words[index]
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                        e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                        print('debug in ruler2 抽取以谓词为中心的事实三元组:' + e1 + "  " + r + "  "+e2)
                        svos.append([e1, r, e2])
                    #   定语后置，动宾关系
                    #  [relation[i], words[i], i, postags[i], heads[i], rely_id[i] - 1, postags[rely_id[i] - 1]]
                    relation = arcs[index][0]  # 向上的?
                    head = arcs[index][2]  # 向上关系的索引d
                    if relation == 'ATT':
                        if 'VOB' in child_dict:  # 向下的关系 卸载服务的接口为uninstallService
                            print("向下的关系, head is " +str(head) + ", child_dict['VOB'][0]:" + str(child_dict['VOB'][0]))
                            e1 = self.complete_e(words, postags, child_dict_list, head - 1)
                            r = words[index]
                            e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                            # 重新组合对应的关系
                            # tmp_str = r + e2
                            # if tmp_str == e1[:len(tmp_str)]:
                            #     e1 = e1[:len(tmp_str)] #?
                            # if tmp_str not in e1:
                            #     print('debug in ruler2 重新组合对应的关系:' + e1 + "  " + r + "  "+e2)
                            #     svos.append([e1, r, e2])

                            tmp_str = r + e2
                            if tmp_str == e1[:len(tmp_str)]:
                                e1 = e1[:len(tmp_str)] #?
                            if tmp_str not in e1:
                                print('debug in ruler2 重新组合对应的关系:' + e1 + "  " + r + "  "+e2)
                                svos.append([e1, r, e2])

                    # 包含有介宾关系的主谓动补关系
                    if 'SBV' in child_dict and 'CMP' in child_dict:
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                        cmp_index = child_dict['CMP'][0]
                        r = words[index] + words[cmp_index]
                        if 'POB' in child_dict_list[cmp_index]:
                            e2 = self.complete_e(words, postags, child_dict_list, child_dict[cmp_index]['POB'][0])
                            print('debug in ruler2 包含有介宾关系的主谓动补关系:' + e1 + "  " + r + "  "+e2)
                            svos.append([e1, r, e2])
        print("debug svos:")
        print(svos)
        return svos

    def complete_e(self, words, postags, child_dict_list, word_index):
        '''对找出的主语或者宾语，进行识别'''
        child_dict = child_dict_list[word_index]
        # print("word_index:" + words[word_index])
        # print(child_dict)
        prefix = ''
        if 'ATT' in child_dict:
            for i in range(len(child_dict['ATT'])):
                prefix += self.complete_e(words, postags, child_dict_list, child_dict['ATT'][i])
        postfix = ''
        if postags[word_index] == 'v':
            if 'VOB' in child_dict:
                postfix += self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
            if 'SBV' in child_dict:
                prefix = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0]) + prefix
        return prefix + words[word_index] + postfix

    def triple_main(self, content):
        sents = self.split_sents(content)
        # print('sent size:' + str(len(sents)))
        svos = []
        for sent in sents:
            # print('debug sent:')
            # print(sent)
            words, postags, child_dict_list, format_parser_list, roles_dict = self.parser.parser_main(sent.encode('utf-8'))
            svo = self.combineRule(words, postags, child_dict_list, format_parser_list, roles_dict)
            svos += svo
        return svos

if __name__ =="__main__":
    # mPyltp = CPyltp('./model/cws.model', './model/pos.model', './model/ner.model', './model/parser.model', './model/pisrl.model')
    # mPyltp.parse("好漂亮的彩虹呀")
    mLtpParser = LtpParser()
    mtest = TripleExtractor(mLtpParser)

    seqNum = 1
    # 文章分句
    sentencesList = mtest.splitData('./operaData/')
    # print(sentencesList)


    # mlist = mtest.triple_main("部署服务的步骤是:先通过关闭服务,然后在部署新服务。")
    # print("show results:" + str(len(mlist)))
    # for item in mlist:
    #     print('s:' + item[0] + ', v:'+item[1] + ', o:' + item[2] + '\n')
    # print(' end for')
    # #print(mtest.triple_main("传统的基于容器的开发要从镜像加载开始。"))
    # ip = '47.115.55.90'
    # port = '7474'
    # username = 'neo4j'
    # password = 'wang654321.'
    # mKB = MKB(ip, port, username, password)
    # for item in mlist:
    #     print('in loop')
    #     mKB.addSPO(item[0], item[1], item[2])
    # print('in end!')
    # mPyltp.ner('我想关闭Alo服务')


    #论文结果测试
    # sentenceTest = "服务平台算法的部署步骤是：如已经存在服务，则先通过关闭该服务,然后在部署新服务。"
    # senten ="电磁炉有辐射吗?:由于电磁炉打破了传统的明火烹调方式采用磁场感应电流（又称为涡流）的加热原理。"#"卸载服务的接口为uninstallService"#"旧服务的卸载方法为直接用语音控制调用平台提供的接口即可。"
    # senten2 = "算法操作平台的服务卸载方法是：随机选择某一个地区的服务器卸载该服务即可，其他地区的服务会同步卸载。"
    # senten3 = "服务平台的建设目标为：本平台基于Kubernetes实现对智能算法应用的分布式和自动化部署、管理和监控。"
    # senten4 = "卸载服务的接口为uninstallService"#"我要关闭算法testAlgorithm"
    # senten5 = "算法操作平台算法管理流程是：部署在平台的算法，支持算法上传和删除，查看算法部署配置和运行情况、占用资源、运行次数、最后调用时间等，修改算法配置，查看算法的使用文档。"
    # words, postags = mLtpParser.postaggerFun(sentenceTest)
    # print(' '.join(words))
    # print("_________________________")
    # print( ' '.join(postags))

    # # 语义角色获取
    # roles_dict = mLtpParser.format_labellerFun(words, postags)
    # print(roles_dict)

    # 增加spo
    ip = '47.115.55.90'
    port = '7474'
    username = 'neo4j'
    password = 'wang654321.'
    mKB = MKB(ip, port, username, password)
    with io.open('./KGdata/questions.txt', 'w', encoding='utf-8') as f:
        for eachSen in sentencesList:
            if len(eachSen) < 8:
                
                continue
            saveDict = {}
            saveDict['seqNum'] = seqNum
            seqNum += 1
            saveDict['preSentence'] = eachSen
            # 依存关系提取
            words, postags, child_dict_list, format_parser_list, roles_dict = mLtpParser.parser_main(eachSen.encode('utf-8'))
            # print(roles_dict)
            svo = mtest.combineRule(words, postags, child_dict_list, format_parser_list, roles_dict)
            print(str(seqNum) + ".句子是："+eachSen)
            print("print the final result:")
            resultList = []
            for item in svo:
                strTmp = item[0].encode('utf-8') + "   " + item[1].encode('utf-8') + "   " +item[2].encode('utf-8') + "\n"
                print(strTmp)
                resultList.append(strTmp)
                mKB.addSPO(item[0], item[1], item[2])
            saveDict['extraResult'] = resultList
            s
            # print(resultList)
            # print("\n\n")
           
    