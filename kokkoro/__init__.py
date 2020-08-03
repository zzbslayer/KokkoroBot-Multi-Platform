import os
import discord

import kokkoro
from kokkoro.msg_handler import handle_message
from kokkoro import config, log, util

logger = log.new_logger('KokkoroBot', config.LOG_LEVEL)

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

    def run(self):
        super().run(self.config.DISCORD_TOKEN)

kkr_bot = KokkoroBot(config)

def get_bot() -> KokkoroBot:
    return kkr_bot