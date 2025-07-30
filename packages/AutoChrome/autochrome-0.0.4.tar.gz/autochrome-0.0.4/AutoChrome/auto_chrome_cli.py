"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/5/29 11:28
文件描述：AutoChrome 命令行工具
文件路径：/AutoChrome/AutoChrome/auto_chrome_cli.py
"""

import sys
import argparse
from . import __version__
from .chrome_downloader import ChromeDownloader


def main():
    parser = argparse.ArgumentParser(
        prog="autochrome",
        description=f"AutoChrome {__version__} 命令行工具：用于下载绿色版 Chromium 浏览器。\n"
                    "功能：\n"
                    "1. 自动从官方镜像源下载最新版Chromium\n"
                    "2. 支持指定特定版本号下载\n"
                    "3. 支持设置自定义下载目录\n"
                    "\n示例：\n"
                    "  autochrome -v\n"
                    "  autochrome cd -h\n"
                    "  autochrome cd -r 123456\n"
                    "  autochrome chromedownloader -d ./chrome\n",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 主命令参数
    parser.add_argument(
        "-v", "--version", action="store_true", help="显示AutoChrome版本号"
    )

    # ChromeDownloader 子命令
    cd_parser = subparsers.add_parser(
        "chromedownloader", aliases=["cd"], help="下载Chrome/Chromium 浏览器"
    )
    cd_parser.add_argument(
        "-d", "--dir", type=str, default=None, help="下载目录（默认：chrome文件夹）"
    )
    cd_parser.add_argument(
        "-r",
        "--revision",
        type=str,
        default=None,
        help="指定Chromium快照版本号（可选）",
    )
    cd_parser.add_argument(
        "-s",
        "--system",
        type=str,
        default=None,
        help="指定目标系统（可选，默认自动检测）",
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.version:
        print(f"AutoChrome 版本号: {__version__}")
        sys.exit(0)

    if args.command in ["chromedownloader", "cd"]:
        downloader = ChromeDownloader(
            download_dir=args.dir,
        )
        downloader.download(revision=args.revision, system=args.system)


if __name__ == "__main__":
    main()
