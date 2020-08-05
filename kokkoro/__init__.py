from kokkoro import log, config
logger = log.new_logger('KokkoroBot', config.LOG_LEVEL)

from kokkoro.common_interface import KokkoroBot

def _init() -> KokkoroBot:
    if config.BOT_TYPE == "discord":
        from kokkoro import discord
        return discord.get_bot()
    elif config.BOT_TYPE == "telegram":
        raise NotImplementedError
    else:
        raise NotImplementedError

kkr_bot: KokkoroBot = _init()

def get_bot() -> KokkoroBot:
    return kkr_bot

