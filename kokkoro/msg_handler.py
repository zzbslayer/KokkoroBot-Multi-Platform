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
        # coupleness
        raise NotImplementedError

    def get_param(self) -> BaseParameter: 
        # Custom parameter of trigger
        raise NotImplementedError
    def get_raw_event(self):
        # coupleness
        raise NotImplementedError

from kokkoro.discord_adaptor import DiscordEvent

def event_adaptor(raw_event) -> EventInterface:
    return DiscordEvent(raw_event)

async def handle_message(bot, raw_event: discord.Message):
    kokkoro.logger.debug(f'Searching for Message Handler...')
    ev = event_adaptor(raw_event)
    for t in trigger.chain:
        sf = t.find_handler(ev)
        if sf:
            trigger_name = t.__class__.__name__
            break

    if not sf:
        kokkoro.logger.debug(f'Message "{ev.get_id()}" triggered nothing')
        return  # triggered nothing.
    sf.sv.logger.info(f'Message {ev.get_id()} triggered {sf.__name__} by {trigger_name}.')

    if sf.only_to_me and not util.only_to_me(ev):
        return  # not to me, ignore.

    if not sf.sv._check_all(ev):
        return  # permission denied.

    try:
        await sf.func(bot, ev)
    except Exception as e:
        sf.sv.logger.error(f'{type(e)} occured when {sf.__name__} handling message {ev.get_id()}.')
        sf.sv.logger.exception(e)