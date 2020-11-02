"""
PCR会战管理命令 v2

猴子也会用的会战管理

命令设计遵循以下原则：
- 中文：降低学习成本
- 唯一：There should be one-- and preferably only one --obvious way to do it.
- 耐草：参数不规范时尽量执行
"""
import math
import os
import re
from datetime import datetime, timedelta
from typing import List
from matplotlib import pyplot as plt
import httpx
import json

from .battlemaster import BattleMaster
from .exception import *

from .argparse import ArgParser, ArgHolder, ParseResult
from .argparse.argtype import *

from . import sv, cb_cmd, cb_prefix

from kokkoro.service import Service
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro import priv, R, util, config

plt.style.use('seaborn-pastel')
plt.rcParams['font.family'] = ['DejaVuSans', 'Microsoft YaHei', 'SimSun', ]

USAGE_ADD_CLAN = '!建会 N公会名 S服务器代号'
USAGE_ADD_MEMBER = '!入会 昵称 (@id)'
USAGE_LIST_MEMBER = '!查看成员'

USAGE_TIP = '\n\n※无需输入尖括号，圆括号内为可选参数'

ERROR_CLAN_NOTFOUND = f'公会未初始化：请*群管理*使用【{USAGE_ADD_CLAN}】进行初始化{USAGE_TIP}'
ERROR_ZERO_MEMBER = f'公会内无成员：使用【{USAGE_ADD_MEMBER}】以添加{USAGE_TIP}'
ERROR_MEMBER_NOTFOUND = f'未找到成员：请使用【{USAGE_ADD_MEMBER}】加入公会{USAGE_TIP}'
ERROR_PERMISSION_DENIED = '权限不足：需*群管理*以上权限'


def _check_clan(bm:BattleMaster):
    clan = bm.get_clan()
    if not clan:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)
    return clan

def _check_member(bm:BattleMaster, uid:str, tip=None):
    mem = bm.get_member(uid) # 时代变了
    if not mem:
        raise NotFoundError(tip or ERROR_MEMBER_NOTFOUND)
    return mem

def _check_admin(ev:EventInterface, tip:str='') -> bool:
    if not priv.check_priv(ev.get_author(), priv.ADMIN):
        raise PermissionDeniedError(ERROR_PERMISSION_DENIED + tip)


@cb_cmd(('建会', 'add-clan'), ArgParser(usage=USAGE_ADD_CLAN, arg_dict={
        'N': ArgHolder(tip='公会名'),
        'S': ArgHolder(tip='服务器地区', type=server_code)}))
async def add_clan(bot: KokkoroBot, ev: EventInterface, args:ParseResult):
    _check_admin(ev)
    bm = BattleMaster(ev.get_group_id())
    if bm.has_clan():
        bm.mod_clan(args.N, args.S)
        await bot.kkr_send(ev, f'公会信息已修改！\n{args.N} {server_name(args.S)}', at_sender=True)
    else:
        bm.add_clan(args.N, args.S)
        await bot.kkr_send(ev, f'公会建立成功！{args.N} {server_name(args.S)}', at_sender=True)



