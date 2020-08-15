from kokkoro.bot import get_bot, get_scheduler

kkr_scheduler = get_scheduler()
kkr_bot = get_bot()

kkr_scheduler.start()
kkr_bot.kkr_run()
