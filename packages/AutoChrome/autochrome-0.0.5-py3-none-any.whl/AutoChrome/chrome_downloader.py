"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/5/29 09:07
文件描述：Chrome绿色版下载工具
文件路径：/AutoChrome/AutoChrome/chrome_downloader.py
"""

import os
import shutil
import zipfile
import tempfile
import platform
import requests
from tqdm import tqdm
from typing import Optional, Dict, Any, Literal


class ChromeDownloader:
    # Chromium最新快照版本号获取URL
    CHROMIUM_SNAPSHOT_URLS: Dict[str, str] = {
        "windows": "https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/LAST_CHANGE",
        "darwin": "https://storage.googleapis.com/chromium-browser-snapshots/Mac/LAST_CHANGE",
        "linux": "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/LAST_CHANGE",
    }
    # Chromium官方快照下载URL模板
    CHROMIUM_DOWNLOAD_URLS: Dict[str, str] = {
        "windows": "https://storage.googleapis.com/chromium-browser-snapshots/Win_x64/{rev}/chrome-win.zip",
        "darwin": "https://storage.googleapis.com/chromium-browser-snapshots/Mac/{rev}/chrome-mac.zip",
        "linux": "https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/{rev}/chrome-linux.zip",
    }

    def __init__(
            self,
            download_dir: Optional[str] = None,
            logger: Optional[Any] = None,
            custom_source: Optional[Dict[str, Dict[str, str]]] = None,
    ):
        """
        Chromium绿色版下载工具

        :param download_dir: 下载目录，默认为当前目录下的 chrome 文件夹
        :param logger: 日志对象
        :param custom_source: 自定义源，格式见文档
        """
        self.system: str = platform.system().lower()
        self.download_dir: str = download_dir or os.path.abspath("chrome")
        self.logger: Optional[Any] = logger
        self.custom_source: Optional[Dict[str, Dict[str, str]]] = custom_source

    def log(self, msg: str, level: str = "info") -> None:
        """
        日志输出

        :param msg: 日志内容
        :param level: 日志等级
        """
        if self.logger:
            getattr(self.logger, level, self.logger.info)(msg)
        else:
            print(msg)

    def get_latest_chromium_revision(
            self, system: Optional[str] = None
    ) -> Optional[str]:
        """
        获取最新的 Chromium 快照版本号

        :param system: 指定系统，默认当前系统
        :return: 版本号
        """
        sys_name: str = (system or self.system).lower()
        url: Optional[str] = None
        # 优先自定义源
        if self.custom_source and sys_name in {
            k.lower(): v for k, v in self.custom_source.items()
        }:
            url = self.custom_source[sys_name].get("latest")
        else:
            url = self.CHROMIUM_SNAPSHOT_URLS.get(sys_name)
        if not url:
            self.log(f"❌ 暂不支持当前系统：{sys_name}", "error")
            return None
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            rev = resp.text.strip()
            self.log(f"✅ 最新Chromium快照版本号：{rev}")
            return rev
        except Exception as e:
            self.log(f"⚠️ 获取Chromium快照版本号失败：{e}", "warning")
            return None

    def download_chromium(
            self, revision: Optional[str] = None, system: Optional[str] = None
    ) -> Optional[str]:
        """
        下载 Chromium 快照

        :param revision: 指定版本号，默认为最新版本
        :param system: 指定系统，默认为当前系统
        :return: 解压目录
        """
        sys_name: str = (system or self.system).lower()
        rev: Optional[str] = revision or self.get_latest_chromium_revision(
            system=sys_name
        )
        if not rev:
            return None
        # 优先自定义源
        if self.custom_source and sys_name in self.custom_source:
            url_tpl = self.custom_source[sys_name].get("download")
        else:
            url_tpl = self.CHROMIUM_DOWNLOAD_URLS.get(sys_name)
        if not url_tpl:
            self.log(f"❌ 暂不支持当前系统：{sys_name}", "error")
            return None
        url = url_tpl.format(rev=rev)
        self.log(f"⬇️  开始下载 Chromium 快照版：{url}")
        extract_dir = os.path.join(self.download_dir, f"chromium_{rev}")
        return self._download_and_extract(url, extract_dir)

    def _find_chrome_exe(self, base_path: str) -> Optional[str]:
        """
        在给定路径下查找 chrome 可执行文件

        :param base_path: 基础路径
        :return: chrome可执行文件路径
        """
        if self.system == "windows":
            return os.path.join(base_path, "chrome-win", "chrome.exe")
        elif self.system == "linux":
            return os.path.join(base_path, "chrome-linux", "chrome")
        elif self.system == "darwin":
            return os.path.join(
                base_path, "chrome-mac", "Chromium.app", "Contents", "MacOS", "Chromium"
            )
        return None

    def _download_and_extract(
            self, url: str, extract_dir: str, desc: str = "⏳ 下载进度"
    ) -> Optional[str]:
        """
        通用下载和解压方法

        :param url: 下载地址
        :param extract_dir: 解压目录
        :param desc: 进度描述
        :return: 解压后的路径
        """
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                os.makedirs(self.download_dir, exist_ok=True)
                with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".zip"
                ) as f, tqdm(
                    total=total, unit="B", unit_scale=True, desc=desc, ncols=80
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                    zip_path = f.name
            self.log(f"✅ 下载完成，解压中...")
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            with zipfile.ZipFile(zip_path, "r") as zip_ref, tqdm(
                    total=len(zip_ref.infolist()), desc="⏳ 解压进度", ncols=80
            ) as pbar:
                for member in zip_ref.infolist():
                    zip_ref.extract(member, extract_dir)
                    pbar.update(1)
            os.remove(zip_path)
            self.log(f"✅ 解压完成，路径：{extract_dir}")
            return extract_dir
        except Exception as e:
            self.log(f"❌ {desc}失败：{e}", "error")
            return None

    def _download_file(
            self, url: str, save_path: str, desc: str = "⏳ 下载进度"
    ) -> Optional[str]:
        """
        通用文件下载方法

        :param url: 下载地址
        :param save_path: 保存路径
        :param desc: 进度描述
        :return: 文件路径
        """
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                os.makedirs(self.download_dir, exist_ok=True)
                with open(save_path, "wb") as f, tqdm(
                        total=total, unit="B", unit_scale=True, desc=desc, ncols=80
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            self.log(f"✅ {desc}完成，路径：{save_path}")
            return save_path
        except Exception as e:
            self.log(f"❌ {desc}失败：{e}", "error")
            return None

    def download(
            self,
            revision: Optional[str] = None,
            system: Optional[Literal["windows", "linux", "darwin"]] = None,
            return_chrome_path: bool = False,
    ) -> Optional[str]:
        """
        下载 Chrome 浏览器

        :param revision: 指定 Chromium 快照版本号，默认为最新版本
        :param system: 指定系统，默认为自动识别
        :param return_chrome_path: 是否返回 chrome 可执行文件路径
        :return: 下载路径或 chrome 可执行文件路径
        """
        sys_name: str = (system or self.system).lower()

        # 优先自定义源
        if self.custom_source:
            self.log("🔍 使用自定义源进行下载")
            custom_rev = revision or self.get_latest_chromium_revision(sys_name)
            if custom_rev:
                path = self.download_chromium(custom_rev, sys_name)
                if path:
                    return self._handle_download_result(path, return_chrome_path)

        # 官方主源
        path = self.download_chromium(revision, sys_name)
        if path:
            return self._handle_download_result(path, return_chrome_path)

        self.log(f"❌ 下载失败！不支持的系统：{sys_name}", "error")
        return None

    def _handle_download_result(
            self, path: str, return_chrome_path: bool
    ) -> Optional[str]:
        """
        处理下载结果，返回路径或chrome可执行文件路径

        :param path: 下载或解压路径
        :param return_chrome_path: 是否返回chrome可执行文件路径
        :return: 路径或chrome可执行文件路径
        """
        if return_chrome_path:
            chrome_path = self._find_chrome_exe(path)
            if chrome_path and os.path.exists(chrome_path):
                self.log(f"✅ 找到 chrome 可执行文件：{chrome_path}")
                return chrome_path

            self.log(
                f"❌ 未找到 chrome 的可执行文件，请前往存放路径手动查找：{path}",
                "warning",
            )
            return None

        self.log(f"✅ Chrome下载完成，存放路径：{path}")
        return path
