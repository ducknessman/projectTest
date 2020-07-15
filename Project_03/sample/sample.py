#！/usr/bin/env python
#! -*-coding:utf-8 -*-
#!@Author : zhuxx
#!@time : 2020/06/23 22:38

import unittest
from SimpleReport import SimpleReport

if __name__ == '__main__':
    test_suite = unittest.defaultTestLoader.discover('../tests', pattern='test*.py')
    result = SimpleReport(test_suite)
    result.report(filename='测试报告', description='测试deafult报告', log_path='.')
