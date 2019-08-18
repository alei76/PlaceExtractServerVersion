#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:menghuanlater

import json
import operator
import Levenshtein
import sqlite3
from copy import deepcopy
from . import filename as myfile
import jieba
import pymysql
from jieba import posseg

g_json_list = []
batch = 10000
db = sqlite3.connect(myfile.sqlite_db_url, check_same_thread=False)
street_road = {u'街道', u'大道', u'路', u'街', u'大街', u'道', u'中路', u'东路', u'西路', u'南路', u'北路',
               u'南街', u'西街', u'东街', u'北街', u'省道', u'乡道', u'国道', u'县道', u'公路', u'高速公路',
               u'专用公路', u'东街道', u'西街道', u'南街道', u'北街道', u'大桥', u'东桥', u'西桥', u'南桥', '北桥', '立交桥',
               '高架桥', '开发区', '铁路', '高速', '镇', '乡', '新区'}
big_tag = ['房地产', '美食', '文化传媒', '休闲娱乐', '教育培训', '汽车服务', '运动健身', '公司企业', '政府机构',
           '自然地物', '旅游景点', '酒店', '交通设施', '生活服务', '医疗', '购物', '金融']
small_tag = [['宿舍', '其他', '住宅区', '写字楼'], ['小吃快餐店', '其他', '咖啡厅', '茶座', '酒吧', '蛋糕甜品店', '外国餐厅', '中餐厅'],
             ['新闻出版', '美术馆', '广播电视', '其他', '艺术团体', '展览馆', '文化宫'],
             ['游戏场所', '休闲广场', '洗浴按摩', '其他', '电影院', '剧院', '网吧', '歌舞厅', '度假村', '农家院', 'ktv'],
             ['科技馆', '小学', '成人教育', '中学', '其他', '亲子教育', '高等院校', '培训机构', '留学中介机构', '图书馆', '幼儿园', '科研机构'],
             ['汽车销售', '其他', '汽车检测场', '汽车配件', '汽车维修', '汽车租赁', '汽车美容'], ['体育场馆', '极限运动场所', '健身中心', '其他'],
             ['园区', '其他', '厂矿', '公司', '农林园艺'],
             ['中央机构', '行政单位', '涉外机构', '民主党派', '党派团体', '其他', '社会团体', '公检法机构', '福利机构', '政治教育机构', '各级政府'],
             ['山峰', '其他', '水系', '岛屿'],
             ['动物园', '公园', '文物古迹', '景点', '游乐园', '博物馆', '其他', '教堂', '风景区', '植物园', '海滨浴场', '水族馆'],
             ['公寓式酒店', '其他', '快捷酒店', '星级酒店'],
             ['加油加气站', '停车场', '其他', '收费站', '公交车站', '桥', '充电站', '港口', '服务区', '火车站', '长途汽车站', '飞机场'],
             ['照相馆', '公用事业', '报刊亭', '邮局', '通讯营业厅', '物流公司', '洗衣店', '图文快印店', '彩票销售点', '宠物服务', '家政服务', '房产中介机构'],
             ['疗养院', '其他', '疾控中心', '综合医院', '诊所', '药店', '体检机构', '专科医院', '急救中心'],
             ['超市', '家具建材', '商铺', '百货商场', '市场', '购物中心', '家电数码', '便利店'], ['信用社', '银行', '投资理财', '其他', '典当行']]

expressway = []
high_speed_rail = []
underground = []
high_flow_capacity = []
high_school = []
high_density = []

administration_code = []
administration_name = []


