# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/7/3 12:56
# @Author  : Zhuxx

import requests

def DDMsg(msg):
    '''
    发送钉钉告警
    :param msg: 钉钉告警信息
    :ps 下面注释的部分为钉钉告警需要@的人的信息，只需要添加电话号码就可以
    :return:
    '''
    url = 'https://oapi.dingtalk.com/robot/send'
    data = {"msgtype": "text","text": {"content": "自动化测试用例遍历结果：{}".format(msg)}}
    response = requests.post(url,json=data)
