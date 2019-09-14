#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:menghuanlater

from . import process as ppro
import re
from . import filename as myfile
import thulac
from copy import deepcopy
import operator

jieba = ppro.jieba
posseg = ppro.posseg

# 加载词典#
thulac_obj = thulac.thulac()
invalid_pos = ['u', 'v', 'e', 'y', 'o', 'w', 'b', 'r', 'eng']

self_pos_set = ['city', 'area', 'town', 'village', 'station']

# 房地产列表
BX_0 = ['宿舍楼', '宿舍', '大厦', '苑', '写字楼', '商务中心', '小区', '花园', '图书馆', '博物馆', '广场', '步行街', '座', '都市', '百货',
        '别墅', '住宅', '住宅楼', '家属楼', '家属院', '龙城', '大学城', '城', '新村', '会展中心', '商务', '社区', '园区', '产业园', '创业园',
        '基地', '工业区', '示范园', '示范区', '湾', '港', '家园', '庭', "工业园", "金贸", "经贸", "巷", "堡", "家属院", "百货大楼", "百货大厦",
        "汽车城", "商务楼", '公寓']
# 公司企业
BX_1 = ['公司', '事务所', '律师所', '工厂', '旅行社', '旅游局', '印刷厂', '厂', '火场']
# 教育培训
BX_2 = ['美术馆', '大学', '中学', '小学', '学院', '学校', '初中', '高中', '幼儿园', '学前班', '科技馆', '教育', '早教',
        '学会', '函授站']
# 购物
BX_3 = ['超市', '商场', '商城', '文具店', '便利店', '购物中心', '专卖店', '科技', '家电', '数码', '经销处', '市场', '商店', '购物']
# 医疗
BX_4 = ['医院', '急救中心', '诊所', '药店', '药房', '康复中心', '药业']
# 旅游景点
BX_5 = ['公园', '山谷', '景区', '寺庙', '寺', '山', '游乐场', '乐园', '索道', '栈道', '教堂', '将军府', '植物园', '动物园',
        '少年宫', '海洋馆']
# 交通设施
BX_6 = ['加油站', '加气战', '收费站', '港口', '码头', '服务区', '火车站', '高铁站', '地铁站', '客运', '飞机场', '桥', '车站', '东站',
        '西站', '南站', '北站']
# 休闲娱乐
BX_7 = ['ktv', 'KTV', '电影院', '网吧', '网咖', '音乐厅', '歌舞厅', '台球', '游戏厅', '会所', '养生馆', '会馆', '体育馆', '体育场']
# 酒店
BX_8 = ['宾馆', '酒店', '旅社', '旅舍', '招待所']
# 美食
BX_9 = ['饭店', '餐馆', '快餐店', '餐厅', '咖啡厅', '酒吧', '茶楼', '甜品店', '蛋糕', '汉堡', '肯德基', '麦当劳', '金拱门',
        '必胜客', '披萨']
# 政府机构
BX_10 = ['派出所', '警察局', '文化局', '监督所', '交通局', '检察局', '供电局', '院', '村', '镇', '庄', '乡', '部队']
# 金融
BX_11 = ['银行', '信用社', '典当行']
# 文化传媒
BX_12 = ['晚报', '报社', '新闻社', '传媒', '电视台', '广播台', '剧团', '展览馆', '会堂']

station_suffix = set([u'快递', u'菜市场', u'交叉口', u'校区', u'南校区', u'北校区', u'东校区', u'北校区', u'中校区', u'东南校区', u'西南校区',
                      u'东北校区', u'西北校区', u'农场', '工作站', '物流', '协会', '联合社', '合作社', '景区', '东区', '南区', '西区', '北区'] + \
                     BX_0 + BX_1 + BX_2 + BX_3 + BX_4 + BX_5 + BX_6 + BX_7 + BX_8 + BX_9 + BX_10 + BX_11 + BX_12)

prob_pos = ['n', 'nz', 'nr', 'nt', 's', 'a', 'm', 'nrt', 'mq']

school_region = [u'南校区', u'北校区', u'东校区', u'北校区', u'中校区', u'东南校区', u'西南校区', u'东北校区', u'西北校区', u'东小区',
                 u'西小区', u'南小区', u'北小区']

number_list = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'幺']

# 干扰数字删除
d_p1 = re.compile("([零一二三四五六七八九十百幺]{6,})|(一万零一号)|(之前的一百[一二三四五六七八九十零]{1,3}号)|"
                  "(请到[一二三四五六七八九十]{1,2}号)|(打一万零一[转按选][一二三四五六七八九十零]号)|"
                  "([一二三四五六七八九十零]号几点)|(幺号码)|(打一万零[转按选][一二三四五六七八九十零]号)|"
                  "(ip[一二三四五六七八九十零幺]{1,3}号)|(工号[是为]?[一二三四五六七八九十零]{1,9}号)|"
                  "(ip(.){0,10}[一二三四五六七八九十零幺]{3,20})|([一二三四五六七八九十零]{1,3}号公寓)|"
                  "((登[录|陆])[一二三四五六七八九十零百拾]号)")
# 优先级(一级二级分类-->后期优化的详细过滤选择)
'''
location_priority = ["房地产-住宅区", "教育培训-高等院校", "购物-百货商场", "购物-购物中心", "医疗-综合医院", "旅游景点-动物园",
                     "旅游景点-公园", "旅游景点-文物古迹", "旅游景点-景点", "旅游景点-海滨浴场", "旅游景点-水族馆", "交通设施-火车站",
                     "交通设施-长途汽车站", "交通设施-飞机场", "房地产-写字楼", "房地产-宿舍", "房地产-其他", "酒店-星级酒店",
                     "教育培训-小学", "教育培训-中学", "交通设施-收费站", "交通设施-服务区", "交通设施-港口", "交通设施-桥",
                     "政府机构-中央机构", "政府机构-公检法机构", "政府机构-政治教育机构", "政府机构-各级政府", "交通设施-加油加气站",
                     "交通设施-停车场", "医疗-疗养院", "医疗-疾控中心", "医疗-专科医院", "医疗-急救中心", "旅游景点-游乐园",
                     "旅游景点-博物馆", "旅游景点-教堂", "旅游景点-风景区", "旅游景点-植物园", "酒店-公寓式酒店", "教育培训-图书馆",
                     "教育培训-科研机构", "教育培训-科技馆", "教育培训-成人教育", "休闲娱乐-休闲广场", "休闲娱乐-电影院", "休闲娱乐-剧院",
                     "休闲娱乐-度假村", "公司企业-园区", "公司企业-其他", "公司企业-厂矿", "公司企业-公司", "公司企业-农林园艺",
                     "金融-信用社", "金融-银行", "文化传媒-新闻出版", "文化传媒-美术馆", "文化传媒-广播电视", "文化传媒-艺术团体",
                     "政府机构-行政单位", "政府机构-涉外机构", "政府机构-民主党派", "政府机构-党派团体", "政府机构-社会团体",
                     "政府机构-福利机构", "交通设施-充电站"]
'''
location_priority = ['房地产', '公司企业', '教育培训', '购物', '医疗', '旅游景点', '交通设施', '休闲娱乐', '酒店', '美食', '政府机构',
                     '金融', '文化传媒']
