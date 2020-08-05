import os
import discord
from PIL import Image
from io import BytesIO
import httpx
from typing import Union

import kokkoro
from kokkoro.typing import overrides
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.discord.discord_adaptor import *
from kokkoro.common_interface import KokkoroBot, SupportedMessageType, EventInterface

def message_preprocess(msg: Union[ResImg, RemoteResImg, Image.Image, str]):
    if isinstance(msg, ResImg) or isinstance(msg, RemoteResImg):
        msg = res_adaptor(msg)
    elif isinstance(msg, Image.Image):
        msg = pil_image(img, filename=filename)
    

class KokkoroDiscordBot(discord.Client, KokkoroBot):
    def __init__(self, config):
        super().__init__() # discord.Client init
        self.config = config
        super().kkr_load_modules(self.config) # KokkoroBot init

    async def on_ready(self):
        kokkoro.logger.info(f'Logged on as {self.user}')

    async def on_message(self, raw_event):
        await super().kkr_on_message(raw_event)

    @overrides(KokkoroBot)
    def kkr_event_adaptor(self, raw_event:discord.Message) -> EventInterface:
        return DiscordEvent(raw_event)

    @overrides(KokkoroBot)
    async def kkr_send(self, ev: DiscordEvent, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        # Convert msg to DiscordImage
        msg = message_adaptor(msg)

        if isinstance(msg, DiscordImage):
            if msg.type == DiscordImage.LOCAL_IMAGE:
                await self._send_local_img(ev.get_channel(), path=msg.img)
            elif msg.type == DiscordImage.REMOTE_IMAGE:
                await self._send_remote_img(ev.get_channel(), url=msg.img, filename=msg.filename)
            elif msg.type == DiscordImage.PIL_IMAGE:
                await self._send_pil_img(ev.get_channel(), img=msg.img, filename=msg.filename)
            return

        if at_sender:
            msg = f'{msg} <@{ev.get_author_id()}>'
        await ev.get_channel().send(msg)

    @overrides(KokkoroBot)
    def kkr_run(self):
        super().run(self.config.discord.DISCORD_TOKEN) # discord_Client run
    
    async def _send_remote_img(self, channel, url, filename="image.png"):
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            with BytesIO(r) as fp:
                await channel.send(file=discord.File(fp=fp, filename=filename))

    async def _send_local_img(self, channel, path):
        await channel.send(file=discord.File(path))

    async def _send_pil_img(self, channel, img:Image.Image, filename="image.png"):
        with BytesIO() as fp:
            img.save(fp, format='PNG')
            fp.seek(0)
            await channel.send(file=discord.File(fp=fp, filename=filename))

kkr_bot = None

def get_bot():
    global kkr_bot
    if kkr_bot == None:
        kkr_bot = KokkoroDiscordBot(kokkoro.config)
    return kkr_bot