# 加载五高一地相关信息
# 可以考虑将相关地点加载入词库中
def load_wgyd_info():
    expressway.clear()
    high_speed_rail.clear()
    underground.clear()
    high_flow_capacity.clear()
    high_school.clear()
    high_density.clear()
    mysql_db = pymysql.connect(myfile.database_ip, myfile.database_user, myfile.database_password, myfile.database_name)
    mysql_cursor = mysql_db.cursor()

    # 高密度
    mysql_cursor.execute("select distinct city, county, community from %s where scenes = '高密度'" % myfile.table_name)
    result = mysql_cursor.fetchall()
    for t in result:
        dic = {"city": "", "area": ""}
        if t[0] is not None and t[0] != "":
            dic['city'] = get_standard_administration_name(t[0])
        if t[1] is not None and t[1] != "":
            dic['area'] = get_standard_administration_name(t[1])
        if t[2] is not None and t[2] != "":
            n1 = t[2]
            n2 = n1.replace("0", "零").replace("1", "一").replace("2", "二").replace("3", "三").replace("4", "四").replace(
                "5", "五").replace("6", "六").replace("7", "七").replace("8", "八").replace("9", "九")
            n3 = n1.replace("0", "零").replace("1", "幺").replace("2", "二").replace("3", "三").replace("4", "四").replace(
                "5", "五").replace("6", "六").replace("7", "七").replace("8", "八").replace("9", "九")
            high_density.append({"city": dic['city'], "area": dic['area'], "name": n1})
            if n1 != n2:
                high_density.append({"city": dic['city'], "area": dic['area'], "name": n2})
            if n3 != n1 and n3 != n2:
                high_density.append({"city": dic['city'], "area": dic['area'], "name": n3})

    # 高流量
    mysql_cursor.execute("select distinct city, county, community from %s where scenes = '高流量'" % myfile.table_name)
    result = mysql_cursor.fetchall()
    for t in result:
        dic = {"city": "", "area": ""}
        if t[0] is not None and t[0] != "":
            dic['city'] = get_standard_administration_name(t[0])
        if t[1] is not None and t[1] != "":
            dic['area'] = get_standard_administration_name(t[1])
        if t[2] is not None and t[2] != "":
            n1 = t[2]
            n2 = n1.replace("0", "零").replace("1", "一").replace("2", "二").replace("3", "三").replace("4", "四").replace(
                "5", "五").replace("6", "六").replace("7", "七").replace("8", "八").replace("9", "九")
            n3 = n1.replace("0", "零").replace("1", "幺").replace("2", "二").replace("3", "三").replace("4", "四").replace(
                "5", "五").replace("6", "六").replace("7", "七").replace("8", "八").replace("9", "九")
            high_flow_capacity.append({"city": dic['city'], "area": dic['area'], "name": n1})
            if n1 != n2:
                high_flow_capacity.append({"city": dic['city'], "area": dic['area'], "name": n2})
            if n3 != n1 and n3 != n2:
                high_flow_capacity.append({"city": dic['city'], "area": dic['area'], "name": n3})
    # 高校
    mysql_cursor.execute("select distinct city, county, community from %s where scenes = '高校'" % myfile.table_name)
    result = mysql_cursor.fetchall()
    for t in result:
        dic = {"city": "", "area": ""}
        if t[0] is not None and t[0] != "":
            dic['city'] = get_standard_administration_name(t[0])
        if t[1] is not None and t[1] != "":
            dic['area'] = get_standard_administration_name(t[1])
        if t[2] is not None and t[2] != "":
            n1 = t[2]
            n2 = n1.replace("0", "零").replace("1", "一").replace("2", "二").replace("3", "三").replace("4", "四").replace(
                "5", "五").replace("6", "六").replace("7", "七").replace("8", "八").replace("9", "九")
            n3 = n1.replace("0", "零").replace("1", "幺").replace("2", "二").replace("3", "三").replace("4", "四").replace(
                "5", "五").replace("6", "六").replace("7", "七").replace("8", "八").replace("9", "九")
            high_school.append({"city": dic['city'], "area": dic['area'], "name": n1})
            if n1 != n2:
                high_school.append({"city": dic['city'], "area": dic['area'], "name": n2})
            if n3 != n1 and n3 != n2:
                high_school.append({"city": dic['city'], "area": dic['area'], "name": n3})
    # 地铁
    mysql_cursor.execute("select distinct community from %s where scenes = '地铁'" % myfile.table_name)
    result = mysql_cursor.fetchall()
    for t in result:
        if t[0] is not None and t[0] != "":
            underground.append(t[0])
    # 高铁
    mysql_cursor.execute("select distinct community from %s where scenes = '高铁'" % myfile.table_name)
    result = mysql_cursor.fetchall()
    for t in result:
        if t[0] is not None and t[0] != "":
            high_speed_rail.append(t[0])
    # 高速
    mysql_cursor.execute("select distinct community from %s where scenes = '高速'" % myfile.table_name)
    result = mysql_cursor.fetchall()
    for t in result:
        if t[0] is not None and t[0] != "":
            expressway.append(t[0])
    mysql_cursor.close()
    mysql_db.close()