# 地点识别的全局变量
INF = 100


class AddrInfoExtract:
    def __init__(self):
        self.__copy_dic = None
        self.__vital_dic = {}
        self.__seg_out = []  # 记录分词结果
        self.__traverse_index = 0  # 记录分词遍历索引的位置
        self.__global_str = ""
        self.__complete_signal = False

    # 模块入口函数
    def module_entrance(self):
        word, pos = self.fetch_data()
        if word == 'NULL' and pos == 'NULL':
            return  # 识别结束
        # 直接终止进入下一个
        elif word in ["公司", "小区", "村子"]:
            return
        elif pos == 'province':
            self.module_entrance()
        elif pos == 'city':
            self.__vital_dic['tag'] = 'city'
            self.__vital_dic['city'] = word
            self.__vital_dic['name'] = word
            self.city_module()
        elif pos == 'area':
            self.__complete_signal = True
            self.__vital_dic['tag'] = 'area'
            self.__vital_dic['area'] = word
            self.__vital_dic['name'] = word
            self.area_module()
        elif pos == 'town':
            self.__complete_signal = True
            self.__vital_dic['tag'] = 'town'
            self.__vital_dic['town'] = word
            self.__vital_dic['name'] = word
            self.town_module()
        elif pos == 'village':
            self.__complete_signal = True
            self.__vital_dic['tag'] = 'village'
            self.__vital_dic['village'] = word
            self.__vital_dic['name'] = word
            self.village_module()
        elif 'station' in pos:
            m = deepcopy(self.__vital_dic)
            self.__vital_dic['tag'] = pos
            self.__complete_signal = True
            self.__vital_dic['name'] = word
            if len(word) <= 2:
                self.__copy_dic = deepcopy(self.__vital_dic)
                self.__vital_dic = m
                self.addr_module(word, pos)
        elif pos == 'ns':
            self.__complete_signal = True
            tag, name = ns_judge(word, False)
            if tag == 'city':
                self.__vital_dic['tag'] = 'city'
                self.__vital_dic['city'] = name
                self.__vital_dic['name'] = name
                self.city_module()
            elif tag == 'area':
                self.__vital_dic['tag'] = 'area'
                self.__vital_dic['area'] = name
                self.__vital_dic['name'] = name
                self.area_module()
            elif tag == "province":
                self.module_entrance()
            else:
                self.addr_module(name, 'ns')
        elif pos in prob_pos:
            self.__complete_signal = True
            self.addr_module(word, pos)
        else:
            return

    # city模块
    def city_module(self):
        word, pos = self.fetch_data()
        if word == 'NULL' and pos == 'NULL':
            return
        if pos == 'ns':
            tag, word2 = ns_judge(word)
            if tag != 'prefix':
                pos = tag
                word = word2
            else:
                self.__complete_signal = True
                self.addr_module(word2, 'ns')
        if pos == 'area':
            self.__vital_dic['tag'] = 'area'
            self.__vital_dic['area'] = word
            self.__vital_dic['name'] = word
            self.area_module()
        elif pos == 'town':
            self.__vital_dic['tag'] = 'town'
            self.__complete_signal = True
            self.__vital_dic['town'] = word
            self.__vital_dic['name'] = word
            self.town_module()
        elif pos == 'village':
            self.__complete_signal = True
            self.__vital_dic['tag'] = 'village'
            self.__vital_dic['village'] = word
            self.__vital_dic['name'] = word
            self.village_module()
        elif 'station' in pos:
            m = deepcopy(self.__vital_dic)
            self.__complete_signal = True
            self.__vital_dic['tag'] = pos
            self.__vital_dic['name'] = word
            if len(word) <= 2:
                self.__copy_dic = deepcopy(self.__vital_dic)
                self.__vital_dic = m
                self.addr_module(word, pos)
        elif (pos in ['city', 'province']) or (pos in prob_pos):
            self.__complete_signal = True
            self.addr_module(word, pos)
        else:
            return
        return

    # country(area)模块
    def area_module(self):
        word, pos = self.fetch_data()
        if word == 'NULL' and pos == 'NULL':
            return
        if pos == 'ns':
            tag, word2 = ns_judge(word)
            if tag != 'prefix':
                pos = tag
                word = word2
            else:
                self.__complete_signal = True
                self.addr_module(word2, 'ns')
        if pos == 'town':
            self.__vital_dic['tag'] = 'town'
            self.__vital_dic['town'] = word
            self.__vital_dic['name'] = word
            self.town_module()
        elif pos == 'village':
            self.__complete_signal = True
            self.__vital_dic['tag'] = 'village'
            self.__vital_dic['village'] = word
            self.__vital_dic['name'] = word
            self.village_module()
        elif 'station' in pos:
            m = deepcopy(self.__vital_dic)
            self.__complete_signal = True
            self.__vital_dic['tag'] = pos
            self.__vital_dic['name'] = word
            if len(word) <= 2:
                self.__copy_dic = deepcopy(self.__vital_dic)
                self.__vital_dic = m
                self.addr_module(word, pos)
        elif (pos in ['city', 'area', 'province']) or (pos in prob_pos):
            self.__complete_signal = True
            self.addr_module(word, pos)
        else:
            return
        return

    # town模块
    def town_module(self):
        word, pos = self.fetch_data()
        if word == 'NULL' and pos == 'NULL':
            return
        if pos == 'ns':
            tag, word2 = ns_judge(word)
            if tag != 'prefix':
                pos = tag
                word = word2
            else:
                self.addr_module(word2, 'ns')
        if pos == 'village':
            self.__vital_dic['tag'] = 'village'
            self.__vital_dic['village'] = word
            self.__vital_dic['name'] = word
            self.village_module()
        elif 'station' in pos:
            m = deepcopy(self.__vital_dic)
            self.__vital_dic['tag'] = pos
            self.__vital_dic['name'] = word
            if len(word) <= 2:
                self.__copy_dic = deepcopy(self.__vital_dic)
                self.__vital_dic = m
                self.addr_module(word, pos)
        elif (pos in ['city', 'area', 'town', 'province']) or (pos in prob_pos):
            self.addr_module(word, pos)
        else:
            return
        return

    # village模块
    def village_module(self):
        # 暂时作为保留函数,后面方位等具体地点识别需要
        return

    # 复杂的地点识别模块
    # param:prefix作为前缀, attribute是当前传进来时识别的词性
    def addr_module(self, prefix, attribute):
        if prefix in ["交口", "大桥"]:
            return
        if attribute == "nrt":
            attribute = "nr"
        if attribute == 'ns':
            tmp_out = thulac_obj.cut(prefix)
            if len(tmp_out) != 1 and tmp_out[0][1] not in [attribute, 'n', 'nt', 'ni', 'nz', 's', 'j', 'g', 'f', 'a'] \
                    and self.__m_and_q(tmp_out) and tmp_out[1][1] not in ['n', 'ns', 'np', 'nz', 'ni']:
                return
        self.__global_str = prefix
        if attribute in ['province', 'city', 'town', 'area', 'village', 'nt']:
            self.__vital_dic['name'] = prefix
        if attribute in ['province', 'city', 'town', 'area', 'village', 'ns', 'a', 'nz', 'nr', 'j']:
            if attribute in ['nr', 'nz']:
                tmp_out = thulac_obj.cut(prefix)
                if len(tmp_out) != 1 and tmp_out[0][1] not in [
                    attribute, 'n', 'np', 'ni', 'nz', 'ns', 's', 'a', 'j', 'g', 'f'] and self.__m_and_q(tmp_out) and \
                        tmp_out[1][1] not in ['n', 'ns', 'np', 'nz', 'ni']:
                    return
                else:
                    self.state_s2(prefix, True)
                    return
            self.state_s1()
        elif attribute in ['m', 'mq'] and check_number(prefix):
            self.state_s1()
        elif "station" in attribute:
            self.state_s1()
        elif attribute in ['nt', 's']:
            tmp_out = thulac_obj.cut(prefix)
            if len(tmp_out) > 1 and tmp_out[0][1] != 'a' and self.__m_and_q(tmp_out):
                return
            if tmp_out[0][1] in ['ns', 'n', 'ni', 'nz', 'f', 'j', 'a', 'g'] or (
                    len(tmp_out) > 1 and tmp_out[1][1] in ['n', 'ns', 'np', 'nz', 'ni']):
                self.state_s1()
            elif tmp_out[0][1] not in ['nt', 's'] and self.__m_and_q(tmp_out):
                return
            self.__vital_dic['tag'] = 'place'
            return
        elif attribute == 'n':
            tmp_out = thulac_obj.cut(prefix)
            if len(tmp_out) != 1 and tmp_out[0][1] not in ['n', 'ns', 'ni', 'np', 'nz', 'j', 'g', 'f'] \
                    and self.__m_and_q(tmp_out) and tmp_out[1][1] not in ['n', 'ns', 'np', 'nz', 'ni']:
                return
            self.state_s2(prefix, False)
        return

    # 复杂地点识别模块的状态组模块
    def state_s1(self):
        word, pos = self.fetch_data()
        if word == 'NULL' and pos == 'NULL':
            # 进行一次检查,检查目前的global_str是否包含路/街道等信息
            if ppro.street_road_judge(self.__global_str) and self.__global_str not in ["道路", "街道"]:
                self.__vital_dic['town'] = self.__global_str
                self.__vital_dic['name'] = self.__global_str
                self.__vital_dic['tag'] = 'town'
                self.__global_str = ""
                self.town_module()
            # 是否为”曼城“之类的城市地点或者村/小区
            elif len(self.__global_str) >= 2 and self.__global_str[-1] in ['城', '园', '厦', '苑', '寓', '区', '村', '庭', '湾',
                                                                           '巷', '铺', '垣',
                                                                           "堡"]:
                # 加强判断
                if self.__global_str in ['小区', '花园', '公寓', '庄园', '大厦', '公园', '社区', '地区', '县城', '市区', '乡村']:
                    return
                self.__vital_dic['name'] = self.__global_str
                self.__vital_dic['tag'] = 'place'
                return
        if pos in ['s', 'nt'] or 'station' in pos:
            # 需要对词尾进行检验,否则杂数据很多
            if word[-1] in ["下", "上", "内", "面", "中", "左", "前", "后", "里"]:
                return
            self.__global_str += word
            self.__vital_dic['name'] = self.__global_str
            self.__vital_dic['tag'] = 'place'
            return
        if pos in ['a', 'nr', 'ns', 'm', 'city', 'area', 'province', 'j', 'nz', 'mq']:
            self.__global_str += word
            if pos == "city":
                self.__vital_dic['city'] = word
            if pos == "area":
                self.__vital_dic['area'] = word
            if pos in ['ns', 'nr', 'nz']:
                tmp = thulac_obj.cut(word)
                if len(tmp) != 1 and tmp[0][1] not in ['a', 'n', 'ni', 'nz', 'ns', 'np', 'f', 's', 'j', 'g', 'ng'] \
                        and self.__m_and_q(tmp) and tmp[1][1] not in ['n', 'ns', 'np', 'nz', 'ni']:
                    self.__global_str = ""
                    return
                else:
                    self.state_s2(word, True)
                    return
            self.state_s1()
        elif pos in ['village', 'town']:
            self.__global_str += word
            self.__vital_dic['name'] = self.__global_str
            if pos == "town" and (word[-2:] in ["大街", "大道", "中路", "东路", "东街", "西路", "西街", "南路", "南街", "北路", "北街"] or
                                  word[-1] in ['街', '路', '道', '镇', '乡']):
                if word[-1] in ['镇', '乡']:
                    self.__vital_dic['town'] = self.__vital_dic['name'] = word
                else:
                    self.__vital_dic['town'] = self.__vital_dic['name']
                self.__vital_dic['tag'] = 'town'
                self.__global_str = ""
                self.town_module()
            else:
                self.__vital_dic['tag'] = 'place'
                self.state_s1()
        elif pos in ['n', 'ng']:
            tmp_out = thulac_obj.cut(word)
            if len(tmp_out) != 1 and tmp_out[0][1] not in ['n', 'np', 'ni', 'nz', 'ns', 'j', 'g', 'f', 'a', 'ng'] \
                    and self.__m_and_q(tmp_out) and tmp_out[1][1] not in ['n', 'ns', 'np', 'nz', 'ni']:
                return
            self.__global_str += word
            self.state_s2(word, True)
        elif word == '道':
            self.__vital_dic['town'] = self.__global_str + word
            self.__vital_dic['name'] = self.__vital_dic['town']
            self.__vital_dic['tag'] = 'town'
            self.town_module()
        # 是否为”曼城“之类的城市地点,针对上层传入的ns类短地点
        elif len(self.__global_str) >= 2 and self.__global_str[-1] in ['城', '园', '厦', '苑', '寓', '区', '村', '湾', '庭', '巷',
                                                                       "堡", '铺', '垣']:
            if self.__global_str in ['小区', '花园', '公寓', '庄园', '大厦', '公园', '社区', '地区', '县城', '市区', '乡村']:
                return
            self.__vital_dic['name'] = self.__global_str
            self.__vital_dic['tag'] = 'place'
            return

    def state_s2(self, obj, mode):
        if ppro.street_road_judge(obj) or obj[-1] in ['乡', '镇']:
            if mode or (len(self.__global_str) >= 3 and self.__global_str[-1] in ['路', '街']):
                self.__vital_dic['town'] = self.__global_str
                self.__vital_dic['name'] = self.__global_str
                self.__vital_dic['tag'] = 'town'
                self.__global_str = ""
                self.town_module()
        elif self.contain_station_suffix(obj):
            if (mode and len(obj) > 1) or len(obj) >= 4:
                self.__vital_dic['name'] = self.__global_str
                self.__global_str = ""
                self.__vital_dic['tag'] = 'place'
            else:
                self.state_s1()
        else:
            self.state_s1()

    # 检查获取的词是否有地点结束尾缀
    @staticmethod
    def contain_station_suffix(obj):
        for x in station_suffix:
            if len(x) > len(obj):
                continue
            if obj[len(obj) - len(x):len(obj)] == x:
                return True
        return False

    # 取分词列表的数据
    def fetch_data(self):
        if self.__traverse_index >= len(self.__seg_out):
            return 'NULL', 'NULL'
        else:
            _x, y = self.__seg_out[self.__traverse_index]
            self.__traverse_index += 1
            return _x, y

    # 根据name识别其中隐含的city
    def __recog_city_from_name(self):
        if self.__vital_dic['tag'] in ['city', 'area', 'town', 'village']:
            return
        if 'city' not in self.__vital_dic.keys() or self.__vital_dic['city'] == "":
            for i in ['石家庄', '承德', '沧州', '唐山', '张家口', '邯郸', '保定', '秦皇岛', '邢台', '廊坊', '衡水']:
                if i in self.__vital_dic['name']:
                    self.__vital_dic['city'] = i
                    return

    # thulac m+q的形式,错误认为分词错误,导致缺失提取
    @staticmethod
    def __m_and_q(cut_list):
        if len(cut_list) == 2 and cut_list[0][1] == "m" and cut_list[1][1] == "q":
            if cut_list[1][0] in ["家", "队", "巷", "庄", "村", "堡"]:
                return False
        return True

    # 单句话中的地址识别抽取(有可能一句话中存在多个地址)
    def get_addr(self, sentence):
        addr_list = []
        for m, n in posseg.lcut(sentence.replace("村儿", "村")):
            if n == 'ug' or n == 'x':
                continue
            else:
                self.__seg_out.append((m, n))
        length = len(self.__seg_out)
        # 使用循环去查看index是否到达边界
        # print(self.__seg_out)
        while self.__traverse_index < length:
            self.__copy_dic = None
            self.module_entrance()
            # 先检查copy_dic存不存在
            if self.__copy_dic is not None:
                addr_list.append(self.__copy_dic)
            # 地点补充识别模块
            if len(self.__vital_dic) > 0 and 'tag' in self.__vital_dic.keys() and 'name' in self.__vital_dic.keys():
                # 加强检测,根据name识别地级市
                self.__recog_city_from_name()
                if self.__vital_dic['name'] in ["国民党", "校园", "园区", "花园", "大银行", "公园", "公园小区", "中村",
                                                "书城", "片区", "家庭", "商场", "商城", "农村", "寒山", "法庭", "法院",
                                                "共产党", "小区", "小区小区", "东区", "南区", "西区", "北区", "新区", "县区",
                                                "小镇", "长城", "省公司", "市公司", "县公司", "苑", "城市", "城区", "县城",
                                                "家园"]:
                    self.__vital_dic["name"] = ""
                if len(self.__vital_dic['name']) >= 3 and self.__vital_dic['name'][-1] == "区" and self.__vital_dic[
                                                                                                      'name'][-3:] in \
                        ["长安区", "桥西区", "新华区", "陉矿区", "裕华区", "藁城区", "鹿泉区", "栾城区", "路南区", "路北区",
                         "古冶区", "开平区", "丰南区", "丰润区", "妃甸区", "海关区", "戴河区", "抚宁区", "邯山区", "丛台区",
                         "复兴区", "峰矿区", "肥乡区", "永年区", "桥东区", "桥西区", "竞秀区", "莲池区", "满城区", "清苑区",
                         "徐水区", "宣化区", "万全区", "崇礼区", "双桥区", "双滦区", "子矿区", "运河区", "广阳区", "安次区",
                         "桃城区", "冀州区"]:
                    self.__vital_dic["name"] = ""
                if self.__vital_dic['name'] in school_region:
                    addr_list = add_school_split_region(addr_list, self.__vital_dic['name'])
                    self.__vital_dic.clear()
                    continue
                if self.__vital_dic['name'] in ["幼儿园"]:
                    if len(addr_list) > 0 and "name" in addr_list[-1].keys() and len(addr_list[-1]['name']) > 0 and \
                            addr_list[-1]['name'][-1] in ["山", "城"]:
                        addr_list[-1]['name'] += self.__vital_dic['name']
                        self.__vital_dic.clear()
                        continue
                if len(self.__vital_dic['name']) >= 4 and self.__vital_dic['name'][0:2] in ['小区', '公寓', '县城', "记录",
                                                                                            "西区", "南区", "北区", "东区"]:
                    self.__vital_dic['name'] = self.__vital_dic['name'][2:]
                if "town" in self.__vital_dic.keys() and len(self.__vital_dic['town']) >= 4 and self.__vital_dic[
                                                                                                    'town'][0:2] in [
                    '小区', '公寓', '县城', "西区", "南区", "北区", "东区"]:
                    self.__vital_dic['town'] = self.__vital_dic['town'][2:]
                if len(self.__vital_dic['name']) >= 4 and self.__vital_dic['name'][0] in ['村', '区', '好', '姐']:
                    self.__vital_dic['name'] = self.__vital_dic['name'][1:]
                self.__vital_dic['signal'] = self.__complete_signal
                addr_list.append(deepcopy(self.__vital_dic))
                self.__vital_dic.clear()
            elif len(self.__vital_dic) > 0 and 'area' in self.__vital_dic.keys() and self.__vital_dic['area'] != "":
                addr_list.append({'city': '', 'area': self.__vital_dic['area'], 'name': self.__vital_dic['area'],
                                  'tag': 'area', 'signal': False})
                self.__vital_dic.clear()
            elif len(self.__vital_dic) > 0 and 'city' in self.__vital_dic.keys() and self.__vital_dic['city'] != "":
                addr_list.append({'city': self.__vital_dic['city'], 'name': self.__vital_dic['city'],
                                  'tag': 'city', 'signal': False})
                self.__vital_dic.clear()
            else:
                pass
        # print(addr_list)
        return addr_list


