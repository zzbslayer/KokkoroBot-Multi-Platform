from kokkoro.util import FreqLimiter
from kokkoro.common_interface import EventInterface

from .. import chara
from . import sv

lmt = FreqLimiter(5)

@sv.on_suffix(('是谁', '是誰'))
@sv.on_prefix(('谁是', '誰是'))
async def whois(bot, ev: EventInterface):
    uid = ev.get_author_id
    if not lmt.check(uid):
        await bot.kkr_send(ev, f'兰德索尔花名册冷却中(剩余 {int(lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    lmt.start_cd(uid)

    name = ev.get_param().remain
    if not name:
        await bot.kkr_send(ev, '请发送"谁是"+别称，如"谁是霸瞳"')
        return
    id_ = chara.name2id(name)
    confi = 100
    guess = False
    if id_ == chara.UNKNOWN:
        id_, guess_name, confi = chara.guess_id(name)
        guess = True
    c = chara.fromid(id_)
    
    if guess:
        lmt.start_cd(uid, 120)
        msg = f'兰德索尔似乎没有叫"{name}"的人...\n角色别称补全计划: github.com/Ice-Cirno/HoshinoBot/issues/5'
        await bot.kkr_send(ev, msg)
        msg = f'\n您有{confi}%的可能在找{guess_name} '
        await bot.kkr_send(ev, msg)

    if confi > 60:
        await bot.kkr_send(ev, c.icon)
        await bot.kkr_send(ev, c.name, at_sender=True)
