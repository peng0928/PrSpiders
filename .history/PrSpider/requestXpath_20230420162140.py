from requests.exceptions import SSLError
import requests
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
__author__ = "penr"


class prequest(Xpath):
    def __init__(self, log):
        self.response = Response()
        self.log = log
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
        return {"user-agent": self.user_agent}

    def get(
        self,
        url,
        headers=None,
        retry_time=3,
        method="GET",
        meta=None,
        encoding="utf-8",
        retry_interval=1,
        timeout=3,
        settion=None,
        *args,
        **kwargs,
    ):
        """
        get method
        :param url: target url
        :param header: headers default:
        :param retry_time: retry time default: 3
        :param retry_interval: retry interval default: 1
        :param timeout: network timeout default: 3
        :return:
        """

        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = self.header
        self.method = method.upper()
        self.retry_time = retry_time
        self.retry_interval = retry_interval
        self.meta_ = meta
        if headers and isinstance(headers, dict):
            if headers.get("user-agent") or headers.get("User-Agent"):
                header = {}
            header.update(headers)
        while True:
            try:
                self.response = requests.request(
                    url=url,
                    headers=header,
                    timeout=timeout,
                    method=self.method,
                    *args,
                    **kwargs,
                )
                self.response.encoding = encoding
                if self.response.ok:
                    return self
                else:
                    raise Exception(f"Respider {self.retry_interval}s")
            except Exception as e:
                if settion.retry:
                    self.log.info(
                        "[Retry] %s [Msg] %s [Interval] %ss" % (url, e, retry_interval)
                    )
                else:
                    self.log.info(
                        "%s [ERRORS] %s [Msg] %s" % (self.current_time, url, e)
                    )

                retry_time -= 1
                if retry_time <= 0 or settion.retry is False:
                    self.response.status_code = (
                        410
                        if not self.response.status_code
                        else self.response.status_code
                    )
                    return self
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
    def code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    def len(self):
        return len(self.response.text)

    @property
    def tree(self):
        return Xpath(self.response.text)

    def xpath(self, xpath_str, **kwargs):
        return Xpath(self.response.text).xpath(xpath_str, **kwargs)

    @property
    def ok(self):
        return self.response.ok

    @property
    def meta(self):
        return self.meta_

    def close(self):
        self.response.close()

    def __str__(self) -> str:
        return f"<Response Code={self.code} Len={self.len}>"
