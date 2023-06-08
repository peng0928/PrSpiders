import os
import time
from typing import Optional
from loguru import logger as loguer
from .requestXpath import prequest
from concurrent.futures import ThreadPoolExecutor, as_completed
from .pyconn import PrMysql
from .log import *


class settions(object):
    """设置"""
    workers: Optional[int] = 10000  # 线程池
    request_num: Optional[int] = 0  # 请求数
    retry_num: Optional[int] = 0  # 重试数
    success_num: Optional[int] = 0  # 成功请求数
    false_num: Optional[int] = 0  # 失败请求数
    start_urls: Optional[list] = None  # 默认请求起始url
    executor: Optional[object] = None  # 线程池处理器
    retry: Optional[bool] = True  # 重试开关，默认开启
    retry_xpath: Optional[str] = None  # 重试开关，默认开启
    pid: Optional[int] = os.getppid()  # 程序进程id
    start_time: Optional[int] = time.time()  # 开始时间
    download_delay: Optional[int] = 0  # 请求下载周期 默认 0s
    download_num: Optional[int] = 5  # 请求下载数量 默认 5/次
    logger: Optional[bool or str] = False  # 日志存储开关，默认关闭；可选（bool|文件名）
    log_level: Optional[str] = 'info'  # 日志等级，默认info
    log_stdout: Optional[bool] = False  # 日志控制台重定向，默认关闭
    futures: Optional[list] = set()  # 线程池对象
    init: Optional[int] = 0  # 日志初始化


