#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author:menghuanlater

import os
path_m = os.path.dirname(os.path.dirname(__file__))  # 定位AddressRelation的路径

jieba_dict_name = os.path.join(path_m, "jieba-add-dict.txt")
sqlite_db_url = os.path.join(path_m, "placeDataBase.db")
heBei_country_above = os.path.join(path_m, "HeBei_Country_Above.txt")
wgyd_excel_file = os.path.join(path_m, "五高一地.xlsx")
ignore_word = os.path.join(path_m, "ignore.txt")
addi_word = os.path.join(path_m, "addition.txt")
replace_word_pair = os.path.join(path_m, "replace.txt")

database_ip = "localhost"
database_user = "root"
database_password = "root"
database_name = "market_data_crawl"
table_name = "t_window_place_info"
