import os
import discord
from PIL import Image
from matplotlib.figure import Figure
from io import BytesIO
import httpx

import kokkoro
from kokkoro.typing import overrides, Union
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.bot.discord.discord_adaptor import *
from kokkoro.bot.discord.discord_util import at
from kokkoro.common_interface import KokkoroBot, SupportedMessageType, EventInterface 

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

    async def _send_by_channel(self, channel, msg:SupportedMessageType, filename="image.png"):
        if isinstance(msg, ResImg):
            if kokkoro.config.RES_PROTOCOL == 'http':
                await self._send_remote_img(channel, url=msg.url, filename=filename)
            elif kokkoro.config.RES_PROTOCOL == 'file':
                await self._send_local_img(channel, path=msg.path)
            else:
                raise NotImplementedError
        elif isinstance(msg, RemoteResImg):
            await self._send_remote_img(channel, url=msg.url, filename=filename)
        elif isinstance(msg, Image.Image):
            await self._send_pil_img(channel, msg, filename=filename)
        elif isinstance(msg, Figure):
            await self._send_matplotlib_fig(channel, msg, filename=filename)
        elif isinstance(msg, str):
            await channel.send(msg)
        else:
            raise NotImplementedError


    @overrides(KokkoroBot)
    async def kkr_send(self, ev: DiscordEvent, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        if isinstance(msg, str) and at_sender:
            msg = f'{msg} <@{ev.get_author_id()}>'

        channel = ev.get_channel()
        await self._send_by_channel(channel, msg, filename)
        

    @overrides(KokkoroBot)
    async def kkr_send_by_group(self, gid, msg: SupportedMessageType, filename="image.png"):
        channel_name=kokkoro.config.bot.discord.BROADCAST_CHANNEL
        guild = self.get_guild(gid)
        channels = guild.channels
        for channel in channels:
            if channel.name == channel_name:
                await self._send_by_channel(channel, msg, filename=filename)
                return
        kokkoro.logger.warning(f"Guild <{guild.id}> doesn't contains channel named as <{channel_name}>")

    @overrides(KokkoroBot)
    def kkr_at(self, uid):
        return at(uid)

    @overrides(KokkoroBot)
    def kkr_run(self):
        super().run(self.config.bot.discord.DISCORD_TOKEN)

    @overrides(KokkoroBot)
    async def kkr_async_run(self):
        await super().start(self.config.bot.discord.DISCORD_TOKEN) # discord_Client start
    
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
        
    async def _send_matplotlib_fig(self, channel, fig:Figure, filename="image.png"):
        with BytesIO() as fp:
            fig.savefig(fp, format='PNG')
            fp.seek(0)
            await channel.send(file=discord.File(fp=fp, filename=filename))
