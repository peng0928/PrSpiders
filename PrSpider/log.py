import sys, os, re
from loguru import logger as loguer

loguercor = loguer.opt(colors=False)

level_dict = {
    'CRITICAL': {"level": "5"},
    'ERROR': {"level": "4"},
    'WARNING': {"level": "3"},
    "SUCCESS": {"level": "3"},
    "INFO": {"level": "2"},
    "DEBUG": {"level": "1"},
    'Print': {"level": "3", "color": "<green>"},
    'Crawl': {"level": "2", "color": "<green>"},
    'Traceback': {"level": "5", "color": "<red>"},
    'Exception': {"level": "4", "color": "<red>"},
    'Crawl Fasle': {"level": "3", "color": "<yellow>"},
    'Retry': {"level": "3", "color": "<yellow>"},
    'Yield': {"level": "1", "color": "<yellow>"},
    'Return': {"level": "3", "color": "<yellow>"},
    'Start': {"level": "2", "color": "<yellow>"},
    'Filter': {"level": "2", "color": "<yellow>"},
    'Downloader': {"level": "2", "color": "<red>"},
    'Pipelines': {"level": "2", "color": "<red>"},
    'Close': {"level": "1", "color": "<red>"},
}


def get_level(level):
    level_list = []
    for k, v in level_dict.items():
        if int(v.get("level")) >= level:
            level_list.append(k)
    return level_list


class Log():
    def __init__(self, cls) -> None:
        self.cls = cls
        log_stdout = getattr(cls, 'log_stdout', True)
        log_level = getattr(cls, 'log_level', 'INFO')
        log_file = getattr(cls, 'logger', False)
        format = getattr(cls, 'log_format', None)
        format = format.replace('color', cls.log_color)
        self.file_name = getattr(cls, 'file_name', 'log.log')
        log_level = log_level if log_level else "INFO"
        try:
            self.level_dict = {
                "warn": 'WARNING',
                "info": 'INFO',
                "debug": 'DEBUG',
                "error": 'ERROR',
                "critical": 'CRITICAL',
                "success": 'SUCCESS',
            }
            self.level_stdout = {
                "critical": get_level(5),
                "error": get_level(4),
                "success": get_level(3),
                "warn": get_level(3),
                "warning": get_level(3),
                "info": get_level(2),
                "debug": get_level(1),
            }
            self.log_stdout, self.log_level, self.log_file = log_stdout, log_level, log_file
            self.format = format
            os.environ['LOGFORMAT'] = format
            loguer.level("DEBUG", color="<green>")
            loguer.level("INFO", color="<cyan>")
            loguer.level("SUCCESS", color="<light-green>")
            loguer.level("WARNING", color="<yellow>")
            loguer.level("ERROR", color="<red>")
            loguer.level("CRITICAL", color="<red>")
            for k, v in level_dict.items():
                color = v.get("color")
                level = v.get("level")
                if color:
                    loguer.level(k, no=int(level) * 10, color=color)
        except Exception as e:
            loguer.exception(e)

    def loggering(self):
        try:
            levels = self.level_dict.get(self.log_level.lower())
            slevel = self.level_stdout.get(self.log_level.lower())
            os.environ['slevel'] = str(slevel)
            format = self.format
            stdout_handler = {
                "sink": sys.stdout,
                "colorize": True,
                "filter": lambda record: record["level"].name in slevel,
                "format": format
            }
            loguer.configure(handlers=[stdout_handler])
            if self.log_stdout:
                sys.stdout = InterceptHandler()
            if self.log_file:
                file_log = getattr(self.cls, 'work_dir', False) if self.log_file is True else self.log_file

                if file_log.startswith('/'):
                    file_log = '.' + file_log
                if file_log.endswith('.log') is False:
                    file_log += '.log'

                if file_log.startswith('./'):
                    loguer.add(file_log, level=levels, format=format)

                elif '://' in file_log:
                    loguer.add(file_log, level=levels, format=format)
                else:
                    loguer.add(file_log, level=levels, format=format)
            return loguer
        except Exception as e:
            loguer.exception(e)


class InterceptHandler():
    def write(self, message):
        if message.strip():
            loguer.log("Print", message.strip())

    def flush(self):
        pass


class loging:
    def __init__(self, log):
        self.loger = log

    def log(self, name, msg):
        self.loger.log(name, msg)

    def add(self, level_name, filename=None, level=30, color="yellow"):
        """
        添加日志级别和文件
        :param level_name: 日志级别名称
        :param filename: 文件名，默认为None
        :param level: 日志级别，默认为30
        :param color: 日志级别颜色，默认为"yellow"
        """
        try:
            self.loger.level(level_name, no=level, color=f'<{color}>')
        except TypeError:
            self.loger.level(level_name, color=f'<{color}>')
        slevel = eval(os.environ['slevel'])
        slevel.append(level_name)
        os.environ['slevel'] = str(slevel)
        stdout_handler = {
            "sink": sys.stdout,
            "colorize": True,
            "filter": lambda record: record["level"].name in slevel,
            "format": os.environ['LOGFORMAT']
        }
        self.loger.configure(handlers=[stdout_handler])
        if filename:
            self.loger.add(filename, level=level_name, format=os.environ['LOGFORMAT'],
                           filter=lambda record: record["level"].name == level_name)

    def print(self, msg):
        self.loger.log('Print', (msg))

    def yie(self, msg):
        self.loger.log('Yield', (msg))

    def crawl(self, msg):
        self.loger.log('Crawl', msg)

    def info(self, msg):
        self.loger.info(msg)

    def exception(self, msg):
        self.loger.exception(msg)

    def warn(self, msg):
        self.loger.warning(msg)

    def warning(self, msg):
        self.loger.warning(msg)

    def error(self, msg):
        self.loger.error(msg)

    def debug(self, msg):
        self.loger.debug(msg)

    def success(self, msg):
        self.loger.success(msg)

    def critical(self, msg):
        self.loger.critical(msg)

    def famat(self, msg):
        self
