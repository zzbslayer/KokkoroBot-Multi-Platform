import os
import discord
from PIL import Image
from io import BytesIO

from kokkoro import log, config
logger = log.new_logger('KokkoroBot', config.LOG_LEVEL)

import kokkoro
from kokkoro.msg_handler import handle_message
from kokkoro import util
from kokkoro.discord_adaptor import DiscordImage

class KokkoroBot(discord.Client):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        for module_name in self.config.MODULES_ON:
            util.load_modules(
                os.path.join(os.path.dirname(__file__), 'modules', module_name),
                f'kokkoro.modules.{module_name}')

    async def on_ready(self):
        kokkoro.logger.info(f'Logged on as {self.user}')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        if message.guild.id not in config.ENABLED_GUILD:
            return

        kokkoro.logger.debug(f'Receive message:{message.content}')
        kokkoro.logger.debug(f'{message}')
        if message.content == 'ping':
            await message.channel.send('pong')

        await handle_message(self, message)

    async def send(self, ctx:discord.Message, msg, at_sender=False):
        if isinstance(msg, DiscordImage):
            if msg.type == DiscordImage.LOCAL_IMAGE:
                await self._send_local_img(ctx.channel, path=msg.img)
            elif msg.type == DiscordImage.REMOTE_IMAGE:
                await self._send_remote_img(ctx.channel, url=msg.img, filename=msg.filename)
            elif msg.type == DiscordImage.PIL_IMAGE:
                await self._send_pil_img(ctx.channel, img=msg.img, filename=msg.filename)
            return

        if at_sender:
            msg = f'{msg} <@{ctx.author.id}>'
        await ctx.channel.send(msg)

    async def _send_remote_img(self, channel, url, filename="image.png"):
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url)
            with BytesIO(r) as fp:
                await channel.send(file=discord.File(fp=fp, filename=filename))

    async def _send_local_img(self, channel, path):
        await channel.send(file=discord.File(path))

    async def _send_pil_img(self, channel, img:Image, filename="image.png"):
        with BytesIO() as fp:
            img.save(fp, format='PNG')
            fp.seek(0)
            await channel.send(file=discord.File(fp=fp, filename=filename))

    def run(self):
        super().run(self.config.DISCORD_TOKEN)

kkr_bot = KokkoroBot(config)

def get_bot() -> KokkoroBot:
    return kkr_bot