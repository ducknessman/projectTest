#！/usr/bin/env python
#! -*-coding:utf-8 -*-
#!@Author : zhuxx
#!@time : 2020/07/14 15:40

import xlrd
import os
from itertools import product

class ReadExcel:

    def __init__(self,filename):
        '''
        获取excel的目录
        :param filename:
        '''
        basic = os.path.abspath(os.path.dirname(__file__))          #本地路径
        self.file_path = os.path.join(basic,filename)               #excel路径

    def read(self):
        '''
        读取excel
        :return:
        '''
        workbook = xlrd.open_workbook(self.file_path)              #生成workbook，获取excel
        sheetname = workbook.sheet_names()                         #获取说有的sheet名称
        for name in sheetname:                                     #遍历名称列表
            title,value = [],[]
            worksheet = workbook.sheet_by_name(name)               #生成当前sheet的工作信息
            nrows,ncols = worksheet.nrows,worksheet.ncols          #获取行数和列数
            for row,col in product(range(nrows),range(ncols)):     #同时遍历行和列
                if row == 0:
                    title.append(worksheet.cell(row,col).value)    #获取title，保存在列表
                else:
                    value.append(worksheet.cell(row,col).value)    #获取处title以外的值
            yield from self.combine_dict(title,value)              #通过管道实现拼接字典

    def combine_dict(self,title,value):
        '''
        将title和value拼装成字典
        :param title: excel的表头
        :param value: excel中的值
        :return: 一个拼装好的字典样式的迭代器
        '''
        for i in range(0,len(value),len(title)):                   #通过长度截断列表
            yield dict(zip(title,value[i:i+len(title)]))           #拼装字典并返回迭代器