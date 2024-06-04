import pickle
import json
import redis
import time, os
import types
import requests
import inspect
import traceback
import threading
import multiprocessing
from typing import Callable, Dict, Union
from .log import *
from .utils import *
from .pipelines import *
from .pyconn import PrMysql
from .Request import SendRequest
from collections.abc import Iterator
from .settion import _IT, settions, filter_settions
from concurrent.futures import ThreadPoolExecutor, as_completed

author = """
 ____
|  _ \ ___ _ __  _ __
| |_) / _ \ '_ \| '__|
|  __/  __/ | | | |
|_|   \___|_| |_|_|
"""


class PrSpiders(settions):

    def __init__(self, **kwargs):
        self.start_preparation()
        self.spider_run()

    def start_preparation(self):
        """初始化工作"""
        self.start_time = time.time()
        self.update_settion()
        assert self.thread_num > 0, 'thread_num must be > 0'
        settions.init += 1
        if settions.init <= 1:
            Log(self).loggering()
        self.loging = loging(loguercor)
        self.executor = ThreadPoolExecutor(self.thread_num)
        self.Request = requests.session() if self.session else requests
        self.pipelines = dict_sort(self.pipelines)
        pipelines_msg = json.dumps(self.pipelines, indent=4)  # 使用json.dumps进行字符串格式化
        loguercor.log('Start', Start % (self.thread_num, self.retry, self.pid, self.download_delay, self.download_num,
                                        self.log_level.upper()))
        loguercor.log('Pipelines', f'Used Pipelines:\n{pipelines_msg}')
        self.open()
        self.cacha_start()
        pipeline_start(self)

    def update_settion(self):
        for name in dir(self):
            if name.startswith('__'):
                pass
            else:
                val = getattr(self, name)
                if name in filter_settions or isinstance(val, types.MethodType):
                    continue
                setattr(settions, name, val)

        if self.custom_settings:
            for key, value in self.custom_settings.items():
                key = key.lower()
                if key in filter_settions:
                    continue
                if isinstance(value, str):
                    if value.isdigit():
                        value = int(value)
                setattr(settions, key, value)

    def spider_run(self):
        """
        线程一: 爬虫业务代码（请求入队列）
        线程二: 监听队列
        """
        self.thread_requests = threading.Thread(target=self.start_call)
        self.thread_queue = threading.Thread(target=self.start_queue)

        # 启动线程
        self.thread_requests.start()
        self.thread_queue.start()

        # 等待线程结束
        self.thread_requests.join()
        self.thread_queue.join()

    def start_queue(self):
        while True:
            qlist = []
            qsize = self.Queues.qsize()
            # 检查队列是否为空
            if not self.Queues.empty():
                queue_list = []
                num_to_download = min(self.download_num, qsize)
                for _ in range(num_to_download):
                    data = self.Queues.get().data
                    wait = data.get('wait')
                    queue_list.append(data)
                    del data['wait']
                    if wait:
                        break
                qlist.append(queue_list)
                if qlist:
                    for qdata in qlist:
                        for item in qdata:
                            task = self.executor.submit(self.make_request, **item)
                            self.futures.add(task)
                if self.futures:
                    for future in as_completed(self.futures):
                        result = future.result()
                        worker_exception = future.exception()
                        result_class_name = result.__class__.__name__
                        if isinstance(result, Iterator) and result_class_name != 'None':
                            try:
                                for item in result:
                                    self.loging.yie(item)
                                    pipeline_process_item(item, self)
                            except Exception as e:
                                self.trace(e)
                        else:
                            pass
                        if worker_exception:
                            self.trace(worker_exception)
                        self.futures.remove(future)
            else:
                if self.thread_requests.is_alive():
                    pass
                else:
                    break
            time.sleep(self.download_delay)

    def trace(self, worker_exception, msg=""):
        formatted_traceback = traceback.format_exception(type(worker_exception),
                                                         worker_exception,
                                                         worker_exception.__traceback__)
        formatted_traceback = f'{msg}'.join(formatted_traceback)
        if self.traceback:
            self.loging.exception(worker_exception)
        else:
            self.loging.error(formatted_traceback)

    def start_call(self, *args, **kwargs):
        self.start(*args, **kwargs)
        pipeline_close(self)
        self.close()
        self.cache_end()

    def start(self, *args, **kwargs):
        self.start_requests(*args, **kwargs)
        settions.event.wait()
        while True:
            if not self.futures and self.Queues.empty():
                break
            time.sleep(self.schedule_time)

    def open(self):
        """爬虫启动前执行函数"""
        pass

    def close(self):
        """爬虫关闭后执行函数"""
        pass

    def start_requests(self, *args, **kwargs):
        if self.start_urls is None:
            raise AttributeError("Crawling could not start: 'start_urls' not found ")
        if isinstance(self.start_urls, list):
            for url in self.start_urls:
                Requests(url=url, callback=self.parse)
        else:
            Requests(url=self.start_urls, callback=self.parse)

    def parse(self, response):
        pass

    def make_request(self, url, callback, headers=None, retry_num=3, method="GET", meta=None, retry=True,
                     encoding="utf-8", retry_time=3, timeout=30, **kwargs):
        try:
            self.request_num += 1
            response = self.download(url=url, headers=headers, retry_time=retry_num, method=method,
                                     meta=meta, retry=retry, encoding=encoding, retry_interval=retry_time,
                                     timeout=timeout, settion=settions, **kwargs)
            self.loging.crawl(f"Response ({response.code}) <{method.upper()} {response.url}>")
            self.retry_num += int(response.meta.get("retry_num"))
            if response and response.ok:
                self.success_num += 1
            else:
                self.false_num += 1
            return callback(response)
        except Exception as e:
            self.trace(e)

    def download(self, **kwargs):
        response = SendRequest(self, self.Request).get(**kwargs)
        return response

    def error(self, response):
        pass

    def process_timestamp(self, t):
        timeArray = time.localtime(int(t))
        formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return formatTime

    def cacha_start(self):
        if self.dont_filter:
            cache_name = self.work_dir.split('\\')[-1] + '.pkl'
            if os.path.exists(cache_name):
                with open(cache_name, 'rb') as file:
                    data = pickle.load(file)
                    for query in data:
                        self.filterSet.add(query)

    def cache_end(self):
        if self.dont_filter:
            cache_name = self.work_dir.split('\\')[-1] + '.pkl'
            with open(cache_name, 'wb') as file:
                pickle.dump(self.filterSet, file)

    def __del__(self):
        """
         类销毁时执行的函数
         """
        end_time = time.time()
        spend_time = end_time - self.start_time
        try:
            average_time = spend_time / self.request_num
        except ZeroDivisionError:
            average_time = 0
        data = [
            ('dont_filter', self.dont_filter),
            ('thread_num', self.thread_num),
            ('download_delay', self.download_delay),
            ('download_num', self.download_num),
            ('request_num', self.request_num),
            ('success_num', self.success_num),
            ('false_num', self.false_num),
            ('retry_num', self.retry_num),
            ('spend_time', '%.3fs' % spend_time),
            ('average_time', '%.3fs' % average_time),
            ('start_time', self.process_timestamp(self.start_time)),
            ('end_time', self.process_timestamp(end_time)),
            ('work_dir', self.work_dir),
            ('pipelines', self.pipelines),
        ]
        m = close_sign(data)
        loguercor.log('Close', m)


