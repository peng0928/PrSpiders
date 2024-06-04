import os
from typing import Optional
from queue import PriorityQueue
from .utils import *
import inspect
import threading

filter_settions = [
    'executor', 'pid', 'init',
]


class _IT:
    def __init__(self, level, data):
        self.level = level
        self.data = data

    def __lt__(self, other):
        if self.level == other.level:
            return len(self.data) < len(other.data)
        return self.level < other.level

    def __str__(self):
        return f'<{self.data}>'


class defaultSettions:
    """默认配置（不建议进行修改）"""
    request_num: Optional[int] = 0  # 请求数
    retry_num: Optional[int] = 0  # 重试数
    success_num: Optional[int] = 0  # 成功请求数
    false_num: Optional[int] = 0  # 失败请求数
    work_dir: Optional[str] = os.getcwd()  # 工作目录
    file_name: Optional[str] = inspect.getframeinfo(inspect.currentframe()).filename  # 文件名
    executor: Optional[object] = object  # 线程池处理器
    pid: Optional[int] = os.getppid()  # 程序进程id
    start_time: Optional[float] = float  # 开始时间
    futures: Optional[list] = set()  # 线程池对象
    Queues: Optional[object] = PriorityQueue()  # 优先级队列
    init: Optional[int] = 0  # 日志初始化
    deep_func: Optional[list] = []  # 深度函数
    Request: Optional[object] = object  # 请求对象
    schedule_time: Optional[float] = 0.0314  # 调度时间
    redis: Optional[dict] = {}  # redis配置
    redis_serve: Optional[object] = object  # redis服务对象
    event: Optional[object] = threading.Event()


class settions(defaultSettions):
    """设置"""
    thread_num: Optional[int] = 10  # 线程数
    start_urls: Optional[list] = None  # 默认请求起始url
    retry: Optional[bool] = True  # 重试开关，默认开启
    retry_xpath: Optional[str] = None  # 重试开关，默认开启
    download_delay: Optional[int] = 0  # 请求下载周期 默认0s
    download_num: Optional[int] = 5  # 请求下载数量 默认5/次
    logger: Optional[bool or str] = False  # 日志存储开关，默认关闭：可选（bool|文件名）
    log_level: Optional[str] = 'DEBUG'  # 日志等级，默认info
    log_color: Optional[str] = 'red'  # 日志颜色，默认红色
    log_stdout: Optional[bool] = False  # 日志控制台重定向，默认关闭
    custom_settings: Optional[dict] = {}  # 通用设置
    session: Optional[bool] = True  # 请求是否开启session;默认开启
    traceback: Optional[bool] = False  # 当程序发生异常时，是否显示堆栈;默认关闭
    log_format: Optional[str] = log_format  # 日志格式 文件utils.log_format
    pipelines: Optional[dict] = {}  # 管道(工作目录)
    dont_filter: bool = False  # 请求去重, False: 开启去重, Ture: 关闭去重
    filterSet: Optional[set] = set()  # 本地去重集合
