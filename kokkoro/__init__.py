from kokkoro import log, config
logger = log.new_logger('KokkoroBot', config.LOG_LEVEL)

from kokkoro import discord
from kokkoro.common_interface import KokkoroBot

def _init() -> KokkoroBot:
    if config.BOT_TYPE == "discord":
        return discord.get_bot()
    else:
        raise NotImplementedError

kkr_bot: KokkoroBot = _init()

def get_bot() -> KokkoroBot:
    return kkr_bot

