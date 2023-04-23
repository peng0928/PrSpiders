# *Welcome to requestXpath !*

## *Introduce*

***Package name**: *requestXpath*
**Introduction**: Inherit the requests module, add xpath functionality to expand the API, and handle request failures
and retries*


> **ProTip:** Request to carry random useragent by default.

## *Introduction to Usage*

| Args             | Values                                          | notes                           |
|------------------|-------------------------------------------------|---------------------------------|
| `method`         | `Examle: "get" or "post" Type: string`          | `Request Method`                |
| `url`            | `Examle: "http://www.example.com" Type: string` | `Request Url`                   |
| `headers`        | `Type: dict`                                    | `Default Random Request Header` |
| `data`           | `Type: dict or string`                          | `Request parameters`            |
| `encoding`       | `Default: "utf-8" Type: string`                 | `Request Encoding`              |
| `retry_time`     | `Default: 3 Type: int`                          | `Retry Count`                   |
| `retry_interval` | `Default: 1 Type: int`                          | `Retry Interval`                |
| `timeout`        | `Default: 3 Type: int`                          | `Request timeout`               |
| `others`         | `*args or **kwargs`                             | `Follow Requests`               | 

## *Get started*

Install Package: pip install requestXpath
Make a request:

    from requestXpath import prequests
    url = 'https://gitee.com/'
    response = prequests.get(url=url)

**GET Status Code**

    response.status_code

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

    response.get_len

**GET Lxml Tree**

    response.tree

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
> parameter： x：xpath； filter：xpath filter；character： line feed；rule：re rule；is_list：reture list

- According to Xpath syntax defaults to extracting text or @href，No //text() or /text()

       content = tree.xpath("//div[@class='tutintro']", filter="strong")
       <class 'str'>
       # Python 的 3.0 版本，常被称为 Python 3000，或简称 Py3k。相对于 Python 的早期版本，这是一个较大的升级。为了不带入过多的累赘，Python 3.0 在设计的时候没有考虑向下兼容。
       # ......
       # Python 2.X 版本的教程
       # 。

- We can find it's gone strong node text
- is_list: return list

       content = tree.xpath("//div[@class='tutintro']", filter="strong", is_list=True)
       <class 'list'>
       # ['Python 的 3.0 版本，常被称为 Python 3000，或简称 Py3k。相对于 Python 的早期版本，这是一个较大的升级。为了不带入过多的累赘，Python 3.0 在设计的时候没有考虑向下兼容。', 'Python 介绍及安装教程我们在', 'Python 2.X 版本的教程', '中已有介绍，这里就不再赘述。', '你也可以点击', 'Python2.x与3\u200b\u200b.x版本区别', '来查看两者的不同。', '本教程主要针对 Python 3.x 版本的学习，如果你使用的是 Python 2.x 版本请移步至', 'Python 2.X 版本的教程', '。']

> **xxpath**

- Native official usage

      tree.xxpath("xpath")

> **dpath**

- Date extraction

      tree.dpath("xpath")

## *Please contact me if there are any bugs*

> email ->
> 1944542244@qq.com

 


