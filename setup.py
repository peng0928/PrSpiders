#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages

__version__ = "2.1.0"

with open("README.md", "r", encoding="utf-8") as fh:
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
    install_requires=["requests", "urllib3", "pickle", "redis",
                      "PrSpiders", 'loguru', 'pymysql', 'parsel'],
    entry_points={"console_scripts": [
        "prspiders = pkg.prspider.PrSpider_CMD:main"]},
    classifiers=[

    ],
)
