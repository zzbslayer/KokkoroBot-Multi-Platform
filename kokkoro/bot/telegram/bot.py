import asyncio
from io import BytesIO
import httpx

from aiogram import Bot, Dispatcher, executor
from aiogram.types.input_file import InputFile
from aiogram.types import Message

import kokkoro
from kokkoro.service import BroadcastTag
from kokkoro.common_interface import KokkoroBot, SupportedMessageType, EventInterface
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.typing import overrides, Figure, Image, List

from .telegram_adaptor import TelegramEvent

class KokkoroTelegramBot(KokkoroBot):
    def __init__(self, config):
        self.config = config
        super().kkr_load_modules(self.config) # KokkoroBot init
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop) # patch for telegram
        self.raw_bot = Bot(config.bot.telegram.TELEGRAM_TOKEN)
        self.dp = Dispatcher(self.raw_bot)

        async def tg_msg_handler(raw_event: Message):
            await self.kkr_on_message(raw_event)

        self.dp.register_message_handler(tg_msg_handler)

    @overrides(KokkoroBot)
    def kkr_event_adaptor(self, raw_event:Message) -> EventInterface:
        return TelegramEvent(raw_event)
        

    @overrides(KokkoroBot)
    async def kkr_send(self, ev: TelegramEvent, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        if isinstance(msg, str):
            await self._send_text(ev.get_group_id(), msg, at_sender=at_sender)
        elif isinstance(msg, ResImg):
            if kokkoro.config.RES_PROTOCOL == 'http':
                await self._send_remote_img(ev.get_group_id(), msg, filename=filename)
            elif kokkoro.config.RES_PROTOCOL == 'file':
                await self._send_local_img(ev.get_group_id(), path=msg.path)
            else:
                raise NotImplementedError
        elif isinstance(msg, RemoteResImg):
            await self._send_remote_img(ev.get_group_id(), url=msg.url, filename=filename)
        elif isinstance(msg, Image.Image):
            await self._send_pil_img(ev.get_group_id(), msg, filename=filename)
        elif isinstance(msg, Figure):
            await self._send_matplotlib_fig(ev.get_group_id(), msg, filename=filename)
        else:
            raise NotImplementedError

    async def _send_text(self, cid, msg, at_sender=False, parse_mode='Markdown'):
        await self.raw_bot.send_message(cid, msg, parse_mode=parse_mode)


    async def _send_remote_img(self, cid, url, filename="image.png"):
        ev = ev.get_raw_event()
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            with BytesIO(r.content) as fp:
                await self.raw_bot.send_photo(cid, photo=InputFile(fp, filename=filename))

    async def _send_local_img(self, cid, path, filename="image.png"):
        await self.raw_bot.send_photo(cid, photo=InputFile(path, filename=filename))

    async def _send_pil_img(self, cid, img:Image.Image, filename="image.png"):
        with BytesIO() as fp:
            img.save(fp, format='PNG')
            fp.seek(0)
            await self.raw_bot.send_photo(cid, photo=InputFile(fp, filename=filename))
        
    async def _send_matplotlib_fig(self, cid, fig:Figure, filename="image.png"):
        with BytesIO() as fp:
            fig.savefig(fp, format='PNG')
            fp.seek(0)
            await self.raw_bot.send_photo(cid, photo=InputFile(fp, filename=filename))
    
    @overrides(KokkoroBot)
    async def kkr_send_by_group(self, gid, msg: SupportedMessageType, tag=BroadcastTag.default, filename="image.png"):
        raise NotImplementedError

    @overrides(KokkoroBot)
    def get_groups(self):
        raise NotImplementedError
    
    @overrides(KokkoroBot)
    def kkr_at(self, uid, parse_mode='Markdown'):
        return f'[inline mention of a user](tg://user?id={uid})'

    @overrides(KokkoroBot)
    def kkr_run(self):
        executor.start_polling(self.dp, skip_updates=True)
    