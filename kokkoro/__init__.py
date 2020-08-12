from kokkoro import log, config
logger = log.new_logger('KokkoroBot', config.LOG_LEVEL)
from kokkoro.common_interface import KokkoroBot
from quart import Quart

def _init() -> KokkoroBot:
    if config.BOT_TYPE == "discord":
        from kokkoro import discord
        return discord.get_bot()
    elif config.BOT_TYPE == "telegram":
        from kokkoro import telegram
        return telegram.get_bot()
    elif config.BOT_TYPE == "wechat_enterprise":
        from kokkoro import wechat_enterprise
        return wechat_enterprise.get_bot()
    else:
        raise NotImplementedError

kkr_bot: KokkoroBot = _init()

def get_bot() -> KokkoroBot:
    return kkr_bot

def _quart_init():
    if config.BOT_TYPE == "wechat_enterprise":
        return kkr_bot.app
    else:
        return Quart(__name__)
        
quart_app : Quart = _quart_init()

def get_app() -> Quart:
    return quart_app

