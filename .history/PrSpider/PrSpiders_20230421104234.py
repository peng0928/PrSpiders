import os
import re
import sys
import logging
import time
import datetime, random
from typing import Optional
from .requestXpath import prequest
from concurrent.futures import ThreadPoolExecutor, as_completed


class settions(object):
    workers: Optional[int] = 1
    request_num: Optional[int] = 0
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
    log: Optional[object] = False
    logger: Optional[bool or str] = False
    log_level: Optional[str] = "info"


class PrSpiders(settions):
    def __init__(self) -> None:
        settions.request_num = self.request_num
        settions.success_num = self.success_num
        settions.false_num = self.false_num
        settions.retry = self.retry
        settions.workers = self.workers
        settions.download_delay = self.download_delay
        settions.download_num = self.download_num
        settions.logger = self.logger
        settions.log_level = self.log_level
        settions.log = self.loggering(self.logger, self.log_level)

        self.log.info(
            "~~~ @PrSpider Start  @Workers %s  @Retry %s  @Pid %s @Download_Delay %s @Download_Num %s @LOG_LEVEL %s ~~~"
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
            self.start_requests()

    def start_requests(cls, **kwargs):
        if isinstance(cls.start_urls, str):
            cls.start_urls = [cls.start_urls]
        url_dim_list = [
            cls.start_urls[i : i + cls.download_num]
            for i in range(0, len(cls.start_urls), cls.download_num)
        ]
        for u in url_dim_list:
            time.sleep(cls.download_delay)
            cls.Requests(callback=cls.parse, url=u, **kwargs)

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
        retry_interval=1,
        timeout=10,
        **kwargs,
    ):
        futures = []
        if not isinstance(request, list):
            raise AttributeError(
                "Requests object must be list: [{'url': 1, 'data': 1, 'meta': {'t': '123'},{'url': 2, 'params': 2}]"
            )
        else:
            url_dim_list = [
                request[i : i + cls.download_num]
                for i in range(0, len(request), cls.download_num)
            ]
            for u in url_dim_list:
                time.sleep(cls.download_delay + random.uniform(0.0000001, 0.0000005))
                for _u in u:
                    time.sleep(random.uniform(0.00000001, 0.00000005))
                    url = _u.get("url")
                    data = _u.get("data", None)
                    params = _u.get("params", None)
                    meta = _u.get("meta", None)
                    kwargs.update({"data": data})
                    kwargs.update({"params": params})
                    futures.append(
                        ThreadPoolExecutor(cls.workers).submit(
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
                    )

            for future in as_completed(futures):
                futures.remove(future)
                worker_exception = future.exception()
                if worker_exception:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cls.log.exception(
                        f"{current_time} [PrSpider Exception] %s" % worker_exception
                    )

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
        retry_interval=1,
        timeout=10,
        **kwargs,
    ):
        futures = []
        if isinstance(url, str):
            url = [url]
        url_dim_list = [
            url[i : i + cls.download_num] for i in range(0, len(url), cls.download_num)
        ]
        for u in url_dim_list:
            time.sleep(cls.download_delay + random.uniform(0.0000001, 0.0000005))
            for _u in u:
                time.sleep(random.uniform(0.00000001, 0.00000005))
                futures.append(
                    ThreadPoolExecutor(cls.workers).submit(
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
                )

        for future in as_completed(futures):
            futures.remove(future)
            worker_exception = future.exception()
            if worker_exception:
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cls.log.exception(
                    f"{current_time} [PrSpider Exception] %s" % worker_exception
                )

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
        timeout=3,
        **kwargs,
    ):
        settions.request_num += 1
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response = prequest(self.log).get(
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
        if response:
            if response.ok:
                settions.success_num += 1
                self.log.info(
                    f"{current_time} [Method] {method} [Status] {response.code} [Url] {url}"
                )
                callback(response)
                return self
            else:
                settions.false_num += 1
                if response:
                    self.log.error(
                        f"{current_time} [Method] {method} [Status] {response.code} [Url] {url}"
                    )
                else:
                    self.log.error(
                        f"{current_time} [Method] {method} [Status] Timeout [Url] {url}"
                    )
                callback(response)
                return self
        else:
            settions.false_num += 1
            if response:
                self.log.error(
                    f"{current_time} [Method] {method} [Status] {response.code} [Url] {url}"
                )
            else:
                self.log.error(
                    f"{current_time} [Method] {method} [Status] Error [Url] {url}"
                )
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
            "warn": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        level = level_dict.get(level.lower())
        logger = logging.getLogger()
        logger.setLevel(level)
        sys.stdout = FileLike(logger)

        formatter = logging.basicConfig(format="%(message)s", level=level)
        # 创建一个handler，用于写入日志文件，并设置日志级别，mode:a是追加写模式，w是覆盖写模式
        if file_log:
            file_log = os.path.basename(__file__) if file_log is True else file_log
            file_log = (
                re.sub("\..*", ".log", file_log)
                if "." in file_log
                else file_log + ".log"
            )
            filename = f"./{file_log}"
            fh = logging.FileHandler(filename=filename, encoding="utf-8", mode="w")
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger

    def __del__(self):
        try:
            prequest().close()
        except:
            pass
        end_time = time.time()
        spend_time = end_time - self.start_time
        try:
            average_time = spend_time / self.request_num
        except ZeroDivisionError:
            average_time = 0
        m = """Spider End.
| ------------------ | ----------------------                               
| `Workers`          | `%s`                                             
| `Download Delay`   | `%s`                                             
| `Download Num`     | `%s`                                             
| `Request Num`      | `%s`                                             
| `Success Num`      | `%s`                                             
| `False Num`        | `%s`                                              
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
            self.process_timestamp(self.start_time),
            self.process_timestamp(end_time),
            spend_time,
            average_time,
        )
        self.log.info(m)


class FileLike:
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        if message != "\n":
            self.logger.log(logging.CRITICAL, message.strip())

    def flush(self):
        pass
