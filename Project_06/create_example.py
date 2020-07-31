#！/usr/bin/env python
#! -*-coding:utf-8 -*-
#!@Author : zhuxx
#!@time : 2020/07/09 21:32

import xmind
import csv
import os
import datetime
from itertools import product

class DealXmind:

    def read_xmind(self,filename):
        workbook = xmind.load(filename)
        values = workbook.getData()
        return values

    def single_deal(self,values):
        infos = self.deal_json(values[0]['topic'])
        use_key = [key for key in infos.keys() if 'title' in key and str(key).split("_").count('topics') > 1]
        double = []
        for i in range(1,len(use_key),1):
            if use_key[i - 1].strip('title') in use_key[i].strip('title'):
                double.append(use_key[i - 1])
        real_key = set(use_key) - set(double)
        return sorted(real_key)


    def create_case(self,filename):
        infos = self.read_xmind(filename)
        key_index = self.single_deal(infos)
        for keys in key_index:
            case = ""
            use = ""
            single = self.exchange_type(keys)
            for i in range(0,len(single),2):
                use = use + ("[{}]"*len(single[i:i+2])).format(*single[i:i+2])
                case = case + "|" + eval("infos[0]['topic']{}['title']".format(use))
            yield from self.__create_case(case)

    def __create_case(self,infos):
        point = 0
        title = ""
        single_infos = {}
        for index,value in enumerate(infos.lstrip('|').split('|')):
            if index > 0 and "【" in value:
                point = index
                try:
                    deses,data = value.split('】')
                    des,level = deses.lstrip('【').replace(" ","").replace("-p","-P").split('-P')
                    title = title + "-" + des
                    single_infos['Test Priority'] = "P{}".format(level)
                    single_infos['Step'] = data.lstrip("\r\n")
                except Exception as e:
                    deses,data = value.split('】')
                    des,level = deses.lstrip('【'),""
                    title = title + "-" + des
                    single_infos['Test Priority'] = "P{}".format(level)
                    single_infos['Step'] = data.lstrip("\r\n")
            elif index > 0 and index > point and point != 0:
                single_infos['Result'] = value
            elif index > 0:
                title = title + "-" + value
        else:
            single_infos['describe'] = title.lstrip("-")
            yield single_infos

    def exchange_type(self,value):
        new = []
        for v in value.split("_")[:-1]:
            try:
                new.append(int(v))
            except ValueError as e:
                new.append("'{}'".format(v))
        return new

    def _construct_key(self,previous_key, separator, new_key, replace_separators=None):
        if replace_separators is not None:
            new_key = str(new_key).replace(separator, replace_separators)
        if previous_key:
            return "{}{}{}".format(previous_key, separator, new_key)
        else:
            return new_key

    def deal_json(self, nested_dict, separator="_", root_keys_to_ignore=set(), replace_separators=None):

        flattened_dict = dict()

        def _flatten(object_, key):
            if not object_:
                flattened_dict[key] = object_
            elif isinstance(object_, dict):
                for object_key in object_:
                    if not (not key and object_key in root_keys_to_ignore):
                        _flatten(object_[object_key],self._construct_key(
                                key,
                                separator,
                                object_key,
                                replace_separators=replace_separators))
            elif isinstance(object_, (list, set, tuple)):
                for index, item in enumerate(object_):
                    _flatten(item,self._construct_key(
                            key,
                            separator,
                            index,
                            replace_separators=replace_separators))
            else:
                flattened_dict[key] = object_

        _flatten(nested_dict, None)
        return flattened_dict

    def write_csv(self,filename):
        titles = 'TCID,Test Summary,describe,Test Repository Path,requirement_id,Test Priority,Component,pre-conditon,Step,Data,Result'.split(",")
        name,topic = os.path.splitext(filename)
        with open('{}_{}.{}'.format(name,datetime.datetime.now().strftime("%Y%m%d%H%M%S"),'csv'),'w',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(titles)
            temp = []
            for value,title in product(self.create_case(filename),titles):
                try:
                    if 'Result' == title:
                        temp.append(value[title])
                        writer.writerow(temp)
                        temp.clear()
                    else:
                        temp.append(value[title])
                except Exception as e:
                    temp.append(" ")

if __name__ == '__main__':
    basic = os.path.abspath(os.path.dirname(__file__))
    for path,_,filenames in os.walk(os.path.join(basic,'data')):
        for filename in filenames:
            real_path = os.path.join(path,filename)
            DealXmind().write_csv(real_path)