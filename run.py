import kokkoro
from kokkoro import config

import asyncio
import threading

kkr_bot = kokkoro.get_bot()
quart_app = kokkoro.get_app()

from kokkoro import web

async def kkr_start():
    await kkr_bot.kkr_run()
async def quart_start():
    await quart_app.run_task(host='0.0.0.0', port=5001, debug=True)

def run_it_forever(loop):
    loop.run_forever()

def loop_run():
    asyncio.get_child_watcher()

    loop = asyncio.get_event_loop()
    loop.create_task(kkr_start())
    loop.create_task(quart_start())

    thread = threading.Thread(target=run_it_forever, args=(loop,))
    thread.start()

if config.BOT_TYPE == "wechat_enterprise":
    kkr_bot.kkr_run()
else:
    loop_run()