class Requests:
    def __init__(self,
                 url: Union[str, list],
                 headers: dict = None,
                 method: str = "GET",
                 meta: dict = None,
                 retry: bool = True,
                 callback: Callable = None,
                 retry_num: int = 3,
                 encoding: str = "utf-8",
                 retry_time: int = 3,
                 timeout: int = 30,
                 priority: int = 0,
                 wait: bool = False,
                 retry_xpath: str = None,
                 dont_filter: bool = False,
                 **kwargs) -> None:

        self.send_to_queues(
            url=url,
            headers=headers,
            method=method,
            meta=meta,
            retry=retry,
            callback=callback,
            retry_num=retry_num,
            encoding=encoding,
            retry_time=retry_time,
            timeout=timeout,
            priority=priority,
            wait=wait,
            retry_xpath=retry_xpath,
            dont_filter=dont_filter,
            **kwargs
        )

    def send_to_queues(self, url: Union[str, list], headers: dict = None, method: str = "GET", meta: dict = None,
                       retry: bool = True, callback: Callable = None, retry_num: int = 3, encoding: str = "utf-8",
                       retry_time: int = 3, timeout: int = 30, priority: int = 0, wait: bool = False,
                       retry_xpath: str = None, dont_filter: bool = False, **kwargs) -> None:

        if not isinstance(url, (str, list)):
            raise TypeError("url must be a string or list of strings")

        if isinstance(url, str):
            query = {
                "url": url,
                "headers": headers,
                "method": method,
                "meta": meta,
                "retry": retry,
                "callback": callback,
                "retry_num": retry_num,
                "encoding": encoding,
                "retry_time": retry_time,
                "timeout": timeout,
                "wait": wait,
                "retry_xpath": retry_xpath,
            }
            frame = inspect.currentframe().f_back
            caller_name = frame.f_code.co_name
            deep = self._calculate_priority(caller_name, priority)
            query.update(**kwargs)
            item = self._create_item(deep, query)
            if not self._should_filter(item, dont_filter):
                self._add_to_queue(item)
            else:
                settions.event.set()
        elif isinstance(url, list):
            for u in url:
                self.send_to_queues(u, headers=headers, method=method, meta=meta, retry=retry, callback=callback,
                                    retry_num=retry_num, encoding=encoding, retry_time=retry_time, timeout=timeout,
                                    priority=priority, retry_xpath=retry_xpath, wait=wait, dont_filter=dont_filter,
                                    **kwargs)

    def _calculate_priority(self, caller_name: str, priority: int) -> int:
        if caller_name == 'send_to_queues':
            return priority
        else:
            if priority != 0:
                return priority
            else:
                deep_func = getattr(settions, "deep_func", [])
                if caller_name not in deep_func:
                    deep_func.append(caller_name)
                return -(deep_func.index(caller_name)) - 1

    def _create_item(self, deep: int, query: dict) -> '_IT':
        # Assume _IT is a predefined class for item structure.
        return _IT(deep, query)

    def _should_filter(self, item: '_IT', dont_filter: bool) -> bool:
        if settions.dont_filter is False:
            if not dont_filter:
                fingerprint = self._calculate_fingerprint(item)
                if self._is_duplicate(fingerprint):
                    loguercor.log('Filter', f'url already exists: {item.data["url"]}')
                    return True
        return False

    def _calculate_fingerprint(self, query: dict) -> str:
        # Use SHA-256 for better security
        query = query.data
        data = {
            "url": query["url"],
            "method": query["method"],
            "params": query.get("params"),
        }
        return sha_hash(data)

    def _is_duplicate(self, fingerprint: str) -> bool:
        # Simplify the logic for duplicate check
        if settions.redis:
            redis_key = f"{settions.redis.get('redis_key')}:fingerprint"
            if settions.redis_serve.sismember(redis_key, fingerprint):
                return True
            else:
                settions.redis_serve.sadd(redis_key, fingerprint)
        else:
            if fingerprint not in settions.filterSet:
                settions.filterSet.add(fingerprint)
            else:
                return True

    def _add_to_queue(self, item: '_IT') -> None:
        settions.Queues.put(item)
        settions.event.set()


