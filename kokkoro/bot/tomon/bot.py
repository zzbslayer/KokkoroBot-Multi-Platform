import asyncio
import nest_asyncio
from tomon_sdk import bot
from requests_toolbelt import MultipartEncoder

import kokkoro
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.typing import overrides, Image, Figure
from kokkoro.bot.tomon.tomon_adaptor import *
from kokkoro.bot.tomon.tomon_util import at

nest_asyncio.apply()
loop = asyncio.get_event_loop()

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
            # multipart_data = MultipartEncoder(
            #     fields = {
            #         'images': (filename, open(msg.path, 'rb')),
            #         'payload_json': '{"content":"test_image_upload"}'
            #     }
            # )
            if kokkoro.config.RES_PROTOCOL == 'http':
                raise NotImplementedError
            elif kokkoro.config.RES_PROTOCOL == 'file':
                await self._bot.api().route(f'/channels/{channel_id}/messages').post(data={}, files=[msg.path])
            else:
                raise NotImplementedError
        elif isinstance(msg, RemoteResImg):
            raise NotImplementedError
        elif isinstance(msg, Image.Image):
            raise NotImplementedError
        elif isinstance(msg, Figure):
            raise NotImplementedError
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