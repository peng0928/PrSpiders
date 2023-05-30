import os
import re
import sys
import time
from typing import Optional
from loguru import logger as loguer
from .requestXpath import prequest
from concurrent.futures import ThreadPoolExecutor, as_completed
from .pyconn import PrMysql




class settions(object):
    workers: Optional[int] = 10000
    request_num: Optional[int] = 0
    retry_num: Optional[int] = 0
    success_num: Optional[int] = 0
    false_num: Optional[int] = 0
    setting: Optional[dict] = None
    start_urls: Optional[list] = None
    executor: Optional[object] = None
    retry: Optional[bool] = True
    pid: Optional[int] = os.getppid()
    start_time: Optional[int] = time.time()
    download_delay: Optional[int] = 0
    download_num: Optional[int] = 5
    logger: Optional[bool or str] = False
    log_level: Optional[str] = "info"
    log_stdout: Optional[bool] = False
    futures: Optional[list] = set()


class PrSpiders(settions):
    def __init__(self, **kwargs) -> None:
        settions.request_num = self.request_num
        settions.success_num = self.success_num
        settions.false_num = self.false_num
        settions.retry = self.retry
        settions.futures = self.futures
        settions.workers = self.workers
        settions.download_delay = self.download_delay
        settions.executor = ThreadPoolExecutor(settions.workers)
        settions.download_num = self.download_num
        settions.logger = self.logger
        settions.log_stdout = self.log_stdout
        settions.log_level = self.log_level
        self.loguer = self.loggering(self.logger, self.log_level)
        loguer.warning(
            "\033[31m~~~ @PrSpider Start  @Workers %s  @Retry %s  @Pid %s @Download_Delay %s @Download_Num %s @LOG_LEVEL %s ~~~\033[0m"
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
                    loguer.error(f'ThreadPoolExecutor workers not enough {len(cls.futures), cls.workers}.')

                for future in as_completed(futures):
                    futures.remove(future)
                    worker_exception = future.exception()
                    cls.futures.remove(future) if future in cls.futures else cls.futures
                    if worker_exception:
                        loguer.error(f"[PrSpider Exception] %s" % worker_exception)

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
                loguer.error(f'ThreadPoolExecutor workers not enough <green>{len(cls.futures)}</green>, {cls.workers}.')

            for future in as_completed(futures):
                futures.remove(future)
                worker_exception = future.exception()
                cls.futures.remove(future) if future in cls.futures else cls.futures
                if worker_exception:
                    loguer.error(f"[PrSpider Exception] %s" % worker_exception)

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
        response = prequest(loguer).get(
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
                loguer.info(
                    f"\033[31m{method.upper()}\033[0m | \033[33m{response.code}\033[0m | \033[34m{url}\033[0m")
                return callable(callback(response))
            else:
                settions.false_num += 1
                loguer.error(
                    f"\033[31m{method.upper()}\033[0m \033[33m{response.code}\033[0m \033[34m{url}\033[0m"
                )
                return callable(callback(response))
        else:
            settions.false_num += 1
            loguer.error(
                f"\033[31m{method.upper()}\033[0m \033[33m{response.code}\033[0m \033[34m{url}\033[0m")
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

    def loggering(self, file_log, level="info"):
        """
        打日志
        :param file_log: 日志文件名，类型string；
        """
        # 创建一个loggger，并设置日志级别
        level_dict = {
            "warn": 'WARNING',
            "info": 'INFO',
            "debug": 'DEBUG',
            "error": 'ERROR',
            "critical": 'CRITICAL',
        }
        level_stdout = {
            "critical": ['Print', 'CRITICAL'],
            "error": ['Print', 'ERROR', 'CRITICAL', ],
            "warn": ['Print', 'WARNING', 'ERROR', 'CRITICAL'],
            "info": ['Print', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            "debug": ['Print', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        }
        levels = level_dict.get(level.lower())
        slevel = level_stdout.get(level.lower())
        loguer.level("TRACE", color="<blue>")
        loguer.level("DEBUG", color="<green>")
        loguer.level("INFO", color="<cyan>")
        loguer.level("SUCCESS", color="<light-green>")
        loguer.level("WARNING", color="<yellow>")
        loguer.level("ERROR", color="<red>")
        loguer.level("CRITICAL", color="<red>")
        stdout_handler = {
            "sink": sys.stdout,
            "filter": lambda record: record["level"].name in slevel,
            "format": "<light-green><b>{time:YYYY-MM-DD HH:mm:ss.SSS}</b></light-green> | <b><level>{level: ^8}</level></b> | <b>{message}</b>"
        }
        loguer.configure(handlers=[stdout_handler])
        if self.log_stdout:
            loguer.level("Print", no=60, color="<green>")
            sys.stdout = InterceptHandler()
        if file_log:
            file_log = os.path.basename(__file__) if file_log is True else file_log
            file_log = (
                re.sub("\..*", ".log", file_log)
                if "." in file_log
                else file_log + ".log"
            )
            filename = f"./{file_log}"
            loguer.add(filename, level=levels)

        return loguer

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
        m = """<Spider End>
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
| ------------------ | ----------------------                            
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
        loguer.info(m)


class InterceptHandler():
    def write(self, message):
        if message.strip():
            loguer.log("Print", message.strip())

    def flush(self):
        pass
