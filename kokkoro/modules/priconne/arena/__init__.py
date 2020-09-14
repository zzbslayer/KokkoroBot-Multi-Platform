import re
import time
from collections import defaultdict

from kokkoro.util import concat_pic, FreqLimiter
from kokkoro.service import Service
from kokkoro.common_interface import *
from kokkoro import R, priv
import kokkoro

from .. import chara

sv = Service('pcr-arena', manage_priv=priv.SUPERUSER, enable_on_default=False)

from ..chara import Chara
from . import arena

lmt = FreqLimiter(5)

aliases = ('怎么拆', '怎么解', '怎么打', '如何拆', '如何解', '如何打', 'jjc查询', 'arena-query')
aliases_b = tuple('b' + a for a in aliases) + tuple('B' + a for a in aliases)
aliases_tw = tuple('台' + a for a in aliases)
aliases_jp = tuple('日' + a for a in aliases)

@sv.on_prefix(aliases)
async def arena_query(bot, ev):
    await _arena_query(bot, ev, region=1)

@sv.on_prefix(aliases_b)
async def arena_query_b(bot, ev):
    await _arena_query(bot, ev, region=2)

@sv.on_prefix(aliases_tw)
async def arena_query_tw(bot, ev):
    await _arena_query(bot, ev, region=3)

@sv.on_prefix(aliases_jp)
async def arena_query_jp(bot, ev):
    await _arena_query(bot, ev, region=4)


async def _arena_query(bot, ev: EventInterface, region: int):

    arena.refresh_quick_key_dic()
    uid = ev.get_author_id()

    if not lmt.check(uid):
        await bot.kkr_send(ev, '您查询得过于频繁，请稍等片刻', at_sender=True)
        return
    lmt.start_cd(uid)

    # 处理输入数据
    defen = ev.get_param().remain
    defen = re.sub(r'[?？，,_]', '', defen)
    defen, unknown = chara.roster.parse_team(defen)

    if unknown:
        _, name, score = chara.guess_id(unknown)
        if score < 70 and not defen:
            return  # 忽略无关对话
        msg = f'无法识别"{unknown}"' if score < 70 else f'无法识别"{unknown}" 您说的有{score}%可能是{name}'
        await bot.kkr_send(ev, msg)
        return
    if not defen:
        await bot.kkr_send(ev, '查询请发送"怎么拆+防守队伍"，无需+号', at_sender=True)
        return
    if len(defen) > 5:
        await bot.kkr_send(ev, '编队不能多于5名角色', at_sender=True)
        return
    if len(defen) < 5:
        await bot.kkr_send(ev, '由于数据库限制，少于5名角色的检索条件请移步pcrdfans.com进行查询', at_sender=True)
        return
    if len(defen) != len(set(defen)):
        await bot.kkr_send(ev, '编队中含重复角色', at_sender=True)
        return
    if any(chara.is_npc(i) for i in defen):
        await bot.kkr_send(ev, '编队中含未实装角色', at_sender=True)
        return
    if 1004 in defen:
        await bot.kkr_send(ev, '\n⚠️您正在查询普通版炸弹人\n※万圣版可用万圣炸弹人/瓜炸等别称', at_sender=True)

    # 执行查询
    sv.logger.info('Doing query...')
    res = await arena.do_query(defen, uid, region)
    sv.logger.info('Got response!')

    # 处理查询结果
    if res is None:
        await bot.kkr_send(ev, '查询出错，请联系维护组调教\n请先移步pcrdfans.com进行查询', at_sender=True)
        return
    if not len(res):
        await bot.kkr_send(ev, '抱歉没有查询到解法\n※没有作业说明随便拆 发挥你的想象力～★\n作业上传请前往pcrdfans.com', at_sender=True)
        return
    res = res[:min(6, len(res))]    # 限制显示数量，截断结果

    sv.logger.info('Arena generating picture...')
    atk_team = [ chara.gen_team_pic(entry['atk']) for entry in res ]
    atk_team = concat_pic(atk_team)
    sv.logger.info('Arena picture ready!')
    await bot.kkr_send(ev, atk_team)

    #     atk_team = '\n'.join(map(lambda entry: ' '.join(map(lambda x: f"{x.name}{x.star if x.star else ''}{'专' if x.equip else ''}" , entry['atk'])) , res)) # text version

    details = [ " ".join([
        f"赞{e['up']}+{e['my_up']}" if e['my_up'] else f"赞{e['up']}",
        f"踩{e['down']}+{e['my_down']}" if e['my_down'] else f"踩{e['down']}",
        e['qkey'],
        "你赞过" if e['user_like'] > 0 else "你踩过" if e['user_like'] < 0 else ""
    ]) for e in res ]

    defen = [ chara.fromid(x).name for x in defen ]
    defen = f"防守方【{' '.join(defen)}】"

    msg = [
        defen,
        f'已为骑士查询到以上进攻方案：',
        f'作业评价：',
        *details,
        '※发送"点赞/点踩"可进行评价'
    ]
    if region == 1:
        msg.append('※使用"b怎么拆"或"台怎么拆"可按服过滤')
    msg.append('Support by pcrdfans_com')

    sv.logger.debug('Arena sending result...')
    await bot.kkr_send(ev, '\n'.join(msg))
    sv.logger.debug('Arena result sent!')

@sv.on_prefix(('点赞', 'arena-like'))
async def arena_like(bot, ev):
    await _arena_feedback(bot, ev, 1)

@sv.on_prefix(('点踩', 'arena_dislike'))
async def arena_dislike(bot, ev):
    await _arena_feedback(bot, ev, -1)

rex_qkey = re.compile(r'^[0-9a-zA-Z]{5}$')
async def _arena_feedback(bot, ev: EventInterface, action:int):
    action_tip = '赞' if action > 0 else '踩'
    qkey = ev.get_param().remain
    if not qkey:
        await bot.kkr_send(ev, f'请发送"点{action_tip}+作业id"，如"点{action_tip}ABCDE"，不分大小写', at_sender=True)
        return
    if not rex_qkey.match(qkey):
        await bot.kkr_send(ev, f'您要点{action_tip}的作业id不合法', at_sender=True)
        return
    try:
        await arena.do_like(qkey, ev.get_author_id(), action)
    except KeyError:
        await bot.kkr_send(ev, '无法找到作业id！您只能评价您最近查询过的作业', at_sender=True)
    await bot.kkr_send(ev, '感谢您的反馈！', at_sender=True)
