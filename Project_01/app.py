from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from util.ReadExcel import ReadExcel
from util.Request import Send
from util.CreateReport import CreateReport

import json
import difflib
import time
import datetime

app = Flask(__name__)

login_info = {'username':'admin','password':'admin'}
all_infos = []

def deal_with(infos):
    infos = [int(i) for i in infos.split(',')]
    result = {}
    testpass,testAll,testFail,totalTime,testSkip = 0,0,0,0,0
    beginTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    testName = '{}{}'.format(all_infos[0][infos[0]]['task_description'],datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
    for index in infos:
        start_time = time.time()
        value = all_infos[0][index]
        response = Send().send(value['task_method'],value['task_url'],value['task_data'])
        compare_result = judge_info(value['task_result'],response)
        end_time = time.time()
        logs = 'the result is {};the response is {}'.format(value['task_result'],response)
        temp = {'className':"{}-{}".format(value['task_name'],value['task_description']),'methodName':value['task_method'],'description':value['task_description'],
                'spendTime':"{}s".format(end_time-start_time),
                'status':compare_result,'log':[logs]}
        if compare_result == '成功':
            testpass += 1
        elif compare_result == '失败':
            testFail += 1
        else:
            testSkip += 1
        testAll += 1
        result.setdefault('testResult',[]).append(temp)
    other = {'testPass':testpass,"testName":testName,'testAll':testAll,"testFail":testFail,'beginTime':beginTime,'totalTime':totalTime,'testSkip':testSkip}
    result.update(other)
    CreateReport().create(result,"{}".format(testName))
    all_infos.clear()

def judge_info(result,response):
    result = json.loads(result)
    temp = []
    if isinstance(response,dict):
        for key,value in result.items():
            if response[key] == value:
                temp.append('成功')
            else:
                temp.append('失败')
    elif isinstance(response,str):
        diff_present = difflib.SequenceMatcher(result,response).ratio()
        if diff_present > 0.8:
            temp.append('成功')
        else:
            temp.append('失败')

    if len(set(temp)) == 1 and list(set(temp))[0] == '成功':
        return '成功'
    elif len(set(temp)) == 1 and list(set(temp))[0] == '失败':
        return '失败'
    else:
        return '失败'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        username = True if login_info['username'] == user else False
        if user and pwd:
            if username:
                if pwd == login_info['password']:
                    return jsonify({'code': 200, 'error': ""})
                else:
                    return jsonify({'code': 401, 'error': '用户名或密码错误'})
            else:
                return jsonify({'code': 401, 'error': '用户名或密码错误'})
        else:
            return jsonify({'code': 401, 'error': '用户名或密码不能为空'})

@app.route('/index_home',methods=['GET',"POST"])
def index_home():
    return render_template('index.html')

@app.route('/show_case',methods=['GET'])
def show_case():
    if request.method == "GET":
        tasks = ReadExcel('demo.xlsx').read()
        all_infos.append(list(tasks))
        return render_template('show_case.html',tasks=all_infos[0])

@app.route('/running_task',methods=['POST'])
def running_task():
    if request.method == "POST":
        ids = request.values.get('id')
        data = deal_with(ids)
        return jsonify(data)
    else:
        return {'msg':'哎呀！出问题了！！','status':1002}


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=8888,debug=True)
