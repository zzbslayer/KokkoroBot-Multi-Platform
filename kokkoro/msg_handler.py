import discord
import kokkoro
from kokkoro import trigger, util
from kokkoro.trigger import BaseParameter

class EventInterface:
    def get_id(self):
        raise NotImplementedError
    def get_author_id(self):
        raise NotImplementedError
    def get_group_id(self):
        raise NotImplementedError
    def get_content(self) -> str:
        raise NotImplementedError
    def get_mentions(self):
        raise NotImplementedError

    def get_param(self) -> BaseParameter: 
        # Custom parameter of trigger
        raise NotImplementedError
    def get_raw_event(self):
        # Call this function means the business is coupling with the infrastructure
        raise NotImplementedError

from kokkoro.discord_adaptor import DiscordEvent

async def handle_message(bot, msg: discord.Message):
    kokkoro.logger.debug(f'Searching for Message Handler...')
    ev = DiscordEvent(msg, None)
    for t in trigger.chain:
        sf = t.find_handler(ev)
        if sf:
            trigger_name = t.__class__.__name__
            break

    if not sf:
        kokkoro.logger.debug(f'Message "{msg.id}" triggered nothing')
        return  # triggered nothing.
    sf.sv.logger.info(f'Message {msg.id} triggered {sf.__name__} by {trigger_name}.')

    if sf.only_to_me and not util.only_to_me(msg):
        return  # not to me, ignore.

    if not sf.sv._check_all(ev):
        return  # permission denied.

    try:
        await sf.func(bot, ev)
    except Exception as e:
        sf.sv.logger.error(f'{type(e)} occured when {sf.__name__} handling message {msg.id}.')
        sf.sv.logger.exception(e)