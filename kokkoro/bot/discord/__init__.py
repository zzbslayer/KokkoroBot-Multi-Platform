from kokkoro import config

kkr_bot = None

def get_bot():
    global kkr_bot
    from kokkoro.bot.discord.bot import KokkoroDiscordBot 
    if kkr_bot == None:
        kkr_bot = KokkoroDiscordBot(config)
    return kkr_bot

