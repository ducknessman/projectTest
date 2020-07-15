#！/usr/bin/env python
#! -*-coding:utf-8 -*-
#!@Author : zhuxx
#!@time : 2020/06/23 22:57

import unittest
from SimpleReport import SimpleReport

if __name__ == '__main__':
    test_suite = unittest.defaultTestLoader.discover('../tests',pattern='test_make_report_interface.py')
    print(test_suite)
    result = SimpleReport(test_suite)
    result.report(filename='接口测试报告',description='接口测试报告测试版',log_path='')