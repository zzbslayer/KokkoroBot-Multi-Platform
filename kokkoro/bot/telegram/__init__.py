import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

from kokkoro import config

kkr_bot = None

def get_bot():
    global kkr_bot
    from kokkoro.telegram.bot import KokkoroTelegramBot 
    if kkr_bot == None:
        kkr_bot = KokkoroTelegramBot(config)
    
    return kkr_bot