class RedisSpider(PrSpiders):
    schedule_time = 3.14
    dont_filter = False

    def open(self):
        self.redis_key = self.redis.get('redis_key', None)
        self.redis_url = self.redis.get('redis_url')
        assert self.redis_key, "redis_key is not None"
        assert self.redis_url, "redis_url is not None"
        redis_conn_pool = redis.ConnectionPool.from_url(self.redis_url, decode_responses=True)
        self.redis_serve = redis.Redis(connection_pool=redis_conn_pool)
        self.loging.info(f"RedisKey: {self.redis_key}")
        self.update_settion()

    def get_data(self):
        for _ in range(self.download_num):
            items = self.redis_serve.rpop(self.redis_key)
            if items:
                yield items

    def start_requests(self, *args, **kwargs):
        for data in self.get_data():
            self.crawl(data)
        time.sleep(self.schedule_time)
        self.start_requests()

    def crawl(self, data):
        self.loging.info(data)


def run_spider(spider: list or object, pool=10):
    """
    爬虫任务启动调度, 采用进程池方式.
    """
    pool = multiprocessing.Pool(pool)
    if isinstance(spider, list):
        for spider_class in spider:
            pool.apply_async(spider_class)
    else:
        pool.apply_async(spider)
    pool.close()
    pool.join()
