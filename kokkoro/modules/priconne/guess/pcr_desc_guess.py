from kokkoro.service import Service
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.modules.priconne import chara

import kokkoro
import os, random

from .. import _pcr_data
from .guess_helper import WinnerJudger, WinningCounter


sv = Service('pcr-desc-guess')

HINT_LIMIT = 5
DB_PATH = os.path.expanduser('~/.kokkoro/pcr_desc_guess_winning_counter.db')

winner_judger = WinnerJudger()

@sv.on_fullmatch(('猜描述排行榜', '猜描述群排行'))
async def description_guess_group_ranking(bot: KokkoroBot, ev: EventInterface):
    members = ev.get_members_in_group()
    gid = ev.get_group_id()
    uid = ev.get_author_id()

    card_winningcount_dict = {}
    winning_counter = WinningCounter(DB_PATH)
    for member in members:
        mid = member.get_id()
        if mid != uid:
            card_winningcount_dict[member.get_nick_name()] = winning_counter._get_winning_number(gid, mid)
    group_ranking = sorted(card_winningcount_dict.items(), key = lambda x:x[1], reverse = True)
    msg = '猜描述小游戏此群排行为:\n'
    for i in range(min(len(group_ranking), 10)):
        if group_ranking[i][1] != 0:
            msg += f'第{i+1}名: {group_ranking[i][0]}, 猜对次数: {group_ranking[i][1]}次\n'
    await bot.kkr_send(ev, msg.strip())

group_hints = {}
group_hint_cnt = {}

@sv.on_fullmatch(('猜描述', '猜角色', '猜人物'))
async def description_guess(bot: KokkoroBot, ev: EventInterface):
    try:
        gid = ev.get_group_id()
        if winner_judger.get_on_off_status(gid):
            await bot.kkr_send(ev, "此轮猜角色还没结束 0x0")
            return
        winner_judger.turn_on(gid)
        msg = f'猜猜这是哪位角色?\n※发送"角色提示"，可以得到更多信息~\n※回答时请加前缀 dg\n※示例：dg 可可萝'
        await bot.kkr_send(ev, msg)
        desc_lable = ['名字', '公会', '生日', '年龄', '身高', '体重', '血型', '种族', '喜好', '声优']
        desc_suffix = ['', '', '', '', 'cm', 'kg', '', '', '', '']
        index_list = list(range(1,10))
        random.shuffle(index_list)
        chara_id_list = list(_pcr_data.CHARA_DATA.keys())
        random.shuffle(chara_id_list)
        chara_id = chara_id_list[0]
        chara_desc_list = _pcr_data.CHARA_DATA[chara_id]
        winner_judger.set_result(gid, chara_id)
        # init
        group_hints[gid] = {
            'index_list': index_list,
            'desc_lable': desc_lable,
            'chara_desc_list': chara_desc_list,
            'desc_suffix': desc_suffix
        }
        group_hint_cnt[gid] = 0
        await hint(bot, ev)
    except Exception as e:
        winner_judger.turn_off(gid)
        raise e

@sv.on_fullmatch(('角色答案', '描述答案', '人物答案', 'desc-answer'))
async def avatar_guess(bot: KokkoroBot, ev: EventInterface):   
    gid = ev.get_group_id()
    if winner_judger.get_on_off_status(gid):
        correct_id = winner_judger.get_result(gid)
        c = chara.fromid(correct_id)
        msg =  f'正确答案是: {c.name}\n很遗憾，没有人答对~'
        await bot.kkr_send(ev, msg)
        await bot.kkr_send(ev, c.icon)

        winner_judger.turn_off(gid)


@sv.on_fullmatch(('描述提示', '人物提示', '角色提示'))
async def hint(bot: KokkoroBot, ev: EventInterface):
    gid = ev.get_group_id()
    if not winner_judger.get_on_off_status(gid):
        await bot.kkr_send(ev, '尚未开始猜角色0x0')
        return
    cnt = group_hint_cnt[gid]
    if cnt >= HINT_LIMIT:
        await bot.kkr_send(ev, '提示次数用完啦0x0\n输入"角色答案"查看答案')
        return
    hints = group_hints[gid]
    desc_index = hints['index_list'][cnt]
    await bot.kkr_send(ev, f'提示{cnt+1}/{HINT_LIMIT}:\n她的{hints["desc_lable"][desc_index]}是 {hints["chara_desc_list"][desc_index]}{hints["desc_suffix"][desc_index]}')
    group_hint_cnt[gid] += 1

@sv.on_prefix('dg')
async def on_input_chara_name(bot: KokkoroBot, ev: EventInterface):
    gid = ev.get_group_id()
    uid = ev.get_author_id()
    if winner_judger.get_on_off_status(gid):
        s = ev.get_param().remain
        cid = chara.name2id(s)
        correct_id = winner_judger.get_result(gid)
        if cid != chara.UNKNOWN and cid == winner_judger.get_result(gid) and winner_judger.get_winner(gid) == None:
            winner_judger.record_winner(gid, uid)
            winning_counter = WinningCounter(DB_PATH)
            winning_counter._record_winning(gid, uid)
            winning_count = winning_counter._get_winning_number(gid, uid)
            nick = ev.get_author().get_nick_name()
            msg_part = f'{nick}猜对了，真厉害！TA已经猜对{winning_count}次了~'
            c = chara.fromid(correct_id)
            msg =  f'正确答案是: {c.name}'
            await bot.kkr_send(ev, msg)
            await bot.kkr_send(ev, c.icon)
            await bot.kkr_send(ev, msg_part)

            winner_judger.turn_off(gid)