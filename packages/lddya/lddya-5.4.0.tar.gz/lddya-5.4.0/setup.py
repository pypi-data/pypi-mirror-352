#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: lidongdong
# Mail: 927052521@qq.com
# Created Time: 2022.10.21  19.50
############################################

from setuptools import setup, find_packages

setup(
    name = "lddya",
    version = "5.4.0",
    keywords = {"pip", "license","licensetool", "tool", "gm"},
    description = "给dd保存数据方法添加一个表头；修复Map类生成数据时，未对size属性进行初始化的问题；允许Map.save新建文件；允许Map设置栅格以及网格线颜色；允许Map追加障碍物绘制；允许Map计算障碍物坐标。Draw模块新增了PlotStyleGenerator类用以创建性的颜色组合。ShanGeTu.draw_way支持所有plot的参数啦，Iter类也支持Plot所有参数。",
    long_description = "具体功能，请自行挖掘。",
    license = "MIT Licence",

    url = "https://github.com/not_define/please_wait",
    author = "lidongdong",
    author_email = "927052521@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['numpy','matplotlib','pygame','pandas']
)
