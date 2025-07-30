"""
作者：Xiaoqiang
微信公众号：XiaoqiangClub
创建时间：2025/6/3 09:06
文件描述：自定义参数类型
文件路径：/AutoChrome/custom_types.py
"""
from DrissionPage.items import *
from DrissionPage import ChromiumOptions
from http.cookiejar import Cookie, CookieJar
from DrissionPage._units.listener import DataPacket
from typing import TypeAlias, Callable, List, Tuple, Union, Optional, Literal

ChromiumOptionsType: TypeAlias = Union[str, int, ChromiumOptions, None]
GetCookieType: TypeAlias = Literal["list", "str", "dict", "json"]
SetCookieType: TypeAlias = Union[Cookie, str, dict, list, tuple, CookieJar]
SelOrEleType: TypeAlias = Union[str, Tuple[str], ChromiumElement, SessionElement, ChromiumFrame]
TabType: TypeAlias = Union[ChromiumTab, MixTab, WebPageTab, None]
ActionTabType: TypeAlias = Union[ChromiumTab, MixTab, WebPageTab, ChromiumFrame, None]
SelectType: TypeAlias = Union[str, int, Tuple[str], List[str], Tuple[int], List[int]]
OptionType: TypeAlias = Literal["text", "index", "value", "locator"]
ClickReturnType: TypeAlias = Optional[Tuple[Union[ChromiumTab, MixTab], ChromiumElement, bool]]
PageCallbackType: TypeAlias = Callable[[Union[ChromiumTab, MixTab], int], any]
FileExistsType: TypeAlias = Literal["skip", "overwrite", "rename", "add", "s", "o", "r", "a"]
StepsCallbackType: TypeAlias = Optional[Callable[[DataPacket], bool]]
ListenReturnType: TypeAlias = Union[List[DataPacket], List[Union[dict, bytes, str, None]], None]
ListenTargetsType: TypeAlias = Union[str, List[str], Literal[True]]
ListenResType: TypeAlias = Union[str, List[str], Literal[True]]