# 将街道、路、村、乡、镇、庄等全部设置为'n'
def set_default_pos_n():
    for x in ppro.street_road:
        jieba.add_word(x, 5, 'n')
    jieba.add_word('村', 5, 'n')
    jieba.add_word('乡', 5, 'n')
    jieba.add_word('镇', 5, 'n')
    jieba.add_word('庄', 5, 'n')
    jieba.add_word('堡', 5, 'n')
    jieba.add_word("庄村", 10, "n")
    jieba.add_word("正", 10, "a")
    jieba.add_word("东路", 100, "n")
    jieba.add_word("西路", 100, "n")
    jieba.add_word("大街", 1000000, "n")
    jieba.add_word("南路", 100, "n")
    jieba.add_word("北路", 100, "n")
    jieba.add_word("上东", 100, "a")
    jieba.add_word("上南", 100, "a")
    jieba.add_word("上北", 100, "a")
    jieba.add_word("上西", 100, "a")
    jieba.add_word("青年", 100, "a")
    jieba.add_word("太和", 1000, "a")


# 将某些词加入异常词集,统一使用ignore
def set_ignore():
    f = open(myfile.ignore_word, "r", encoding="UTF-8")
    for i in f.readlines():
        if i != "\n":
            jieba.add_word(i.replace("\n", "").replace("\r", ""), 10000, "ignore")


