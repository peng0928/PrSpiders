from urllib.parse import urljoin
import re, time, copy
from lxml import etree
from datetime import timedelta, datetime
from table_parse import tb_parse
import unicodedata
from .PrSpiders import logging


class Xpath(object):
    def __init__(self, response, encoding='utf-8'):
        if isinstance(response, str):
            self.res = etree.HTML(response)
        else:
            response.encoding = encoding
            self.res = etree.HTML(response.text)

    def xpath(self, x=None, filter='style|script', character=True, is_list=False, easy=False, rule=None):
        """
        x: xpath 语法
        filter: 过滤器
        character: join方法带换行
        is_list: 是否为列表 True 列表,
        easy: xpath默认子集关系
        rule: 正则提取
        """
        try:
            self.treeres = xpath_filter(self.res, filter)
            self.treeres = self.treeres.xpath(x)
            return prxpath(xp=self.treeres, xp_rule=x)
        except Exception as e:
            logging.error(e)

    def xxpath(self, x=None):
        return self.res.xpath(x)

    def dpath(self, x=None, rule=None):
        x = x.split('|')
        x = [i + '//text()' if '/@' not in i else i for i in x]
        x = '|'.join(x)
        obj = self.res.xpath(x)
        obj = [i.replace('\n', '').strip() for i in obj]
        obj = ' '.join(obj)
        obj = self.process_date(data=obj, rule=rule)
        return obj

    def tbxpath(self, tb_xpath=None, p='S', text=None, lable='th'):
        if text is None:
            text = self.res
        return tb_parse.tbxpath(tb_xpath=tb_xpath, p=p, text=text, lable=lable)

    def fxpath(self, x=None, p='', h='', rule=None):
        le = x.split('|')
        if len(le) > 1:
            x = x.split('|')
            for item in x:
                p += item + '//text()|'
                h += item + '//@href|'
            p = p[:-1]
            h = h[:-1]
        else:
            p = x + '//text()'
            h = x + '//@href'

        filename = self.res.xpath(p) or None
        filelink = self.res.xpath(h) or None
        fn = []
        fk = []
        try:
            if filename is not None and filelink is not None:
                for i in range(len(filelink)):
                    is_file = bool(
                        re.search(r'(\.tar|\.shtml|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)',
                                  str(filename[i])))
                    is_link = bool(
                        re.search(r'(\.tar|\.shtml|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)',
                                  str(filelink[i])))
                    if is_file or is_link:
                        fn.append(filename[i])
                        fk.append(filelink[i])
                    else:
                        pass
                if fn is not None and fk is not None:
                    filename = '|'.join(fn)
                    filename = self.replace(filename).replace('\n', '')
                    filelink = [urljoin(rule, i) for i in fk]
                    filelink = '|'.join(filelink)

                if len(filelink) == 0 or len(filename) == 0:
                    return None, None
                else:
                    return filename, filelink
            else:
                return None, None
        except:
            return None, None

    def replace(self, str):
        result = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(
            1).encode("utf-8").decode("unicode-escape"), str)
        result = re.sub(r'(\\r|\\n|\\t|\xa0|\\u[0-9]{4})', lambda x: '', result)
        result = unicodedata.normalize('NFKC', result)
        return result.strip()

    def process_text(self, obj, character=True, is_list=False):
        try:
            obj = [self.replace(i) for i in obj]
            obj = [i for i in obj if len(i) > 0]
            if is_list:
                return obj
            character = '\n' if character else ''
            result = character.join(obj)
            return result
        except Exception as e:
            print(e)
            return None


class prxpath():

    def __init__(self, xp=None, xp_rule=None):
        self.xp = xp

        self._expr = xp_rule

    def getall(self):
        if isinstance(self.xp, list):
            self.xp = [prxpath(_, self._expr) for _ in self.xp]
        return self.xp

    def get(self):
        return self.xp

    def xpath(self, xp_rule=None, filter=None):
        self._expr = xp_rule
        self.treeres = xpath_filter(self.xp, filter)
        xp = self.treeres.xpath(xp_rule)
        return prxpath(xp, xp_rule)

    def text(self, lists=False, warps=0, repl=True):
        """
        :param lists: 是否返回列表,True返回列表
        :param warps: 换行符合 0*\n
        :param repl: 文本进行格式化
        :return:  返回解析文本的字符串或者列表
        """
        text_xpath = './/text()'
        if 'text()' in self._expr:
            return self.xp
        warps = '\n' * warps
        if isinstance(self.xp, list):
            self.result = [_.xpath(text_xpath) for _ in self.xp]
            if lists is False:
                self.result = [f'{warps}'.join([replace(i) for i in _]) for _ in self.result] if repl is True else [
                    f'{warps}'.join(_) for _ in self.result]
                self.result = [replace(_) for _ in self.result]
                self.result = [_ for _ in self.result if _ != '']
                self.result = f'{warps}'.join(self.result) if len(self.result) == 1 else self.result
            else:
                self.result = [f'{warps}'.join(_) for _ in self.result]
                self.result = [replace(_) for _ in self.result] if repl else self.result

        else:
            self.result = self.xp.xpath(text_xpath)
            if lists is False:
                self.result = [replace(_) for _ in self.result] if repl else self.result
                self.result = f'{warps}'.join(self.result)

        return self.result

    def date(self):
        text = self.text()
        if isinstance(text, str):
            return Process_Date.process_date(text)
        else:
            pass

    def __str__(self) -> str:
        data = self.xp
        return f"<{type(self).__name__} xpath={self._expr!r} data={data}>"