@cb_cmd(('查看公会', 'list-clan'), ArgParser('!查看公会'))
async def list_clan(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clans = bm.list_clan()
    if len(clans):
        clans = map(lambda x: f"{x['name']}({server_name(x['server'])})", clans)
        msg = ['本群指定唯一公会：', *clans]
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
    else:
        raise NotFoundError(ERROR_CLAN_NOTFOUND)


@cb_cmd(('入会', 'add-member'), ArgParser(usage=USAGE_ADD_MEMBER, arg_dict={
        '': ArgHolder(tip='昵称', default=''),
        '@': ArgHolder(tip='id', type=str, default=0)}))
async def add_member(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    uid = args['@'] or args.uid
    name = args[''] or args.name
    author = ev.get_author()

    if uid == None:
        uid = ev.get_author_id()
    else:
        if uid != ev.get_author_id():
            _check_admin(ev, '才能添加其他人')
            if not ev.whether_user_in_group(uid):
                raise NotFoundError(f'Error: 无法获取该群员信息，请检查{uid}是否属于本群')
        ## if we can't get name from mentions
        # if not name and :
        #     m = await bot.get_group_member_info(self_id=ctx['self_id'], group_id=bm.group, user_id=uid)
        #     name = m['card'] or m['nickname'] or str(m['user_id'])

    name = name or author.get_nick_name() or author.get_name()

    mem = bm.get_member(uid)
    if mem:
        bm.mod_member(uid, name, mem['last_sl'], mem['authority_group'])
        await bot.kkr_send(ev, f'成员{bot.kkr_at(uid)}昵称已修改为{name}')
    else:
        bm.add_member(uid, name)
        await bot.kkr_send(ev, f"成员{bot.kkr_at(uid)}添加成功！欢迎{name}加入{clan['name']}")


@cb_cmd(('查看成员', '成员查看', '查询成员', '成员查询', 'list-member'), ArgParser(USAGE_LIST_MEMBER))
async def list_member(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    mems = bm.list_member()
    if l := len(mems):
        # 数字太多会被腾讯ban
        mems = map(lambda x: '{uid} | {name}'.format_map(x), mems)
        msg = [ f"\n{clan['name']}   {l}/30 人\n____ ID ____ | 昵称", *mems]
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
    else:
        raise NotFoundError(ERROR_ZERO_MEMBER)


@cb_cmd(('退会', 'del-member'), ArgParser(usage='!退会 (@id)', arg_dict={
        '@': ArgHolder(tip='id', type=str, default=0)}))
async def del_member(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    uid = args['@'] or args.uid or ev.get_author_id()
    mem = _check_member(bm, uid, '公会内无此成员')

    if uid != ev.get_author_id():
        _check_admin(ev, '才能踢人')
    bm.del_member(uid)
    await bot.kkr_send(ev, f"成员{mem['name']}已从公会删除", at_sender=True)


@cb_cmd(('清空成员', 'clear-member'), ArgParser('!清空成员'))
async def clear_member(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    _check_admin(ev)
    msg = f"{clan['name']}已清空！" if bm.clear_member() else f"{clan['name']}已无成员"
    await bot.kkr_send(ev, msg, at_sender=True)


@cb_cmd(('一键入会', 'batch-add-member'), ArgParser('!一键入会'))
async def batch_add_member(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    _check_admin(ev)
    mlist = ev.get_members_in_group()

    if len(mlist) > 50:
        raise ClanBattleError('群员过多！一键入会仅限50人以内群使用')

    self_id = config.BOT_ID
    succ, fail = 0, 0
    for m in mlist:
        if m.get_id() != self_id:
            try:
                bm.add_member(m.get_id(), m.get_nick_name() or m.get_name() or m.get_id())
                succ += 1
            except DatabaseError:
                fail += 1
    msg = f'批量注册完成！成功{succ}/失败{fail}\n使用【{USAGE_LIST_MEMBER}】查看当前成员列表'
    await bot.kkr_send(ev, msg, at_sender=True)


def _gen_progress_text(clan_name, round_, boss, hp, max_hp, score_rate):
    return f"{clan_name} 当前进度：\n{round_}周目 {BattleMaster.int2kanji(boss)}王    SCORE x{score_rate:.1f}\nHP={hp:,d}/{max_hp:,d}"


async def process_challenge(bot:KokkoroBot, ev:EventInterface, ch:ParseResult):
    """
    处理一条报刀 需要保证challenge['flag']的正确性
    """

    bm = BattleMaster(ev.get_group_id())
    now = datetime.now() - timedelta(days=ch.get('dayoffset', 0))
    clan = _check_clan(bm)
    mem = _check_member(bm, ch.uid)

    cur_round, cur_boss, cur_hp = bm.get_challenge_progress(now)
    round_ = ch.round or cur_round
    boss = ch.boss or cur_boss
    is_current = (round_ == cur_round) and (boss == cur_boss)
    is_future  = (round_ > cur_round) or (round_ == cur_round and boss > cur_boss)
    flag = ch.flag
    msg = ['']
    if not is_current:
        msg.append('⚠️上报与当前进度不一致')
    if is_future:
        cur_hp = bm.get_boss_hp(round_, boss, clan['server'])

    damage = None
    if (is_current or is_future):
        # 当前或未来boss并且是尾刀，则自动将伤害设置为当前血量
        if BattleMaster.has_damage_kind_for(ch.flag, BattleMaster.LAST):
            damage = cur_hp
    if not damage:
        if not ch.damage:
            raise NotFoundError('请给出伤害值')
        damage = ch.damage

    # 上一刀如果是尾刀，这一刀就是补偿刀
    challenges = bm.list_challenge_of_user_of_day(mem['uid'], now)
    if len(challenges) > 0 and challenges[-1]['flag'] == BattleMaster.LAST:
        flag = flag | BattleMaster.EXT
        msg.append('⚠️已自动标记为补时刀')

    if (is_current or is_future):
        # 伤害校对
        if damage >= cur_hp:
            if damage > cur_hp:
                damage = cur_hp
                msg.append(f'⚠️过度虐杀 伤害数值已自动修正为{damage}')
            # 不是尾刀，则标记为尾刀
            if not BattleMaster.has_damage_kind_for(flag, BattleMaster.LAST):
                flag = flag | BattleMaster.LAST
                msg.append('⚠️已自动标记为尾刀')
        elif BattleMaster.has_damage_kind_for(flag, BattleMaster.LAST):
            damage = cur_hp
            msg.append(f'⚠️尾刀伤害已自动修正为{damage}')

    remain_hp = cur_hp - damage if (is_current or is_future) else -1

    eid = bm.add_challenge(mem['uid'], round_, boss, damage, remain_hp, flag, now)
    aft_round, aft_boss, aft_hp = bm.get_challenge_progress(now)
    max_hp, score_rate = bm.get_boss_info(aft_round, aft_boss, clan['server'])
    msg.append(f"记录编号E{eid}：\n{mem['name']}给予{round_}周目{bm.int2kanji(boss)}王{damage:,d}点伤害\n")
    msg.append(_gen_progress_text(clan['name'], aft_round, aft_boss, aft_hp, max_hp, score_rate))
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)

    # 判断是否更换boss，呼叫预约
    if aft_round != cur_round or aft_boss != cur_boss:
        await call_subscribe(bot, ev, aft_round, aft_boss)

    await auto_unlock_boss(bot, ev, bm)
    await auto_unsubscribe(bot, ev, bm.group, mem['uid'], boss)

def isDD(damage):
    return damage < 600000

import random
async def jiuzhe(bot, ev):
    msglist = ['就这？', R.img('就这.jpg')]
    index = random.randint(0, len(msglist)-1)
    await bot.kkr_send(ev, msglist[index])

@cb_cmd(('出刀', '报刀', 'add-challenge'), ArgParser(usage='!出刀 <伤害值> (@id)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int),
    '@': ArgHolder(tip='id', type=str, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0),
    'D': ArgHolder(tip='日期差', type=int, default=0)}))
async def add_challenge(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args['@'] or args.uid or ev.get_author_id(),
        'flag': BattleMaster.NORM,
        'dayoffset': args.get('D', 0)
    })
    await process_challenge(bot, ev, challenge)

    damage = args.get('')
    if isDD(damage):
        await jiuzhe(bot, ev)



@cb_cmd(('出尾刀', '收尾', '尾刀', 'add-challenge-last'), ArgParser(usage='!出尾刀 (<伤害值>) (@<id>)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int, default=0),
    '@': ArgHolder(tip='id', type=str, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge_last(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args['@'] or args.uid or ev.get_author_id(),
        'flag': BattleMaster.LAST
    })
    await process_challenge(bot, ev, challenge)


@cb_cmd(('出补时刀', '补时刀', '补时', 'add-challenge-ext'), ArgParser(usage='!出补时刀 <伤害值> (@id)', arg_dict={
    '': ArgHolder(tip='伤害值', type=damage_int),
    '@': ArgHolder(tip='id', type=str, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge_ext(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': args.get(''),
        'uid': args['@'] or args.uid or ev.get_author_id(),
        'flag': BattleMaster.EXT
    })
    await process_challenge(bot, ev, challenge)


@cb_cmd(('掉刀', 'add-challenge-timeout'), ArgParser(usage='!掉刀 (@id)', arg_dict={
    '@': ArgHolder(tip='id', type=str, default=0),
    'R': ArgHolder(tip='周目数', type=round_code, default=0),
    'B': ArgHolder(tip='Boss编号', type=boss_code, default=0)}))
async def add_challenge_timeout(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    challenge = ParseResult({
        'round': args.R,
        'boss': args.B,
        'damage': 0,
        'uid': args['@'] or args.uid or ev.get_author_id(),
        'flag': BattleMaster.TIMEOUT
    })
    await process_challenge(bot, ev, challenge)


@cb_cmd(('删刀', 'del-challenge'), ArgParser(usage='!删刀 E记录编号', arg_dict={
    'E': ArgHolder(tip='记录编号', type=int)}))
async def del_challenge(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    now = datetime.now()
    clan = _check_clan(bm)

    ch = bm.get_challenge(args.E, now)
    if not ch:
        raise NotFoundError(f'未找到出刀记录E{args.E}')
    if ch['uid'] != ev.get_author_id():
        _check_admin(ev, '才能删除其他人的记录')
    bm.del_challenge(args.E, now)
    await bot.kkr_send(ev, f"{clan['name']}已删除{bot.kkr_at(ch['uid'])}的出刀记录E{args.E}", at_sender=True)


# TODO 将预约信息转至数据库
SUBSCRIBE_PATH = os.path.expanduser('~/.kokkoro/clanbattle_sub/')
SUBSCRIBE_MAX = [99, 6, 6, 6, 6, 6]
os.makedirs(SUBSCRIBE_PATH, exist_ok=True)

class SubscribeData:

    def __init__(self, data:dict):
        for i in '12345':
            data.setdefault(i, [])
            data.setdefault('m' + i, [])
            l = len(data[i])
            if len(data['m' + i]) != l:
                data['m' + i] = [None] * l
        data.setdefault('tree', [])
        data.setdefault('lock', [])
        if 'max' not in data or len(data['max']) != 6:
            data['max'] = [99, 6, 6, 6, 6, 6]
        self._data = data

    @staticmethod
    def default():
        return SubscribeData({
            '1':[], '2':[], '3':[], '4':[], '5':[],
            'm1':[], 'm2':[], 'm3':[], 'm4':[], 'm5':[],
            'tree':[], 'lock':[],
            'max': [99, 6, 6, 6, 6, 6]
        })

    def get_sub_list(self, boss:int):
        return self._data[str(boss)]

    def get_memo_list(self, boss:int):
        return self._data[f'm{boss}']

    def get_tree_list(self):
        return self._data['tree']

    def get_sub_limit(self, boss:int):
        return self._data['max'][boss]

    def set_sub_limit(self, boss:int, limit:int):
        self._data['max'][boss] = limit

    def add_sub(self, boss:int, uid:str, memo:str):
        self._data[str(boss)].append(uid)
        self._data[f'm{boss}'].append(memo)

    def remove_sub(self, boss:int, uid:str):
        s = self._data[str(boss)]
        m = self._data[f'm{boss}']
        i = s.index(uid)
        s.pop(i)
        m.pop(i)

    def add_tree(self, uid:str):
        self._data['tree'].append(uid)

    def clear_tree(self):
        self._data['tree'].clear()

    def get_lock_info(self):
        return self._data['lock']

    def set_lock(self, uid:str, ts):
        self._data['lock'] = [ (uid, ts) ]

    def clear_lock(self):
        self._data['lock'].clear()

    def dump(self, filename):
        with open(filename, 'w', encoding='utf8') as f:
            json.dump(self._data, f, ensure_ascii=False)


def _load_sub(gid) -> SubscribeData:
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8') as f:
            return SubscribeData(json.load(f))
    else:
        return SubscribeData.default()


def _save_sub(sub:SubscribeData, gid):
    filename = os.path.join(SUBSCRIBE_PATH, f"{gid}.json")
    sub.dump(filename)


def _gen_namelist_text(bot:KokkoroBot, bm:BattleMaster, uidlist:List[str], memolist:List[str]=None, do_at=False):
    if do_at:
        mems = map(lambda x: str(bot.kkr_at(x)), uidlist)
    else:
        mems = map(lambda x: bm.get_member(x) or {'name': str(x)}, uidlist)
        mems = map(lambda x: x['name'], mems)
    if memolist:
        mems = list(mems)
        for i in range(len(mems)):
            if i < len(memolist) and memolist[i]:
                mems[i] = f"{mems[i]}：{memolist[i]}"
    return mems


SUBSCRIBE_TIP = ''

@cb_cmd(('预约', 'subscribe'), ArgParser(usage='!预约 <Boss号> M留言', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code),
    'M': ArgHolder(tip='留言', default='')}))
async def subscribe(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    uid = ev.get_author_id()
    _check_clan(bm)
    _check_member(bm, uid)

    sub = _load_sub(bm.group)
    boss = args['']
    memo = args.M
    boss_name = bm.int2kanji(boss)
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    limit = sub.get_sub_limit(boss)
    if uid in slist:
        raise AlreadyExistError(f'您已经预约过{boss_name}王了')
    msg = ['']
    if len(slist) < limit:
        sub.add_sub(boss, uid, memo)
        _save_sub(sub, bm.group)
        msg.append(f'已为您预约{boss_name}王！')
    else:
        msg.append(f'预约失败：{boss_name}王预约人数已达上限')
    msg.append(f'=== 当前队列 {len(slist)}/{limit} ===')
    msg.extend(_gen_namelist_text(bot, bm, slist, mlist))
    msg.append(SUBSCRIBE_TIP)
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)


@cb_cmd(('取消预约', '预约取消', 'unsubscribe'), ArgParser(usage='!取消预约 <Boss号>', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code)}))
async def unsubscribe(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    uid = ev.get_author_id()
    _check_clan(bm)
    _check_member(bm, uid)

    sub = _load_sub(bm.group)
    boss = args['']
    boss_name = bm.int2kanji(boss)
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    limit = sub.get_sub_limit(boss)
    if uid not in slist:
        raise NotFoundError(f'您没有预约{boss_name}王')
    sub.remove_sub(boss, uid)
    _save_sub(sub, bm.group)
    msg = [ f'\n已为您取消预约{boss_name}王！' ]
    msg.append(f'=== 当前队列 {len(slist)}/{limit} ===')
    msg.extend(_gen_namelist_text(bot, bm, slist, mlist))
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)


async def auto_unsubscribe(bot:KokkoroBot, ev:EventInterface, gid, uid, boss):
    sub = _load_sub(gid)
    slist = sub.get_sub_list(boss)
    if uid not in slist:
        return
    sub.remove_sub(boss, uid)
    _save_sub(sub, gid)
    await bot.kkr_send(ev, f'已为{bot.kkr_at(uid)}自动取消{BattleMaster.int2kanji(boss)}王的订阅')


async def call_subscribe(bot:KokkoroBot, ev:EventInterface, round_:int, boss:int):
    bm = BattleMaster(ev.get_group_id())
    msg = []
    sub = _load_sub(bm.group)
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    tlist = sub.get_tree_list()
    if slist:
        msg.append(f"您们预约的老{BattleMaster.int2kanji(boss)}出现啦！")
        msg.extend(_gen_namelist_text(bot, bm, slist, mlist, do_at=True))
    if slist and tlist:
        msg.append("==========")
    if tlist:
        msg.append(f"以下成员可以下树了")
        msg.extend(map(lambda x: str(bot.kkr_at(x)), tlist))
        sub.clear_tree()
        _save_sub(sub, bm.group)
    if msg:
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=False)    # do not at the sender


@cb_cmd(('查询预约', '预约查询', '查看预约', '预约查看', 'list-subscribe'), ArgParser('!查询预约'))
async def list_subscribe(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    msg = [ f"\n{clan['name']}当前预约情况：" ]
    sub = _load_sub(bm.group)
    for boss in range(1, 6):
        slist = sub.get_sub_list(boss)
        mlist = sub.get_memo_list(boss)
        limit = sub.get_sub_limit(boss)
        msg.append(f"========\n{bm.int2kanji(boss)}王: {len(slist)}/{limit}")
        msg.extend(_gen_namelist_text(bot, bm, slist, mlist))
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)


@cb_cmd(('清空预约', '预约清空', '清理预约', '预约清理', 'clear-subscribe'), ArgParser('!清空预约', arg_dict={
    '': ArgHolder(tip='Boss编号', type=boss_code)}))
async def clear_subscribe(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    _check_admin(ev, '才能清理预约队列')
    sub = _load_sub(bm.group)
    boss = args['']
    slist = sub.get_sub_list(boss)
    mlist = sub.get_memo_list(boss)
    if slist:
        slist.clear()
        mlist.clear()
        _save_sub(sub, bm.group)
        await bot.kkr_send(ev, f"{bm.int2kanji(boss)}王预约队列已清空", at_sender=True)
    else:
        raise NotFoundError(f"无人预约{bm.int2kanji(boss)}王")


@cb_cmd(('预约上限', 'set-subscribe-limit'), ArgParser(usage='!预约上限 B<Boss号> <上限值>', arg_dict={
    'B': ArgHolder(tip='Boss编号', type=boss_code),
    '': ArgHolder(tip='上限值', type=int)
}))
async def set_subscribe_limit(bot:KokkoroBot, ev, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    _check_admin(ev, '才能设置预约上限')
    limit = args['']
    if not (0 < limit <= 30):
        raise ClanBattleError('预约上限只能为1~30内的整数')
    sub = _load_sub(bm.group)
    sub.set_sub_limit(args.B, limit)
    _save_sub(sub, bm.group)
    await bot.kkr_send(ev, f'{bm.int2kanji(args.B)}王预约上限已设置为：{limit}')


@cb_cmd(('挂树', '上树', 'add-sos'), ArgParser('!挂树'))
async def add_sos(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    uid = ev.get_author_id()
    clan = _check_clan(bm)
    _check_member(bm, uid)

    sub = _load_sub(bm.group)
    tree = sub.get_tree_list()
    if uid in tree:
        raise AlreadyExistError("您已在树上")
    sub.add_tree(uid)
    _save_sub(sub, bm.group)
    msg = [ "\n您已上树，本Boss被击败时将会通知您",
           f"目前{clan['name']}挂树人数为{len(tree)}人：" ]
    msg.extend(_gen_namelist_text(bot, bm, tree))
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
    await bot.kkr_send(ev, R.img('priconne/挂树.jpg'))


@cb_cmd(('查树', 'list-sos'), ArgParser('!查树'))
async def list_sos(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    sub = _load_sub(bm.group)
    tree = sub.get_tree_list()
    msg = [ f"\n目前{clan['name']}挂树人数为{len(tree)}人：" ]
    msg.extend(_gen_namelist_text(bot, bm, tree))
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)


@cb_cmd(('锁定', '申请出刀', 'lock'), ArgParser('!锁定'))
async def lock_boss(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    _check_clan(bm)
    _check_member(bm, ev.get_author_id())

    sub = _load_sub(bm.group)
    lock = sub.get_lock_info()
    if lock:
        uid, ts = lock[0]
        time = datetime.fromtimestamp(ts)
        mem = bm.get_member(uid) or {'name': str(uid)}
        delta = datetime.now() - time
        delta = timedelta(seconds=round(delta.total_seconds()))     # ignore miliseconds
        msg = f"\n锁定失败：{mem['name']}已于{delta}前锁定了Boss"
        await bot.kkr_send(ev, msg, at_sender=True)
    else:
        uid = ev.get_author_id()
        time = datetime.now()
        sub.set_lock(uid, datetime.now().timestamp())
        _save_sub(sub, bm.group)
        msg = f"已锁定Boss"
        await bot.kkr_send(ev, msg, at_sender=True)


@cb_cmd(('解锁', 'unlock'), ArgParser('!解锁'))
async def unlock_boss(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    _check_clan(bm)

    sub = _load_sub(bm.group)
    lock = sub.get_lock_info()
    if lock:
        uid, ts = lock[0]
        time = datetime.fromtimestamp(ts)
        if uid != ev.get_author_id():
            mem = bm.get_member(uid) or {'name': str(uid)}
            delta = datetime.now() - time
            delta = timedelta(seconds=round(delta.total_seconds()))     # ignore miliseconds
            _check_admin(ev, f"才能解锁其他人\n解锁失败：{mem['name']}于{delta}前锁定了Boss")
        sub.clear_lock()
        _save_sub(sub, bm.group)
        msg = f"\nBoss已解锁"
        await bot.kkr_send(ev, msg, at_sender=True)
    else:
        msg = "\n无人锁定Boss"
        await bot.kkr_send(ev, msg, at_sender=True)


async def auto_unlock_boss(bot:KokkoroBot, ev:EventInterface, bm:BattleMaster):
    sub = _load_sub(bm.group)
    lock = sub.get_lock_info()
    if lock:
        uid, ts = lock[0]
        time = datetime.fromtimestamp(ts)
        if uid != ev.get_author_id():
            mem = bm.get_member(uid) or {'name': str(uid)}
            delta = datetime.now() - time
            delta = timedelta(seconds=round(delta.total_seconds()))     # ignore miliseconds
            msg = f"⚠️{mem['name']}于{delta}前锁定了Boss，您出刀前未申请锁定！"
            await bot.kkr_send(ev, msg, at_sender=True)
        else:
            sub.clear_lock()
            _save_sub(sub, bm.group)
            msg = f"\nBoss已自动解锁"
            await bot.kkr_send(ev, msg, at_sender=True)


@cb_cmd(('进度', '进度查询', '查询进度', '进度查看', '查看进度', '状态', 'progress'), ArgParser(usage='!进度'))
async def show_progress(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    r, b, hp = bm.get_challenge_progress(datetime.now())
    max_hp, score_rate = bm.get_boss_info(r, b, clan['server'])
    msg = _gen_progress_text(clan['name'], r, b, hp, max_hp, score_rate)
    await bot.kkr_send(ev, '\n' + msg, at_sender=True)


@cb_cmd(('统计', '伤害统计', 'stat-damage'), ArgParser(usage='!伤害统计'))
async def stat_damage(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    now = datetime.now()
    clan = _check_clan(bm)

    yyyy, mm, _ = bm.get_yyyymmdd(now)
    stat = bm.stat_damage(now)

    yn = len(stat)
    if not yn:
        await bot.kkr_send(ev, f"{clan['name']}{yyyy}年{mm}月会战统计数据为空", at_sender=True)
        return

    stat.sort(key=lambda x: x[2][0], reverse=True)
    total = [ s[2][0] for s in stat ]
    name = [ s[1] for s in stat ]
    y_pos = list(range(yn))
    y_size = 0.3 * yn + 1.0
    unit = 1e4
    unit_str = 'w'

    # convert to pre-sum
    for s in stat:
        d = s[2]
        d[0] = 0
        for i in range(2, 6):
            d[i] += d[i - 1]
    pre_sum_dmg = [
        [ s[2][b] for s in stat ] for b in range(6)
    ]

    # generate statistic figure
    fig, ax = plt.subplots()
    fig.set_size_inches(10, y_size)
    ax.set_title(f"{clan['name']}{yyyy}年{mm}月会战伤害统计")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(name)
    ax.set_ylim((-0.6, yn - 0.4))
    ax.invert_yaxis()
    ax.set_xlabel('伤害')
    colors = ['#00a2e8', '#22b14c', '#b5e61d', '#fff200', '#ff7f27', '#ed1c24']
    bars = [ ax.barh(y_pos, pre_sum_dmg[b], align='center', color=colors[b]) for b in range(5, -1, -1) ]
    bars.reverse()
    ax.ticklabel_format(axis='x', style='plain')
    for b in range(1, 6):
        for i, rect in enumerate(bars[b]):
            x = (rect.get_width() + bars[b - 1][i].get_width()) / 2
            y = rect.get_y() + rect.get_height() / 2
            d = pre_sum_dmg[b][i] - pre_sum_dmg[b - 1][i]
            if d > unit:
                ax.text(x, y, f'{d/unit:.0f}{unit_str}', ha='center', va='center')
            if b == 5:
                ax.text(rect.get_width() + 10, y, f'{total[i]/unit:.0f}{unit_str}', ha='left', va='center')
    plt.subplots_adjust(left=0.12, right=0.96, top=1 - 0.35 / y_size, bottom=0.55 / y_size)

    await bot.kkr_send(ev, fig)
    plt.close()

    msg = f"※分数统计请发送“!分数统计”"
    await bot.kkr_send(ev, msg, at_sender=True)


@cb_cmd(('分数统计', 'stat-score'), ArgParser(usage='!分数统计'))
async def stat_score(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    now = datetime.now()
    clan = _check_clan(bm)

    yyyy, mm, _ = bm.get_yyyymmdd(now)
    stat = bm.stat_score(now)
    stat.sort(key=lambda x: x[2], reverse=True)

    if not len(stat):
        await bot.kkr_send(ev, f"{clan['name']}{yyyy}年{mm}月会战统计数据为空", at_sender=True)
        return

    # msg = [ f"\n{yyyy}年{mm}月会战{clan['name']}分数统计：" ]
    # for _, _, name, score in stat:
    #     score = f'{score:,d}'           # 数字太多会被腾讯ban，用逗号分隔
    #     blank = '  ' * (11-len(score))  # QQ字体非等宽，width(空格*2) == width(数字*1)
    #     msg.append(f"{blank}{score}分 | {name}")

    # generate statistic figure
    fig, ax = plt.subplots()
    score = list(map(lambda i: i[2], stat))
    yn = len(stat)
    name = list(map(lambda i: i[1], stat))
    y_pos = list(range(yn))

    if score[0] >= 1e8:
        unit = 1e8
        unit_str = 'e'
    else:
        unit = 1e4
        unit_str = 'w'

    y_size = 0.3 * yn + 1.0
    fig.set_size_inches(10, y_size)
    bars = ax.barh(y_pos, score, align='center')
    ax.set_title(f"{clan['name']}{yyyy}年{mm}月会战分数统计")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(name)
    ax.set_ylim((-0.6, yn - 0.4))
    ax.invert_yaxis()
    ax.set_xlabel('分数')
    ax.ticklabel_format(axis='x', style='plain')
    for rect in bars:
        w = rect.get_width()
        ax.text(w, rect.get_y() + rect.get_height() / 2, f'{w/unit:.2f}{unit_str}', ha='left', va='center')
    plt.subplots_adjust(left=0.12, right=0.96, top=1 - 0.35 / y_size, bottom=0.55 / y_size)
    await bot.kkr_send(ev, fig)
    plt.close()
    msg = f"※伤害统计请发送“!伤害统计”"
    await bot.kkr_send(ev, msg, at_sender=True)


async def _do_show_remain(bot:KokkoroBot, ev:EventInterface, args:ParseResult, at_user:bool):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    if at_user:
        _check_admin(ev, '才能催刀。您可以用【!查刀】查询余刀')
    rlist = bm.list_challenge_remain(datetime.now() - timedelta(days=args.get('D', 0)))
    rlist.sort(key=lambda x: x[2] + x[3], reverse=True)
    msg = [ f"\n{clan['name']}今日余刀：" ]
    sum_remain = 0
    for uid, name, r_n, r_e in rlist:
        if r_n or r_e:
            msg.append(f"剩{r_n}刀 补时{r_e}刀 | {bot.kkr_at(uid) if at_user else name}")
            sum_remain += r_n

    if len(msg) == 1:
        await bot.kkr_send(ev, f"今日{clan['name']}所有成员均已下班！各位辛苦了！", at_sender=True)
    else:
        msg.append(f'共计剩余{sum_remain}刀')
        msg.append('若有负数说明报刀有误 请注意核对\n使用“!出刀记录 @id”可查看详细记录')
        if at_user:
            msg.append("=========\n在？阿sir喊你出刀啦！")
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
        if at_user:
            await bot.kkr_send(ev, R.img('priconne/催刀.jpg'))


@cb_cmd(('查刀', 'list-remain'), ArgParser(usage='!查刀', arg_dict={
        'D': ArgHolder(tip='日期差', type=int, default=0)}))
async def list_remain(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    await _do_show_remain(bot, ev, args, at_user=False)
@cb_cmd(('催刀', 'urge-remain'), ArgParser(usage='!催刀'))
async def urge_remain(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    await _do_show_remain(bot, ev, args, at_user=True)


@cb_cmd(('出刀记录', 'list-challenge'), ArgParser(usage='!出刀记录 (@id)', arg_dict={
        '@': ArgHolder(tip='id', type=str, default=0),
        'D': ArgHolder(tip='日期差', type=int, default=0)}))
async def list_challenge(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)

    now = datetime.now() - timedelta(days=args.D)
    zone = bm.get_timezone_num(clan['server'])
    uid = args['@'] or args.uid
    if uid:
        mem = _check_member(bm, uid, '公会内无此成员')
        challen = bm.list_challenge_of_user_of_day(mem['uid'], now, zone)
    else:
        challen = bm.list_challenge_of_day(now, zone)

    msg = [ f'{clan["name"]}出刀记录：\n编号|出刀者|周目|Boss|伤害|标记' ]
    challenstr = 'E{eid:0>3d}|{name}|r{round}|b{boss}|{dmg: >7,d}{flag_str}'
    for c in challen:
        mem = bm.get_member(c['uid'])
        c['name'] = mem['name'] if mem else c['uid']
        flag = c['flag']
        c['flag_str'] = '|' + ','.join(BattleMaster.damage_kind_to_string(flag))
        msg.append(challenstr.format_map(c))
    await bot.kkr_send(ev, '\n'.join(msg))


@cb_cmd(('合刀计算', '补偿刀计算', 'boss-slayer'), ArgParser(usage='!补偿刀计算 50w 60w', arg_dict={'': ArgHolder(tip='伤害')})) # 由于需要输入两个伤害，因此 ArgParser 仅仅是摆设
async def boss_slayer(bot, ev: EventInterface, args: ParseResult):
    bm = BattleMaster(ev.get_group_id())
    clan = _check_clan(bm)
    if clan['server'] == BattleMaster.SERVER_CN:
        servertag = '**国服合刀**'
        ext0 = 100
    else:
        servertag = '**日服/台服合刀**'
        ext0 = 110 # 日服补偿刀20秒起

    remain = ev.get_param().remain
    prm = re.findall("(\d+)([kK千]?)([wW万]?)", remain)

    if len(prm) != 2:
        usage = "【用法/用例】\n!补偿刀计算 伤害1 伤害2"
        await bot.kkr_send(ev, usage, at_sender=True)
        return

    r, b, hp = bm.get_challenge_progress(datetime.now())
    dmg1 = int(prm[0][0])
    dmg2 = int(prm[1][0])
    dmg1 = dmg1 * (1000 if prm[0][1] else 1) * (10000 if prm[0][2] else 1)
    dmg2 = dmg2 * (1000 if prm[1][1] else 1) * (10000 if prm[1][2] else 1)
    if dmg1 + dmg2 < hp:
        msg = '0x0 这两刀合起来还打不死BOSS喔'
    else:
        if dmg1 >= hp and dmg2 >= hp:
            ans1 = f'先出{dmg1:,}，BOSS直接就被打死啦'
            ans2 = f'先出{dmg2:,}，BOSS直接就被打死啦'
        elif dmg1 >= hp and dmg2 < hp:
            ans1 = f'先出{dmg1:,}，BOSS直接就被打死啦'
            ext2 = min(math.ceil(ext0-((hp-dmg2)/dmg1)*90), 90)
            ans2 = f'先出{dmg2:,}再出{dmg1:,}，返还时间{ext2}秒'
        elif dmg1 < hp and dmg2 >= hp:
            ext1 = min(math.ceil(ext0-((hp-dmg1)/dmg2)*90), 90)
            ans1 = f'先出{dmg1:,}再出{dmg2:,}，返还时间{ext1}秒'
            ans2 = f'先出{dmg2:,}，BOSS直接就被打死啦'
        else:
            ext1 = min(math.ceil(ext0-((hp-dmg1)/dmg2)*90), 90)
            ans1 = f'先出{dmg1:,}再出{dmg2:,}，返还时间{ext1}秒'
            ext2 = min(math.ceil(ext0-((hp-dmg2)/dmg1)*90), 90)
            ans2 = f'先出{dmg2:,}再出{dmg1:,}，返还时间{ext2}秒'

        not_my_fault = "计算结果仅供参考，可能与游戏内实际返还时间有偏差"
        msg = '\n'.join([servertag, ans1, ans2, not_my_fault])
    await bot.kkr_send(ev, msg, at_sender=False)


async def get_cookies(url, **kwargs):
    async with httpx.AsyncClient() as client:
        r = await client.get(url, **kwargs)
        return r.cookies

async def post(url, **kwargs):
    async with httpx.AsyncClient() as client:
        r = await client.post(url, **kwargs)
        return r.json()


RANK_API_NAME = "https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/name/0"
RANK_API_LEADER = "https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/leader/0"
RANK_API_RANK = "https://service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com/rank"
@cb_cmd('排名', ArgParser(
    usage='！排名 C<公会名> L<会长名> R<排名> 默认查询本群公会。各参数不兼容。',
    arg_dict={
        'C':ArgHolder(tip='公会名', type=str, default=''),
        'L':ArgHolder(tip='会长名', type=str, default=''),
        'R':ArgHolder(tip='会长名', type=str, default='')}))
async def clan_rank(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    clan_name = args.get('C')
    leader = args.get('L')
    rank = args.get('R')

    # default
    if clan_name == '' and leader == '' and rank == '':
        bm = BattleMaster(ev.get_group_id())
        clan = _check_clan(bm)
        clan_name = clan['name']
        url = RANK_API_NAME
    elif clan_name != '':
        url = RANK_API_NAME
    elif leader != '':
        url = RANK_API_LEADER
    elif rank != '':
        url = f'{RANK_API_RANK}/{rank}'
    body = json.dumps({'clanName':clan_name, 'leaderName': leader})
    headers = {
        "Sec-Fetch-Site":"cross-site",
        "Sec-Fetch-Mode":"cors",
        "Sec-Fetch-Dest":"empty",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate", # don't include br
        "Accept-Language": "zh-Hans-CN, zh-Hans; q=0.8, en-US; q=0.5, en; q=0.3",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Custom-Source": "KokkoroBot",
        "Host": "service-kjcbcnmw-1254119946.gz.apigw.tencentcs.com",
        "Origin": "https://kengxxiao.github.io",
        "Referer": "https://kengxxiao.github.io/Kyouka/",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }

    try:
        cookies = await get_cookies("https://kengxxiao.github.io/Kyouka/")
        cookies.set('fav', '[]', domain='kengxxiao.github.io') # cookies is a must
        res = await post(url, headers=headers, data=body, cookies=cookies)
    except Exception as e:
        print(e)
        await bot.kkr_send(ev, '查询出错，请稍后再试', at_sender=True)
        return

    if 'data' not in res:
        print(body)
        print(res)
        await bot.kkr_send(ev, '未找到公会', at_sender=True)
        return
    msg = []
    for data in res['data']:
        info = f"{data['clan_name']} 目前第{data['rank']}名 总伤害 {data['damage']}"
        if leader != '':
            info += f" 会长 {data['leader_name']}"
        msg.append(info)
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)