set_default_pos_n()
set_ignore()


# tag为place的权重识别,权重越高,等级越低
# ---> 如果没有,返回INF
def tag_of_place_weight(name):
    for i in BX_0:
        if i in name:
            return 0
    for i in BX_1:
        if i in name:
            return 1
    for i in BX_2:
        if i in name:
            return 2
    for i in BX_3:
        if i in name:
            return 3
    for i in BX_4:
        if i in name:
            return 4
    for i in BX_5:
        if i in name:
            return 5
    for i in BX_6:
        if i in name:
            return 6
    for i in BX_7:
        if i in name:
            return 7
    for i in BX_8:
        if i in name:
            return 8
    for i in BX_9:
        if i in name:
            return 9
    for i in BX_10:
        if i in name:
            return 10
    for i in BX_11:
        if i in name:
            return 11
    for i in BX_12:
        if i in name:
            return 12
    return INF


# 有限状态机分层次模块

# ns判别函数
# param:jieba识别的ns的词
# return:ns是省/市/县/区正经地址前缀,利用jieba去识别下属性
def ns_judge(target, have_city=True):
    if have_city and target == '河北':
        return 'prefix', target
    elif not have_city and target == '河北':
        return "province", "河北省"

    rs1 = posseg.lcut(target + "市")
    w, _p = rs1[0]
    if _p == "city":
        return 'city', w
    elif _p == "area":
        return "area", w
    rs1 = posseg.lcut(target + "区")
    w, _p = rs1[0]
    if _p == 'area':
        return "area", w
    rs1 = posseg.lcut(target + "县")
    w, _p = rs1[0]
    if _p == 'area':
        return "area", w
    return "prefix", target


