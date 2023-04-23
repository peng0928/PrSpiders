# encoding:utf-8

from pkg import __version__
import argparse

from .start import start_code, spider


def get_version():
    return __version__


def main():
    # args = docopt(__doc__, version=__version__)
    # print(args)

    parse = argparse.ArgumentParser()  # 创建参数对象
    parse.add_subparsers(
        title="PrSpiders CMD",
        help="prspiders cmd help",
        description="快速开始爬虫项目,快速查看、查找页面信息 | Quickly start crawler projects, quickly view and find page information",
    )
    parse.add_argument(
        "-v", "--version", help="版本 | version", action="version", version=get_version()
    )
    parse.add_argument("-url", metavar="解析url | parse url")
    parse.add_argument("-keys", metavar="匹配关键字 | re keys")
    parse.add_argument(
        "-s",
        "--start",
        help="Start Project",
    )
    args = parse.parse_args()  # 解析参数对象获得解析对象
    start = args.start
    keys = args.keys
    url = args.url
    if start:
        start_code(start)
        print("完成", start)

    if url:
        spider(url)


if __name__ == "__main__":
    main()
