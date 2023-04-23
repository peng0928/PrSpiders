import os
from PrSpider import PrSpiders

code_str = """from PrSpider import PrSpiders


class Spider(PrSpiders):
    start_urls = 'https://www.runoob.com'

    def parse(self, response):
        # print(response.text)
        print(response.code, response.url)


if __name__ == '__main__':
    Spider()
"""


def start_code(name):
    code_path = str(os.getcwd()) + "\\PrSpider_" + name + ".py"
    print(code_path)
    with open(code_path, mode="w", encoding="utf-8") as f:
        f.write(code_str)


class spider(PrSpiders):
    def __init__(self, url):
        self.url = url
        super().__init__()

    def start_requests(self, **kwargs):
        PrSpiders.Requests(url=self.url, callback=self.parse)

    def parse(self, response):
        print(response.text)
        print(response)