# 检查数词是否有用
def check_number(word):
    for item in number_list:
        if item in word:
            return True
    return False


# 补全以及五高一地识别的相关字段填充
def complete_and_wgyd_rec(addr):
    if len(addr) == 0:
        return addr
    if "signal" not in addr.keys() or addr['signal']:
        keys = addr.keys()
        if 'city' not in keys:
            addr['city'] = ""
        if 'area' not in keys:
            addr['area'] = ""
        if 'town' not in keys:
            addr['town'] = ""
        if 'village' not in keys:
            addr['village'] = ""
        addr = ppro.station_complete(addr)
    addr['wgyd_code'] = str(ppro.wgyd_recognize(addr['name'], city=addr['city'], area=addr['area']))
    return addr


# 学院学校等加上校区
def add_school_split_region(addr_list, region_name):
    for inc in range(0, len(addr_list)):
        item = addr_list[inc]['name']
        if '学校' in item or '学院' in item or '大学' in item:
            addr_list[inc]['name'] += region_name
    return addr_list


# 补充小区/国际尾缀
def append_district(addr_list, init_content):
    if len(addr_list) == 0:
        return addr_list
    else:
        for index, item in enumerate(addr_list):
            if "name" in item.keys() and item["tag"] not in ["city", "area", "town", "village"]:
                if len(item["name"]) >= 2 and (item["name"] + "小区") in init_content and "小区" not in item["name"]:
                    addr_list[index]["name"] += "小区"
                    addr_list[index]["add_tag"] = "小区"
                elif len(item["name"]) >= 2 and (item["name"] + "国际") in init_content and "国际" not in item["name"]:
                    addr_list[index]["name"] += "国际"
                elif index > 0 and addr_list[index - 1]["tag"] == "village" and addr_list[index - 1]["name"][-1] in [
                    "村", "庄"] and \
                        item["tag"] not in ["city", "area", "town", "village"] and item["name"][-1] in ["寺", "堂", "祠"]:
                    if (addr_list[index - 1]["name"] + item["name"]) in init_content:
                        addr_list[index]["name"] = addr_list[index - 1]["name"] + addr_list[index]["name"]
        return addr_list