class PrSpiders(settions):
    """PrSpiders"""

    def __init__(self, **kwargs) -> None:
        settions.init += 1
        if settions.init <= 1:
            Log(self.log_stdout, self.log_level, self.logger).loggering()
        settions.request_num = self.request_num
        settions.success_num = self.success_num
        settions.false_num = self.false_num
        settions.retry = self.retry
        settions.retry_xpath = self.retry_xpath
        settions.futures = self.futures
        settions.workers = self.workers
        settions.download_delay = self.download_delay
        settions.executor = ThreadPoolExecutor(settions.workers)
        settions.download_num = self.download_num
        settions.logger = self.logger
        settions.log_stdout = self.log_stdout
        settions.log_level = self.log_level
        loguercor.log('Start',
                      "<red>~~~ @PrSpider Start  @Workers %s  @Retry %s  @Pid %s @Download_Delay %s @Download_Num %s @LOG_LEVEL %s ~~~</red>"
                      % (
                          self.workers,
                          self.retry,
                          self.pid,
                          self.download_delay,
                          self.download_num,
                          self.log_level.upper(),
                      )
                      )
        if not self.start_urls and not hasattr(self, "start_requests"):
            raise AttributeError("Crawling could not start: 'start_urls' not found ")
        else:
            self.start_requests(**kwargs)

    def start_requests(self, **kwargs):
        if isinstance(self.start_urls, str):
            self.start_urls = [self.start_urls]
        url_dim_list = [
            self.start_urls[i: i + self.download_num]
            for i in range(0, len(self.start_urls), self.download_num)
        ]
        for u in url_dim_list:
            time.sleep(self.download_delay)
            self.Requests(callback=self.parse, url=u, **kwargs)

    @classmethod
    def RequestsMap(
            cls,
            request=None,
            callback=None,
            headers=None,
            retry_time=3,
            method="GET",
            meta=None,
            encoding="utf-8",
            retry_interval=3,
            timeout=30,
            **kwargs,
    ):
        futures = set()
        if not isinstance(request, list):
            raise AttributeError(
                "Requests object must be list: [{'url': 1, 'data': 1, 'meta': {'t': '123'},{'url': 2, 'params': 2}]"
            )
        else:
            url_dim_list = [
                request[i: i + cls.download_num]
                for i in range(0, len(request), cls.download_num)
            ]
            for u in url_dim_list:
                time.sleep(cls.download_delay)
                for _u in u:
                    url = _u.get("url")
                    data = _u.get("data", None)
                    params = _u.get("params", None)
                    json = _u.get("json", None)
                    meta = _u.get("meta", None)
                    kwargs.update({"data": data}) if data else kwargs
                    kwargs.update({"params": params}) if params else kwargs
                    kwargs.update({"json": json}) if json else kwargs
                    task = cls.executor.submit(
                        cls.fetch,
                        url=url,
                        callback=callback,
                        headers=headers,
                        timeout=timeout,
                        retry_time=retry_time,
                        method=method,
                        meta=meta,
                        encoding=encoding,
                        retry_interval=retry_interval,
                        **kwargs,
                    )
                    futures.add(task)
                    cls.futures.add(task)

                if len(cls.futures) > cls.workers:
                    loguercor.error(
                        f'<yellow>ThreadPoolExecutor workers not enough {len(cls.futures), cls.workers}.</yellow>')

                for future in as_completed(futures):
                    futures.remove(future)
                    worker_exception = future.exception()
                    cls.futures.remove(future) if future in cls.futures else cls.futures
                    if worker_exception:
                        loguercor.error(f"<red>[PrSpider Exception] %s</red>" % worker_exception)

    @classmethod
    def Requests(
            cls,
            url=None,
            callback=None,
            headers=None,
            retry_time=3,
            method="GET",
            meta=None,
            encoding="utf-8",
            retry_interval=3,
            timeout=30,
            **kwargs,
    ):
        if isinstance(url, str):
            url = [url]
        url_dim_list = [
            url[i: i + cls.download_num] for i in range(0, len(url), cls.download_num)
        ]
        futures = set()
        for u in url_dim_list:
            time.sleep(cls.download_delay)
            for _u in u:
                task = cls.executor.submit(
                    cls.fetch,
                    url=_u,
                    callback=callback,
                    headers=headers,
                    timeout=timeout,
                    retry_time=retry_time,
                    method=method,
                    meta=meta,
                    encoding=encoding,
                    retry_interval=retry_interval,
                    **kwargs,
                )
                futures.add(task)
                cls.futures.add(task)

            if len(cls.futures) > cls.workers:
                loguercor.error(
                    f'<yellow>ThreadPoolExecutor workers not enough {len(cls.futures)}</yellow>, {cls.workers}.')

            for future in as_completed(futures):
                futures.remove(future)
                worker_exception = future.exception()
                cls.futures.remove(future) if future in cls.futures else cls.futures
                if worker_exception:
                    loguercor.error(f"<red>[PrSpider Exception] %s</red>" % worker_exception)

    @classmethod
    def fetch(
            self,
            url,
            callback,
            headers=None,
            retry_time=3,
            method="GET",
            meta=None,
            encoding="utf-8",
            retry_interval=1,
            timeout=30,
            **kwargs,
    ):
        settions.request_num += 1
        response = prequest().get(
            url,
            headers=headers,
            retry_time=retry_time,
            method=method,
            meta=meta,
            encoding=encoding,
            retry_interval=retry_interval,
            timeout=timeout,
            settion=settions,
            **kwargs,
        )
        self.retry_num += int(response.meta.get("retry_num"))
        if response:
            if response.ok:
                settions.success_num += 1
                loguercor.log('Crawl',
                              f"<red>{method.upper()}</red> <yellow>{response.code}</yellow> <blue>{url}</blue>")
                return callable(callback(response))
            else:
                settions.false_num += 1
                loguercor.error(f"<red>{method.upper()}</red> <yellow>{response.code}</yellow> <blue>{url}</blue>")
                return callable(callback(response))
        else:
            settions.false_num += 1
            loguercor.error(f"<red>{method.upper()}</red> <yellow>{response.code}</yellow> <blue>{url}</blue>")
            callback(response)
            return self

    @classmethod
    def parse(self, response):
        raise NotImplementedError(
            f"{self.__class__.__name__}.parse callback is not defined"
        )

    def process_timestamp(self, t):
        timeArray = time.localtime(int(t))
        formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return formatTime

    @classmethod
    def PrMysql(self, **kwargs):
        return PrMysql(loguer=loguer, **kwargs)

    def __del__(self):
        end_time = time.time()
        spend_time = end_time - self.start_time
        try:
            average_time = spend_time / self.request_num
        except ZeroDivisionError:
            average_time = 0
        m = """<green><Spider End>
| ------------------ | ----------------------                               
| `Workers`          | `%s`                                             
| `Download Delay`   | `%s`                                             
| `Download Num`     | `%s`                                             
| `Request Num`      | `%s`                                             
| `Success Num`      | `%s`                                             
| `False Num`        | `%s`                                              
| `Retry Num`        | `%s`                                              
| `Start Time`       | `%s`                                              
| `End Time`         | `%s`                                             
| `Spend Time`       | `%.3fs`                                          
| `Average Time`     | `%.3fs`         
| ------------------ | ---------------------- </green>                          
        """ % (
            self.workers,
            self.download_delay,
            self.download_num,
            self.request_num,
            self.success_num,
            self.false_num,
            self.retry_num,
            self.process_timestamp(self.start_time),
            self.process_timestamp(end_time),
            spend_time,
            average_time,
        )
        loguer.opt(colors=True).info(m)
