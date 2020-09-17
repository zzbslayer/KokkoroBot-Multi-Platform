from kokkoro import config

kkr_bot = None

def get_bot():
    global kkr_bot
    if kkr_bot == None:
        from kokkoro.bot.wechat_enterprise.bot import KokkoroWechatEpBot
        kkr_bot = KokkoroWechatEpBot(config)
    return kkr_bot