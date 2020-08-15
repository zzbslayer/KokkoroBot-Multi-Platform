from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kokkoro.common_interface import KokkoroBot
from kokkoro import config

def _init_bot() -> KokkoroBot:
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

kkr_bot: KokkoroBot = None
kkr_scheduler: AsyncIOScheduler = None

def get_scheduler() -> AsyncIOScheduler:
    global kkr_scheduler
    if kkr_scheduler == None:
        kkr_scheduler = AsyncIOScheduler()
    return kkr_scheduler

def get_bot() -> KokkoroBot:
    global kkr_bot
    if kkr_bot == None:
        kkr_bot = _init_bot()
    return kkr_bot

