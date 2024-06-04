import unicodedata
import re, time, copy
from parsel import Selector
from urllib.parse import urljoin
from PrSpider.log import loguercor
from datetime import timedelta, datetime
from .dateParse import Process_Date


def replace(str):
    result = re.sub("([\r]|[\n]|[\t]|[\xa0])", lambda x: "", str)
    return result.strip()


class Css:
    def __init__(self, response):
        self.response = response
        self.selector = Selector(response.text)

    def css(self, query, **kwargs):
        selector = self.selector.css(query, **kwargs)
        return CssIterator(selector, query, self.response)


class CssIterator:

    def __init__(self, selector=None, rule=None, response=None):
        """
            selector: xpath 对象
            rule: xpath 语法
            response: response 对象
        """
        self.rule = rule
        self.selector = selector
        self.response = response
        self.iterTree = iter(list(self.selector))

    def __iter__(self):
        return self

    def __next__(self):
        selector = next(self.iterTree)
        return CssSelector(selector, self.rule, self.response)

    def __str__(self):
        return repr(self.selector)

    def text(self, lists=False, warps=0, repl=True):
        """
        :param lists: 是否返回列表,True返回列表
        :param warps: 换行符合 0*\n
        :param repl: 文本进行格式化
        :return:  返回解析文本的字符串或者列表
        """
        text_xpath = "::text"
        if "::text" in self.rule:
            return self.selector.getall()
        warps = "\n" * warps
        if isinstance(self.selector, list):
            result = [_.css(text_xpath).getall() for _ in self.selector]
            if lists is False:
                result = (
                    [f"{warps}".join([replace(i) for i in _]) for _ in result]
                    if repl is True
                    else [f"{warps}".join(_) for _ in result]
                )
                result = [replace(_) for _ in result]
                result = [_ for _ in result if _ != ""]
                result = (
                    f"{warps}".join(result)
                    if len(result) == 1
                    else result
                )
            else:
                result = [f"{warps}".join(_) for _ in result]
                result = [replace(_) for _ in result] if repl else result

        else:
            result = self.selector.xpath(text_xpath).getall()
            if lists is False:
                result = [replace(_) for _ in result] if repl else result
                result = f"{warps}".join(result)

        return result

    def getall(self):
        return self.selector.getall()

    def get(self):
        return self.selector.get()

    def href(self):
        """
        :return: 返回解析的链接
        """
        href_xpath = ".//@href"
        if "/@href" in self.rule:
            return self.selector
        if isinstance(self.selector, list):
            result = [_.xpath(href_xpath).getall() for _ in self.selector]
        else:
            result = self.selector.xpath(href_xpath).getall()

        if result:
            result = [i if i else i for i in result]
            result = [''.join(i) if isinstance(i, list) else i for i in result]
            result = [urljoin(self.response.url, i) if 'http' not in i else i for i in result]
        if len(result) == 1 and isinstance(result, list):
            result = result[0]
        return result

    def date(self):
        text = self.text()
        if isinstance(text, str):
            return Process_Date.process_date(text)
        else:
            text = ''.join(self.text())
            return Process_Date.process_date(text)

    def css(self, query, **kwargs):
        selector = self.selector.css(query, **kwargs)
        return CssIterator(selector, query, self.response)


class CssSelector:

    def __init__(self, selector=None, rule=None, response=None):
        """
            selector: xpath 对象
            rule: xpath 语法
            response: response 对象
        """
        self.rule = rule
        self.selector = selector
        self.response = response

    def __str__(self):
        return repr(self.selector)

    def text(self, lists=False, warps=0, repl=True):
        """
        :param lists: 是否返回列表,True返回列表
        :param warps: 换行符合 0*\n
        :param repl: 文本进行格式化
        :return:  返回解析文本的字符串或者列表
        """
        text_css = "::text"
        if "::text" in self.rule:
            return self.selector.getall()
        warps = "\n" * warps
        if isinstance(self.selector, list):
            result = [_.css(text_css).getall() for _ in self.selector]
            if lists is False:
                result = (
                    [f"{warps}".join([replace(i) for i in _]) for _ in result]
                    if repl is True
                    else [f"{warps}".join(_) for _ in result]
                )
                result = [replace(_) for _ in result]
                result = [_ for _ in result if _ != ""]
                result = (
                    f"{warps}".join(result)
                    if len(result) == 1
                    else result
                )
            else:
                result = [f"{warps}".join(_) for _ in result]
                result = [replace(_) for _ in result] if repl else result

        else:
            result = self.selector.css(text_css).getall()
            if lists is False:
                result = [replace(_) for _ in result] if repl else result
                result = f"{warps}".join(result)

        return result

    def getall(self):
        return self.selector.getall()

    def get(self):
        return self.selector.get()

    def href(self):
        """
        :return: 返回解析的链接
        """
        href_xpath = ".//@href"
        if "/@href" in self.rule:
            return self.selector
        if isinstance(self.selector, list):
            result = [_.xpath(href_xpath).getall() for _ in self.selector]
        else:
            result = self.selector.xpath(href_xpath).getall()

        if result:
            result = [i if i else i for i in result]
            result = [''.join(i) if isinstance(i, list) else i for i in result]
            result = [urljoin(self.response.url, i) if 'http' not in i else i for i in result]
        if len(result) == 1 and isinstance(result, list):
            result = result[0]
        return result

    def date(self):
        text = self.text()
        if isinstance(text, str):
            return Process_Date.process_date(text)
        else:
            text = ''.join(self.text())
            return Process_Date.process_date(text)

    def css(self, query, **kwargs):
        selector = self.selector.css(query, **kwargs)
        return CssIterator(selector, query, self.response)


