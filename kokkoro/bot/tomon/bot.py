import os
import asyncio
import nest_asyncio
from tomon_sdk import bot
from requests_toolbelt import MultipartEncoder
from io import BytesIO
import httpx

from random import choice
from string import ascii_letters

import kokkoro
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.typing import overrides, Image, Figure
from kokkoro.bot.tomon.tomon_adaptor import *
from kokkoro.bot.tomon.tomon_util import at

nest_asyncio.apply()
loop = asyncio.get_event_loop()

def rand_temp_file():
    rand_name = ''.join(choice(ascii_letters) for i in range(10)) + '.png'
    dst = os.path.join("/var/tmp/", rand_name)
    return dst

class KokkoroTomonBot(KokkoroBot):
    def __init__(self, config):
        self.config = config
        super().kkr_load_modules(self.config)

        def on_message(data):
            if data.get('e') == 'MESSAGE_CREATE':
                raw_event = data.get('d')
                if raw_event.get('author') == None:
                    return # ignore system msg
                loop.run_until_complete(self.kkr_on_message(raw_event))

        self._bot = bot.Bot()
        self._bot.on(bot.OpCodeEvent.DISPATCH, on_message)

    def get_raw_bot(self):
        return self._bot

    @overrides(KokkoroBot)
    def kkr_event_adaptor(self, raw_event) -> TomonEvent:
        return TomonEvent(raw_event)
    
    @overrides(KokkoroBot)
    async def kkr_send(self, ev: TomonEvent, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        channel_id = ev.get_channel_id()
        
        if isinstance(msg, str):
            payload = {}
            payload['content'] = msg
            await self._bot.api().route(f'/channels/{channel_id}/messages').post(data=payload)
        elif isinstance(msg, ResImg):
            if kokkoro.config.RES_PROTOCOL == 'http':
                async with httpx.AsyncClient() as client:
                    r = await client.get(url)
                    with BytesIO(r) as fp:
                        path=rand_temp_file()
                        with open(path,'wb') as temp: 
                            temp.write(fp.read())

                await self._bot.api().route(f'/channels/{channel_id}/messages').post(data={}, files=[path])

            elif kokkoro.config.RES_PROTOCOL == 'file':
                await self._bot.api().route(f'/channels/{channel_id}/messages').post(data={}, files=[msg.path])
            else:
                raise NotImplementedError
        elif isinstance(msg, RemoteResImg):
            async with httpx.AsyncClient() as client:
                r = await client.get(msg.url)
                with BytesIO(r) as fp:
                    path=rand_temp_file()
                    with open(path,'wb') as temp: 
                        temp.write(fp.read())

            await self._bot.api().route(f'/channels/{channel_id}/messages').post(data={}, files=[path])

        elif isinstance(msg, Image.Image):
            with BytesIO() as fp:
                msg.save(fp, format='PNG')
                fp.seek(0)
                path=rand_temp_file()
                with open(path,'wb') as temp: 
                    temp.write(fp.read())

            await self._bot.api().route(f'/channels/{channel_id}/messages').post(data={}, files=[path])
        elif isinstance(msg, Figure):
            with BytesIO() as fp:
                msg.savefig(fp, format='PNG')
                fp.seek(0)
                path=rand_temp_file()
                with open(path,'wb') as temp: 
                    temp.write(fp.read())

            await self._bot.api().route(f'/channels/{channel_id}/messages').post(data={}, files=[path])
        else:
            raise NotImplementedError

    @overrides(KokkoroBot)
    def kkr_run(self):
        async def run():
            await self._bot.start(kokkoro.config.bot.tomon.TOMON_TOKEN)
        
        loop.run_until_complete(run())

    @overrides(KokkoroBot)
    def kkr_at(self, uid):
        return at(uid)
    
    @overrides(KokkoroBot)
    def get_groups(self) -> List[TomonGroup]:
        raw_groups = asyncio.run(self._bot.api().route(f'/users/@me/guilds').get())
        return TomonGroup.from_raw_groups(raw_groups)