import uuid
import requests
import time
from hashlib import md5
from requests.models import Response
from .useragent import get_ua
from .xpathApi import Xpath
from .cssApi import Css
from .log import loguercor

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


class SendRequest(Xpath):
    def __init__(self, Prspider, Request):
        self.retry_num = 0
        self.session = Request
        self.Prspider = Prspider
        self.response = Response()
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

    def get(self, url, headers=None, retry_time=3, method="GET", meta=None, encoding="utf-8", retry_interval=3,
            timeout=30, settion=None, retry=True, retry_xpath=None, *args, **kwargs):
        """
        get method
        :param url: target url
        :param header: headers default:
        :param retry_time: retry time default: 3
        :param retry_interval: retry interval default: 1
        :param timeout: network timeout default: 3
        :return:
        """
        header = self.header
        self.method = method.upper()
        self.retry_time = retry_time
        self.retry_interval = retry_interval
        self.meta_ = {"retry_num": self.retry_num}
        self.meta_.update(meta) if meta else meta
        if headers and isinstance(headers, dict):
            if headers.get("user-agent") or headers.get("User-Agent"):
                header = {}
            header.update(headers)
        while True:
            try:
                self.response = self.session.request(url=url, headers=header, timeout=timeout, method=self.method,
                                                     *args, **kwargs)
                self.response.encoding = encoding
                if self.response.ok:
                    retry_xpath = retry_xpath if retry_xpath else settion.retry_xpath
                    if retry_xpath and retry is True:
                        xpath_check = self.xpath(retry_xpath).getall()
                        if not xpath_check:
                            raise Exception(
                                f"Response Xpath Parse False ({self.code}) <{self.method} {self.url}>")

                    return self
                else:
                    raise Exception(f"Request False %s" % self.code)

            except Exception as e:
                retry_time -= 1
                self.retry_num += 1
                if retry_time < 0 or self.Prspider.retry is False or retry is False:
                    loguercor.log("Crawl Fasle", f"{e}")
                    self.meta_["retry_num"] = self.retry_num
                    callable(self.Prspider.error(self))
                    return self
                else:
                    loguercor.log(
                        "Retry", f"Response ({self.code}) <{self.method} {self.url}>")
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

    def json(self):
        try:
            return self.response.json()
        except Exception as e:
            raise ValueError(f'JSON FORMAT FALSE ==> {self.url}')

    def json_match(self, json_str, defaule=None):
        if not json_str or not isinstance(json_str, str):
            loguercor.error(f"Invalid JSON MATCH String: {json_str}")
            return None
        try:
            defaule = self.json()
            json_original = defaule.copy()
            json_split = json_str.split('.')
            for item in json_split:
                try:
                    if item.isdigit():
                        defaule = defaule[int(item)]
                    else:
                        defaule = defaule.get(item)
                except Exception as e:
                    loguercor.error(
                        f"JSON MATCH Flase: <{e}> (now: {item}) (origin: {json_str}) (Json Data: {json_original})")
                    return None
        except Exception as e:
            loguercor.error(f"JSON MATCH Flase, Except ==> {e}")
        return defaule

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
    def cookies(self):
        try:
            return requests.utils.dict_from_cookiejar(self.response.cookies)
        except:
            raise Exception('Get Response Cookie False')

    @property
    def request_cookies(self):
        try:
            return requests.utils.dict_from_cookiejar(self.response.request._cookies)
        except:
            raise Exception('Get Request Cookie False')

    @property
    def tree(self):
        return Xpath(self.response.text)

    def xpath(self, query, **kwargs):
        return Xpath(self.response).xpath(query, **kwargs)

    def css(self, query, **kwargs):
        return Css(self.response).css(query, **kwargs)

    @property
    def ok(self):
        try:
            return self.response.ok
        except Exception as e:
            return False

    @property
    def meta(self):
        return self.meta_

    @property
    def uuid(self):
        """
        生成一个唯一id(希望你能用到)
        :return:
        """
        new_uuid = uuid.uuid4()
        uuid_str = new_uuid.hex
        return uuid_str

    @property
    def request_id(self):
        """
        生成一个请求id(希望你能用到)
        :return:
        """
        urlcode = md5(self.url.encode())
        # 使用哈希对象的摘要生成 UUID
        uuid_str = uuid.UUID(urlcode.hexdigest()).hex
        return uuid_str

    def __del__(self):
        try:
            self.response.close()
        except:
            pass

    def __str__(self) -> str:
        return f"<Response Code={self.code} Len={self.len}>"
