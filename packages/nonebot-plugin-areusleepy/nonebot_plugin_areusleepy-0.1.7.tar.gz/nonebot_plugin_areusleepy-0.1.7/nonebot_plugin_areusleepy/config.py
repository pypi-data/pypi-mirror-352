from pydantic import BaseModel
from typing import List, Optional


class Config(BaseModel):
    # 基本配置
    sleepy_command: str = 'areusleepy'  # 触发命令
    sleepy_prompt_loading: bool = True  # 是否提示获取中
    sleepy_show_details: bool = False  # 是否显示详细信息

    # Sleepy 服务配置
    sleepy_url: str = 'https://sleepy-preview.wyf9.top'  # Sleepy 服务地址
    sleepy_timeout: float = 5.0  # 请求超时 (秒)
    sleepy_retries: int = 3  # 请求失败时的重试次数

    # 定时任务配置
    sleepy_scheduler_enabled: bool = False  # 是否启用定时任务
    sleepy_scheduler_cron: str = '0 9,21 * * *'  # Cron 表达式，默认每天 9:00 和 21:00
    sleepy_scheduler_groups: List[str] = []  # 推送的群组列表