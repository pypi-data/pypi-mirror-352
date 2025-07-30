"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/5/21 11:28
最后修改时间：2025/6/3 09:06
项目介绍：基于 DrissionPage 封装的自用API，用于网页自动化。
文件路径：/AutoChrome/AutoChrome/__init__.py
版权声明：© 2025 Xiaoqiang. All Rights Reserved.

使用本项目需满足以下条款，如使用过程中出现违反任意一项条款的情形，授权自动失效。
* 禁止将 DrissionPage 应用到任何可能违反当地法律规定和道德约束的项目中
* 禁止将 DrissionPage 用于任何可能有损他人利益的项目中
* 禁止将 DrissionPage 用于攻击与骚扰行为
* 遵守 Robots 协议，禁止将 DrissionPage 用于采集法律或系统 Robots 协议不允许的数据

使用 DrissionPage 发生的一切行为均由使用人自行负责。
因使用 DrissionPage 进行任何行为所产生的一切纠纷及后果均与版权持有人无关，
版权持有人不承担任何使用 DrissionPage 带来的风险和损失。
版权持有人不对 DrissionPage 可能存在的缺陷导致的任何损失负任何责任。
"""

from AutoChrome.custom_types import *
from AutoChrome.auto_chrome import AutoChrome
from AutoChrome.chrome_downloader import ChromeDownloader

# https://drissionpage.cn/get_start/import/

import DrissionPage
from DrissionPage import *
from DrissionPage.items import *
from DrissionPage.errors import *
from DrissionPage.common import *
from DownloadKit import *

# 版本号
VERSION = "0.0.4"
# 作者
AUTHOR = "Xiaoqiang"
# 邮箱
EMAIL = "xiaoqiangclub@hotmail.com"
# 项目描述
DESCRIPTION = "基于 DrissionPage 封装的自用API，用于网页自动化。"

__title__ = "AutoChrome"
__version__ = VERSION
__author__ = AUTHOR
__description__ = DESCRIPTION

__all__ = [
    "__title__",
    "__version__",
    "__author__",
    "__description__",
    "VERSION",
    "AUTHOR",
    "DESCRIPTION",
    "EMAIL",
    "AutoChrome",
    "ChromeDownloader",
]
