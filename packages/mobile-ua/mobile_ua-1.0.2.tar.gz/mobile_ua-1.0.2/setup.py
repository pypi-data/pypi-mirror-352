# -*- coding: utf-8-*-
from setuptools import setup, find_packages
import os, io

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    # 以下为必需参数
    name='mobile_ua',  # 模块名
    version='1.0.2',  # 当前版本
    description='Randomly obtain the Useragent of the mobile phone',  # 简短描述
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='white.tie',
    author_email='1042798703@qq.com',
    license='MIT',
    url='https://gitee.com/tieyongjie/mobile_ua',
    install_requires=[
        'pandas',
        'numpy'
    ],
    packages=['mobile_ua'],
    package_data={
        'mobile_ua': ['UA.pkl'],
    },
    package_dir={'': 'src'}
)
