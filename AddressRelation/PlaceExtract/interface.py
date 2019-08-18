#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:menghuanlater
# 地点识别接口
from . import extract_addr as pea
from . import filename as myfile
import os

jieba = pea.jieba
replace_pairs = []  # 纠正语音错误


def load_replace_pairs():
    if not os.path.exists(myfile.replace_word_pair):
        print("纠正词对文件不存在")
        return
    f = open(myfile.replace_word_pair, "r", encoding="UTF-8")
    for item in f.readlines():
        items = item.replace("\r", "").replace("\n", "").split("-")
        if len(items) > 0:
            replace_pairs.append((items[0], items[1]))
    f.close()


# 字典加载需要5~10s的时间
# 加载字典,jieba内置的容易出现实际加载失败的情况,而且使用自己写的加载函数比使用内置函数要快很多,之前加载基本需要40~60s的时间,比较奇怪
def load_userdict(file_path1, file_path2):
    if not os.path.exists(file_path1) and not os.path.exists(file_path2):
        print("自定义地址词典路径不对,无法加载")
        return
    f = open(file_path1, "r", encoding="UTF-8")
    for item in f.readlines():
        items = item.replace("\r", "").replace("\n", "").split(" ")
        jieba.add_word(items[0], int(items[1]), items[2])
    f.close()
    # 加载自定义词,额外设置的名词等
    f = open(file_path2, "r", encoding="UTF-8")
    for item in f.readlines():
        items = item.replace("\r", "").replace("\n", "").split(" ")
        jieba.add_word(items[0], int(items[1]), items[2])
    f.close()


load_userdict(myfile.jieba_dict_name, myfile.addi_word)
load_replace_pairs()

interface_usage = 0


def filter_by_replace_pairs(text: str):
    for t in replace_pairs:
        text = text.replace(t[0], t[1])
    return text


# 传入json数据
# 返回json数据
def get_addr(json_dic):
    global interface_usage
    data = json_dic['data']
    return_dic = {'data': []}
    for item in data:
        add_item = pea.interface_interaction(filter_by_replace_pairs(item['content']))
        add_item['id'] = item['id']
        return_dic['data'].append(add_item)
    interface_usage += 1
    if interface_usage % 10 == 0:
        pea.ppro.load_wgyd_info()
    return return_dic


if __name__ == '__main__':
    print(get_addr({"data": [{"content": "23680_55960_A_我住在秦皇西大街四号这里信号不是太好啊",  "id": "00deee82284a474c97ceeb3906122c61"}]}))