# 初始化加载
def initial():
    global administration_name, administration_code
    # 市-县行政区划
    file = open(myfile.heBei_country_above, "r", encoding="UTF-8")
    stream = file.readlines()
    for i in stream:
        items = i.replace("\n", "").replace("\r", "").split("\t")
        if len(items) != 2:
            continue
        administration_code.append({'code': items[0], 'name': items[1]})
        administration_name.append({'code': items[0], 'name': items[1]})
        if items[0][4:6] != "00":
            jieba.add_word(items[1], 10000, "area")
        if len(items[1]) >= 5 and items[1][len(items[1]) - 3:] == "自治县":
            administration_name.append({'code': items[0], 'name': items[1][0:len(items[1]) - 3]})
            if items[0][4:6] != "00":
                jieba.add_word(items[1][0:len(items[1]) - 3], 10000, "area")
        elif len(items[1]) >= 3 and items[1][len(items[1]) - 1] in ['市', '区', '县']:
            administration_name.append({'code': items[0], 'name': items[1][0:len(items[1]) - 1]})
            if items[0][4:6] != "00":
                jieba.add_word(items[1][0:len(items[1]) - 1], 10000, "area")
    lis = ['青龙县', '青龙自治县', '青龙', '丰宁县', '丰宁自治县', '丰宁', '宽城县', '宽城自治县', '宽城', '围场县', '围场自治县', '围场',
           '孟村县', '孟村自治县', '孟村', '大厂县', '大厂自治县']
    for i in lis:
        jieba.add_word(i, 10000, 'area')
        if '青龙' in i:
            administration_name.append({'code': "130321", 'name': i})
        elif '丰宁' in i:
            administration_name.append({'code': "130826", 'name': i})
        elif '宽城' in i:
            administration_name.append({'code': "130827", 'name': i})
        elif '围场' in i:
            administration_name.append({'code': "130828", 'name': i})
        elif '孟村' in i:
            administration_name.append({'code': "130930", 'name': i})
        elif '大厂' in i:
            administration_name.append({'code': "131028", 'name': i})
    jieba.add_word("石家庄", 100000, "city")
    jieba.add_word("承德", 100000, "city")
    jieba.add_word("张家口", 100000, "city")
    jieba.add_word("邢台", 100000, "city")
    jieba.add_word("秦皇岛", 100000, "city")
    jieba.add_word("邯郸", 100000, "city")
    jieba.add_word("衡水", 100000, "city")
    jieba.add_word("保定", 100000, "city")
    jieba.add_word("沧州", 100000, "city")
    jieba.add_word("唐山", 100000, "city")
    jieba.add_word("廊坊", 100000, "city")
    administration_name.append({'code': "130100", 'name': "石家庄"})
    administration_name.append({'code': "130800", 'name': "承德"})
    administration_name.append({'code': "130700", 'name': "张家口"})
    administration_name.append({'code': "130500", 'name': "邢台"})
    administration_name.append({'code': "130300", 'name': "秦皇岛"})
    administration_name.append({'code': "130400", 'name': "邯郸"})
    administration_name.append({'code': "131100", 'name': "衡水"})
    administration_name.append({'code': "130600", 'name': "保定"})
    administration_name.append({'code': "130900", 'name': "沧州"})
    administration_name.append({'code': "130200", 'name': "唐山"})
    administration_name.append({'code': "131000", 'name': "廊坊"})
    administration_name = sorted(administration_name, key=operator.itemgetter("name"))
    administration_code = sorted(administration_code, key=operator.itemgetter("code"))
    file.close()

    load_wgyd_info()


