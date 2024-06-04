import re
import time
import copy
import unicodedata
from parsel import Selector
from urllib.parse import urljoin
from PrSpider.log import loguercor
from .dateParse import Process_Date
from datetime import timedelta, datetime


def replace(str):
    result = re.sub("([\r]|[\n]|[\t]|[\xa0])", lambda x: "", str)
    return result.strip()


def node_remove(selector, filter):
    if filter is None or filter == "":
        return selector
    else:
        filter_num = filter.split("|")
        if len(filter_num) > 1:
            filter = filter.split("|")
            filter = "//" + "|//".join(filter)
        else:
            filter = "//" + filter
        nodes_to_remove = selector.xpath(filter)
        # 遍历要删除的节点，并逐个删除
        for node in nodes_to_remove:
            node.drop()
        return selector


class Xpath(object):
    def __init__(self, response, encoding="utf-8"):
        self.response = response
        if isinstance(response, str):
            self.tree = Selector(response)
        else:
            response.encoding = encoding
            self.tree = Selector(response.text)

    def xpath(self, x=None, f="", **kwargs):
        """
        x: xpath 语法
        f: 过滤器
        """
        try:
            self.tree = node_remove(self.tree, f)
            self.tree = self.tree.xpath(x, **kwargs)
            return XpathIterator(self.tree, x, self.response)
        except Exception as e:
            loguercor.log('WARNING', f'Xpath Parses WARNING: {e}')
            return None

    def fxpath(self, x=None, p="", h="", rule=None):
        le = x.split("|")
        if len(le) > 1:
            x = x.split("|")
            for item in x:
                p += item + "//text()|"
                h += item + "//@href|"
            p = p[:-1]
            h = h[:-1]
        else:
            p = x + "//text()"
            h = x + "//@href"

        filename = self.res.xpath(p) or None
        filelink = self.res.xpath(h) or None
        fn = []
        fk = []
        try:
            if filename is not None and filelink is not None:
                for i in range(len(filelink)):
                    is_file = bool(
                        re.search(
                            r"(\.tar|\.shtml|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)",
                            str(filename[i]),
                        )
                    )
                    is_link = bool(
                        re.search(
                            r"(\.tar|\.shtml|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)",
                            str(filelink[i]),
                        )
                    )
                    if is_file or is_link:
                        fn.append(filename[i])
                        fk.append(filelink[i])
                    else:
                        pass
                if fn is not None and fk is not None:
                    filename = "|".join(fn)
                    filename = self.replace(filename).replace("\n", "")
                    filelink = [urljoin(rule, i) for i in fk]
                    filelink = "|".join(filelink)

                if len(filelink) == 0 or len(filename) == 0:
                    return None, None
                else:
                    return filename, filelink
            else:
                return None, None
        except:
            return None, None

    def replace(self, str):
        result = re.sub(
            r"(\\u[a-zA-Z0-9]{4})",
            lambda x: x.group(1).encode("utf-8").decode("unicode-escape"),
            str,
        )
        result = re.sub(
            r"(\\r|\\n|\\t|\xa0|\\u[0-9]{4})", lambda x: "", result)
        result = unicodedata.normalize("NFKC", result)
        return result.strip()

    def process_text(self, obj, character=True, is_list=False):
        try:
            obj = [self.replace(i) for i in obj]
            obj = [i for i in obj if len(i) > 0]
            if is_list:
                return obj
            character = "\n" if character else ""
            result = character.join(obj)
            return result
        except Exception as e:
            print(e)
            return None

    def __str__(self):
        return str(self.tree)


class XpathIterator:

    def __init__(self, selector=None, rule=None, response=None):
        """
            selector: xpath 对象
            rule: xpath 语法
            response: response 对象
        """
        self.rule = rule
        self.selector = selector
        self.response = response
        self.iterTree = iter(self.selector)

    def __iter__(self):
        return self

    def __next__(self):
        selector = next(self.iterTree)
        return XpathSelector(selector, self.rule, self.response)

    def __str__(self):
        return repr(self.selector)

    def text(self, lists=False, warps=0, repl=True):
        """
        :param lists: 是否返回列表,True返回列表
        :param warps: 换行符合 0*\n
        :param repl: 文本进行格式化
        :return:  返回解析文本的字符串或者列表
        """
        text_xpath = ".//text()"
        if "/text()" in self.rule:
            return self.selector.getall()
        warps = "\n" * warps
        if isinstance(self.selector, list):
            result = [_.xpath(text_xpath).getall() for _ in self.selector]
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
            return self.selector.getall()
        if isinstance(self.selector, list):
            result = [_.xpath(href_xpath).getall() for _ in self.selector]
        else:
            result = self.selector.xpath(href_xpath).getall()

        if result:
            result = [i if i else i for i in result]
            result = [''.join(i) if isinstance(i, list) else i for i in result]
            result = [urljoin(self.response.url, i)
                      if 'http' not in i else i for i in result]
        if len(result) == 1 and isinstance(result, list):
            result = result[0]
        return result

    def date(self):
        text = self.text()
        if isinstance(text, str):
            return Process_Date.process_date(text)
        else:
            text = self.text(lists=True)
            return [Process_Date.process_date(str(i)) for i in text]

    def xpath(self, x=None, f="", **kwargs):
        """
        x: xpath 语法
        f: 过滤器
        """
        try:
            selector = node_remove(self.selector, f)
            selector = self.selector.xpath(x, **kwargs)
            return XpathIterator(selector, x, self.response)
        except Exception as e:
            loguercor.log('WARNING', f'Xpath Parses WARNING: {e}')
            return None


class XpathSelector:

    def __init__(self, selector=None, rule=None, response=None):
        """
            selector: xpath 对象
            rule: xpath 语法
            response: response 对象
        """
        self.rule = rule
        self.selector = selector
        self.response = response

    def text(self, lists=False, warps=0, repl=True):
        """
        :param lists: 是否返回列表,True返回列表
        :param warps: 换行符合 0*\n
        :param repl: 文本进行格式化
        :return:  返回解析文本的字符串或者列表
        """
        text_xpath = ".//text()"
        if "/text()" in self.rule:
            return self.selector.getall()
        warps = "\n" * warps
        if isinstance(self.selector, list):
            result = [_.xpath(text_xpath).getall() for _ in self.selector]
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

    def xpath(self, x=None, f="", **kwargs):
        """
        x: xpath 语法
        f: 过滤器
        """
        try:
            selector = node_remove(self.selector, f)
            selector = self.selector.xpath(x, **kwargs)
            return XpathIterator(selector, x, self.response)
        except Exception as e:
            loguercor.log('WARNING', f'Xpath Parses WARNING: {e}')
            return None

    def href(self):
        """
        :return: 返回解析的链接
        """
        href_xpath = ".//@href"
        if "/@href" in self.rule:
            return self.selector.getall()
        if isinstance(self.selector, list):
            result = [_.xpath(href_xpath).getall() for _ in self.selector]
        else:
            result = self.selector.xpath(href_xpath).getall()
        if result:
            result = [i if i else i for i in result]
            result = [''.join(i) if isinstance(i, list) else i for i in result]
            result = [urljoin(self.response.url, i)
                      if 'http' not in i else i for i in result]
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

    def __str__(self):
        return repr(self.selector)
