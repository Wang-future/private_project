import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller


class LtpParser:
    def __init__(self):
        LTP_PATH = "D:\workspace\project\\NLPcase\\eventTripExtraction\\ltp_data"
        # 分词
        self.segmentor = Segmentor()
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
        self.labeller.label(os.path.join(LTP_PATH, 'pisrl.model'))

    def format_labeller(self, words, postags):
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
            roles_dict[role.index] = {arg.name: {arg.name, arg.range.start, arg.range.end} for arg in role.arguments}
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
        return child_dict_list, format_parser_list

    def parser_main(self, sent):
        '''依存关系分析的主函数'''
        words = list(self.segmentor.segment(sent))
        postags = list(self.postagger.postag(words))
        arcs = self.parser.parse(words, postags)
        child_dict_list, format_parser_list = self.build_parser_child_dict(words, postags, arcs)
        roles_dict = self.format_labeller(words, postags)
        return words, postags, child_dict_list, format_parser_list, roles_dict

import re


class TripleExtractor:
    def __init__(self):
        self.parser = LtpParser()

    # 对文章进行分句处理
    def split_sents(self, content):
        return [sent for sent in re.split(r'[？?！!。；;：:\n\r]', content) if sent]

    def ruler1(self, words, postags, roles_dict, role_index):
        '''利用语义角色标注，直接获取主谓宾三元组，基于A0,A1,A2'''
        v = words[role_index]  # 动词
        role_info = roles_dict[role_index]  # 获得角色的信息
        if 'A0' in role_info.keys() and 'A1' in role_info.keys():
            s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2] + 1)
                         if postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]
                         ])
            o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2] + 1)
                         if postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]
                         ])
            if s and o:
                return '1', [s, v, o]# 0 chage to o
        return '4', []

    def ruler2(self, words, postags, child_dict_list, arcs, roles_dict):
        '''基于依存结构进行关系提取'''
        svos = []
        for index in range(len(postags)):
            tmp = 1
            # 先利用语义角色进行标注，进行提取
            if index in roles_dict:
                flag, triple = self.ruler1(words, postags, roles_dict, index)
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
                        e1 = self.complete(words, postags, child_dict_list, child_dict['SVB'][0])
                        e2 = self.complete(words, postags, child_dict_list, child_dict['VOB'][0])
                        svos.append([e1, r, e2])
                    #
                    #  [relation[i], words[i], i, postags[i], heads[i], rely_id[i] - 1, postags[rely_id[i] - 1]]
                    relation = arcs[index][0]  # 向上的?
                    head = arcs[index][2]  # 向上关系的索引d
                    if relation == 'ATT':
                        if 'VOB' in child_dict:  # 向下的关系
                            e1 = self.complete(words, postags, child_dict_list, head - 1)
                            r = words[index]
                            e2 = self.complete(words, postags, child_dict_list, child_dict['VOB'][0])
                            # 重新组合对应的关系
                            tmp_str = r + e2
                            if tmp_str == e1[:len(tmp_str)]:
                                e1 = e1[len(tmp_str)] #
                            if tmp_str not in e1:
                                svos.append([e1, r, e2])
                    # 包含有介宾关系的主谓动补关系
                    if 'SBV' in child_dict and 'CMP' in child_dict:
                        e1 = self.complete(words, postags, child_dict_list, child_dict['SBV'][0])
                        cmp_index = child_dict['CMP'][0]
                        r = words[index] + words[cmp_index]
                        if 'POB' in child_dict_list[cmp_index]:
                            e2 = self.complete(words, postags, child_dict_list, child_dict[cmp_index]['POB'][0])
                            svos.append([e1, r, e2])
        return svos

    def complete_e(self, words, postags, child_dict_list, word_index):
        '''对找出的主语或者宾语，进行识别'''
        child_dict = child_dict_list[word_index]
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
        svos = []
        for sent in sents:
            words, postags, child_dict_list, format_parser_list, roles_dict = self.parser.parser_main(sent)
            svo = self.ruler2(words, postags, child_dict_list, format_parser_list, roles_dict)
            svos += svo
        return svos