# 折半查找_code
def binary_search_code(code):
    low = 0
    high = len(administration_code) - 1
    while low <= high:
        mid = int((low + high) / 2)
        if code == administration_code[mid]['code']:
            return mid
        elif code < administration_code[mid]['code']:
            high = mid - 1
        else:
            low = mid + 1
    return -1


# 折半查找name
def binary_search_name(name):
    low = 0
    high = len(administration_name) - 1
    while low <= high:
        mid = int((low + high) / 2)
        if name == administration_name[mid]['name']:
            return mid
        elif name < administration_name[mid]['name']:
            high = mid - 1
        else:
            low = mid + 1
    return -1


# 获取名字的标准化格式
def get_standard_administration_name(name):
    index = binary_search_name(name)
    if index >= 0:
        code = administration_name[index]['code']
        index = binary_search_code(code)
        return administration_code[index]['name']
    else:
        return name


# 市/县是否匹配
def is_city_county_match(city="", county=""):
    if city == "" or county == "":
        return True
    if len(city) >= 2 and len(county) >= 2 and city[0:2] == county[0:2]:
        return True
    index = binary_search_name(city)
    city_code = administration_name[index]['code']
    prob_code_list = []
    index = binary_search_name(county)
    j = index
    while j >= 0:
        code = administration_name[j]['code']
        if administration_name[j]['name'] == county:
            if code[4:6] != "00":
                prob_code_list.append(code)
        else:
            break
        j -= 1
    j = index + 1
    while j < len(administration_name):
        code = administration_name[j]['code']
        if administration_name[j]['name'] == county:
            if code[4:6] != "00":
                prob_code_list.append(code)
        else:
            break
        j += 1
    for i in prob_code_list:
        if i[0:4] == city_code[0:4]:
            return True
    return False


# 获取二级行政区域值
def get_second_region_name(area):
    index = binary_search_name(area)
    if index >= 0:
        code = administration_name[index]['code']
        index = binary_search_code(code[0:4] + "00")
        return administration_code[index]['name']
    else:
        return ""


# 街道的判断
# param:n
# return:bool
def street_road_judge(target):
    if target in ["楼道", "小区楼道"]:
        return False
    for i in street_road:
        if len(target) >= len(i) and target[-len(i):] == i:
            return True
    return False


def is_able_generate_street(target):
    if street_road_judge(target):
        return False
    for x in street_road:
        if x in target:
            return True
    return False


