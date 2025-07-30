# AutoChrome

> AutoChrome 是基于 [DrissionPage](https://drissionpage.cn/) 封装的浏览器自动化工具，支持自动下载 Chrome、丰富的页面操作、元素操作、网络监听、文件下载、日志管理等功能，适用于数据采集、自动化测试等场景。

注意：AutoChrome 是一个自用模块，部分功能 `未进行充分测试`，请谨慎使用！

## 主要特性

- **自动下载 Chrome 浏览器**：本地无浏览器时自动下载并配置。
- **类型安全**：参数和返回值均有详细类型注解，IDE 友好。
- **丰富的日志系统**：支持控制台和文件日志，日志格式可选，异常信息详细。
- **页面与元素操作**：支持多种元素定位、点击、滚动、翻页、cookie 操作等。
- **网络监听**：支持按 URL、方法、资源类型监听网络请求，支持回调筛选。
- **文件下载**：支持多线程分块下载、断点续传、重命名、并发/阻塞下载。
- **异常处理健壮**：所有关键操作均有异常捕获与日志记录，便于排查问题。
- **跨平台支持**：支持 Windows/Linux/Mac，部分功能仅限 Windows（如窗口隐藏/显示）。

## 安装依赖

1. 安装 AutoChrome：
   ```bash
   pip install -U AutoChrome
   ```
2. Windows 系统如需窗口隐藏功能，需安装 pypiwin32（windows系统下会自动安装）：
   ```bash
   pip install -i https://mirrors.aliyun.com/pypi/simple/ pypiwin32
   ```
3. 其它依赖请参考 `pyproject.toml` 或根据报错提示安装。

---

## 快速开始

```python
from AutoChrome.auto_chrome import AutoChrome

with AutoChrome(
    headless=True,
    auto_download_browser=True,
    console_log_level="INFO",
    log_file="autochrome.log",
    log_debug_format=True
) as browser:
    browser.get("https://www.example.com")
    print(browser.latest_tab.html)
```

## 主要用法

### 1. 浏览器初始化参数

- `start_url`: 启动后自动访问的页面
- `headless`: 是否无头模式
- `browser_path`: 指定 Chrome 路径
- `user_data_path`: 用户数据目录
- `auto_download_browser`: 自动下载 Chrome
- `console_log_level`/`log_file_level`: 日志等级
- `log_file`: 日志文件路径
- `log_debug_format`: 日志格式（True 为详细调试格式）

### 2. 页面与元素操作

```python
# 访问页面
browser.get("https://www.example.com")

# 获取元素（用于数据提取）
ele = browser.ele_for_data('div.content')
# 获取多个元素
eles = browser.eles_for_data('div.item')

# 通过 XPath 定位并点击
tab, ele, ok = browser.click_xpath('//a[text()="下一页"]', verify_text_appear="下一页")
```

### 3. Cookie 操作

```python
# 获取 cookies
cookies = browser.get_cookies(return_type="dict")
# 设置 cookies 并验证
browser.set_cookies(cookies, verify_str="登录成功")
```

### 4. 滚动操作

```python
browser.scroll_to_page_bottom()
browser.scroll_to_page_top()
```

### 5. 自动翻页与回调

```python
def parse_page(tab, page_index):
    # 解析页面逻辑
    return tab.html

results = browser.next_page(
    page_callback=parse_page,
    max_pages=5,
    verify_text="下一页"
)
```

### 6. 文件下载

```python
missions = browser.download(
    urls=["https://example.com/file1.zip", "https://example.com/file2.zip"],
    rename=["file1", "file2"],
    save_path="downloads",
    concurrent=True
)
```

### 7. 网络监听

```python
def filter_packet(packet):
    return "api/data" in packet.url

data = browser.listen_network(
    targets="api/data",
    methods="GET",
    count=2,
    steps=True,
    steps_callback=filter_packet,
    return_res=True
)
```

## 命令行工具

AutoChrome 提供命令行工具 `autochrome`，用于下载绿色版 Chromium 浏览器。

### 使用方式

```bash
autochrome cd [OPTIONS]
```

### 支持的子命令

- `cd`, `chromedownloader`: 下载 Chromium 浏览器

### 参数说明

| 参数               | 类型 | 描述                               |
| ------------------ | ---- | ---------------------------------- |
| `-d`, `--dir`      | str  | 下载目录（默认：chrome 文件夹）    |
| `-r`, `--revision` | str  | 指定 Chromium 快照版本号（可选）   |
| `--system`         | str  | 指定目标系统（可选，默认自动检测） |

### 示例

```bash
# 下载最新版 Chromium
autochrome cd

# 指定下载目录
autochrome cd -d ./chrome

# 指定 Chromium 快照版本号
autochrome cd -r 123456
```

---

## 日志与异常

- 所有操作均有详细日志输出，异常信息包含异常类型和描述。
- 日志格式可选，便于调试和生产环境排查。

## 注意事项

- **仅支持 Chromium 内核浏览器**，如 Chrome、Edge。
- 自动下载 Chrome 需联网，且默认下载到当前目录的 `chrome` 文件夹。
- 部分功能如窗口隐藏/显示仅支持 Windows 且需安装 `pypiwin32`。
- **窗口隐藏功能仅支持 Windows 且需安装 pypiwin32**。
- 建议使用虚拟环境管理依赖。
- 部分高级功能需参考 [DrissionPage 官方文档](https://drissionpage.cn/)。
- 打包程序请参考 [官方文档](https://drissionpage.cn/advance/packaging)

---

## 常见问题

- **浏览器无法启动/找不到驱动**：请确保已正确安装 Chrome/Edge，并配置好环境变量或手动指定驱动路径。
- **元素定位失败**：请检查定位表达式是否正确，或适当增加超时时间。
- **网络监听无结果**：确认目标接口是否被正确捕获，可尝试调整 `targets`、`methods`、`res_type` 参数。

---

## 联系与支持

- 作者：Xiaoqiang
- 微信公众号：XiaoqiangClub
- 反馈与建议请通过邮件联系：xiaoqiangclub@hotmail.com

---

## ☕ 请我喝咖啡 ☕

> 更多内容请关注微信公众号：XiaoqiangClub

![支持我](https://gitee.com/xiaoqiangclub/xiaoqiangapps/raw/master/images/xiaoqiangclub_ad.png)
