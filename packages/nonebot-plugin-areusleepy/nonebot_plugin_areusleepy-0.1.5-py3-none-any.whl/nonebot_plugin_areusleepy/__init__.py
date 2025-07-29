from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

# =========== require dependency ============
require("nonebot_plugin_alconna")
require("nonebot-plugin-apscheduler")

from . import __main__ as __main__

from .config import Config

__version__ = "0.1.5"
__plugin_meta__ = PluginMetadata(
    name="AreYouSleepy",
    description="基于 sleepy-project/sleepy 项目的状态查询插件！",
    usage="/areusleepy [url]",
    type="application",
    homepage="https://github.com/Murasame-Dev/nonebot-plugin-areusleepy",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna"
        "nonebot-plugin-apscheduler"
    ),
    config=Config,
)

config = get_plugin_config(Config)