# 提供地点补全功能(输入的地点,查询所需的JSON文件)
# 返回一个标准地址字典
def station_complete(station_dic):
    if station_dic['city'] != "" and station_dic['area'] != "" and station_dic["town"] != "":
        return station_dic
    cursor = db.cursor()
    # 先对city area字段进行标准化处理, 沧州-沧州市, 不处理后面的查询可能会查不到数据
    station_dic['city'] = get_standard_administration_name(station_dic['city'])
    station_dic['area'] = get_standard_administration_name(station_dic['area'])
    name_copy = station_dic["name"]
    if "add_tag" in station_dic.keys():
        station_dic["name"] = station_dic["name"][0: len(station_dic["name"]) - len(station_dic["add_tag"])]
    if station_dic['city'] == '':
        if station_dic['area'] == '':
            if station_dic['town'] == '':
                if station_dic['village'] == '':
                    result = cursor.execute("select DISTINCT city, area, town, village, tag from base where name='%s' group by city,area" %
                                            (station_dic['name'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and "
                        "village = '%s' group by city,area" % (station_dic['name'], station_dic['village'])).fetchall()

            else:
                if station_dic['village'] == '':
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and "
                        "town = '%s' group by city,area" % (station_dic['name'], station_dic['town'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and "
                        "town = '%s' and village = '%s' group by city,area" % (station_dic['name'], station_dic['town'],
                                                            station_dic['village'])).fetchall()
        else:
            if station_dic['town'] == '':
                if station_dic['village'] == '':
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and "
                        "area = '%s' group by city,area" % (station_dic['name'], station_dic['area'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and "
                        "area = '%s' and village = '%s' group by city,area" % (
                            station_dic['name'], station_dic['area'], station_dic['village'])).fetchall()

            else:
                if station_dic['village'] == '':
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and "
                        "area = '%s' and town = '%s' group by city,area" % (station_dic['name'], station_dic['area'],
                                                         station_dic['town'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and "
                        "area = '%s' and town = '%s' and village = '%s' group by city,area" % (station_dic['name'],
                                                                            station_dic['area'],
                                                                            station_dic['town'],
                                                                            station_dic['village'])).fetchall()
    else:
        if station_dic['area'] == '':
            if station_dic['town'] == '':
                if station_dic['village'] == '':
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' group by city,area" %
                        (station_dic['name'], station_dic['city'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' and "
                        "village = '%s' group by city,area" % (
                            station_dic['name'], station_dic['city'], station_dic['village'])).fetchall()

            else:
                if station_dic['village'] == '':
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' and "
                        "town = '%s' group by city,area" % (station_dic['name'], station_dic['city'], station_dic['town'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' and "
                        "town = '%s' and village = '%s' group by city,area" % (
                            station_dic['name'], station_dic['city'], station_dic['town'],
                            station_dic['village'])).fetchall()
        else:
            if station_dic['town'] == '':
                if station_dic['village'] == '':
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' and "
                        "area = '%s' group by city,area" % (station_dic['name'], station_dic['city'], station_dic['area'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' and "
                        "area = '%s' and village = '%s' group by city,area" % (
                            station_dic['name'], station_dic['city'], station_dic['area'],
                            station_dic['village'])).fetchall()

            else:
                if station_dic['village'] == '':
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' and "
                        "area = '%s' and town = '%s' group by city,area" % (
                            station_dic['name'], station_dic['city'], station_dic['area'],
                            station_dic['town'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town, village, tag from base where name='%s' and city = '%s' and "
                        "area = '%s' and town = '%s' and village = '%s' group by city,area" % (
                            station_dic['name'], station_dic['city'], station_dic['area'], station_dic['town'],
                            station_dic['village'])).fetchall()
    station_dic["name"] = name_copy
    if len(result) == 1:
        choose = result[0]
        station_dic['city'] = choose[0]
        station_dic['area'] = choose[1]
        station_dic['town'] = choose[2]
        station_dic['village'] = choose[3]
        station_dic['tag'] = choose[4]
        return station_dic
    elif len(result) > 1:
        # 检查一下city是否为空
        if station_dic['area'] != "" and station_dic['city'] == "":
            result = cursor.execute(
                "select DISTINCT city from base where name = '%s' and tag = 'area'" % station_dic['area']).fetchall()
            if len(result) == 1:
                station_dic['city'] = result[0][0]
        return station_dic
    else:
        # 没查询到,要自己做一些查询补全,对于town city area做标准化处理
        if station_dic['village'] != "":
            if station_dic['city'] != "":
                if station_dic['area'] != "":
                    result = cursor.execute("select DISTINCT city, area, town from base where name = '%s' and  "
                                            "city = '%s' and area = '%s' and tag = 'village' group by city,area" %
                                            (station_dic['village'], station_dic['city'],
                                             station_dic['area'])).fetchall()
                else:
                    result = cursor.execute("select DISTINCT city, area, town from base where name = '%s' and  "
                                            "city = '%s' and tag = 'village' group by city,area" %
                                            (station_dic['village'], station_dic['city'])).fetchall()
            else:
                if station_dic['area'] != "":
                    result = cursor.execute("select DISTINCT city, area, town from base where name = '%s' and "
                                            "area = '%s' and tag = 'village' group by city,area" %
                                            (station_dic['village'], station_dic['area'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area, town from base where name = '%s' and tag = 'village' group by city,area" %
                        station_dic['village']).fetchall()
            if len(result) == 1:
                choose = result[0]
                if station_dic['city'] == "":
                    station_dic['city'] = choose[0]
                if station_dic['area'] == "":
                    station_dic['area'] = choose[1]
                if station_dic['town'] == "":
                    station_dic['town'] = choose[2]
                    # 做一次检测,如果town与area不符合,则置town为空
                    if station_dic['area'] != "" and choose[2] != "":
                        result = cursor.execute(
                            "SELECT 1 WHERE '%s' IN (SELECT DISTINCT area FROM base where name = '%s' and tag = 'town')" %
                            (station_dic['area'], choose[2])).fetchall()
                        if result is None or len(result) == 0:
                            station_dic['town'] = ""
                return station_dic

        if station_dic['town'] != "":
            if station_dic['city'] != "":
                if station_dic['area'] != "":
                    result = cursor.execute("select DISTINCT city, area from base where name = '%s' and "
                                            "city = '%s' and area = '%s' and tag = 'town' group by city,area" %
                                            (station_dic['town'], station_dic['city'], station_dic['area'])).fetchall()
                else:
                    result = cursor.execute("select DISTINCT city, area from base where name = '%s' and "
                                            "city = '%s' and tag = 'town' group by city,area" %
                                            (station_dic['town'], station_dic['city'])).fetchall()
            else:
                if station_dic['area'] != "":
                    result = cursor.execute("select DISTINCT city, area from base where name = '%s' and  "
                                            "area = '%s' and tag = 'town' group by city,area" %
                                            (station_dic['town'], station_dic['area'])).fetchall()
                else:
                    result = cursor.execute(
                        "select DISTINCT city, area from base where name = '%s' and tag = 'town' group by city,area" % station_dic[
                            'town']).fetchall()
            if len(result) == 1:
                choose = result[0]
                if station_dic['city'] == "":
                    station_dic['city'] = choose[0]
                if station_dic['area'] == "":
                    station_dic['area'] = choose[1]
                return station_dic
        # city补全
        if station_dic['area'] != "" and station_dic['city'] == "":
            result = cursor.execute(
                "select DISTINCT city from base where name = '%s' and tag = 'area'" % station_dic['area']).fetchall()
            if len(result) == 1:
                station_dic['city'] = result[0][0]
        return station_dic


# 识别地点是否是五高一地(地名)
# 返回值：0,1(高铁),2(高校),3(高速公路),4(高流量商圈),5(高密度住宅),6(地铁)
def wgyd_recognize(station, city="", area=""):
    if station == "":
        return 0
    for x in high_flow_capacity:
        if judge_station(x["name"], station) and (x["city"] == get_standard_administration_name(city) or city == "") \
                and (x['area'] == get_standard_administration_name(area) or area == "" or x["area"] == ""):
            return 4
    for x in high_density:
        if judge_station(x["name"], station) and (x["city"] == get_standard_administration_name(city) or city == "") \
                and (x['area'] == get_standard_administration_name(area) or area == "" or x["area"] == ""):
            return 5
    for x in high_school:
        if judge_station(x["name"], station) and (x["city"] == get_standard_administration_name(city) or city == "") \
                and (x['area'] == get_standard_administration_name(area) or area == "" or x["area"] == ""):
            return 2
    for x in expressway:
        if judge_station(x, station):
            return 3
    for x in high_speed_rail:
        if judge_station(x, station):
            return 1
    for x in underground:
        if judge_station(x, station):
            return 6
    return 0


# 判断两个地名是否是等价的
def judge_station(station1, station2):
    K = 0.81  # 相似度暂定阈值
    if station1 in station2 or station2 in station1:
        return True
    elif Levenshtein.ratio(station1, station2) >= K:
        return True
    else:
        return False


# 预加载和相关初始化
initial()


if __name__ == '__main__':
    # print(get_standard_administration_name("丰润"))
    # print(posseg.lcut("丰润区人民医院"))
    # print(is_city_county_match(city="石家庄", county="桥西区"))
    print(wgyd_recognize("安平格林豪泰", city="石家庄"))
