"""
-------------------------------------------------
   File Name:     prequest
   Description :   Network Requests Class
   Author :        penr
   date:          2023/02/16
-------------------------------------------------
   Change Activity:
                   2023/02/16:
-------------------------------------------------
"""

"""
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
"""

from .requestXpath import prequest
from .pxpath import Xpath
prequests = prequest()

__author__ = 'penr'
