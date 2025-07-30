"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/5/21 09:06
文件描述：浏览器自动化
文件路径：/AutoChrome/AutoChrome/auto_chrome.py
"""

import os
import math
import time
import platform

from DownloadKit import DownloadKit
from DownloadKit.mission import Mission
from DrissionPage.common import Actions
from DrissionPage import Chromium, SessionOptions
from DrissionPage._units.downloader import DownloadMission

from AutoChrome.custom_types import *
from AutoChrome.logger import LoggerBase
from AutoChrome.chrome_downloader import ChromeDownloader


class AutoChrome(Chromium):
    def __new__(cls, *args, **kwargs):
        """
        创建 Chromium 实例
        https://drissionpage.cn/browser_control/browser_options
        """
        # 初始化日志
        log = cls._logger_init(
            console_log_level=kwargs.get("console_log_level", "INFO"),
            log_file_level=kwargs.get("log_file_level", "WARNING"),
            log_file=kwargs.get("log_file", None),
            log_debug_format=kwargs.get("log_debug_format", False),
        )

        addr_or_opts = kwargs.get("addr_or_opts", None)
        session_options = kwargs.get("session_options", None)

        # 实例化 ChromiumOptions
        co = ChromiumOptions()
        port = None  # 浏览器启动端口

        if isinstance(addr_or_opts, ChromiumOptions):
            instance = super().__new__(cls, addr_or_opts=addr_or_opts, session_options=session_options)
            # 👈 关键：保存为实例属性，供 __init__ 使用
            instance.co = addr_or_opts
            instance.log = log
            log.debug(f"⚙️ 用户设置了 ChromiumOptions 配置")
            return instance
        elif isinstance(addr_or_opts, str):
            log.debug(f"🔧 用户设置了 Chromium 地址：{addr_or_opts}")
            co.set_address(addr_or_opts)  # 设置地址
        elif isinstance(addr_or_opts, int):

            port = addr_or_opts  # 获取端口号

        # 设置端口或自动分配端口
        if port:
            log.debug(f"🔧 浏览器启动端口为：{port}")

            co.set_local_port(port)
        elif kwargs.get("auto_port", False):
            log.debug(f"🔧 浏览器启动端口为：{kwargs.get('auto_port')}")
            co.auto_port()

        # 设置浏览器路径
        browser_path = kwargs.get("browser_path")
        if browser_path:
            log.debug(f"🔧 浏览器路径为：{browser_path}")
            co.set_browser_path(browser_path)

        # 设置用户数据路径
        user_data_path = kwargs.get("user_data_path")
        if user_data_path:
            log.debug(f"🔧 用户数据路径为：{user_data_path}")
            co.set_user_data_path(user_data_path)

        # 设置代理
        proxy = kwargs.get("proxy")
        if proxy:
            log.debug(f"🔧 设置浏览器代理为：{proxy}")
            co.set_proxy(proxy)

        # 设置无痕模式
        incognito = kwargs.get("incognito", False)
        if incognito:
            log.debug(f"🔧 设置浏览器无痕模式为：{incognito}")
            co.incognito(True)

        # 设置无头模式
        headless = kwargs.get("headless", False)
        if headless:
            log.debug(f"🔧 设置浏览器无头模式为：{headless}")
            co.headless(True)

        instance = super().__new__(cls, addr_or_opts=co, session_options=session_options)
        # 👈 关键：保存为实例属性，供 __init__ 使用
        instance.co = co
        instance.log = log
        return instance

    def __init__(
            self,
            start_url: Optional[str] = None,
            addr_or_opts: ChromiumOptionsType = None,
            session_options: Union[SessionOptions, Literal[False], None] = None,
            headless: bool = False,
            browser_path: Optional[str] = None,
            user_data_path: Optional[str] = None,
            proxy: Optional[dict] = None,
            incognito: bool = False,
            auto_port: bool = False,
            auto_handle_alert: bool = False,
            alert_accept: bool = True,
            auto_download_browser: bool = True,
            browser_download_path: Optional[str] = None,
            chrome_save_path: Optional[str] = None,
            console_log_level: Literal[
                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            ] = "INFO",
            log_file_level: Literal[
                "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            ] = "WARNING",
            log_file: Optional[str] = None,
            log_debug_format: bool = False,
    ):
        """
        网页自动化
        多浏览器操作文档：
        https://drissionpage.cn/browser_control/connect_browser/#%EF%B8%8F-%E5%A4%9A%E6%B5%8F%E8%A7%88%E5%99%A8%E5%85%B1%E5%AD%98

        :param start_url: 启动页面
        :param addr_or_opts: Chromium 浏览器的端口、地址 或 设置好的 ChromiumOptions 对象，如果是一个设置好的ChromiumOptions对象，后面的相关参数失效:https://drissionpage.cn/browser_control/browser_options/#%EF%B8%8F%EF%B8%8F-%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95
        :param session_options: Chromium 的 session_options 参数
        :param headless: 是否启用无头模式
        :param browser_path: 设置浏览器路径，默认为：None，使用系统默认浏览器
        :param user_data_path: 设置用户数据路径 > https://drissionpage.cn/browser_control/connect_browser#-%E5%8D%95%E7%8B%AC%E6%8C%87%E5%AE%9A%E6%9F%90%E4%B8%AA%E7%94%A8%E6%88%B7%E6%96%87%E4%BB%B6%E5%A4%B9
        :param proxy: 设置浏览器代理（格式：协议://ip:port），默认为：None，不使用代理 > https://drissionpage.cn/browser_control/browser_options/#-set_proxy
        :param auto_port: 是否自动分配端口，仅当 chrome_options=None 时生效 > https://drissionpage.cn/browser_control/connect_browser#-auto_port%E6%96%B9%E6%B3%95
        :param incognito: 是否启用无痕模式启动，默认为 False
        :param auto_handle_alert: 是否设置所有标签页都自动处理 alert 弹窗，默认为 False
        :param alert_accept: 自动处理 alert 弹窗时，是否默认点击“确定”，默认为 True，否则点击“取消”
        :param auto_download_browser: 当本地环境没有Chrome浏览器时自动下载浏览器，默认为 True
        :param browser_download_path: 使用浏览器进行下载，文件存放的目录，默认为 None，默认下载到程序当前路径
        :param chrome_save_path: 自动下载 Chromium 浏览器存放的目录，默认为 None，当前目录的 chrome 文件夹
        :param console_log_level: 终端显示的日志等级，默认为："INFO"
        :param log_file: 日志文件路径，默认为: None 不保存
        :param log_file_level: 日志文件保存的日志等级，默认为："WARNING"
        :param log_debug_format: 是否使用调试格式，默认为：False
                                - False："%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s：%(message)s"
                                - True："%(asctime)s - %(levelname)s：%(message)s"
        """
        # 只初始化一次
        if getattr(self, "_autochrome_inited", False):
            self.log.warning("⚠️ AutoChrome 已初始化，请勿重复执行！")
            return
        self._autochrome_inited = True

        self.start_url = start_url

        try:
            super().__init__(
                addr_or_opts=self.co, session_options=session_options
            )
        except Exception as e:
            self.log.error(f"🚨 创建浏览器对象失败：{type(e).__name__} - {e}")
            if auto_download_browser:  # 当本地环境没有Chrome浏览器时自动下载浏览器
                self.log.info("🎈 未找到浏览器，尝试自动下载浏览器...")
                chrome_path = ChromeDownloader(
                    download_dir=chrome_save_path, logger=self.log
                ).download(return_chrome_path=True)
                if not chrome_path:
                    raise Exception("🚨 自动下载浏览器失败，请手动安装 Chrome 浏览器！")
                addr_or_opts.set_browser_path(chrome_path)
                super().__init__(
                    addr_or_opts=self.co, session_options=session_options
                )
            else:
                raise Exception(f"🚨 创建浏览器对象失败：{type(e).__name__} - {e}")

        # 设置浏览器下载的文件的保存路径
        if browser_download_path:
            # https://drissionpage.cn/download/browser/#%EF%B8%8F-clickto_download
            self.set.download_path(browser_download_path)

        # 设置别名
        self.close_chrome = self.close_browser
        self.open = self.get
        self.downloader: DownloadKit = self.latest_tab.download  # 下载器对象

        if auto_handle_alert:  # 自动处理 alert 弹窗
            self.set.auto_handle_alert(accept=alert_accept)
        if self.start_url:
            self.latest_tab.get(self.start_url)

    @staticmethod
    def _logger_init(
            console_log_level: str = "INFO",
            log_file_level: str = "WARNING",
            log_file: Optional[str] = None,
            log_debug_format: bool = False,
    ) -> LoggerBase:
        """
        日志初始化

        :param console_log_level: 终端显示的日志等级，默认为: "INFO"
        :param log_file_level: 日志文件保存的日志等级，默认为: "WARNING"
        :param log_file: 日志保存文件路径，默认为: None 不保存
        :param log_debug_format: 默认为: False
                            - False："%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s：%(message)s"
                            - True："%(asctime)s - %(levelname)s：%(message)s"
        """
        logger = LoggerBase(
            "AutoChrome",
            console_log_level=console_log_level,
            log_file_level=log_file_level,
            log_file=log_file,
            log_format=(
                "%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s：%(message)s"
                if log_debug_format
                else "%(asctime)s - %(levelname)s：%(message)s"
            ),
        )
        return logger.logger

    def get(
            self,
            url: str = None,
            tab: TabType = None,
            **kwargs,
    ) -> bool:
        """
        访问网页
        https://drissionpage.cn/SessionPage/visit/#%EF%B8%8F%EF%B8%8F-get

        :param url: 要访问的网址，默认为：None，刷新当前页面
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param kwargs: 访问网页的参数 > https://drissionpage.cn/browser_control/visit/#-get
        :return:
            - True: 成功访问网页
            - False: 访问网页失败
        """
        tab = tab or self.latest_tab
        if not url:
            self.log.info("🔄 刷新当前页面...")
            tab.refresh(ignore_cache=True)
            return True

        self.log.info(f"🌐 正在访问网页: {url}...")
        try:
            return tab.get(url=url, **kwargs)
        except Exception as e:
            self.log.error(f"🚨 访问网页失败：{type(e).__name__} - {e}")
            return False

    def get_cookies(
            self,
            tab: TabType = None,
            all_info: bool = False,
            return_type: GetCookieType = "list",
    ) -> Union[List[dict], str, dict]:
        """
        获取 标签页的cookies
        https://drissionpage.cn/SessionPage/get_page_info/#%EF%B8%8F%EF%B8%8F-cookies-%E4%BF%A1%E6%81%AF

        :param tab: 标签页，默认为: None, 使用 self.latest_tab
        :param all_info: 是否获取所有信息，默认为: False, 仅获取 name、value、domain 的值
        :param return_type: 返回类型，默认为: list, 可选值：list、str、dict、json, 注意：str 和 dict 都只会保留 'name'和 'value'字段; json 返回的是 json格式的字符串
        :return:
        """
        tab = tab or self.latest_tab
        c = tab.cookies(all_info=all_info)
        if return_type == "list":
            return c
        elif return_type == "str":
            return c.as_str()
        elif return_type == "dict":
            return c.as_dict()
        elif return_type == "json":
            return c.as_json()
        else:
            raise ValueError("return_type 参数错误！")

    def set_cookies(
            self,
            cookies: SetCookieType,
            tab: TabType = None,
            refresh: bool = True,
            verify_str: Optional[str] = None,
    ) -> Optional[bool]:
        """
        给标签页设置 cookies
        https://drissionpage.cn/tutorials/functions/set_cookies

        :param cookies: cookies 的值，支持字符串和字典格式
        :param tab: 标签页，默认为: None, 使用 self.latest_tab
        :param refresh: 是否刷新页面，默认为: True, 刷新页面
        :param verify_str: 是否验证 cookies 设置成功，默认为: None, 不验证; 为 字符串 时会自动刷新页面。并且验证页面是否包含 verify_str 字符串.
        :return: 如果 verify=True，则返回一个布尔值，表示 cookies 是否设置成功；否则返回 None
        """
        tab = tab or self.latest_tab
        tab.set.cookies(cookies)

        if refresh or verify_str:
            self.log.info("🔄 刷新页面...")
            tab.refresh()

        if verify_str:
            self.log.info("🔍 正在验证 cookies 是否设置成功...")
            if verify_str in tab.html:
                self.log.info("✅ cookies 设置成功！")
                return True
            else:
                self.log.error("❌ cookies 设置失败/已失效！")
                return False
        return None

    @property
    def is_windows(self) -> bool:
        """
        检查当前操作系统是否为 Windows
        :return: 如果是 Windows 系统，返回 True；否则返回 False
        """
        return platform.system() == "Windows"

    def hide_tab(
            self, tab: TabType = None
    ) -> None:
        """
        此方法用于隐藏签页窗口，但是会导致整个浏览器窗口被隐藏。
        与 headless 模式不一样，这个方法是直接隐藏浏览器进程。在任务栏上也会消失。
        只支持 Windows 系统，并且必需已安装 pypiwin32 库才可使用。
        pip install -i https://mirrors.aliyun.com/pypi/simple/ -U pypiwin32
        https://drissionpage.cn/browser_control/page_operation/#-setwindowhide

        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :return:
        """
        if not self.is_windows:
            self.log.error("❌ 此方法仅支持 Windows 系统！")
            return

        self.log.info("🙈 隐藏浏览器窗口...")
        tab = tab or self.latest_tab
        tab.set.window.hide()

    def show_tab(
            self, tab: TabType = None
    ) -> None:
        """
        显示标签页，该操作会显示整个浏览器。
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :return:
        """
        if not self.is_windows:
            self.log.error("❌ 此方法仅支持 Windows 系统！")
            return

        self.log.info("👀 显示浏览器窗口...")
        tab = tab or self.latest_tab
        tab.set.window.show()

    def close_browser(
            self,
            close_latest_tab=False,
            close_other_tabs=False,
            close_session=False,
            timeout: float = 3,
            kill_process=False,
            del_user_data=False,
    ) -> List[bool]:
        """
        关闭浏览器
        :param close_latest_tab: 关闭最新标签页
        :param close_other_tabs: 关闭其他标签页，仅当 close_current_tab=True 时生效
        :param close_session: 是否同时关闭内置 Session 对象，只对自己有效，仅当 close_current_tab=True 时生效
        :param timeout: 关闭浏览器超时时间，单位秒
        :param kill_process: 是否立刻强制终止进程
        :param del_user_data: 是否删除用户数据
        :return: [close_tab, close_browser]，分别表示关闭标签页和关闭浏览器的结果
        """
        close_tab = False
        close_browser = False

        try:
            if close_latest_tab:  # 关闭当前标签页
                self.log.info("🗂️ 正在关闭标签页，请稍等...")
                self.latest_tab.close(others=close_other_tabs, session=close_session)
            close_tab = True
        except Exception as e:
            self.log.error(f"❌ 关闭标签页出错: {type(e).__name__} - {e}")

        try:
            # 关闭浏览器
            self.log.info("🛑 正在关闭浏览器...")
            self.quit(timeout=timeout, force=kill_process, del_data=del_user_data)
            self.log.info("✅ 浏览器已关闭！")
            close_browser = True
        except Exception as e:
            self.log.error(f"❌ 关闭浏览器出错: {type(e).__name__} - {e}")

        return [close_tab, close_browser]

    def ele_for_data(
            self,
            selector: Union[str, Tuple[str]],
            tab: TabType = None,
            index: int = 1,
            timeout: Optional[float] = None,
    ) -> SessionElement:
        """
        获取单个静态元素用于提取数据
        https://drissionpage.cn/get_start/concept#-%E5%85%83%E7%B4%A0%E5%AF%B9%E8%B1%A1
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-s_ele

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组 > https://drissionpage.cn/browser_control/get_elements/syntax#%EF%B8%8F%EF%B8%8F-%E5%9F%BA%E6%9C%AC%E6%A6%82%E5%BF%B5
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.s_ele(selector, index=index, timeout=timeout)

    def eles_for_data(
            self,
            selector: Union[str, Tuple[str]],
            tab: TabType = None,
            timeout: Optional[float] = None,
    ) -> List[SessionElement]:
        """
        获取静态元素用于提取数据
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-s_eles

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.s_eles(selector, timeout=timeout)

    def xpath_for_data(
            self,
            xpath: str,
            tab: TabType = None,
            index: Optional[int] = 1,
            timeout: Optional[float] = None,
    ) -> Union[SessionElement, List[SessionElement]]:
        """
        使用 Xpath 获取单个静态元素用于提取数据
        https://drissionpage.cn/browser_control/get_elements/syntax/#-xpath-%E5%8C%B9%E9%85%8D%E7%AC%A6-xpath

        :param xpath: Xpath表达式，可 F12 下直接鼠标右键——复制XPath; 用 xpath 在元素下查找时，最前面 // 或 / 前面的 . 可以省略。
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1。当 index=None 时，返回所有匹配的元素，相当于 s_eles。
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab
        if index is None:
            return tab.s_eles(f"xpath:{xpath}", timeout=timeout)

        return tab.s_ele(f"xpath:{xpath}", index=index, timeout=timeout)

    def xpath_for_action(
            self,
            xpath: str,
            tab: TabType = None,
            index: Optional[int] = 1,
            timeout: Optional[float] = None,
    ) -> ChromiumElement:
        """
        使用 Xpath 定位单个元素用于执行操作
        https://drissionpage.cn/get_start/concept#-%E5%85%83%E7%B4%A0%E5%AF%B9%E8%B1%A1
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-ele

        :param xpath: Xpath表达式，可 F12 下直接鼠标右键——复制XPath; 用 xpath 在元素下查找时，最前面 // 或 / 前面的 . 可以省略。
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.ele(f"xpath:{xpath}", index=index, timeout=timeout)

    def ele_for_action(
            self,
            selector: Union[str, Tuple[str]],
            tab: TabType = None,
            index: Optional[int] = 1,
            timeout: Optional[float] = None,
    ) -> Union[ChromiumElement, ChromiumFrame, SessionElement, None]:
        """
        定位单个元素用于执行操作
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-ele

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.ele(selector, index=index, timeout=timeout)

    @staticmethod
    def _verify_after_action(
            tab: Union[ChromiumTab, MixTab],
            verify_selector_appear: Optional[Union[str, Tuple[str]]] = None,
            verify_selector_disappear: Optional[Union[str, Tuple[str]]] = None,
            verify_text_appear: Optional[str] = None,
            verify_text_disappear: Optional[str] = None,
            verify_url_changed: bool = False,
            verify_url: Optional[str] = None,
            old_url: Optional[str] = None,
            verify_timeout: float = 5.0,
    ) -> bool:
        """
        通用点击后验证逻辑，返回True/False
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-ele

        :param tab: 标签页对象，类型为 ChromiumTab
        :param verify_selector_appear: 验证点击后页面上出现的元素定位
        :param verify_selector_disappear: 验证点击后页面上消失的元素定位
        :param verify_text_appear: 验证点击后页面上出现的文本
        :param verify_text_disappear: 验证点击后页面上消失的文本
        :param verify_url_changed: 验证点击后页面 url 是否发生变化
        :param verify_url: 验证点击后页面 url 是否为指定值
        :param old_url: 点击前的 url
        :param verify_timeout: 验证等待超时时间（秒）
        :return: 验证是否通过
        """
        start_time = time.time()
        while time.time() - start_time < verify_timeout:
            if verify_selector_appear:
                found = tab.ele(verify_selector_appear)
                if found:
                    return True
            if verify_selector_disappear:
                if not tab.ele(verify_selector_disappear):
                    return True
            if verify_text_appear:
                if verify_text_appear in tab.html:
                    return True
            if verify_text_disappear:
                if verify_text_disappear not in tab.html:
                    return True
            if verify_url_changed and old_url and tab.url != old_url:
                return True
            if verify_url and tab.url == verify_url:
                return True
            tab.wait(0.3)
        return False

    def click_ele(
            self,
            sel_or_ele: SelOrEleType,
            tab: TabType = None,
            index: Optional[int] = 1,
            timeout: Optional[float] = None,
            by_js: Optional[bool] = None,
            c_timeout: float = 1.5,
            wait_stop: bool = True,
            expect_new_tab: bool = False,
            verify_selector_appear: Optional[Union[str, Tuple[str]]] = None,
            verify_selector_disappear: Optional[Union[str, Tuple[str]]] = None,
            verify_text_appear: Optional[str] = None,
            verify_text_disappear: Optional[str] = None,
            verify_url_changed: bool = False,
            verify_url: Optional[str] = None,
            verify_timeout: float = 5.0,
            retry_times: int = 0,
    ) -> ClickReturnType:
        """
        点击元素，并可选验证点击生效或跳转新页面
        https://drissionpage.cn/browser_control/ele_operation/#-clickfor_new_tab

        :param sel_or_ele: 元素的定位信息。可以是查询字符串，loc 元组，或一个 ChromiumElement 对象
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :param by_js: 指定点击行为方式。为 None 时自动判断，为 True 用 JS 方式点击，为 False 用模拟点击。
        :param c_timeout: 模拟点击的超时时间（秒），等待元素可见、可用、进入视口，默认为 1.5 秒
        :param wait_stop: 点击前是否等待元素停止运动，默认为 True
        :param expect_new_tab: 是否预期点击后会打开新标签页（推荐用于 a 标签或 target=_blank 等情况）
        :param verify_selector_appear: 验证点击后页面上出现的元素定位（可选）
        :param verify_selector_disappear: 验证点击后页面上消失的元素定位（可选）
        :param verify_text_appear: 验证点击后页面上出现的文本（可选）
        :param verify_text_disappear: 验证点击后页面上消失的文本（可选）
        :param verify_url_changed: 验证点击后页面 url 是否发生变化（可选）
        :param verify_url: 验证点击后页面 url 是否为指定值（可选）
        :param verify_timeout: 验证等待超时时间（秒），默认 5 秒
        :param retry_times: 点击失败时重试的次数，默认为 0：不重试
        :return:
            - 若 expect_new_tab=True，返回 [新标签页对象, 元素对象, True/False(验证结果)]，未检测到新标签页则返回 [当前tab, 元素对象, False]；
            - 若有验证条件，返回 [当前tab, 元素对象, True/False(验证结果)]；
            - 否则返回 [当前tab, 元素对象, 点击结果]；
            - 未找到元素时返回 None
        """
        tab = tab or self.latest_tab

        for attempt in range(retry_times + 1):
            ele = self._parse_sel_or_ele(
                sel_or_ele, tab=tab, index=index, timeout=timeout
            )
            if not ele:
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {sel_or_ele}，第{attempt + 1}次")
                    continue
                return None

            need_verify = any(
                [
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                ]
            )

            try:
                if expect_new_tab:
                    new_tab = ele.click.for_new_tab(by_js=by_js)
                    if new_tab:
                        if not need_verify:
                            return [new_tab, ele, True]

                        old_url = (
                            new_tab.url if (verify_url_changed or verify_url) else None
                        )
                        result = self._verify_after_action(
                            new_tab,
                            verify_selector_appear,
                            verify_selector_disappear,
                            verify_text_appear,
                            verify_text_disappear,
                            verify_url_changed,
                            verify_url,
                            old_url,
                            verify_timeout,
                        )
                        return [new_tab, ele, result]
                    self.log.warning("⚠️ 未检测到新标签页打开")
                    if attempt < retry_times:
                        self.log.info(
                            f"🔁 重试点击元素: {sel_or_ele}，第{attempt + 1}次"
                        )
                        continue
                    return [tab, ele, False]

                # https://drissionpage.cn/browser_control/ele_operation/#-click%E5%92%8Cclickleft
                click_result = ele.click(
                    by_js=by_js, timeout=c_timeout, wait_stop=wait_stop
                )
                # click_result 不是bool，期望返回True/False，判断是否点击成功
                is_success = bool(click_result)
                if not need_verify:
                    return [tab, ele, is_success]

                old_url = tab.url if (verify_url_changed or verify_url) else None
                result = self._verify_after_action(
                    tab,
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                    old_url,
                    verify_timeout,
                )
                return [tab, ele, result]
            except Exception as e:
                self.log.error(f"❌ 点击元素异常: {type(e).__name__} - {e}")
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {sel_or_ele}，第{attempt + 1}次")
                    continue
                return None
        return None

    def click_xpath(
            self,
            xpath: Union[str, Tuple[str]],
            tab: TabType = None,
            index: Optional[int] = 1,
            timeout: Optional[float] = None,
            by_js: Optional[bool] = None,
            c_timeout: float = 1.5,
            wait_stop: bool = True,
            expect_new_tab: bool = False,
            verify_selector_appear: Optional[Union[str, Tuple[str]]] = None,
            verify_selector_disappear: Optional[Union[str, Tuple[str]]] = None,
            verify_text_appear: Optional[str] = None,
            verify_text_disappear: Optional[str] = None,
            verify_url_changed: bool = False,
            verify_url: Optional[str] = None,
            verify_timeout: float = 5.0,
            retry_times: int = 0,
    ) -> ClickReturnType:
        """
        点击通过 Xpath 定位的元素，并可选验证点击效果或是否跳转新页面。
        https://drissionpage.cn/browser_control/ele_operation/#-clickfor_new_tab

        :param xpath: Xpath 表达式，用于定位要点击的元素
        :param tab: 操作的标签页对象，默认使用当前标签页
        :param index: 匹配的第几个元素，从 1 开始，负数表示从后往前
        :param timeout: 等待元素出现的超时时间（秒）
        :param by_js: 是否使用 JS 方式点击，None 时自动判断
        :param c_timeout: 模拟点击的超时时间（秒），等待元素可见、可用、进入视口
        :param wait_stop: 点击前是否等待元素停止运动
        :param expect_new_tab: 点击下一页会有新标签页打开，默认为 False。
        :param verify_selector_appear: 验证点击后页面上出现的元素定位
        :param verify_selector_disappear: 验证点击后页面上消失的元素定位
        :param verify_text_appear: 验证点击后页面上出现的文本
        :param verify_text_disappear: 验证点击后页面上消失的文本
        :param verify_url_changed: 验证点击后页面 url 是否发生变化
        :param verify_url: 验证点击后页面 url 是否为指定值
        :param verify_timeout: 验证等待超时时间（秒）
        :param retry_times: 点击失败时重试的次数，默认为 0：不重试
        :return:
            - 若 expect_new_tab=True，返回 [新标签页对象, 元素对象, True/False(验证结果)]，未检测到新标签页则返回 [当前tab, 元素对象, False]；
            - 若有验证条件，返回 [当前tab, 元素对象, True/False(验证结果)]；
            - 否则返回 [当前tab, 元素对象, 点击结果]；
            - 未找到元素时返回 None
        """
        for attempt in range(retry_times + 1):
            ele = self.xpath_for_action(xpath, tab, index, timeout)
            if not ele:
                self.log.error(f"❌ 未找到元素: {xpath}")
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {xpath}，第{attempt + 1}次")
                    continue
                return None

            tab = tab or self.latest_tab

            need_verify = any(
                [
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                ]
            )

            try:
                if expect_new_tab:
                    new_tab = ele.click.for_new_tab(
                        by_js=by_js, timeout=c_timeout, wait_stop=wait_stop
                    )
                    if new_tab:
                        if not need_verify:
                            return [new_tab, ele, True]

                        old_url = (
                            new_tab.url if (verify_url_changed or verify_url) else None
                        )
                        result = self._verify_after_action(
                            new_tab,
                            verify_selector_appear,
                            verify_selector_disappear,
                            verify_text_appear,
                            verify_text_disappear,
                            verify_url_changed,
                            verify_url,
                            old_url,
                            verify_timeout,
                        )
                        return [new_tab, ele, result]
                    self.log.warning("⚠️ 未检测到新标签页打开")
                    if attempt < retry_times:
                        self.log.info(f"🔁 重试点击元素: {xpath}，第{attempt + 1}次")
                        continue
                    return [tab, ele, False]

                click_result = ele.click(
                    by_js=by_js, timeout=c_timeout, wait_stop=wait_stop
                )
                # click_result 不是bool，期望返回True/False，判断是否点击成功
                is_success = bool(click_result)
                if not need_verify:
                    return [tab, ele, is_success]

                old_url = tab.url if (verify_url_changed or verify_url) else None
                result = self._verify_after_action(
                    tab,
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                    old_url,
                    verify_timeout,
                )
                return [tab, ele, result]
            except Exception as e:
                self.log.error(f"❌ 点击元素异常: {type(e).__name__} - {e}")
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {xpath}，第{attempt + 1}次")
                    continue
                return None
        return None

    def auto_find_next_selector(
            self,
            tab: TabType = None,
            timeout: float = 5.0,
    ) -> ChromiumElement:
        """
        查找文本为 “下一页” 的 button 或 a标签的元素
        https://drissionpage.cn/browser_control/get_elements/syntax#-xpath-%E5%8C%B9%E9%85%8D%E7%AC%A6-xpath

        :param tab: 标签页对象
        :param timeout: 查找超时时间（秒）
        :return: 下一页按钮的元素对象
        """
        tab = tab or self.latest_tab
        # 查找文本为 “下一页” 的 button 或 a 标签元素，normalize-space 用于去除文本两端的空格；not(@disabled) 用于排除已禁用的按钮
        sel = 'xpath://button[normalize-space(text())="下一页" and not(@disabled)] | //a[normalize-space(text())="下一页"]'
        return self.ele_for_action(sel, tab=tab, timeout=timeout)

    def _run_callback(
            self,
            page_callback: Callable,
            *args,
            tab: TabType = None,
            refresh_on_None: bool = False,
            ignore_cache: bool = False,
            retry_times: int = 0,
            **kwargs,
    ) -> any:
        """
        运行回调函数，并处理异常和重试逻辑。

        :param page_callback: 页面回调函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :param tab: 标签页对象，默认为 None
        :param refresh_on_None: 回调函数返回 None 或异常时是否刷新页面
        :param ignore_cache: 刷新页面时是否忽略缓存
        :param retry_times: 重试次数
        :return: 回调函数的返回结果，全部失败时返回 None
        """
        current_tab = tab or self.latest_tab
        for attempt in range(retry_times + 1):
            try:
                result = page_callback(*args, **kwargs)
                if result is not None:
                    return result
            except Exception as e:
                self.log.error(f"❌ page_callback 执行异常: {type(e).__name__} - {e}")

            if refresh_on_None and attempt < retry_times:
                self.log.info(
                    f"🔄 回调返回 None 或异常，刷新页面进行第 {attempt + 1} 次重试..."
                )
                try:
                    current_tab.refresh(ignore_cache=ignore_cache)
                except Exception as e:
                    self.log.error(f"❌ 刷新页面异常: {type(e).__name__} - {e}")

            time.sleep(0.5)
        return None

    def next_page(
            self,
            page_callback: PageCallbackType,
            parse_current_page: bool = True,
            callback_retry_times: int = 0,
            page_fail_stop: bool = False,
            expect_new_tab: bool = False,
            next_selector: Optional[Union[str, Tuple[str]]] = None,
            tab: TabType = None,
            max_pages: Optional[int] = None,
            verify_selector: Optional[Union[str, Tuple[str]]] = None,
            verify_text: Optional[str] = None,
            verify_timeout: float = 5.0,
            timeout: float = 5.0,
            retry_times: int = 0,
            wait_time: float = 0.3,
    ) -> list:
        """
        通用翻页函数，自动点击“下一页”按钮，支持自定义查找和翻页逻辑。

        :param page_callback: 每次翻页后执行的回调函数，参数为(tab, page_index)，返回 None 表示处理失败，配合 callback_retry_times 参数程序会重试该页。非 None 时正常。
        :param parse_current_page: 是否解析当前页数据，默认为 True。
        :param callback_retry_times: page_callback 返回 None时重试的次数
        :param page_fail_stop: 如果 page_callback 返回 None，是否停止翻页。默认为 False，继续翻页。
        :param expect_new_tab: 点击下一页会有新标签页打开，默认为 False。
        :param next_selector: 下一页按钮的定位信息。为 None 时自动查找常见“下一页”按钮或a标签。
        :param tab: 标签页对象，默认为：self.latest_tab
        :param max_pages: 最大页数（默认起始页是第 1 页），None 表示自动翻页直到没有“下一页”
        :param verify_selector: 翻页后用于验证的元素定位
        :param verify_text: 翻页后用于验证的文本
        :param verify_timeout: 验证等待超时时间
        :param timeout: 查找“下一页”按钮的超时时间（秒）
        :param retry_times: 点击 下一页 失败时重试的次数
        :param wait_time: 每次翻页后的等待时间（秒）
        :return: parse_result，包含每一页 page_callback 的返回结果
        """
        tab = tab or self.latest_tab
        page_index = 1  # 页码索引，默认起始页是 1
        parse_result = []

        # 先处理当前页（如果需要）
        if parse_current_page:
            self.log.info("📄 处理起始页数据...")
            cb_result = self._run_callback(
                page_callback, tab, page_index, retry_times=callback_retry_times
            )
            parse_result.append(cb_result)
            if cb_result is None and page_fail_stop:
                self.log.error("❌ page_callback 处理起始页时返回 None，停止翻页")
                return parse_result

        while True:
            # 翻页前判断是否达到最大页数
            if max_pages is not None:
                if page_index >= max_pages:
                    self.log.info(f"⏭️ 已达到最大页数：{max_pages}，停止翻页")
                    break

            self.log.info(f"➡️ 开始翻页，当前页数: {page_index}")

            # 查找“下一页”按钮元素
            if next_selector is None:
                next_ele = self.auto_find_next_selector(tab, timeout=timeout)
            else:
                next_ele = self.ele_for_action(next_selector, tab=tab, timeout=timeout)

            if not next_ele:
                self.log.info("⛔ 未找到“下一页”按钮，停止翻页")
                break

            click_result = self.click_ele(
                next_ele,
                tab=tab,
                expect_new_tab=expect_new_tab,
                verify_selector_appear=verify_selector,
                verify_text_appear=verify_text,
                verify_timeout=verify_timeout,
                retry_times=retry_times,
            )

            if click_result is None:
                self.log.info("❌ 点击“下一页”按钮失败，停止翻页")
                break

            tab, _, is_success = click_result

            if not is_success:
                self.log.info("⚠️ 点击“下一页”按钮未通过验证，停止翻页")
                break

            page_index += 1
            self.log.info(f"📄 使用 page_callback 处理第 {page_index} 页...")

            cb_result = self._run_callback(
                page_callback, tab, page_index, retry_times=callback_retry_times
            )
            parse_result.append(cb_result)
            if cb_result is None and page_fail_stop:
                self.log.error(
                    f"❌ page_callback 处理第 {page_index} 页时返回 None，停止翻页！"
                )
                break

            tab.wait(wait_time)

        return parse_result

    def actions(
            self, tab: ActionTabType = None
    ) -> Actions:
        """
        获取 Actions 对象，用于执行复杂的用户交互操作
        https://drissionpage.cn/browser_control/actions#-%E4%BD%BF%E7%94%A8%E6%96%B0%E5%AF%B9%E8%B1%A1

        :param tab: 标签页对象，默认为 self.latest_tab
        :return: Actions 对象
        """
        tab = tab or self.latest_tab
        return Actions(tab)

    def scroll_to_page_bottom(
            self,
            tab: ActionTabType = None,
            retry_times: int = 0,
    ) -> bool:
        """
        滚动到页面底部
        https://drissionpage.cn/browser_control/page_operation/#-scrollto_bottom

        :param tab: 标签页对象，默认为 self.latest_tab
        :param retry_times: 滚动失败时重试的次数，默认为 0
        :return: 成功返回 True，失败返回 False
        """
        tab = tab or self.latest_tab

        for attempt in range(retry_times + 1):
            try:
                result = tab.scroll.to_bottom()
                if result:
                    self.log.info("✅ 已滚动到页面底部！")
                    return True
                else:
                    self.log.warning("⚠️ 未能滚动到页面底部!")
            except Exception as e:
                self.log.error(f"❌ 滚动到页面底部失败: {type(e).__name__} - {e}")

            if attempt < retry_times:
                self.log.info(f"🔁 即将进行第 {attempt + 1} 次重试 ...")
            else:
                break

        return False

    def scroll_ele_to_see(
            self,
            sel_or_ele: SelOrEleType,
            tab: TabType = None,
            index: Optional[int] = 1,
            timeout: Optional[float] = None,
            center: Optional[bool] = None,
            retry_times: int = 0,
    ) -> bool:
        """
        滚动页面直到元素可见
        https://drissionpage.cn/browser_control/ele_operation#-scrollto_see

        :param sel_or_ele: 元素的定位信息。可以是查询字符串，loc 元组，或一个 ChromiumElement 对象
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :param center: 是否尽量滚动到页面正中，为 None 时如果被遮挡则滚动到页面正中
        :param retry_times: 滚动失败时重试的次数，默认为 0
        :return: 成功返回 True，失败返回 False
        """
        for attempt in range(retry_times + 1):
            try:
                ele = self._parse_sel_or_ele(sel_or_ele, tab=tab, index=index, timeout=timeout)
                if not ele:
                    return False

                result = ele.scroll.to_see(center=center)
                if result:
                    self.log.info("✅ 已滚动到元素可见位置！")
                    return True
                else:
                    self.log.warning("⚠️ 未能滚动到元素可见位置!")
            except Exception as e:
                self.log.error(f"❌ 滚动到元素可见位置失败: {type(e).__name__} - {e}")

            if attempt < retry_times:
                self.log.info(f"🔁 即将进行第 {attempt + 1} 次重试 ...")
            else:
                break

        return False

    def scroll_to_ele_bottom(
            self,
            ele: ChromiumElement,
            retry_times: int = 0,
    ) -> bool:
        """
        滚动到元素底部
        https://drissionpage.cn/browser_control/ele_operation/#-scrollto_bottom

        :param ele: 元素对象
        :param retry_times: 滚动失败时重试的次数，默认为 0
        :return: 成功返回 True，失败返回 False
        """
        for attempt in range(retry_times + 1):
            try:
                result = ele.scroll.to_bottom()
                if result:
                    self.log.info("✅ 已滚动到元素底部！")
                    return True
                else:
                    self.log.warning("⚠️ 未能滚动到元素底部!")
            except Exception as e:
                self.log.error(f"❌ 滚动到元素底部失败: {type(e).__name__} - {e}")

            if attempt < retry_times:
                self.log.info(f"🔁 即将进行第 {attempt + 1} 次重试 ...")
            else:
                break

        return False

    def scroll_to_page_top(
            self,
            tab: ActionTabType = None,
            retry_times: int = 0,
    ) -> bool:
        """
        滚动到页面顶部
        https://drissionpage.cn/browser_control/page_operation/#-scrollto_top

        :param tab: 标签页对象，默认为 self.latest_tab
        :param retry_times: 滚动失败时重试的次数，默认为 0
        :return: 成功返回 True，失败返回 False
        """
        tab = tab or self.latest_tab

        for attempt in range(retry_times + 1):
            try:
                result = tab.scroll.to_top()
                if result:
                    self.log.info("✅ 已滚动到页面顶部！")
                    return True
                else:
                    self.log.warning("⚠️ 未能滚动到页面顶部!")
            except Exception as e:
                self.log.error(f"❌ 滚动到页面顶部失败: {type(e).__name__} - {e}")

            if attempt < retry_times:
                self.log.info(f"🔁 即将进行第 {attempt + 1} 次重试 ...")
            else:
                break

        return False

    def scroll_to_ele_top(
            self,
            ele: ChromiumElement,
            retry_times: int = 0,
    ) -> bool:
        """
        滚动到元素顶部
        https://drissionpage.cn/browser_control/ele_operation/#-scrollto_top

        :param ele: 元素对象
        :param retry_times: 滚动失败时重试的次数，默认为 0
        :return: 成功返回 True，失败返回 False
        """
        for attempt in range(retry_times + 1):
            try:
                result = ele.scroll.to_top()
                if result:
                    self.log.info("✅ 已滚动到元素顶部！")
                    return True
                else:
                    self.log.warning("⚠️ 未能滚动到元素顶部!")
            except Exception as e:
                self.log.error(f"❌ 滚动到元素顶部失败: {type(e).__name__} - {e}")

            if attempt < retry_times:
                self.log.info(f"🔁 即将进行第 {attempt + 1} 次重试 ...")
            else:
                break

        return False

    def __enter__(self):
        """
        支持with语句进入上下文
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支持with语句退出上下文时自动关闭浏览器
        """
        self.close_browser()

    def download_with_browser(
            self,
            selector: Union[str, Tuple[str]],
            timeout: Optional[float] = None,
            tab: TabType = None,
            not_download: bool = False,
            not_download_sleep: float = None,
            save_path: Optional[str] = None,
            rename: Optional[str] = None,
            suffix: Optional[str] = None,
            file_exists: FileExistsType = "overwrite",
            new_tab: bool = False,
            by_js: bool = False,
            show_progress: bool = True,
            del_cache: bool = True,
            cache_timeout: float = 1,
            download_timeout: float = None,
            cancel_if_timeout: bool = True,
    ) -> Union[DownloadMission, dict]:
        """
        [browser]使用浏览器原生下载功能下载当前页面的文件。
        https://drissionpage.cn/download/browser/#%EF%B8%8F-clickto_download

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组
        :param timeout: 等待元素出现的超时时间（秒），默认为 None 使用页面对象设置
        :param tab: 标签页对象，默认为 self.latest_tab
        :param not_download: 是否不下载文件，默认为 False，如果为 True 则只返回下载任务信息而不实际下载文件
        :param not_download_sleep: 如果 not_download 为 True，等待下载任务信息的时间（秒），默认为 None 不等待，如果数据（size）不全可以调试等待时间
        :param save_path: 保存文件的目录路径（不含文件名），为 None 保存到当前路径 或 初始化设置的 browser_download_path 路径
        :param rename: 重命名文件名，可不带后缀，程序会自动补充，为 None 则不修改
        :param suffix: 重命名的文件后缀名（不需要加 .），如 'pdf'，为 None 则不修改
        :param file_exists: 遇到同名文件时的处理方式，可选 'skip', 'overwrite', 'rename', 'add', 's', 'o', 'r', 'a'，默认：覆盖源文件 > https://drissionpage.cn/download/browser/#%EF%B8%8F-%E5%90%8C%E5%90%8D%E6%96%87%E4%BB%B6%E7%9A%84%E5%A4%84%E7%90%86
        :param new_tab: 是否在新标签页中下载，默认为 False
        :param by_js: 是否用 js 方式点击，默认为 False，模拟点击
        :param show_progress: 是否显示下载进度，默认为 True
        :param del_cache: 是否删除缓存文件，默认为 True，仅 not_download=True 时生效！
        :param cache_timeout: 删除缓存文件的超时时间，默认为 1 秒
        :param download_timeout: 下载超时时间（秒），默认为 None，使用页面对象默认超时时间
        :param cancel_if_timeout: 下载超时后是否取消下载任务，默认为 True
        :return: 下载任务信息字典
        """
        tab = tab or self.latest_tab
        try:
            ele = self.ele_for_action(selector, tab=tab, timeout=timeout)
            # 重名处理
            self.set.when_download_file_exists(file_exists)
            self.log.info("📥 使用浏览器获取原生下载数据...")
            mission = ele.click.to_download(
                save_path=save_path,
                rename=rename,
                suffix=suffix,
                new_tab=new_tab,
                by_js=by_js,
                timeout=download_timeout,
            )

            if not_download:
                self.log.info(f"🔍 获取 <{mission.name}> 的下载任务信息...")
                if not_download_sleep:
                    time.sleep(not_download_sleep)
                self.cancel_download_task_browser(mission)  # 取消下载任务
                # 缓存文件路径
                cache_file = os.path.join(mission.tmp_path, mission.id)
                self.log.debug(f"🗑️  缓存文件路径: {cache_file}")
                if del_cache:
                    for _ in range(math.ceil(cache_timeout / 0.5)):
                        if os.path.exists(cache_file):
                            try:
                                os.remove(cache_file)
                                self.log.info(f"🗑️  已删除缓存文件: {cache_file}")
                            except Exception as e:
                                self.log.error(
                                    f"❌ 删除缓存文件失败: {type(e).__name__} - {e}"
                                )
                            break
                        time.sleep(0.5)

                return self.get_download_task_info_browser(mission, all_info=False)

            self.log.info(f"✅ 已添加下载 <{mission.name}> 的任务，等待下载完成...")
            mission.wait(
                show=show_progress,
                timeout=download_timeout,
                cancel_if_timeout=cancel_if_timeout,
            )

            return mission
        except Exception as e:
            self.log.error(f"❌ 浏览器原生下载失败: {type(e).__name__} - {e}")
            return None

    @staticmethod
    def cancel_download_task_browser(mission: DownloadMission) -> None:
        """
        [browser]取消未完成的浏览器原生下载任务
        https://drissionpage.cn/download/browser#-%E5%8F%96%E6%B6%88%E4%BB%BB%E5%8A%A1

        :param mission: 下载任务的 ID
        :return: 无返回
        """
        mission.cancel()

    def get_download_task_info_browser(
            self, mission: DownloadMission, all_info: bool = True
    ) -> dict:
        """
        [browser]获取浏览器原生下载任务的信息
        https://drissionpage.cn/download/browser#-%E8%8E%B7%E5%8F%96%E4%BB%BB%E5%8A%A1%E4%BF%A1%E6%81%AF

        :param mission: 下载任务对象
        :param all_info: 是否获取所有信息，默认为 True
        :return: 下载任务信息字典
        """

        task_info = {
            "download_url": mission.url,
            "tab_id": mission.tab_id,
            "id": mission.id,
            "filename": mission.name,
            "size": mission.total_bytes,  # 字节数
            "save_path": mission.folder,
            "tmp_path": mission.tmp_path,
        }

        if all_info:
            task_info.update(
                {
                    "is_done": mission.is_done,
                    "rate": mission.rate,
                    "state": mission.state,  # 'running', 'done', 'canceled', 'skipped'
                    "fullpath": mission.final_path,
                    "downloaded_size": mission.received_bytes,  # 字节数
                }
            )

        self.log.debug(f"🔍 获取下载任务信息成功: {task_info}")

        return task_info

    def download(
            self,
            selector: Union[str, Tuple[str]] = None,
            urls: Union[str, List[str]] = None,
            tab: TabType = None,
            new_tab: bool = False,
            by_js: bool = False,
            rename: Union[str, List[str]] = None,
            save_path: Optional[str] = None,
            suffix: Optional[Union[str, List[str]]] = None,
            file_exists: FileExistsType = "overwrite",
            split: bool = True,
            block_size: Optional[str] = None,
            concurrent: bool = True,
            show_progress: bool = True,
            wait_finish: bool = False,
            threads: int = 3,
            retry_times: int = 2,
            retry_interval: float = 3,
            timeout: Union[int, float] = 5,
            proxies: str = None,
            **kwargs,
    ) -> List[Mission]:
        """
        [requests]文件下载
        https://drissionpage.cn/download/DownloadKit/
        https://drissionpage.cn/DownloadKitDocs/

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组，仅当 urls=None 有效！
        :param urls: 下载的文件 URL，可以是单个 URL 字符串或 URL 列表
        :param tab: 标签页对象，默认为 self.latest_tab
        :param new_tab: 是否在新标签页中下载，默认为 False
        :param by_js: 是否用 js 方式点击，默认为 False，模拟点击
        :param rename: 重命名文件名（或文件名列表），与 urls 一一对应，可不带后缀，程序会自动补充
        :param save_path: 保存文件的目录路径（不含文件名），为 None 时使用浏览器默认下载目录
        :param suffix: 重命名的文件后缀名（注意：不需要加在后缀前加 .），可以是字符串或与 urls 等长的列表
        :param file_exists: 遇到同名文件时的处理方式，可选 'skip', 'overwrite', 'rename', 'add', 's', 'o', 'r', 'a'，默认：覆盖源文件 > https://drissionpage.cn/DownloadKitDocs/usage/settings/#setif_file_existsxxxx
        :param split: 是否允许多线程分块下载，默认情况下，超过 50M 的文件会自动分块下载。
        :param block_size: 分块下载时每块的大小，单位为字节，可用'K'、'M'、'G'为单位，如'50M'，默认 50MB
        :param concurrent: 是否使用并发下载，否则使用阻塞式单个下载
        :param show_progress: 是否显示下载进度，当 concurrent=False 时生效！
        :param wait_finish: 是否等待所有下载任务完成，默认为 False。若为 True，则会阻塞当前线程直到所有下载任务完成 > https://drissionpage.cn/DownloadKitDocs/usage/misssions/#_3
        :param threads: 同时运行的线程数，默认为 3
        :param retry_times: 下载失败时重试的次数，默认为 2
        :param retry_interval: 重试间隔时间，单位为秒，默认为 3
        :param timeout: 连接超时时间，单位为秒，默认为 5 秒，0表示不限时
        :param proxies: 代理设置，默认为 None，例：'127.0.0.1:1080' > https://drissionpage.cn/DownloadKitDocs/usage/settings/#setproxies
        :param kwargs: 传递给 download 方法的其它参数
        :return: Mission下载对象列表 > https://drissionpage.cn/download/DownloadKit/#-%E4%BB%BB%E5%8A%A1%E5%AF%B9%E8%B1%A1
        """
        if urls is None and selector is None:
            raise ValueError("⚠️  请先设置下载的文件 URL 或元素选择器 selector！")

        if isinstance(urls, str):
            urls = [urls]
        if urls is None:
            task_info = self.download_with_browser(
                selector=selector,
                tab=tab,
                not_download=True,
                new_tab=new_tab,
                by_js=by_js,
            )
            download_url = task_info.get("download_url")
            if download_url:
                urls = [download_url]
                self.log.debug(f"🔍 从元素获取下载 URL: {download_url}")

        if rename is not None and isinstance(rename, str):
            rename = [rename]
        if rename is not None and len(rename) != len(urls):
            self.log.warning("⚠️  rename 列表长度与 urls 不一致，将忽略 rename 参数。")
            rename = None

        # 处理 suffix
        if suffix is not None:
            if isinstance(suffix, str):
                suffix_list = [suffix] * len(urls)
            elif isinstance(suffix, list):
                if len(suffix) != len(urls):
                    self.log.warning(
                        "⚠️  suffix 列表长度与 urls 不一致，将忽略 suffix 参数。"
                    )
                    suffix_list = [None] * len(urls)
                else:
                    suffix_list = suffix
            else:
                suffix_list = [None] * len(urls)
        else:
            suffix_list = [None] * len(urls)

        # 全局参数设置
        self.downloader.set.roads(threads)
        self.downloader.set.retry(retry_times)
        self.downloader.set.interval(retry_interval)
        self.downloader.set.timeout(timeout)
        if save_path:
            self.downloader.set.save_path(save_path)
        if proxies:
            self.downloader.set.proxies(proxies)
        if block_size:
            self.downloader.set.block_size(block_size)

        results = []
        for idx, url in enumerate(urls):
            file_rename = None
            if rename is not None:
                file_rename = rename[idx]
            file_suffix = suffix_list[idx] if suffix_list else None

            self.log.info(
                f"📥 {'添加并发式' if concurrent else '正在阻塞式'}下载任务: {url}{f' >>> 重命名为：{file_rename}' if file_rename else ''}{f'，后缀：{file_suffix}' if file_suffix else ''}"
            )

            mission = self.downloader.add(
                file_url=url,
                save_path=save_path,
                rename=file_rename,
                suffix=file_suffix,
                file_exists=file_exists,
                split=split,
                **kwargs,
            )
            results.append(mission)
            if not concurrent:
                # 阻塞式逐个下载
                mission.wait(show_progress)

        if wait_finish:
            self.log.info("⏳ 等待所有下载任务完成...")
            self.downloader.wait(show=show_progress)

        return results

    @property
    def all_download_tasks(self) -> dict:
        """
        [requests]获取所有下载任务。该属性返回一个dict，保存了所有下载任务。以任务对象的id为 key。
        https://drissionpage.cn/download/DownloadKit/#-%E8%8E%B7%E5%8F%96%E5%85%A8%E9%83%A8%E4%BB%BB%E5%8A%A1%E5%AF%B9%E8%B1%A1
        """
        return self.downloader.missions

    @property
    def all_download_failed_tasks(self) -> List[Mission]:
        """
        [requests]获取所有下载失败的任务。该属性返回一个列表，保存了所有下载失败的任务对象。
        https://drissionpage.cn/download/DownloadKit/#-%E8%8E%B7%E5%8F%96%E4%B8%8B%E8%BD%BD%E5%A4%B1%E8%B4%A5%E7%9A%84%E4%BB%BB%E5%8A%A1
        """
        return self.downloader.get_failed_missions()

    @staticmethod
    def cancel_download_task(mission: Mission) -> None:
        """
        [requests]取消未完成的下载任务
        https://drissionpage.cn/DownloadKitDocs/usage/misssions/#_4

        :param mission: 下载任务的 ID
        :return: 无返回
        """
        mission.cancel()

    def cancel_all_download_task(self) -> None:
        """
        [requests]取消所有未完成的下载任务
        :return: 无返回
        """
        self.downloader.cancel()

    @staticmethod
    def get_download_task_info(mission: Mission) -> dict:
        """
        [requests]获取下载任务详情
        https://drissionpage.cn/DownloadKitDocs/usage/misssions/#mission

        :param mission: 下载任务 Mission 对象
        :return: 任务信息字典
        """

        return {
            "id": mission.id,
            "method": mission.method,
            "result": mission.result,
            "is_done": mission.is_done,
            "size": mission.size,
            "tasks_count": mission.tasks_count,
            "done_tasks_count": mission.done_tasks_count,
            "rate": mission.rate,
            "state": mission.state,
            "info": mission.info,
            "file_name": mission.file_name,
            "save_path": mission.path,
            "data": mission.data,  # 任务数据
            "recorder": mission.recorder,  # 返回记录器对象
        }

    def listen_network(
            self,
            targets: ListenTargetsType = True,
            tab: TabType = None,
            tab_url: Optional[str] = None,
            timeout: Optional[float] = 10,
            count: int = 0,
            steps: bool = False,
            steps_callback: StepsCallbackType = None,
            is_regex: bool = False,
            methods: Union[str, List[str]] = ("GET", "POST"),
            res_type: ListenResType = True,
            stop_loading: bool = False,
            raise_err: bool = True,
            fit_count: bool = True,
            retry_times: int = 0,
            return_res: bool = False,
    ) -> ListenReturnType:
        """
        监听网页中的网络请求，并返回捕获到的数据包。
        https://drissionpage.cn/browser_control/listener
        https://drissionpage.cn/browser_control/visit/#-none%E6%A8%A1%E5%BC%8F%E6%8A%80%E5%B7%A7
        https://drissionpage.cn/browser_control/listener/#%EF%B8%8F-datapacket%E5%AF%B9%E8%B1%A1

        :param targets: 要匹配的数据包 url 特征，可用列表指定多个，默认为：True 获取所有数据包
        :param tab: 要监听的浏览器标签页，默认为：None，使用 self.latest_tab
        :param tab_url: 要监听的标签页 URL，默认为：None，自动刷新当前 tab
        :param timeout: 等待数据包的最大时间（秒），默认 10 秒，为 None 表示无限等待
        :param count: 要捕获的数据包数量，默认 1 个，当 steps=True and count=0 时监听所有数据
        :param steps: 是否实时获取数据，默认：False，为 True 时 targets 参数失效，使用 steps_callback 来筛选数据包 > https://drissionpage.cn/browser_control/listener/#-listensteps
        :param steps_callback: 一个判断数据包是否保留的回调函数，接收 DataPacket 对象，返回 True 保留，False 丢弃
        :param is_regex: 是否将 targets 作为正则表达式处理，默认：False
        :param methods: 要监听的请求方法，如 'GET'、'POST'，可传入字符串或列表
        :param res_type: 要监听的资源类型，如 'xhr'、'fetch'、'png'，默认：True 监听所有类型
        :param stop_loading: 是否在捕获数据包后停止页面加载，默认为 False
        :param raise_err: 超时是否抛出异常，默认抛出，设置为 False：超时会返回 False
        :param fit_count: 是否必须捕获到 count 个数据包才返回，默认 True：超时会返回 None，设置为 False：超时会返回已捕捉到的数据包。仅对 targets 生效！
        :param retry_times: 捕获失败时重试的次数，默认为 0 表示不重试
        :param return_res: 是否直接返回数据包的 response 的 body 数据，默认为：True：如果是 json 格式，转换为 dict；如果是 base64 格式，转换为 bytes，其它格式直接返回文本
        :return: 捕获到的数据包列表，超时或未捕获到数据包时返回 None；return_res=True 时返回 response 的 body 数据列表
        """
        tab = tab or self.latest_tab
        targets = True if steps else targets  # 如果 steps=True，则 targets 无效
        if not steps and count == 0:
            raise ValueError("⚠️  请设置 count 参数，steps=True 时 count=0 无效！")
        self.log.info(
            f"📡 监听方式：{'实时获取（targets参数失效）' if steps else '等待捕获'}，"
            f"📡 监听目标：{targets}（正则模式：{is_regex}），"
            f"方法：{methods}，"
            f"资源类型：{'所有类型' if res_type is True else res_type}，"
            f"目标数量：{count}{'（超时会返回 None）' if fit_count else '超时会返回已捕捉到的数据包'}，"
            f"返回 response 数据：{return_res}，"
            f"超时时间：{timeout} 秒。"
        )

        for attempt in range(retry_times + 1):
            self.log.info("📡 开始监听网络请求...")

            try:
                tab.listen.start(
                    targets=targets,
                    is_regex=is_regex,
                    method=methods,
                    res_type=res_type,
                )
            except Exception as e:
                self.log.error(f"❌ 启动监听器失败: {type(e).__name__} - {e}")
                return None

            try:
                if tab_url:
                    self.log.info(f"🌐 访问：{tab_url} 以开始捕获数据包...")
                    tab.get(tab_url)
                else:
                    self.log.info("🔄 刷新页面以开始捕获数据包...")
                    tab.refresh(ignore_cache=True)
            except Exception as e:
                self.log.error(f"❌ 页面刷新或访问失败: {type(e).__name__} - {e}")
                tab.listen.stop()
                return None

            if steps:
                self.log.info("⌛ steps 实时获取数据包...")
                result = []
                need_count = 0
                # https://drissionpage.cn/browser_control/listener/#%EF%B8%8F-datapacket%E5%AF%B9%E8%B1%A1
                for packet in tab.listen.steps(timeout=timeout):

                    if count != 0 and need_count >= count:
                        break

                    if steps_callback:
                        self.log.debug(
                            f"📦 数据包 >>> TabID：{packet.tab_id}，FrameID：{packet.frameId}，数据包：{packet.url}，方法：{packet.method}，类型：{packet.resourceType}，链接成功：{not packet.is_failed}"
                        )
                        try:
                            if steps_callback(packet):
                                result.append(packet)
                                need_count += 1
                                self.log.info(
                                    f"📦 已获取数据包：{need_count}/{count}，地址：{packet.url}，方法：{packet.method}，类型：{packet.resourceType}，链接成功：{not packet.is_failed}"
                                )
                        except Exception as e:
                            self.log.error(
                                f"❌ 遍历 steps 异常: {type(e).__name__} - {e}"
                            )
                            continue
                    else:
                        raise Exception(
                            "⚠️  请设置 listen_network 方法的 steps_callback 参数！"
                        )
            else:
                self.log.info("⌛ wait 等待捕获数据包...")
                # https://drissionpage.cn/browser_control/listener/#-listenwait
                try:
                    result = tab.listen.wait(
                        count=count,
                        timeout=timeout,
                        fit_count=fit_count,
                        raise_err=raise_err,
                    )
                    if count == 1:
                        result = [result]
                except Exception as e:
                    self.log.warning(
                        f"⚠️  捕获数据包时发生异常: {type(e).__name__} - {e}"
                    )
                    result = None

            tab.listen.stop()
            self.log.info("🛑 关闭监听器，监听结束！")

            if stop_loading:
                self.log.info("🛑 停止页面加载...")
                tab.stop_loading()

            if not result or (fit_count and count != 0 and len(result) < count):
                self.log.warning(
                    f"⚠️  捕获到的数据包数量 {len(result) if result else 0} 少于预期的 {count} 个！"
                )
                if attempt < retry_times:
                    self.log.info(f"🔁 即将进行第 {attempt + 1} 次重试 ...")
                    continue
                return None

            self.log.info(f"📦 已捕获 {len(result)} 个数据包。")

            # https://drissionpage.cn/browser_control/listener/#-response%E5%AF%B9%E8%B1%A1
            if return_res:

                def get_body(pkt):
                    try:
                        return pkt.response.body
                    except Exception as ee:
                        self.log.warning(
                            f"⚠️ 获取 response 数据失败: {type(ee).__name__} - {ee}"
                        )
                        return None

                return [get_body(pkt) for pkt in result]

            return result

        return None

    def _safe_get(self, obj, attr, default: any = None):
        """
        获取对象的属性

        :param obj: 对象
        :param attr: 属性名
        :param default: 默认值
        :return:
        """
        try:
            # 尝试获取属性
            return getattr(obj, attr, default)
        except Exception as e:
            self.log.error(f"❌ 获取属性 {attr} 失败: {type(e).__name__} - {e}")
            return None

    def datapacket_request_to_dict(self, request: DataPacket) -> dict:
        """
        将 Request 对象解析为 dict，属性不存在时返回 None
        https://drissionpage.cn/browser_control/listener/#-request%E5%AF%B9%E8%B1%A1

        :param request: Request 对象
        :return: dict
        """
        return {
            "url": self._safe_get(request, "url"),
            "method": self._safe_get(request, "method"),
            "params": self._safe_get(request, "params"),
            "headers": self._safe_get(request, "headers"),
            "cookies": self._safe_get(request, "cookies"),
            "postData": self._safe_get(request, "postData"),
        }

    def datapacket_response_to_dict(self, response: DataPacket) -> dict:
        """
        将 Response 对象解析为 dict，属性不存在时返回 None
        https://drissionpage.cn/browser_control/listener/#-response%E5%AF%B9%E8%B1%A1

        :param response: Response 对象
        :return: dict
        """
        return {
            "url": self._safe_get(response, "url"),
            "headers": self._safe_get(response, "headers"),
            "body": self._safe_get(response, "body"),
            "raw_body": self._safe_get(response, "raw_body"),
            "status": self._safe_get(response, "status"),
            "statusText": self._safe_get(response, "statusText"),
        }

    def datapacket_failinfo_to_dict(self, failInfo: DataPacket) -> dict:
        """
        将 FailInfo 对象解析为 dict，属性不存在时返回 None
        https://drissionpage.cn/browser_control/listener/#-response%E5%AF%B9%E8%B1%A1

        :param failInfo: FailInfo 对象
        :return: dict
        """
        return {
            "errorText": self._safe_get(failInfo, "errorText"),
            "canceled": self._safe_get(failInfo, "canceled"),
            "blockedReason": self._safe_get(failInfo, "blockedReason"),
            "corsErrorStatus": self._safe_get(failInfo, "corsErrorStatus"),
        }

    def datapacket_to_dict(self, packet: DataPacket) -> dict:
        """
        将 DataPacket 对象解析为 dict，属性不存在时返回 None
        https://drissionpage.cn/browser_control/listener/#%EF%B8%8F-datapacket%E5%AF%B9%E8%B1%A1

        :param packet: DataPacket 对象
        :return: dict
        """
        return {
            "tab_id": self._safe_get(packet, "tab_id"),
            "frameId": self._safe_get(packet, "frameId"),
            "target": self._safe_get(packet, "target"),
            "url": self._safe_get(packet, "url"),
            "method": self._safe_get(packet, "method"),
            "is_failed": self._safe_get(packet, "is_failed"),
            "resourceType": self._safe_get(packet, "resourceType"),
            "request": self.datapacket_request_to_dict(
                self._safe_get(packet, "request")
            ),
            "response": self.datapacket_response_to_dict(
                self._safe_get(packet, "response")
            ),
            "fail_info": self.datapacket_failinfo_to_dict(
                self._safe_get(packet, "fail_info")
            ),
        }

    def _parse_sel_or_ele(
            self,
            sel_or_ele: SelOrEleType,
            tab: TabType = None,
            index: int = 1,
            timeout: Optional[float] = None,
    ) -> Union[ChromiumElement, ChromiumFrame, SessionElement, None]:
        """
        解析选择器或元素对象，返回元素对象
        :param sel_or_ele: 选择器、元组或元素对象
        :param tab: 标签页，默认为 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒）
        :return: ChromiumElement 对象或 None
        """
        if isinstance(sel_or_ele, (ChromiumElement, ChromiumFrame, SessionElement)):
            return sel_or_ele
        elif isinstance(sel_or_ele, (str, tuple)):
            ele = self.ele_for_action(sel_or_ele, tab=tab, index=index, timeout=timeout)
            if isinstance(ele, NoneElement):
                self.log.error(f"❌ 未找到元素: {sel_or_ele}")
                return None
            return ele
        else:
            raise TypeError("sel_or_ele 必须是字符串、元组或 ChromiumElement 对象。")

    def upload_file(
            self,
            sel_or_ele: SelOrEleType,
            file_paths: Union[str, list],
            upload_sel_or_ele: Union[SelOrEleType, None] = None,
            tab: TabType = None,
            index: int = 1,
            by_js: bool = None,
            timeout: Optional[float] = None,
            **kwargs,
    ) -> bool:
        """
        上传文件到 input[type="file"] 元素
        https://drissionpage.cn/browser_control/upload/

        :param sel_or_ele: 触发文件选择框 的元素定位（选择器、元组或元素对象）
        :param upload_sel_or_ele: 选择文件后，有一些还需要点击 上传 按钮（选择器、元组或元素对象）
        :param file_paths: 本地文件路径，支持字符串或字符串列表（多文件）
        :param tab: 标签页对象，默认为 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param by_js: 指定点击行为方式。为 None 时自动判断，为 True 用 JS 方式点击，为 False 用模拟点击。
        :param timeout: 等待元素出现的超时时间（秒）
        :param kwargs: upload_sel_or_ele 相关的其他参数
        :return: 操作是否成功，注意：这并不代表上传成功！
        """
        tab = tab or self.latest_tab
        try:
            ele = self._parse_sel_or_ele(
                sel_or_ele, tab=tab, index=index, timeout=timeout
            )
            if not ele:
                return False

            # 支持多文件
            if isinstance(file_paths, str):
                file_paths = [file_paths]
            self.log.info(f"📤 上传文件: {file_paths}")
            ele.click.to_upload(file_paths, by_js=by_js)
            self.log.info("✅ 上传操作结束，请手动检查上传结果！")

            if upload_sel_or_ele:
                self.log.info("👆 点击 上传按钮")
                self.click_ele(
                    upload_sel_or_ele, tab=tab, timeout=timeout, by_js=by_js, **kwargs
                )

            return True
        except Exception as e:
            self.log.error(f"❌ 文件上传失败: {type(e).__name__} - {e}")
            return False

    @staticmethod
    def _select_single_option(s_ele, option, option_type, timeout) -> bool:
        """
        辅助函数：选择单个选项
        """
        if isinstance(option, int):
            return s_ele.select.by_index(option, timeout=timeout)
        elif isinstance(option, str):
            if option_type == "text":
                return s_ele.select(option, timeout=timeout)
            elif option_type == "value":
                return s_ele.select.by_value(option, timeout=timeout)
            elif option_type == "locator":
                return s_ele.select.by_locator(option, timeout=timeout)
            else:
                raise ValueError(f"❌ {option} 对应的 option_type 应该为 text、value 或 locator")
        else:
            raise ValueError(f"❌ 选项必须是 str 或 int 类型")

    @staticmethod
    def _select_multi_option(s_ele, options, option_type, timeout) -> bool:
        """
        辅助函数：选择多个选项
        """
        if all(isinstance(item, int) for item in options):
            if option_type == "index":
                return s_ele.select.by_index(options, timeout=timeout)
            else:
                raise ValueError(f"❌ {options} 对应的 option_type 应该为 index")
        elif all(isinstance(item, str) for item in options):
            if option_type == "text":
                return s_ele.select(options, timeout=timeout)
            elif option_type == "value":
                return s_ele.select.by_value(options, timeout=timeout)
            elif option_type == "locator":
                return s_ele.select.by_locator(options, timeout=timeout)
            else:
                raise ValueError(f"❌ {options} 对应的 option_type 应该为 text、value 或 locator")
        else:
            raise ValueError(f"❌ {options} 的选项必须为统一的 str 或 int 类型")

    def select_option(self,
                      select_sel_or_ele: SelOrEleType,
                      options: SelectType,
                      option_type: OptionType = "text",
                      tab: TabType = None,
                      timeout: Optional[float] = None) -> bool:
        """
        从 <select> 下拉列表中选择特定选项
        https://drissionpage.cn/browser_control/ele_operation/#%EF%B8%8F%EF%B8%8F-%E5%88%97%E8%A1%A8%E9%80%89%E6%8B%A9

        :param select_sel_or_ele: <select>下拉列表元素对象 或 元素定位（选择器、元组或元素对象）
        :param options: 要选择的选项文本 或 索引，支持列表形式进行多选
        :param option_type: 选择项的类型，可以是 ["text", "index", "value", "locator"]
        :param tab: 标签页对象，默认为 self.latest_tab
        :param timeout: 等待元素出现的超时时间（秒）
        :return: 选择是否成功
        """
        # 定位下拉列表
        s_ele = self._parse_sel_or_ele(select_sel_or_ele, tab=tab, timeout=timeout)
        if not s_ele:
            self.log.error(f"❌ 未找到列表元素: {select_sel_or_ele}")
            return False

        # 判断是否为多选列表
        is_multi = s_ele.select.is_multi

        # 单选逻辑
        if not is_multi:
            try:
                success = self._select_single_option(s_ele, options, option_type, timeout)
                if success:
                    self.log.info(f"✅ 选项 {options} 已选择")
                    return True
                else:
                    self.log.error(f"❌ 选项 {options} 未找到")
                    return False
            except ValueError as e:
                self.log.error(str(e))
                return False

        # 多选逻辑
        else:
            if not isinstance(options, (list, tuple)):
                raise ValueError(f"❌ 多选列表的选项必须是列表或元组类型")
            try:
                success = self._select_multi_option(s_ele, options, option_type, timeout)
                if success:
                    self.log.info(f"✅ 选项 {options} 已选择")
                    return True
                else:
                    self.log.error(f"❌ 选项 {options} 未找到")
                    return False
            except ValueError as e:
                self.log.error(str(e))
                return False

    def wait_ele_displayed(
            self,
            sel_or_ele: SelOrEleType,
            transform: bool = False,
            tab: TabType = None,
            index: int = 1,
            timeout: float = None,
            raise_error: bool = None
    ) -> bool:
        """
        等待指定元素出现在页面上并可见。
        https://drissionpage.cn/browser_control/waiting/#-waitele_displayed

        :param sel_or_ele: 元素的定位信息。可以是查询字符串、loc 元组或一个 ChromiumElement 对象
        :param transform: 是否是等待元素从隐藏状态变成显示状态，默认为 False：https://drissionpage.cn/browser_control/waiting/#-waitdisplayed
        :param tab: 标签页对象，默认为 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒）
        :param raise_error: 等待失败时是否报错，为 None 时根据 Settings 设置。
        :return: 如果元素成功显示返回 True，否则返回 False
        """
        tab = tab or self.latest_tab
        try:
            self.log.info(f"⏳ 等待元素出现: {sel_or_ele}")
            if transform:
                ele = self._parse_sel_or_ele(sel_or_ele, tab=tab, index=index, timeout=timeout)
                if not ele:
                    self.log.error(f"❌ 未找到元素: {sel_or_ele}")
                result = ele.wait.displayed(timeout=timeout, raise_err=raise_error)
            else:
                result = tab.wait.ele_displayed(sel_or_ele, timeout=timeout, raise_err=raise_error)
            if result:
                self.log.info(f"✅ 元素已出现: {sel_or_ele}")
            else:
                self.log.warning(f"⚠️  超时元素仍未出现: {sel_or_ele}")
            return bool(result)
        except Exception as e:
            self.log.error(f"❌ 等待元素出现时发生异常: {type(e).__name__} - {e}")
            return False

    def wait_ele_hidden(
            self,
            sel_or_ele: SelOrEleType,
            transform: bool = False,
            tab: TabType = None,
            index: int = 1,
            timeout: float = 10.0,
            raise_error: bool = None
    ) -> bool:
        """
        等待指定元素从页面上隐藏或移除。
        https://drissionpage.cn/browser_control/waiting/#-waitele_hidden

        :param sel_or_ele: 元素的定位信息。可以是查询字符串、loc 元组或一个 ChromiumElement 对象
        :param transform: 是否是等待元素从显示状态变成隐藏状态，默认为 False：https://drissionpage.cn/browser_control/waiting/#-waithidden
        :param tab: 标签页对象，默认为 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 最大等待时间（秒），默认为 10 秒
        :param raise_error: 等待失败时是否报错，为 None 时根据 Settings 设置。
        :return: 如果元素成功隐藏返回 True，否则返回 False
        """
        tab = tab or self.latest_tab
        try:
            self.log.info(f"⏳ 等待元素隐藏: {sel_or_ele}")
            if transform:
                ele = self._parse_sel_or_ele(sel_or_ele, tab=tab, index=index, timeout=timeout)
                if not ele:
                    self.log.error(f"❌ 未找到元素: {sel_or_ele}")
                result = ele.wait.hidden(timeout=timeout, raise_err=raise_error)
            else:
                result = tab.wait.ele_hidden(sel_or_ele, timeout=timeout, raise_err=raise_error)
            if result:
                self.log.info(f"✅ 元素已隐藏: {sel_or_ele}")
            else:
                self.log.warning(f"⚠️ 超时元素仍未隐藏: {sel_or_ele}")
            return result
        except Exception as e:
            self.log.error(f"❌ 等待元素隐藏时发生异常: {type(e).__name__} - {e}")
            return False
