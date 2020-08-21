import kokkoro
from kokkoro.bot import get_bot, get_scheduler

if kokkoro.config.BOT_TYPE != "tomon":
    kkr_scheduler = get_scheduler()
    kkr_scheduler.start()

kkr_bot = get_bot()
kkr_bot.kkr_run()
