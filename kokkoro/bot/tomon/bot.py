import asyncio
import nest_asyncio
from tomon_sdk import bot

import kokkoro
from kokkoro.bot.tomon.tomon_adaptor import *
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.typing import overrides, Image, Figure

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

    @overrides(KokkoroBot)
    def kkr_event_adaptor(self, raw_event) -> TomonEvent:
        return TomonEvent(raw_event)
    
    @overrides(KokkoroBot)
    async def kkr_send(self, ev: TomonEvent, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        channel_id = ev.get_channel_id()
        
        if isinstance(msg, str):
            payload = {}
            payload['content'] = msg
        elif isinstance(msg, ResImg):
            raise NotImplementedError
        elif isinstance(msg, RemoteResImg):
            raise NotImplementedError
        elif isinstance(msg, Image.Image):
            raise NotImplementedError
        elif isinstance(msg, Figure):
            raise NotImplementedError

        await self._bot.api().route('/channels/{}/messages'.format(channel_id)).post(data=payload)


    @overrides(KokkoroBot)
    def kkr_run(self):
        async def run():
            await self._bot.start(kokkoro.config.bot.tomon.TOMON_TOKEN)
        
        loop.run_until_complete(run())

    @overrides(KokkoroBot)
    def kkr_at(self, uid):
        return f'<@{uid}>'
