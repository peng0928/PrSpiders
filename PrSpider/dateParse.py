import re, time, copy
from PrSpider.log import loguercor
from datetime import timedelta, datetime


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
            loguercor.warning('@Date时间处理错误 | [%s] | %s' % (data, e))
            return None

    @classmethod
    def repl_date(self, l: str):
        res = "".join(l).strip()
        res = re.sub("年|月|/", "-", res)
        res = re.sub("日|秒", "", res)
        res = re.sub("时|分|：", ":", res)
        return self.timechange(res)

    @classmethod
    def timechange(self, start_date):
        # todo 2022-1-1 12:00 这种格式未适应
        if ':' in start_date:
            start_date = self.check_len(start_date)
        daterule = "%Y-%m-%d" if ":" not in start_date else "%Y-%m-%d %H:%M:%S"
        dateres = datetime.strptime(start_date, daterule)
        return dateres

    @classmethod
    def parse_time(self, s_time):
        result_time = ""
        res = self.re_match(s_time)
        if res:
            result_time = self.repl_date(res)
        # 6天前
        elif "天前" in s_time:
            days = re.findall("(\d+)天前", s_time)[0]
            result_time = (datetime.now() - timedelta(days=int(days))).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # 昨天 18:03
        elif "昨天" in s_time:
            try:
                last_time = re.findall(r".*?(\d{1,2}:\d{1,2})", s_time)[0]
            except:
                last_time = '00:00'
            days_ago = datetime.now() - timedelta(days=int(1))
            y_m_d = (
                    str(days_ago.year) + "-" + str(days_ago.month) + "-" + str(days_ago.day)
            )
            _time = y_m_d + " " + last_time
            result_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.strptime(_time, "%Y-%m-%d %H:%M")
            )

        elif "前天" in s_time:
            try:
                last_time = re.findall(r".*?(\d{1,2}:\d{1,2})", s_time)[0]
            except:
                last_time = '00:00'
            days_ago = datetime.now() - timedelta(days=int(2))
            y_m_d = (
                    str(days_ago.year) + "-" + str(days_ago.month) + "-" + str(days_ago.day)
            )
            _time = y_m_d + " " + last_time
            result_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.strptime(_time, "%Y-%m-%d %H:%M")
            )

        # 28分钟前
        elif "分钟前" in s_time:
            minutes = re.findall("(\d+)分钟", s_time)[0]
            minutes_ago = (datetime.now() - timedelta(minutes=int(minutes))).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            result_time = minutes_ago

        elif "秒前" in s_time:
            second = re.findall("(\d+)秒前", s_time)[0]
            second_ago = (datetime.now() - timedelta(seconds=int(second))).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            result_time = second_ago

        # 06-29 1月12日
        elif (
                re.findall(r"\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}日", s_time) and len(s_time) <= 5
        ):
            s_time = s_time.replace("月", "-").replace("日", "")
            now_year = str(datetime.now().year)
            _time = now_year + "-" + s_time
            result_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.strptime(_time, "%Y-%m-%d")
            )

        # 1小时前
        elif "小时前" in s_time:
            hours = re.findall("(\d+|半)小时前", s_time)[0]
            hours = 0.5 if hours == "半" else hours
            hours_ago = (datetime.now() - timedelta(hours=float(hours))).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            result_time = hours_ago

        return result_time

    @classmethod
    def parse_txt(self, data):
        while "  " in data:
            data = data.replace("  ", " ")
        return data

    @classmethod
    def check_len(self, date):
        fommat = '0000:00:00 00:00:00'
        len_date = len(date)
        if len_date >= 11 and len_date < 19:
            date = str(date) + str(fommat[len_date: 19])
        return date

    @classmethod
    def re_match(self, s_time):
        match_list = []
        start_rule = [
            "\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}时\d{1,2}分\d{1,2}秒",
            "\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}时\d{1,2}分\d{1,2}",
            "\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}:\d{1,2}:\d{1,2}",
            "\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}：\d{1,2}：\d{1,2}",
            "\d{4}\S\d{1,2}\S\d{1,2}\S? \d{1,2}:\d{1,2}",
            "\d{4}\S\d{1,2}\S\d{1,2}",
        ]
        for item in start_rule:
            result = re.findall(item, s_time)
            if result:
                for data in result:
                    match_list.append(data)
        best_date = max(match_list, key=len)
        right_match = list(filter(lambda x: len(x) == 19, match_list))
        if len(right_match) > 1:
            loguercor.warning(f"@Date时间解析结果存在多个 -> {right_match} | @当前选择结果为 -> {best_date}")
        return best_date
