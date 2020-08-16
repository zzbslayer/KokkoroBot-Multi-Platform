import kokkoro
from kokkoro import trigger, util, config
from kokkoro.platform_patch import preprocess_message

async def handle_message(bot, ev):
    kokkoro.logger.debug(f'Receive message:{ev.get_content()}')
    
    preprocess_message(ev)
    kokkoro.logger.debug(f'Searching for Message Handler...')
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