from PrSpider import PrSpiders


class Spider(PrSpiders):
    start_urls = 'http://example.com'

    def parse(self, response):
        # print(response.text)
        print(response.code, response.url)


if __name__ == '__main__':
    Spider()