# 读取待处理字符串,识别地点列表
# param:需要处理的字符串
# return: 地址
def get_location(text):
    addr_list = []
    p = re.compile("(\d*_\d*_)A_")
    text = re.sub(p, "A_", text)
    sentences = text.split('A_')
    for _x in sentences:
        addr_get_object = AddrInfoExtract()
        item = addr_get_object.get_addr(_x)
        # print(item)
        if len(item) > 0:
            addr_list.extend(item)
    # 对话地址筛选
    # print(addr_list)
    addr = complete_and_wgyd_rec(second_layer_filter_addr(append_district(addr_list, text)))
    return addr


# 根据提取出的所有的city,area进行匹配校验,返回最终的city, area
def decide_final_city_area(city_dic, area_dic):
    """
    :param city_dic: 地级市表
    :param area_dic: 县级市表
    :return: city, area
    """
    if len(city_dic) == 0 and len(area_dic) > 0:
        return "", sorted(area_dic.items(), key=lambda t: t[1], reverse=True)[0][0]
    elif len(city_dic) > 0 and len(area_dic) == 0:
        return sorted(city_dic.items(), key=lambda t: t[1], reverse=True)[0][0], ""
    elif len(city_dic) == 0 and len(area_dic) == 0:
        return "", ""
    match_list = []
    for i in city_dic.keys():
        for j in area_dic.keys():
            if ppro.is_city_county_match(city=i, county=j):
                match_list.append("%s|%s" % (i, j))
    if len(match_list) == 0:
        return sorted(city_dic.items(), key=lambda t: t[1], reverse=True)[0][0], ""
    else:
        return match_list[0].split("|")


# 第二层过滤,针对多个句子的地点过滤
def second_layer_filter_addr(addr_list):
    if len(addr_list) == 0:
        return {}
    # 先进行重复项删除
    addr_list = sorted(addr_list, key=operator.itemgetter('name'))
    # 进行优先选择
    station_list = []
    town_dic = {}
    area_dic = {}
    city_dic = {}
    for x in addr_list:
        if x['tag'] == 'place' or 'station' in x['tag'] or x['tag'] == 'village':
            station_list.append(x)
            # 加强性检查,如果有市/县/镇,则加入区域dic
            if 'town' in x.keys() and x['town'] != '' and x['town'][-1] in ['镇', '乡', '街', '路']:
                if x['town'] not in town_dic.keys():
                    town_dic[x['town']] = 1
                else:
                    town_dic[x['town']] += 1
            if 'area' in x.keys() and x['area'] != '':
                if x['area'] not in area_dic.keys():
                    area_dic[x['area']] = 1
                else:
                    area_dic[x['area']] += 1
            if 'city' in x.keys() and x['city'] != '':
                if x['city'] not in city_dic.keys():
                    city_dic[x['city']] = 1
                else:
                    city_dic[x['city']] += 1
        elif x['tag'] == 'town':
            if x['town'] in ["小镇", "弘道", "道路", "大路", "大道"]:
                continue
            if x['town'] not in town_dic.keys():
                town_dic[x['town']] = 1
            else:
                town_dic[x['town']] += 1
            if 'area' in x.keys() and x['area'] != '':
                if x['area'] not in area_dic.keys():
                    area_dic[x['area']] = 1
                else:
                    area_dic[x['area']] += 1
            if 'city' in x.keys() and x['city'] != '':
                if x['city'] not in city_dic.keys():
                    city_dic[x['city']] = 1
                else:
                    city_dic[x['city']] += 1
        elif x['tag'] == 'area':
            if x['area'] not in area_dic.keys():
                area_dic[x['area']] = 1
            else:
                area_dic[x['area']] += 1
            if 'city' in x.keys() and x['city'] != '':
                if x['city'] not in city_dic.keys():
                    city_dic[x['city']] = 1
                else:
                    city_dic[x['city']] += 1
        else:
            if x['city'] not in city_dic.keys():
                city_dic[x['city']] = 1
            else:
                city_dic[x['city']] += 1
    # 暴力组装
    # 做一个预组装字典{city, area, town}
    assembly = {'town': '', 'city': decide_final_city_area(city_dic, area_dic)[0],
                'area': decide_final_city_area(city_dic, area_dic)[1]}
    if len(town_dic) > 0:
        assembly['town'] = sorted(town_dic.items(), key=lambda t: (t[1], len(t[0])), reverse=True)[0][0]
    # print(station_list)
    if len(station_list) == 1:
        # 对单独的station做地区填充
        if 'city' not in station_list[0].keys() or station_list[0]['city'] == "":
            station_list[0]['city'] = assembly['city']
        else:
            station_list[0]['city'] = ppro.get_standard_administration_name(station_list[0]['city'])
        if 'town' not in station_list[0].keys() or station_list[0]['town'] == "":
            station_list[0]['town'] = assembly['town']
        if 'area' not in station_list[0].keys() or station_list[0]['area'] == "":
            if station_list[0]['city'] != "" and assembly['area'] != "" and \
                    ppro.is_city_county_match(station_list[0]['city'], assembly['area']):
                station_list[0]['area'] = assembly['area']
            elif station_list[0]['city'] == "":
                station_list[0]['area'] = assembly['area']
        return handle_extra_prefix(station_list[0])
    elif len(station_list) < 1:
        if len(town_dic) > 0:
            return {'tag': 'town', 'city': assembly['city'], 'area': assembly['area'], 'town': assembly['town'],
                    'name': assembly['town'], 'signal': True}
        if len(area_dic) > 0:
            return {'tag': 'area', 'city': assembly['city'], 'area': assembly['area'], 'name': assembly['area'],
                    'signal': True}
        return {'tag': 'city', 'city': assembly['city'], 'name': assembly['city'], 'signal': True}
    else:
        # 村的话设置为政府机构同等级
        new_station_list = []
        for k in station_list:
            if k['name'] in ['东小区', '南小区', '北小区', '西小区']:
                k['weight'] = INF
            if k['tag'] == "village":
                k['weight'] = location_priority.index('政府机构')
            elif k['tag'] == 'place':
                k['weight'] = tag_of_place_weight(k['name'])
            else:
                big = int((k['tag'].replace("station", "").split('_'))[0])
                name = ppro.big_tag[big]
                if name in location_priority:
                    k['weight'] = location_priority.index(name)
                else:
                    k['weight'] = INF
            append_flag = True
            for item in new_station_list:
                a = deepcopy(item)
                a.pop("count")
                if operator.eq(a, k):
                    append_flag = False
                    item['count'] += 1
                    break
            if append_flag:
                k['count'] = 1
                new_station_list.append(k)
        station_list = sorted(new_station_list,
                              key=lambda t: (
                                  t['weight'], max(100 - len(t['name']), 96), 100 - t['count'], 100 - len(t['name'])))
        target = station_list[0]
        if ('city' not in target.keys()) or target['city'] == "":
            target['city'] = assembly['city']
        if ('area' not in target.keys()) or target['area'] == "":
            target['area'] = assembly['area']
        if ('town' not in target.keys()) or target['town'] == "":
            target['town'] = assembly['town']
        return handle_extra_prefix(target)