def replace(str):
    result = re.sub('([\r]|[\n]|[\t]|[\xa0])', lambda x: '', str)
    return result.strip()


class Process_Date:
    """处理时间类"""

    @classmethod
    def process_date(self, data=None):
        if data is None or len(data) == 0:
            return None
        data = self.parse_txt(data)
        try:
            result = self.parse_time(data)
            return result
        except Exception as e:
            logging.error(e)
            return None

    @classmethod
    def repl_date(self, l: list):
        if len(l) > 1:
            raise ValueError('匹配时间数量超过一个')
        res = ''.join(l).strip()
        res = re.sub('年|月|/', '-', res)
        res = re.sub('日|秒', '', res)
        res = re.sub('时|分|：', ':', res)
        return self.timechange(res)

    @classmethod
    def timechange(self, start_date):
        daterule = '%Y-%m-%d' if ':' not in start_date else '%Y-%m-%d %H:%M:%S'
        dateres = datetime.strptime(start_date, daterule)
        return dateres

    @classmethod
    def parse_time(self, s_time):
        result_time = ''
        start_rule = '(\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}时\d{1,2}分\d{1,2}秒' \
                     '|\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}时\d{1,2}分\d{1,2}' \
                     '|\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}:\d{1,2}:\d{1,2}' \
                     '|\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}：\d{1,2}：\d{1,2}' \
                     '|\d{4}\S\d{1,2}\S\d{1,2}\S?)'
        # 1、2017-06-15
        res = re.findall(start_rule, s_time)
        if res:
            result_time = self.repl_date(res)
        # 6天前
        elif u'天前' in s_time:
            days = re.findall(u'(\d+)天前', s_time)[0]
            result_time = (datetime.now() - timedelta(days=int(days))).strftime("%Y-%m-%d %H:%M:%S")

        # 昨天 18:03
        elif u'昨天' in s_time:
            last_time = re.findall(r'.*?(\d{1,2}:\d{1,2})', s_time)[0]
            days_ago = datetime.now() - timedelta(days=int(1))
            y_m_d = str(days_ago.year) + '-' + str(days_ago.month) + '-' + str(days_ago.day)
            _time = y_m_d + ' ' + last_time
            result_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(_time, "%Y-%m-%d %H:%M"))

        elif u'前天' in s_time:
            last_time = re.findall(r'.*?(\d{1,2}:\d{1,2})', s_time)[0]
            days_ago = datetime.now() - timedelta(days=int(2))
            y_m_d = str(days_ago.year) + '-' + str(days_ago.month) + '-' + str(days_ago.day)
            _time = y_m_d + ' ' + last_time
            result_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(_time, "%Y-%m-%d %H:%M"))

        # 28分钟前
        elif u'分钟前' in s_time:
            minutes = re.findall(u'(\d+)分钟', s_time)[0]
            minutes_ago = (datetime.now() - timedelta(minutes=int(minutes))).strftime("%Y-%m-%d %H:%M:%S")
            result_time = minutes_ago

        elif u'秒前' in s_time:
            second = re.findall(u'(\d+)秒前', s_time)[0]
            second_ago = (datetime.now() - timedelta(seconds=int(second))).strftime("%Y-%m-%d %H:%M:%S")
            result_time = second_ago

        # 06-29 1月12日
        elif re.findall(r'\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}日', s_time) and len(s_time) <= 5:
            s_time = s_time.replace('月', '-').replace('日', '')
            now_year = str(datetime.now().year)
            _time = now_year + '-' + s_time
            result_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(_time, "%Y-%m-%d"))

        # 1小时前
        elif u'小时前' in s_time:
            hours = re.findall(u'(\d+|半)小时前', s_time)[0]
            hours = 0.5 if hours == '半' else hours
            hours_ago = (datetime.now() - timedelta(hours=float(hours))).strftime("%Y-%m-%d %H:%M:%S")
            result_time = hours_ago

        return result_time

    @classmethod
    def parse_txt(self, data):
        while '  ' in data:
            data = data.replace('  ', ' ')
        return data


def xpath_filter(response=None, filter=None):
    if filter is None or filter == '':
        return response
    else:
        response = copy.deepcopy(response)
        filter_num = filter.split('|')
        if len(filter_num) > 1:
            filter = filter.split('|')
            filter = '//' + '|//'.join(filter)
        else:
            filter = '//' + filter
        ele = response.xpath(filter)
        for e in ele:
            e.getparent().remove(e)
        return response
