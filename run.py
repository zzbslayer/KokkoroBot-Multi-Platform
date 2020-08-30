import asyncio
from threading import Thread

import kokkoro
from kokkoro.bot import get_bot, get_scheduler

if kokkoro.config.BOT_TYPE != "tomon":
    kkr_scheduler = get_scheduler()
    kkr_scheduler.start()
else:
    def run_scheduler():
        kokkoro.logger.info("scheduler thread running")
        from kokkoro.bot.tomon import get_scheduler_loop
        scheduler_loop = get_scheduler_loop()
        kkr_scheduler = get_scheduler(scheduler_loop)
        kkr_scheduler.start()
        scheduler_loop.run_forever()

    t = Thread(target=run_scheduler)
    t.start()
    
kkr_bot = get_bot()
kkr_bot.kkr_run()
