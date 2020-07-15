# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/24 17:06
# @Author  : Zhuxx


from Project_02.HttpServer import HttpServerApp

app = HttpServerApp()     #主程序实例

if __name__ == '__main__':
    '''
    主程序入口
    '''
    app.run(host='127.0.0.1', port=8765 ,threaded=True)
