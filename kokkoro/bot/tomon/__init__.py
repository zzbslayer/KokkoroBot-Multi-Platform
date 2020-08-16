from kokkoro import config

kkr_bot = None

def get_bot():
    global kkr_bot
    from kokkoro.bot.tomon.bot import KokkoroTomonBot 
    if kkr_bot == None:
        kkr_bot = KokkoroTomonBot(config)
    return kkr_bot
