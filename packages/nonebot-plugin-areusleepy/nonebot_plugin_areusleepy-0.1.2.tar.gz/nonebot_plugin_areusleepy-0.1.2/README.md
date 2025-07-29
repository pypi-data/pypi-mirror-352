<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# NoneBot-Plugin-AreUSleepy

_✨基于 [sleepy-project/sleepy](https://github.com/sleepy-project/sleepy) 项目的状态查询插件！ ✨_

[![python3](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>

## 📖 介绍

此插件可以发送在 [sleepy-project/sleepy](https://github.com/sleepy-project/sleepy) 目前的状态信息，可以显示用户的设备是否在使用中，正在听的歌曲 (支持情况以 sleepy 项目为准)，支持多设备状态列表

## 💿 安装

以下提到的方法 任选**其一**即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-areusleepy
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-areusleepy
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-nonebot-plugin-areusleepy
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-areusleepy
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-areusleepy
```

</details>
<details>
<summary>uv</summary>

```bash
uv add nonebot-plugin-areusleepy
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_areusleepy"
]
```

</details>

## ⚙️ 配置

env 配置示例，变量后面为默认配置:

```ini
# 基本配置
sleepy_command="aresleepy"    # 触发命令
sleepy_prompt_loading=true # 是否在发送消息前显示 "正在获取, 请稍候"
sleepy_show_details=false  # 是否显示详细信息 (状态的 id, 设备的 id, 最后更新时间的时区)

# Sleepy 服务配置
sleepy_url="https://status.0d000721.xin" # Sleepy 服务地址, 必须以 http:// 或 https:// 开头, 不以 / 结尾
sleepy_timeout=5.0                       # 请求超时 (秒)
sleepy_retries=3                         # 重试次数

# sleepy 定时任务配置
sleepy_scheduler_enabled: bool = False  # 是否启用定时任务
sleepy_scheduler_cron: str = '0 9,21 * * *'  # Cron 表达式，默认每天 9:00 和 21:00
sleepy_scheduler_groups: List[str] = []  # 推送的群组列表，默认为空，开启定时任务后必须配置此项
```

## 🎉 使用

用法:

- `/sleepy` - 查询配置中网站的在线状态
- `/sleepy [url]` - 查询其他网站的在线状态
  * 如: `/sleepy https://sleepy.wyf9.top`
  * **注意: `url` 必须以 `http://` 或 `https://` 开头**

### 效果图

![兄弟你睡了吗喵！！！！！！](./areisleepyyyyyy.png)

## 📞 联系

### Sleepy 项目

QQ 群组: [点此加群](https://siiway.top/t/qq)
Discord: [点此加入服务器](https://siiway.top/t/dc)
[更多联系方式](https://siiway.top/about/contact)

> *人较多, 请注明来意*

### 本项目

TG群组：[点此加入](https://t.me/LoveMurasame)
QQ群：[1049319982](https://qm.qq.com/q/DfTsIDXuc8)
作者邮箱：<congyu@sbhfy.cn>

> *大概率没人*

## 💡 鸣谢

本项目基于 [sleepy-project/sleepy: Are you sleeping?](https://github.com/sleepy-project/sleepy)

感谢 Sleepy 开发者 [wyf9](https://github.com/wyf9) 重构插件

## 📝 更新日志

### 0.1.0

重构插件



### 0.1.2

添加了定时任务
