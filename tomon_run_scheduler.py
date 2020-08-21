import asyncio
import kokkoro
from kokkoro.bot import get_bot, get_scheduler

kkr_scheduler = get_scheduler()
kkr_bot = get_bot() # load modules
kkr_bot._bot.api()._token = kokkoro.config.bot.tomon.TOMON_TOKEN

kkr_scheduler.start()

try:
    loop = asyncio.get_event_loop()
    loop.run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
