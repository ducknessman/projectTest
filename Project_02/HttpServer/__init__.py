# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/24 17:06
# @Author  : Zhuxx

from flask import Flask, render_template, session, request, redirect, url_for
from HttpServer.views.account import account as account_blueprint
from HttpServer.views.home import home as home_blueprint


def HttpServerApp():
    app = Flask(__name__)                                           #flask实例
    app.jinja_env.auto_reload = True                                #css,js热加载
    app.config['TEMPLATES_AUTO_RELOAD'] = True                      #加载文件热加载
    app.register_blueprint(account_blueprint, url_prefix='/manage') #注册登录蓝图
    app.register_blueprint(home_blueprint)                          #注册主页面蓝图
    app.config.from_object('settings.BasicConfig')                  #加载settings的文件

    @app.before_request
    def check():
        '''
        登陆前验证session
        :return:
        '''
        if (not session.get('user') and not request.path.startswith('/static')
                and request.path != '/manage/login'):
            return redirect(url_for('account.login'))

    @app.template_filter("split_path")
    def split_path(path):
        '''
        目录文件切割
        :param path:
        :return:
        '''
        path_list = path.split('/')
        path_list = [[path_list[i - 1], '/'.join(path_list[:i])] for i in range(1, len(path_list)+1)]
        return path_list

    @app.errorhandler(404)
    def error(error_no):
        '''
        错误信息
        :param error_no:
        :return:
        '''
        return "请使用正确的url访问: /index?"

    return app
