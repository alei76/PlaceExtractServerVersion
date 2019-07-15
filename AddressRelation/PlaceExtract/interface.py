#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:menghuanlater
# 地点识别接口
from . import extract_addr as pea
from . import filename as myfile
import os

jieba = pea.jieba


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

interface_usage = 0


# 传入json数据
# 返回json数据
def get_addr(json_dic):
    global interface_usage
    data = json_dic['data']
    return_dic = {'data': []}
    for item in data:
        add_item = pea.interface_interaction(item['content'])
        add_item['id'] = item['id']
        return_dic['data'].append(add_item)
    interface_usage += 1
    if interface_usage % 10 == 0:
        pea.ppro.load_wgyd_info()
    return return_dic


if __name__ == '__main__':
    print(get_addr({"data": [{"content": "390_920_A_！1560_3960_A_！4650_7070_A_很高兴为您服务。7640_11500_A_哎你好那个你帮我查一下我们家这个网上不去了。12280_22660_A_宽带是吧对上面说一下安装的位置是在哪儿上去开通了那个那个鼓楼上城二期十五号幺三零四？23410_24380_A_您稍等。25520_27530_A_光猫上现在有没有闪红灯？28650_30170_A_光猫上。30720_34580_A_么么闪红灯都是的话则是皇马也不知道。35540_39030_A_就是除了那个路由器和连接电视的机顶盒。39400_40540_A_！40840_42660_A_就是运动没上红灯。43410_45850_A_稍微这边我帮您检测一下稍等。46180_47230_A_！49830_54690_A_帮您看了一下您刚才说的安装位置线路是没有故障问题的。54990_59480_A_如果说连接不上呢我这儿帮您做一个快速的恢复处理操作吧？59890_92110_A_您稍后只需要把光猫和路由器切断电源等待十分钟十分钟过后再次连接就可以恢复正常了哈等十分钟是吧我刚才打过了霸王以后插头也不管我走吧了就插上了也得先给我回复一下然后我再查是吧那我这儿帮您把端口给您重新启动一下稍还需要爸爸妈妈爸爸了就行了对现在锻炼就可以先哎好嘞麻烦了不客气还有其他可以帮您吗那个没有了我先看看吧？92480_95550_A_套餐感谢来电麻烦稍后做评价。", "id": "00deee82284a474c97ceeb3906122c61"}]}))
