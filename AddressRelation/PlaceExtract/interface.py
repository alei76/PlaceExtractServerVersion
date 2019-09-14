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
    print(get_addr({"data": [{"content": "420_1010_A_2420_5430_A_5850_7610_A_您好很高兴为您服务！8020_13540_A_您好我想反馈一下我这个地方四g手机流量一点都没有没法上网？14710_20530_A_哦那什么位置使用的我帮您看一下和平东路二百八十号大厦。22760_26460_A_哦和平东路二百八十号德汇大厦是吗？26990_30700_A_和合大厦和合是石家庄的吗？31520_32800_A_对长安区的。33290_35140_A_请稍等我帮您看一下。35770_37990_A_哦除了这个位置就没事了是吧？38540_42730_A_不在这个位置了打别的位置了就没事了是吗？43260_47380_A_稍等多长时间了出现这种情况。48070_49090_A_一张天了吗？50470_52260_A_合适哪个合呢？53360_54630_A_我和你的哦。55040_62360_A_哦两个应该合适那个盒子的河坝下面自己去掉那个。62810_65330_A_哦请稍等。67450_68280_A_。69370_70680_A_高层的吗？71890_73770_A_对河北大厦。74650_76660_A_稍等我看一下。91900_107410_A_根据您说的这个情况我这看了一下哦提示当前这个位置的话是哦信号覆盖区这个情况的话我们这儿已经了解了额已经有工作人员正在处理当中给您介绍给您带来不便了请您谅解一下。108650_110010_A_等多长时间？110690_116060_A_额这个目前没有得到通知但是咱们这儿已经有工作人员处理当中了您可以稍后再关注一下。117730_121930_A_行好嘞谢谢不客气其他我这号能帮到您的吗？122710_123540_A_没了谢谢！124000_127170_A_哦不客气感谢来电祝您生活愉快再见？",  "id": "00deee82284a474c97ceeb3906122c61"}]}))
