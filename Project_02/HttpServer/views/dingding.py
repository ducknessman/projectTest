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
    url = 'https://oapi.dingtalk.com/robot/send?access_token=511b02522a1f0d28e61e68cd874c3b7a5c20cd83efadba558039ab4567a9846e'
    data = {"msgtype": "text","text": {"content": "自动化测试用例遍历结果：{}".format(msg)},
            # "at": {
            #     "atMobiles": [
            #         "13550629276"
            #     ],
            #     "isAtAll": False
            # }
            }
    response = requests.post(url,json=data)
