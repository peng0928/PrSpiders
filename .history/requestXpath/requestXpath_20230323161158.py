from requests.exceptions import SSLError
import requests
import logging
import time
import json
from requests.models import Response
from .useragent import get_ua
from .pxpath import Xpath
import datetime

"""
-------------------------------------------------
   File Name:     prequest
   Description :   Network Requests Class
   Author :        penr
   date:          2023/02/16
-------------------------------------------------
   Change Activity:
                   2023/02/16:
-------------------------------------------------
"""
__author__ = 'penr'
__version__ = 0.1
logging.basicConfig(format='%(message)s', level=logging.INFO)


class prequest(Xpath):
    def __init__(self):
        self.response = Response()
        self.amount = 0
        self.samount = 0
        self.famount = 0
        self.start_time = time.time()

    @property
    def user_agent(self):
        """
        :return: an User-Agent at random
        """
        return get_ua()

    @property
    def header(self):
        """
        :return: basic header
        """
        return {'user-agent': self.user_agent}

    def get(self, url, headers=None, retry_time=3, method='get', encoding='utf-8', retry_interval=1, timeout=3, *args,
            **kwargs):
        """
        get method
        :param url: target url
        :param header: headers default:
        :param retry_time: retry time default: 3
        :param retry_interval: retry interval default: 1
        :param timeout: network timeout default: 3
        :return:
        """
        self.current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        header = self.header
        self.method = method
        self.retry_time = retry_time
        self.retry_interval = retry_interval
        if headers and isinstance(headers, dict):
            header.update(headers)
        while True:
            try:
                self.amount += 1
                self.response = requests.request(
                    url=url, headers=header, timeout=timeout, method=method, *args, **kwargs)
                self.response.encoding = encoding
                if self.response.status_code == 200:
                    self.samount += 1
                    logging.info(
                        f'{self.current_time} [Spider] True [Method] {method} [Num] {self.amount} [Status] {self.response.status_code} [Url]: {self.response.url}')
                    return self
                else:
                    logging.error(
                        f'{self.current_time} [Spider] False [Method] {self.method} [Num] {self.amount} [Status] {self.response.status_code} [Url]: {self.response.url}')
                    raise Exception(f'Respider {self.retry_interval}s')
            except SSLError as e:
                self.famount += 1
                logging.error(e)
                return self
            except Exception as e:
                self.famount += 1
                logging.error(e)
                retry_time -= 1
                if retry_time <= 0:
                    return None
                time.sleep(retry_interval)

    @property
    def text(self):
        return self.response.text

    @property
    def content(self):
        return self.response.content

    @property
    def url(self):
        return self.response.url

    @property
    def history(self):
        return self.response.history

    @property
    def json(self):
        return json.loads(self.response.text)

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    def get_len(self):
        return len(self.response.text)

    @property
    def tree(self):
        return Xpath(self.response.text)

    def __del__(self):
        self.end_time = time.time()
        spend_time = self.end_time - self.start_time
        msg = """
Requests: %s
Success Requests: %s
False Requests: %s
Requests Time: %s
        """ % (self.amount, self.samount, self.famount, spend_time)
        logging.info(msg)
