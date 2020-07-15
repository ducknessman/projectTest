#！/usr/bin/env python
#! -*-coding:utf-8 -*-
#!@Author : zhuxx
#!@time : 2020/06/23 22:38

import requests
import unittest


class ITAutoTestCase(unittest.TestCase):
    '''
    测试报告的基础用例
    '''

    def test_open_baidu(self):
        '''百度测试'''
        url = 'https://www.baidu.com'
        response = requests.get(url)
        self.assertEqual(response.status_code,'200')

    def test_page(self):
        '''一般浏览器测试'''
        url = 'https://www.bkex.co/api/notice/current/v2'
        data = {'language':1}
        response = requests.get(url,params=data)
        result = response.json()
        compare = {"msg":"success","code":0,"data":{"id":26,"type":1,"title":"BKEX-太和稳健策略结构型封闭式基金","url":"https://bkex.zendesk.com/hc/zh-cn/articles/360049903154","content":"https://bkex-dev-pub-hz.oss-cn-hangzhou.aliyuncs.com/notice/notice20200623161415228.png"},"status":0}
        self.assertEqual(result,compare)