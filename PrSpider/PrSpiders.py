import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import datetime
import os
import re
from typing import Optional
from .requestXpath import prequest

logging.basicConfig(format='%(message)s', level=logging.INFO)


class settions:
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
    download_delay: Optional[int] = 1
    download_num: Optional[int] = 5


class PrSpiders(settions):
    def __init__(self) -> None:
        settions.request_num = self.request_num
        settions.success_num = self.success_num
        settions.false_num = self.false_num
        settions.retry = self.retry
        settions.workers = self.workers
        settions.download_delay = self.download_delay
        settions.download_num = self.download_num
        logging.info(
            '****************** @PrSpider Start  @Workers %s  @Retry %s  @Pid %s @Download_Delay %s @Download_Num %s ******************'
            % (self.workers, self.retry, self.pid, self.download_delay, self.download_num))
        if not self.start_urls and not hasattr(self, 'start_requests'):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found ")
        else:
            self.start_requests()

    def start_requests(cls, **kwargs):
        if isinstance(cls.start_urls, str):
            cls.start_urls = [cls.start_urls]
        url_dim_list = [cls.start_urls[i:i + cls.download_num]
                        for i in range(0, len(cls.start_urls), cls.download_num)]
        for u in url_dim_list:
            time.sleep(cls.download_delay)
            cls.Requests(callback=cls.parse,
                         url=u, **kwargs)

    @classmethod
    def RequestsMap(cls, request=None, callback=None, headers=None, retry_time=3, method='GET', meta=None,
                    encoding='utf-8', retry_interval=1, timeout=10, **kwargs):
        futures = []
        if not isinstance(request, list):
            raise AttributeError(
                "Requests object must be list: [{'url': 1, 'data': 1},{'url': 2, 'params': 2}]")
        else:
            url_dim_list = [request[i:i + cls.download_num]
                            for i in range(0, len(request), cls.download_num)]
            for u in url_dim_list:
                time.sleep(cls.download_delay)
                for _u in u:
                    url = _u.get('url')
                    data = _u.get('data', None)
                    params = _u.get('params', None)
                    meta = _u.get('meta', None)
                    kwargs.update({"data": data})
                    kwargs.update({"params": params})
                    futures.append(
                        ThreadPoolExecutor(cls.workers).submit(cls.fetch, url=url, callback=callback, headers=headers,
                                                               timeout=timeout,
                                                               retry_time=retry_time,
                                                               method=method, meta=meta, encoding=encoding,
                                                               retry_interval=retry_interval, **kwargs))

                for future in as_completed(futures):
                    worker_exception = future.exception()
                    if worker_exception:
                        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        logging.exception(
                            f'{current_time} [PrSpider Exception] %s' % worker_exception)

    @classmethod
    def Requests(cls, url=None, callback=None, headers=None, retry_time=3, method='GET', meta=None,
                 encoding='utf-8', retry_interval=1, timeout=10, **kwargs, ):
        futures = []
        if isinstance(url, str):
            url = [url]
        url_dim_list = [url[i:i + cls.download_num]
                        for i in range(0, len(url), cls.download_num)]
        for u in url_dim_list:
            time.sleep(cls.download_delay)
            for _u in u:
                futures.append(
                    ThreadPoolExecutor(cls.workers).submit(cls.fetch, url=_u, callback=callback, headers=headers,
                                                           timeout=timeout,
                                                           retry_time=retry_time,
                                                           method=method, meta=meta, encoding=encoding,
                                                           retry_interval=retry_interval, **kwargs))

        for future in as_completed(futures):
            worker_exception = future.exception()
            if worker_exception:
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logging.exception(
                    f'{current_time} [PrSpider Exception] %s' % worker_exception)

    @classmethod
    def fetch(self, url, callback, headers=None, retry_time=3, method='GET', meta=None,
              encoding='utf-8', retry_interval=1, timeout=3, **kwargs):
        settions.request_num += 1
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time.sleep(self.download_delay)
        response = prequest().get(url, headers=headers, retry_time=retry_time, method=method, meta=meta,
                                  encoding=encoding, retry_interval=retry_interval, timeout=timeout,
                                  settion=settions, **kwargs)
        if response:
            if response.ok:
                settions.success_num += 1
                logging.info(
                    f'{current_time} [PrSpider] True [Method] {method} [Status] {response.code} [Url] {url}')
                callback(response)
                return self
            else:
                settions.false_num += 1
                if response:
                    logging.error(
                        f'{current_time} [PrSpider] False [Method] {method} [Status] {response.code} [Url] {url}')
                else:
                    logging.error(
                        f'{current_time} [PrSpider] Error [Method] {method} [Status] Timeout [Url] {url}')
                callback(response)
                return self
        else:
            settions.false_num += 1
            if response:
                logging.error(
                    f'{current_time} [PrSpider] False [Method] {method} [Status] {response.code} [Url] {url}')
            else:
                logging.error(
                    f'{current_time} [PrSpider] Error [Method] {method} [Status] Timeout [Url] {url}')
            callback(response)
            return self

    @classmethod
    def parse(self, response, **kwargs):
        raise NotImplementedError(
            f'{self.__class__.__name__}.parse callback is not defined')

    def process_timestamp(self, t):
        timeArray = time.localtime(int(t))
        formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return formatTime

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
        m = """
-->Spider Close Status.
| ------------------ | ----------------------
| `Requests`         | `Response Close.`                                 
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
            self.workers, self.download_delay, self.download_num, self.request_num, self.success_num, self.false_num,
            self.process_timestamp(self.start_time), self.process_timestamp(
                end_time), spend_time,
            average_time
        )
        logging.info(m)