# 处理小区词前面的多余赘述问题
def handle_extra_prefix(station_dic):
    if station_dic["name"] == "" and len(station_dic["name"] <= 4):
        return station_dic
    extra_num_p = re.compile("[零一二三四五六七八九十百]{1,5}号")
    m = re.search(extra_num_p, station_dic["name"])
    if m is not None and m.start() == 0:
        station_dic["name"] = station_dic["name"].replace(m.group(0), "")
    if station_dic["name"][-2:] not in ["学校", "大学", "学院", "中学", "小学", "高中", "职高"] and len(station_dic["name"]) >= 6:
        # station_dic["name"] = station_dic["name"].replace(station_dic["city"], "").replace(station_dic["area"], "")
        if station_dic["city"] != "" and station_dic["city"] in station_dic["name"]:
            index = station_dic["name"].rfind(station_dic["city"])
            if len(station_dic["name"]) - index >= 3:
                station_dic["name"] = station_dic["name"][index+len(station_dic["city"]):]
        if station_dic["city"] != "" and station_dic["city"] not in station_dic["name"] and \
                station_dic["city"][0:len(station_dic["city"])-1] in station_dic["name"]:
            index = station_dic["name"].rfind(station_dic["city"][0:len(station_dic["city"])-1])
            if len(station_dic["name"]) - index >= 3:
                station_dic["name"] = station_dic["name"][index + len(station_dic["city"]) - 1:]
        if station_dic["area"] != "" and station_dic["area"] in station_dic["name"]:
            index = station_dic["name"].rfind(station_dic["area"])
            if len(station_dic["name"]) - index >= 3:
                station_dic["name"] = station_dic["name"][index + len(station_dic["area"]):]
    return station_dic


