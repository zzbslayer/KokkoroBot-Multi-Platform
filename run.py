import kokkoro
from kokkoro import config

import asyncio
import threading

kkr_bot = kokkoro.get_bot()
quart_app = kokkoro.get_app()

from kokkoro import web

def loop_run():
    async def kkr_start_task():
        await kkr_bot.kkr_async_run()
    async def quart_start_task():
        await quart_app.run_task(host='0.0.0.0', port=5001, debug=True)

    asyncio.get_child_watcher()

    loop = asyncio.get_event_loop()
    loop.create_task(kkr_start_task())
    loop.create_task(quart_start_task())

    def run_it_forever(loop):
        loop.run_forever()

    thread = threading.Thread(target=run_it_forever, args=(loop,))
    thread.start()

def main():
    if config.ENABLE_WEB:
        if config.BOT_TYPE == "wechat_enterprise":
            kkr_bot.kkr_run()
        else:
            loop_run()
    else:
        kkr_bot.kkr_run()

main()
