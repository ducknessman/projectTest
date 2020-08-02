# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/24 17:06
# @Author  : Zhuxx

from flask import Blueprint, render_template, current_app, send_from_directory, request, jsonify,redirect,url_for,session
# from Project_02.HttpServer.views.dingding import DDMsg
import os
import time
import csv
import json
import platform
from collections import defaultdict

home = Blueprint('home', __name__)

scv_global_info = defaultdict(dict)                 #全局数据

class DocumentReader:
    '''
    获取全局的路径并处理路径
    '''
    def __init__(self, real_path):
        self.real_path = real_path   #传入的根路径，为该类的全局路径
        self.data = {
            "code": 0,
            "msg": "",
            "count": 0,
            "data": []
        }                           #基础数据格式
        self.flag = 1               #数据编号
        self.temp = {}              #临时存储深度字典

    def dirs_tree(self,path, depth):
        '''
        用于生成目录格式的树状结构数据
        :param path: 目标路径
        :param depth: 初始深度
        :return:
        '''
        os.chdir(path)
        real_len = len(self.real_path.split('\\')) if platform.system() == "Windows" else len(self.real_path.split('/'))    #获取目标路径长度
        _time = time.strftime("%Y/%m/%d %H:%M", time.localtime(os.path.getctime(path)))                                     #获取文件或文件夹时间
        single_path = '/'.join(path.replace("\\", '/').split('/')[real_len:])                                               #隐藏绝对路径
        #初始根目录
        if depth == 0:
            self.data['data'].append({'authorityId': self.flag, 'authorityName': path.replace('\\','/').split('/')[-1], 'orderNumber': depth,
                   'menuUrl': single_path,'menuIcon': '', 'size': '-','createTime':_time,'authority':'文件夹','isMenu':0,"parentId":-1})
            self.temp[path] = self.flag
            self.flag += 1

        for item in os.listdir(path):
            if os.path.isdir(item) and depth == 0:
                self.data['data'].append({'authorityId': self.flag, 'authorityName': item,
                     'orderNumber': depth + 1, 'menuUrl': single_path,'menuIcon': '', 'size': '-',
                     'createTime':_time,'authority':'文件夹','isMenu':0,"parentId":self.temp[path]})
                self.flag += 1
            elif os.path.isfile(item):
                file_type = os.path.splitext(item)[1].strip('.')
                size = self.get_size(os.path.getsize(item))
                self.data['data'].append({'authorityId': self.flag, 'authorityName': item,
                     'orderNumber': depth, 'menuUrl': single_path,'menuIcon': file_type, 'size': size,
                     'createTime':_time,'authority':'文件','isMenu':1,"parentId":self.temp[path]})
                self.flag += 1
            else:
                self.data['data'].append({'authorityId': self.flag , 'authorityName': item,
                       'orderNumber': depth, 'menuUrl': single_path, 'menuIcon': '', 'size': '-',
                       'createTime': _time, 'authority': '文件夹', 'isMenu': 0, "parentId": self.temp[path]})
                self.flag += 1
            newitem = path + '/' + item                          #拼接目录
            if os.path.isdir(newitem):
                #进入迭代，进行深度遍历
                self.temp[newitem] = self.flag - 1
                self.dirs_tree(newitem, depth + 1)

    def analysis_dir(self):
        '''
        分析目录结构
        :return: 标准的json格式
        '''
        self.dirs_tree(self.real_path,0)
        return self.data

    @staticmethod
    def get_size(size):
        '''
        静态方法，更改文件大小为对应格式
        :param size: 问价大小，为字节
        :return:
        '''
        if size < 1024:
            return '%d  B' % size
        elif 1024 <= size < 1024 * 1024:
            return '%.2f KB' % (size / 1024)
        elif 1024 * 1024 <= size < 1024 * 1024 * 1024:
            return '%.2f MB' % (size / (1024 * 1024))
        else:
            return '%.2f GB' % (size / (1024 * 1024 * 1024))


