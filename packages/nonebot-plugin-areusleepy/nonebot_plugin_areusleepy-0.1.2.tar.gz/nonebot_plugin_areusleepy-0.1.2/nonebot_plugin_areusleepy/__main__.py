# coding: utf-8

# --- 导入模块

from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Event as BaseEvent, Message
from nonebot import get_plugin_config, get_bot
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot_plugin_apscheduler import scheduler
from nonebot.log import logger

import requests
from urllib.parse import urljoin

from .config import Config

# --- 获取配置

config: Config = get_plugin_config(Config)

# --- 处理函数


def get_data(base_url: str, retries: int = config.sleepy_retries) -> tuple[bool, (dict | str)]:
    '''
    请求 api 获取数据

    :param base_url: 服务地址
    :param retries: 重试次数
    :return bool: 是否成功
    :return dict | str: 返回数据 (如成功则为返回数据 (dict), 如失败则为错误信息 (str))
    '''
    success = False
    data = '未知错误'
    query_url = urljoin(base_url, '/query?version=1')  # version=1 -> 为未来 (可能) 的 Sleepy /query API 修改提供兼容

    while retries > 0:
        try:
            resp: requests.Response = requests.get(
                url=query_url,
                timeout=config.sleepy_timeout,
                allow_redirects=True
            )
            data = resp.json()
            success = True
            break
        except Exception as e:
            data = f'请求 {query_url} 出错: {e}'
            retries -= 1
    return success, data


def slice_text(text: str, max_length: int) -> str:
    '''
    截取指定长度文本

    :param text: 原文本
    :param max_length: 最大长度

    :return str: 处理后文本
    '''
    if (
        len(text) <= max_length or  # 文本长度小于指定截取长度
        max_length == 0  # 截取长度设置为 0 (禁用)
    ):
        return text
    else:
        return f'{text[:max_length-3]}...'


def parse_data(url: str, data: dict) -> str:
    '''
    处理返回的数据

    :param url: 网站地址
    :param data: /query 返回数据
    :return str: 处理后的消息文本
    '''
    devices = []
    n = '\n'
    if data.get('device'):
        raw_devices: dict = data.get('device')
        status_slice: int = data.get('device_status_slice')
        for i in raw_devices.keys():
            device: dict = raw_devices[i]
            devices.append(f'''
 - {device['show_name']}{f" ({i})" if config.sleepy_show_details else ""}
   * 状态: {"✅正在线上 Hi~ o(*￣▽￣*)ブ" if device['using'] else "❌离线 /(ㄒoㄒ)/~~"}
   * 应用: {slice_text(device['app_name'], status_slice)}
'''[1:-1])
    ret = f'''
👋你好 {url}

👀 在线状态
状态: {data['info']['name']}{f" ({data['status']})" if config.sleepy_show_details else ""}
详细信息: {data['info']['desc']}

💻 设备状态
{n.join(devices) if devices else '无'}

⏱ 最后更新: {data['last_updated']}{f" ({data['timezone']})" if config.sleepy_show_details else ""}
'''[1:-1]
    return ret

# --- 定义命令


rusleepy = on_command(
    cmd=config.sleepy_command
)


@rusleepy.handle()
async def handle_status(msg: Message = CommandArg()):
    '''
    处理 /sleepy (默认) 命令
    '''    # 获取参数
    query_url = msg.extract_plain_text().strip() or config.sleepy_url
    
    # 提示获取中
    if config.sleepy_prompt_loading:
        await rusleepy.send(f'正在从 {query_url} 获取状态, 请稍候...')

    success, data = get_data(query_url)
    if success:
        # 成功 -> 处理数据
        try:
            # 确保 data 是 dict 类型
            if isinstance(data, dict):
                parsed = parse_data(query_url, data)
            else:
                parsed = f'数据格式错误: {data}'
        except Exception as e:
            parsed = f'处理状态信息失败: {e}'
        await rusleepy.send(parsed)
    else:
        # 失败 -> 返回错误
        await rusleepy.send(f'获取状态信息失败: {data}')


# --- 定时任务功能

async def send_scheduled_status():
    '''
    定时发送状态信息
    '''
    if not config.sleepy_scheduler_enabled:
        return
    
    # 获取状态数据
    query_url = config.sleepy_url
    success, data = get_data(query_url)
    
    if not success:
        logger.error(f'定时任务获取状态失败: {data}')
        return
    
    # 确保 data 是 dict 类型
    if not isinstance(data, dict):
        logger.error(f'定时任务获取到的数据格式错误: {data}')
        return
    
    try:
        parsed = parse_data(query_url, data)
        message = f'📅 定时状态推送\n\n{parsed}'
    except Exception as e:
        logger.error(f'定时任务处理状态信息失败: {e}')
        return
    
    # 获取机器人实例
    try:
        bot = get_bot()
    except Exception as e:
        logger.error(f'获取机器人实例失败: {e}')
        return
    
    # 向配置的群组发送消息
    for group_id in config.sleepy_scheduler_groups:
        try:
            await rusleepy.send(group_id=int(group_id), message=message)
            logger.info(f'定时状态已发送到群组: {group_id}')
        except Exception as e:
            logger.error(f'向群组 {group_id} 发送定时状态失败: {e}')


# 注册定时任务
if config.sleepy_scheduler_enabled:
    scheduler.add_job(
        send_scheduled_status,
        "cron",
        id="sleepy_scheduled_status",
        **{k: v for k, v in zip(
            ["second", "minute", "hour", "day", "month", "day_of_week"],
            config.sleepy_scheduler_cron.split()
        ) if v != "*"},
        misfire_grace_time=60,
        replace_existing=True
    )
    logger.info(f'定时任务已启用，Cron 表达式: {config.sleepy_scheduler_cron}')