# 与接口交互数据的函数
def interface_interaction(content):
    p = re.compile('\s+')
    pre_dic = get_location(re.sub(p, "", content))
    # 项转换
    return_dic = {'location_city': '', 'location_county': '', 'location_street': '', 'location_community': '',
                  'place_area': '', 'place_building': '', 'place_block': '', 'place_floor': '',
                  'place_orientation': '', 'window_place': ''}
    if len(pre_dic) == 0:
        return return_dic
    # 路和街道的处理,他们都是town
    if 'station' in pre_dic['tag'] or 'place' in pre_dic['tag'] or 'village' in pre_dic['tag']:
        return_dic['place_area'] = pre_dic['name']
    return_dic['window_place'] = pre_dic['wgyd_code']
    # 当区域词不存在且street是某某街 某某路的时候, 查询是否存在类似“秦皇西大街九号”、“新兴路二十四号”这种
    if return_dic['place_area'] == "" and pre_dic["town"] != "" and pre_dic["town"][-1] in ["路", "街"]:
        road_region_p = re.compile("%s[一二三四五六七八九十百]{1,5}号(附近)?" % pre_dic["town"])
        m = re.search(road_region_p, content)
        if m is not None:
            return_dic['place_area'] = m.group(0)
            pre_dic['tag'] = "station0_7"
            content = content.replace(m.group(0), "")
    # 根据pre_dic中的字段对return_dic进行补充
    keys = pre_dic.keys()
    if 'city' in keys:
        return_dic['location_city'] = ppro.get_standard_administration_name(pre_dic['city'])
    if 'area' in keys:
        return_dic['location_county'] = ppro.get_standard_administration_name(pre_dic['area'])
        if return_dic['location_city'] != "" and return_dic['location_county'] != "" \
                and not ppro.is_city_county_match(return_dic['location_city'], return_dic['location_county']):
            return_dic['location_county'] = ""
    if 'town' in keys:
        return_dic['location_street'] = pre_dic['town']
    # TODO: 根据country强制修改city,根据city强制修改wgyd
    if return_dic['location_county'] in ['雄县', '安新', '容城', '安新县', '容城县']:
        return_dic['location_city'] = '雄安新区'
    if return_dic['location_county'] == '滦县':  # 2018年9月撤滦县建立滦州市,原滦县应该全部改为滦州市
        return_dic['location_county'] = '滦州市'
    # 根据类别标签去进行场所标注
    if pre_dic['tag'] == 'place' or 'station' in pre_dic['tag']:
        noise_p = re.compile("(客服中心)[一二三四五六七八九十零]+号")
        content = re.sub(noise_p, "", content)
        name = pre_dic['name']
        lis1 = ['公司', '大厦', '学校', '学院', '校区', '大学', '酒店', '公园', '厂', '都市', '科技园', '贸', '公寓',
                '小学', '幼儿园', '中学', '初中', '高中', '城', '所', '办', '处', '站', '馆', '宫', '场', '一中', '二中']
        lis2 = ['区', '家园', '花园', '府', '苑', '公寓', '宿舍', '墅', '住宅', '院', '楼', '园区', '巷', '庭', '湾', "堡",
                '新村', "光华", "明珠", "万达", '景园', '百货']
        for x in lis1:
            if len(name) >= len(x) and name[-len(x):] == x:
                m = building_labeling(content)
                return_dic['place_building'] = m[0]
                return_dic['place_floor'] = m[1]
                return_dic['place_orientation'] = m[2]
                return return_dic
        for x in lis2:
            if len(name) >= len(x) and name[-len(x):] == x:
                m = housing_labeling(content)
                return_dic['place_building'] = m[0]
                return_dic['place_block'] = m[1]
                return_dic['place_floor'] = m[2]
                return_dic['place_orientation'] = m[3]
                return return_dic
        # 如果都没有执行,加强测试,对station0_开头的都视为小区
        if 'station0_' in pre_dic['tag']:
            m = housing_labeling(content)
            return_dic['place_building'] = m[0]
            return_dic['place_block'] = m[1]
            return_dic['place_floor'] = m[2]
            return_dic['place_orientation'] = m[3]
            return return_dic
    elif pre_dic['tag'] == 'village':
        return_dic['place_orientation'] = village_labeling(content)
    elif pre_dic['tag'] == 'town' and ppro.is_able_generate_street(pre_dic['name']):
        return_dic['place_orientation'] = road_labeling(content)
    return return_dic


# 场所标注函数
def building_labeling(content):
    content = re.sub(d_p1, "", content)

    p1 = re.compile("((([A-Z]?[零一二三四五六七八九十幺])|([零一二三四五六七八九十幺]+))座)|([零一二三四五六七八九十幺]+((号楼)|号))")
    p2 = re.compile("(([零一二三四五六七八九十百幺])+(层|层楼|楼))|((地下|负)[零一二三四五六七八九十幺]+层)")
    p21 = re.compile("[一二三四五六七八九幺]{1,2}零[一二三四五六七八九幺]")
    p22 = re.compile("([幺一二][零一二])零[一二三四五六七八九十百幺]{1,2}")
    p3 = re.compile("([往朝向路][东南西北中])|附近|门口|教室|图书馆|宿舍|[东南西北中][边门]|办公[室区]|休息室|卫生间|会议室")
    m1 = re.search(p1, content)
    m2 = re.search(p2, content)
    m21 = re.search(p21, content)
    m22 = re.search(p22, content)
    m3 = re.search(p3, content)
    lis = []
    if m1 is None:
        lis.append("")
    else:
        lis.append(m1.group(0))
    if m2 is None:
        if m21 is None:
            if m22 is None:
                lis.append("")
            else:
                lis.append(m22.group(0))
        else:
            lis.append(m21.group(0))
    else:
        lis.append(m2.group(0))
    if m3 is None:
        lis.append("")
    else:
        lis.append(m3.group(0))
    return lis


def housing_labeling(content):
    content = re.sub(d_p1, "", content)

    p1 = re.compile("([零一二三四五六七八九十百幺])+(号楼|[栋幢])")
    p11 = re.compile("([零一二三四五六七八九十百幺])+(号)")
    p2 = re.compile("([零一二三四五六七八九十百幺])+(单元)")
    p3 = re.compile("(([零一二三四五六七八九十百幺])+(层|层楼|楼))|((地下|负)[零一二三四五六七八九十幺]+层)")
    p31 = re.compile("[一二三四五六七八九幺]{1,2}零[一二三四五六七八九幺]")
    p32 = re.compile("([幺一二][零一二])零[一二三四五六七八九十百幺]{1,2}")
    p4 = re.compile("厨房|楼道|客厅|地下车库|车库|卧室|卫生间|阳台|书房|[东南西北中][门]|门口")
    m1 = re.search(p1, content)
    m11 = re.search(p11, content)
    m2 = re.search(p2, content)
    m3 = re.search(p3, content)
    m31 = re.search(p31, content)
    m32 = re.search(p32, content)
    m4 = re.search(p4, content)
    lis = []
    if m1 is None:
        if m11 is None:
            lis.append("")
        else:
            lis.append(m11.group(0))
    else:
        lis.append(m1.group(0))
    if m2 is None:
        lis.append("")
    else:
        lis.append(m2.group(0))
    if m3 is None:
        if m31 is None:
            if m32 is None:
                lis.append("")
            else:
                lis.append(m32.group(0))
        else:
            lis.append(m31.group(0))
    else:
        lis.append(m3.group(0))
    if m4 is None:
        lis.append("")
    else:
        lis.append(m4.group(0))
    return lis


def village_labeling(content):
    p = re.compile("村西口|村东口|村南口|村北口|村东|村西|村中|村南|村北|([往朝向][东南西北中])|([东南西北中][侧边])")
    m = re.search(p, content)
    if m is None:
        return ""
    else:
        return m.group(0)


def road_labeling(content):
    p = re.compile("路口|入口|出口|交叉口|交口|([往朝向路][东南西北中])|([东南西北中][侧边])")
    m = re.search(p, content)
    if m is None:
        return ""
    else:
        return m.group(0)


if __name__ == '__main__':
    # jieba.add_word("联合小区", 100, "station0_2")
    print(get_location("20510_22670_A_目标在同台路"))
