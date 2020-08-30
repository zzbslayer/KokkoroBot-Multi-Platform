import asyncio

from kokkoro import config

kkr_bot = None

def get_bot():
    global kkr_bot
    from kokkoro.bot.tomon.bot import KokkoroTomonBot 
    if kkr_bot == None:
        kkr_bot = KokkoroTomonBot(config)
    return kkr_bot

scheduler_loop = asyncio.new_event_loop()
def get_scheduler_loop():
    return scheduler_loop