#！/usr/bin/env python
#! -*-coding:utf-8 -*-
#!@Author : zhuxx
#!@time : 2020/07/14 16:55

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError

class Send:

    def __init__(self,retries=3):
        self.adapter = HTTPAdapter(max_retries=retries)                                                #重试机制
        self.session = requests.Session()                                                              #使用session发送请求
        self.headers = {}                                                                              #默认headers
        self.cookies = {}                                                                              #默认cookies

    def send(self,method,url,data,headers=None,cookies=None,timeout=5):
        '''
        发送请求
        :param method: 请求方法
        :param url: 请求地址
        :param data: 请求数据
        :param headers: 请求头
        :param cookies: 登陆状态
        :param timeout: 超时时间
        :return:
        请求结果
        '''
        self.session.mount(url,self.adapter)
        headers = {**self.headers,**headers} if headers else self.headers                              #判断是否存在headers
        cookies = cookies if cookies else self.cookies                                                 #判断是否存在cookies
        if method.upper() == "GET":
            data = data if data else {}
            response = self.session.get(url,params=data,headers=headers,cookies=cookies,timeout=timeout)
            result = self.get_result(response)
        elif method.upper() == 'POST':
            response = self.judge_data(url,data,headers=headers,cookies=cookies,timeout=timeout)
            result = self.get_result(response)
        elif method.upper() == "PUT":
            response = self.session.put(url,data,headers=headers,cookies=cookies,timeout=timeout)
            result = self.get_result(response)
        else:
            response = self.session.delete(url,data=data,headers=headers,cookies=cookies,timeout=timeout)
            result = self.get_result(response)
        return result

    def get_result(self,response):
        '''
        获取请求结果
        :param response:requests类型的请求结合
        :return:
        正常情况下为json字段，异常情况为txt
        '''
        try:
            result = response.json()
            return result
        except Exception as e:
            result = response.text
            return result

    def judge_data(self,url,data,**kwargs):
        '''
        主要判断post请求的字段
        :param url: 请求请求
        :param data: 数据集
        :param kwargs: 其他字段
        :return:
        requests的结果集
        '''
        self.session.mount(url, self.adapter)
        try:
            response = self.session.post(url,data=data,**kwargs)
            return response
        except Exception as e:
            response = self.session.post(url,json=data,**kwargs)
            return response
        except ConnectionError as ce:
            raise "the error info is :{}".format(ce)