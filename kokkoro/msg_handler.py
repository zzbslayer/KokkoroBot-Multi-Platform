import discord
import kokkoro
from kokkoro import trigger, utils

async def handle_message(bot, msg: discord.Message):
    kokkoro.logger.debug(f'Searching for Message Handler...')
    for t in trigger.chain:
        sf, param = t.find_handler(msg)
        if sf:
            trigger_name = t.__class__.__name__
            break

    if not sf:
        kokkoro.logger.debug(f'Message "{msg.id}" triggered nothing')
        return  # triggered nothing.
    sf.sv.logger.info(f'Message {msg.id} triggered {sf.__name__} by {trigger_name}.')

    if sf.only_to_me and not utils.only_to_me(msg):
        return  # not to me, ignore.

    #if not sf.sv._check_all(event):
    #    return  # permission denied.

    try:
        await sf.func(bot, msg, param)
    except Exception as e:
        sf.sv.logger.error(f'{type(e)} occured when {sf.__name__} handling message {event.message_id}.')
        sf.sv.logger.exception(e)