class ReadFile:

    '''
    读取文件
    '''
    def find_path(self,path,find_str):
        '''
        找到文件路径
        :param path:需要寻找的路径
        :param find_str: 需要寻找的字段
        :return:
        '''
        infos = {}
        for root,_,filenames in os.walk(path):
            for file in filenames:
                msg = self.judge_file(os.path.join(root,file),find_str)
                if msg:
                    infos.setdefault(root.split('\\')[-1],[]).append(msg)
        if infos != {}:
            return list(infos.keys())[0],infos
        else:
            return False

    def judge_file(self,filename,single):
        '''
        判断文件类型
        :param filename:绝对文件路径
        :param single: 寻找的对应标志（ps:寻找字段）
        :return:
        '''
        name,flag = filename.split('.')
        if flag == 'csv':
            return self.find_str(filename,single)
        elif flag in ['xls,xlsx']:
            pass
    
    def find_str(self,filename,flag):
        '''
        寻找特定字段
        :param filename:文件绝对路径
        :param flag: 寻找的对应标志（ps:寻找字段）
        :return:
        '''
        infos = self.read_csv(filename)
        single = []
        for index,value in enumerate(infos):
            if flag == value[2].split('-')[0] and index != 0:
                single.append(index+1)
        if single == []:
            pass
        else:
            return '存在线索的文件为：{}；在以下行中出现：{}'.format(filename.split('\\')[-1],single)

    def deal_info(self,filename):
        '''
        处理字段变成便准字典格式
        :param filename: 文件绝对路径
        :return:
        '''
        title,values = [],[]
        for index,value in enumerate(self.read_csv(filename)):
            if index == 0:
                title = [i.lower().replace(" ","_") for i in value]
            else:
                values.append(value)
        real_info = [dict(zip(title,use)) for use in values]
        return real_info

    def read_csv(self,filename):
        '''
        读取csv文件
        :param filename: 文件绝对路径
        :return:
        '''
        with open(filename,'r') as f:
            reader = csv.reader(f)
            return list(reader)

    def write_scv(self,filename,infos):
        '''
        写入csv文件
        :param filename: 文件绝对路径
        :param infos: 需要写入的信心，格式为：[[1,1,1],[2,2,2]]
        :return:
        '''
        with open(filename,'w',newline='') as f:
            w = csv.writer(f)
            for info in infos:
                w.writerow(info)


@home.route('/index')
def index():
    '''
    页面根目录
    :param path_uri: 根路径
    :return:
    '''
    return render_template('index.html', path='',error_info='')

@home.errorhandler(500)
def error():
    '''
    错误信息页面
    :param error:错误信息
    :return:
    '''
    return render_template('index.html', error_info='哎呀，出错了。')

@home.route('/show_data',methods=['GET','POST'])
def show_data():
    '''
    js获取读取文件数据
    :return:
    '''
    auth = session['user']
    for key,value in scv_global_info[auth].items():
        return jsonify(value)

@home.route('/show_excel')
def show_excel():
    '''
    csv数据展示页面
    :return:
    '''
    path = request.args.get('path') if request.args.get('path') else ""
    filename = request.args.get('filename')
    auth = session['user']
    if path or path == '':
        base_dir = current_app.config['BASEDIR']
        real_path = os.path.join(base_dir,path,filename)
        if scv_global_info[real_path]:
            return render_template('index.html',error_info='{},正在使用该文档，请稍后在进行编辑。'.format(scv_global_info[real_path]),path='')
        else:
            info = ReadFile().deal_info(real_path)
            scv_global_info.setdefault(auth,{})[real_path] = info
            scv_global_info[real_path] = auth
            return render_template('show_excel.html')

@home.route('/save_infos',methods=['POST'])
def save_infos():
    '''
    保存修改后的文件
    :return:
    '''
    model = current_app.config['TITLE']
    use_model = model.split(',')
    save_info = []
    auth = session['user']
    temp_dict = {'Test Summary':'test_summary','Incoming_id':'incoming_id'}
    if request.method == "POST":
        infos = request.get_data()
        values = json.loads(infos)
        for value in values:
            temp = []
            for name in use_model:
                if name in temp_dict:
                    temp.append(value[temp_dict[name]])
                else:
                    temp.append(value[name])
            save_info.append(temp)
    save_info.insert(0,use_model)
    for k,v in scv_global_info[auth].items():
        ReadFile().write_scv(k,save_info)
        scv_global_info[auth][k].pop()
        scv_global_info.pop(k)
    return redirect(url_for('home.index'))

@home.route('/return_local')
def return_local():
    '''
    返回根目录
    :return:
    '''
    scv_global_info.clear()
    return redirect(url_for('home.index'))

@home.route('/search_info',methods=['GET','POST'])
def search_info():
    '''
    查找字段，通过js传回来的字段进行处理，查找
    :return:
    '''
    if request.method == "GET":
        key = request.args.get('key')
        base_dir = current_app.config['BASEDIR']
        read = ReadFile()
        path,msg = read.find_path(base_dir,key)
        # DDMsg(msg)                                                    #钉钉消息发送，需要可以放开注释
        return render_template('index.html',path='', error_info=msg)

@home.route('/get_all_files',methods=['GET','POST'])
def get_file_infos():
    base_dir = current_app.config['BASEDIR']
    file_reader = DocumentReader(base_dir)
    infos = file_reader.analysis_dir()
    return jsonify(infos)