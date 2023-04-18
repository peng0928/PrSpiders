#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
__version__ = '0.3.1'

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="PrSpiders",
    version=__version__,
    author="penr",
    author_email="1944542244@qq.com",
    description="Inherit the requests module, add xpath functionality to expand the API, and handle request failures and retries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/peng0928/prequests",
    packages=find_packages(),
    install_requires=["requests", "urllib3", "lxml", "xpinyin", "PrSpiders"],
    entry_points={"console_scripts": ["prspiders = pkg.prspider.PrSpider_CMD:main"]},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
