# *[PrSpiders线程池爬虫框架](a)*

## *PrSpiders安装*

 - *`pip install Scrapy`*


## *开始	Go start!*

**1.Demo**
   

    from PrSpider import PrSpiders  
      
      
    class Spider(PrSpiders):  
        start_urls = 'https://www.runoob.com'  
      
        def parse(self, response):  
            # print(response.text)  
		    print(response, response.code, response.url)  
      #<Response Code=200 Len=323273> 200 https://www.runoob.com/
      
    if __name__ == '__main__':  
        Spider()
       
**2.重写入口函数-start_requests**

> start_requests是框架的启动入口，PrSpiders.Requests是发送请求的发送，参数下面会列举。

    from PrSpider import PrSpiders  
      
      
    class Spider(PrSpiders):  
      
        def start_requests(self, **kwargs):  
            start_urls = 'https://www.runoob.com'  
            PrSpiders.Requests(url=start_urls, callback=self.parse)  
      
        def parse(self, response):  
            # print(response.text)  
            print(response, response.code, response.url)  
      
      
    if __name__ == '__main__':  
        Spider()


**3.PrSpiders基本配置**

> 底层使用ThreadPoolExecutor

    workers: 线程数
    retry: 是否开启请求失败重试，默认开启
    download_delay: 请求周期
    download_num: 每次线程请求数量，默认1秒5个请求

> 使用方法如下

    from PrSpider import PrSpiders  
      
      
    class Spider(PrSpiders):  
      workers = 5  
      retry = False  
      download_delay = 3  
      download_num = 10  
      
      def start_requests(self, **kwargs):  
            start_urls = 'https://www.runoob.com'  
            PrSpiders.Requests(url=start_urls, callback=self.parse)  
      
      def parse(self, response):  
            # print(response.text)  
            print(response, response.code, response.url)  
    
      
      
    if __name__ == '__main__':  
        Spider()

**4.PrSpiders.Requests基本配置**

> 基本参数：
> url：请求网址
> callback：回调函数
> headers：请求头
> retry_time：请求失败重试次数
> method：请求方式（默认Get方法），
> meta：回调参数传递
> encoding：编码格式（默认utf-8）
> retry_interval：重试间隔
> timeout：请求超时时间（默认10s）
> **kwargs：继承requests的参数如（data, params, proxies）

        PrSpiders.Requests(url=start_urls, headers={}, method='post', encoding='gbk', callback=self.parse,  
      retry_time=10, retry_interval=0.5, meta={'hhh': 'ggg'})

  

## *Api*

**GET Status Code**

    response.code

**GET Text**

    response.text

**GET Content**

    response.content
**GET Url**

    response.url

**GET History**

    response.history

**GET Headers**

    response.headers

**GET Text Length**

    response.len

**GET Lxml Xpath**

    response.xpath

## *Xpath Api*
**Example**

    from requestXpath import prequests  
    url = 'https://www.runoob.com/python3/python3-tutorial.html'  
    response = prequests.get(url=url)  
    tree = response.tree  
    title = tree.xpath("//div[@id='content']/h1")
    print(title)
    # Python 3 教程

> **xpath**
parameter： x：xpath； filter：xpath filter；character： line feed；rule：re rule；is_list：reture list
 - According to Xpath syntax defaults to extracting text or @href，No //text() or /text()

    
       content = tree.xpath("//div[@class='tutintro']", filter="strong")
       <class 'str'>
       # Python 的 3.0 版本，常被称为 Python 3000，或简称 Py3k。相对于 Python 的早期版本，这是一个较大的升级。为了不带入过多的累赘，Python 3.0 在设计的时候没有考虑向下兼容。
       # ......
       # Python 2.X 版本的教程
       # 。

     

       
## *Please contact me if there are any bugs*


> email ->
> 1944542244@qq.com

 


