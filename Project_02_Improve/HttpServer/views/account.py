# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/24 17:06
# @Author  : Zhuxx

from flask import Blueprint, current_app,render_template, request, session, redirect, url_for, jsonify

account = Blueprint('account', __name__)


@account.route('/home')
def home():
    '''
    home页面
    :return:
    '''
    return "<h2>欢迎访问系统主页</h2>"


@account.route('/login', methods=["GET", "POST"])
def login():
    '''
    登录页面，通过js方式进行调用，相关信息参见account.html页面
    :return:
    '''
    if request.method == "GET":
        return render_template('account.html')
    else:
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        user_pwd = current_app.config['USERINFO']
        if user_pwd[user]==pwd and user in user_pwd.keys():               #默认用户名密码
            session['user'] = user
            return jsonify({"code": 200, "error": ""})
        else:
            return jsonify({"code": 401, "error": "用户名或密码错误"})


@account.route('/logout')
def logout():
    '''
    退出登录页面
    :return:
    '''
    del session['user']
    return redirect(url_for('account.login'))
