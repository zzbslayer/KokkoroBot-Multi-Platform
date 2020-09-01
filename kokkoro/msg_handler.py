import kokkoro
from kokkoro import trigger, util, config, priv
from kokkoro.platform_patch import preprocess_message

async def handle_message(bot, ev):
    kokkoro.logger.debug(f'Receive message:{ev.get_content()}')
    if ev.get_content() in [None, ""]:
        return # ignore 
        
    to_me = preprocess_message(ev)
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

    if sf.only_to_me and not to_me:
        return  # not to me, ignore.

    gid = ev.get_group_id()
    if not sf.sv.check_enabled(gid):
        await bot.kkr_send(ev, f'服务 <{sf.sv.name}> 未启用，请呼叫管理员开启服务 0x0 ', at_sender=True)
        return
    if priv.check_block_group(gid): # not used now
        return
    if not priv.check_priv(ev.get_author(), sf.sv.use_priv): # permission denied
        await bot.kkr_send(ev, '权限不足 0x0 ', at_sender=True)
        return



    try:
        await sf.func(bot, ev)
    except Exception as e:
        sf.sv.logger.error(f'{type(e)} occured when {sf.__name__} handling message {ev.get_id()}.')
        sf.sv.logger.exception(e)