import discord

import kokkoro
from kokkoro.msg_handler import handle_message
from kokkoro import config

class KokkoroBot(discord.Client):
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
