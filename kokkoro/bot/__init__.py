from kokkoro.common_interface import KokkoroBot
from kokkoro import config

def _init() -> KokkoroBot:
    if config.BOT_TYPE == "discord":
        from kokkoro.bot import discord
        return discord.get_bot()
    elif config.BOT_TYPE == "telegram":
        from kokkoro.bot import telegram
        return telegram.get_bot()
    elif config.BOT_TYPE == "wechat_enterprise":
        from kokkoro.bot import wechat_enterprise
        return wechat_enterprise.get_bot()
    else:
        raise NotImplementedError

kkr_bot: KokkoroBot = _init()

def get_bot() -> KokkoroBot:
    return kkr_bot