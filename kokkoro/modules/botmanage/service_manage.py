from functools import cmp_to_key

from argparse import ArgumentParser

from kokkoro import priv
from kokkoro.service import Service, BoradcastService
from kokkoro.common_interface import EventInterface, KokkoroBot

PRIV_TIP = f'群员={priv.NORMAL} GameMaster={priv.SUPERUSER}'

sv = Service('service_management',use_priv=priv.ADMIN, manage_priv=priv.SUPERUSER, visible=False)

def svs_to_msg(svs, gid, verbose_all, only_hidden, bc=False):
    msg = [f"群{gid}推送服务一览："] if bc else [f"群{gid}服务一览："]
    svs = map(lambda sv: (sv, sv.check_enabled(gid)), svs)
    key = cmp_to_key(lambda x, y: (y[1] - x[1]) or (-1 if x[0].name < y[0].name else 1 if x[0].name > y[0].name else 0))
    svs = sorted(svs, key=key)
    for sv, on in svs:
        if verbose_all or (sv.visible ^ only_hidden):
            x = '○' if on else '×'
            if bc:
                msg.append(f"|{x}| {sv.name} | {sv.broadcast_tag}")
            else:
                msg.append(f"|{x}| {sv.name}")
    return '\n'.join(msg)

@sv.on_prefix(('lssv','服务列表', '功能列表'), only_to_me=False)
async def lssv(bot: KokkoroBot, ev: EventInterface):
    parser = ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-i', '--invisible', action='store_true')
    parser.add_argument('-g', '--group', type=int, default=0)
    args = parser.parse_args(ev.get_param().remain)
    
    verbose_all = args.all
    only_hidden = args.invisible
    if ev.get_author_id() in bot.config.SUPER_USER:
        gid = args.group or ev.get_group_id()
        if not gid:
            await bot.kkr_send(ev, 'Usage: -g|--group <group_id> [-a|--all]')
            return
    else:
        gid = ev.get_group_id()

    msg = svs_to_msg(Service.get_loaded_services().values(), gid, verbose_all, only_hidden)
    await bot.kkr_send(ev, msg)

@sv.on_prefix(('lsbcsv','推送服务列表', '推送列表'), only_to_me=False)
async def lsbcsv(bot: KokkoroBot, ev: EventInterface):
    parser = ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-i', '--invisible', action='store_true')
    parser.add_argument('-g', '--group', type=int, default=0)
    args = parser.parse_args(ev.get_param().remain)
    
    verbose_all = args.all
    only_hidden = args.invisible
    if ev.get_author_id() in bot.config.SUPER_USER:
        gid = args.group or ev.get_group_id()
        if not gid:
            await bot.kkr_send(ev, 'Usage: -g|--group <group_id> [-a|--all]')
            return
    else:
        gid = ev.get_group_id()

    msg = svs_to_msg(BoradcastService.get_loaded_bc_services().values(), gid, verbose_all, only_hidden, bc=True)
    await bot.kkr_send(ev, msg)


@sv.on_prefix(('enable', '启用', '开启', '打开'), only_to_me=False)
async def enable_service(bot:KokkoroBot, ev):
    await switch_service(bot, ev, turn_on=True)

@sv.on_prefix(('disable', '禁用', '关闭'), only_to_me=False)
async def disable_service(bot:KokkoroBot, ev):
    await switch_service(bot, ev, turn_on=False)

async def switch_service(bot, ev:EventInterface , turn_on:bool):
    action_tip = '启用' if turn_on else '禁用'

    names = ev.get_param().remain.split()
    if not names:
        await bot.kkr_send(ev, f"空格后接要{action_tip}的服务名", at_sender=True)
        return
    group_id = ev.get_group_id()
    svs = Service.get_loaded_services()
    succ, notfound = [], []
    for name in names:
        if name in svs:
            sv = svs[name]
            u_priv = priv.get_user_priv(ev.get_author())
            if u_priv >= sv.manage_priv:
                sv.set_enable(group_id) if turn_on else sv.set_disable(group_id)
                succ.append(name)
            else:
                try:
                    await bot.kkr_send(ev, f'权限不足！{action_tip}{name}需要：{sv.manage_priv}，您的：{u_priv}\n{PRIV_TIP}', at_sender=True)
                except:
                    pass
        else:
            notfound.append(name)
    msg = []
    if succ:
        msg.append(f'已{action_tip}服务：' + ', '.join(succ))
    if notfound:
        msg.append('未找到服务：' + ', '.join(notfound))
    if msg:
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)