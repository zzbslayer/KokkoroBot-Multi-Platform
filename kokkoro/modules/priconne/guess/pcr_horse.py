# 作者来自 hoshino群 @Lost℃ 2435994901
# 重构 @zzbslayer
import os
import random
import json
from collections import defaultdict

import kokkoro
from kokkoro import R
from kokkoro.bot import get_bot
from kokkoro.common_interface import EventInterface, KokkoroBot
from kokkoro.service import Service
from kokkoro.util import DailyNumberLimiter, concat_pic
from .. import chara

# '[赛马]兰德索尔赛🐎大赛'
sv = Service('pcr-horse')

_pool_config_file = os.path.expanduser('~/.kokkoro/group_pool_config.json')
_group_pool = {}
POOL = ('MIX', 'JP', 'TW', 'BL')
DEFAULT_POOL = POOL[0]

try:
    with open(_pool_config_file, encoding='utf8') as f:
        _group_pool = json.load(f)
except FileNotFoundError as e:
    sv.logger.warning('group_pool_config.json not found, will create when needed.')
_group_pool = defaultdict(lambda: DEFAULT_POOL, _group_pool)


lmt = DailyNumberLimiter(5)


special_object = [
    '🙉',  '💧', '🗿', '🎂'
]


numb = ['1️⃣', '2️⃣', '3️⃣', '4️⃣']


class Player(object):

    def __init__(self, pool_name:str = "MIX"):
        super().__init__()
        self.load_chara(pool_name)

    def load_chara(self, pool_name:str):
        config = kokkoro.config.modules.priconne.horse_pool
        pool = config[pool_name]
        self.player = pool["player"]
        self.number = pool["number"]

    def get_chara(self):
        result = []
        c = chara.fromname(random.choice(self.player), 3)
        result.append(c)
        while len(result) != 4:
            c = chara.fromname(random.choice(self.player), 3)
            result_name = [f'{i.name}' for i in result]
            if c.name not in result_name:
                result.append(c)
        return result

    def get_num(self):
        result = []
        for _ in range(4):
            c = chara.fromname(self.number[_], 3)
            result.append(c)
        return result


g_status_dict = {}
g_uid_dict = {}
STONE = [500, 400, 300, 250]

#生成模拟赛道数组(1→无其他物品，2→加速圈，4→弹簧跳板，0→传送魔法阵，-1→水洼/石块/魔物)
def genl(a):
    px = []
    s = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, -1, -1, -1, -1, -1, -1, 4, 4, 0]
    for _ in range(a):
        random.shuffle(s)
        i = random.randint(0, len(s) - 1)
        x = s[i]
        px.append(x)
        if x == 0:
            for _i in range(_ + 1, a - 2):
                x = 1
                px.append(x)
            x = 0
            px.append(x)
            x = s[random.randint(0, len(s) - 1)]
            px.append(x)
            return px
    return px

#转换数组为符号&emoji
def gen_w(l, i:int):
    m = f'{numb[i-1]}'
    for _ in l:
        if _ == 1:
            m += f'☰'
        if _ == 2:
            m += f'⏩'
        if _ == 4:
            m += f'🛷'
        if _ == -1:
            m += f'{random.choice(special_object)}'
        if _ == 0:
            m += f'✡'
    return m


def step(y, z:int):
    x = 0
    if y[z] != 0:
        x = y[z]
        return x
    if y[z] == 0:
        x = 13 - z
        return x

class HorseTrack:
    TRACK_LEN = 15
    def __init__(self):
        self.track1 = genl(HorseTrack.TRACK_LEN)
        self.track2 = genl(HorseTrack.TRACK_LEN)
        self.track3 = genl(HorseTrack.TRACK_LEN)
        self.track4 = genl(HorseTrack.TRACK_LEN)
    
    def __str__(self):
        return f'{gen_w(self.track1, 1)}\n{gen_w(self.track2, 2)}\n{gen_w(self.track3, 3)}\n{gen_w(self.track4, 4)}'

class HorseStatus:
    def __init__(self, gid, track: HorseTrack, charactors, multi_player=False):
        self.gid = gid
        self.track = track
        self.charactors = charactors
        self.multi_player = multi_player
        self.selection = {} # (charactor, uid)
        self.force_finish = False

    def is_unselected(self):
        return len(self.selection) == 0
    
    def set_force_finish(self, flag: bool):
        if self.multi_player:
            self.force_finish = flag

    def calculate_rank(self):
        track = self.track
        charactors = self.charactors
        pri = []
        r_pri = [] # [1st, 2nd, 3rd, 4th]
        
        a = b = c = d = 0
        for _ in range(HorseTrack.TRACK_LEN):
            a += step(track.track1, _)
            b += step(track.track2, _)
            c += step(track.track3, _)
            d += step(track.track4, _)
            if a >= HorseTrack.TRACK_LEN:
                pri.append(charactors[0])
            if b >= HorseTrack.TRACK_LEN:
                pri.append(charactors[1])
            if c >= HorseTrack.TRACK_LEN:
                pri.append(charactors[2])
            if d >= HorseTrack.TRACK_LEN:
                pri.append(charactors[3])
        pri_r = [a, b, c, d]
        pri_r = sorted(pri_r, reverse=True)
        for _ in pri_r:
            if a == _:
                pri.append(charactors[0])
            if b == _:
                pri.append(charactors[1])
            if c == _:
                pri.append(charactors[2])
            if d == _:
                pri.append(charactors[3])
        for k in pri:
            if k not in r_pri:
                r_pri.append(k)
        return r_pri

    '''
    Call this once if not multi_player
    '''
    def add_player(self, uid, chara_name):
        if chara_name in self.selection.keys():
            return False
        self.selection[chara_name] = uid
        return True
    
    def is_finished(self):
        if self.force_finish:
            return True
        if self.multi_player:
            if len(self.selection) == 4:
                return True
        else:
            if len(self.selection) == 1:
                return True
        return False

    async def get_result(self):
        msg = '========================\n'
        msg += f'{self.track}\n'
        chara_rank = self.calculate_rank()
        bot = get_bot()

        if self.multi_player:
            # assert len(self.selection) == 4
            for i in range(0, 4):
                chara_name = chara_rank[i]
                
                uid = self.selection.get(chara_name)
                if uid == None:
                    msg += f'第{i+1}位：{chara_name}\n'
                else:
                    at_user = await bot.kkr_at_by_uid(uid, self.gid)
                    msg += f'{at_user} 第{i+1}位：{chara_name} 宝石×{STONE[i]}\n'
        else:
            # assert len(self.selection) == 1
            for i in range(0, 4):
                chara_name = chara_rank[i]
                msg += f'第{i+1}位：{chara_name}\n'
            for j in range(4):
                for k, v in self.selection.items():
                    chara_name = k
                    uid = v 
                if chara_name == chara_rank[j]:
                    at_user = await bot.kkr_at_by_uid(uid, self.gid)
                    msg += f'{at_user} 恭喜获得第{j+1}位奖励，宝石×{STONE[j]}\n'
        msg += "========================"
        return msg

@sv.on_prefix(('赛马', '兰德索尔杯', 'horse', '赛🐴'), only_to_me=False)
async def pcr_horse(bot, ev: EventInterface):
    remain = ev.get_param().remain
    await _horse(bot, ev, remain=='-m')

@sv.on_fullmatch(('多人赛🐴', '多人赛马', '多人兰德索尔杯', 'multi-horse'), only_to_me=False)
async def pcr_horse_force_multi(bot, ev: EventInterface):
    await _horse(bot, ev, True)

async def _horse(bot, ev, multi_player):
    global g_status_dict, g_uid_dict
    gid = ev.get_group_id()
    uid = ev.get_author_id()
    
    if not lmt.check(uid):
        await bot.kkr_send(ev, '今天已经赛过5次力', at_sender=True)
        return
    if g_status_dict.get(gid) != None:
        await bot.kkr_send(ev, '上一场比赛尚未结束，请等待', at_sender=True)
        return
    lmt.increase(uid)
    await bot.kkr_send(ev, f'第○届兰德索尔杯比赛开始！', at_sender=True)

    # Charactors
    player = Player(_group_pool[gid])
    result = player.get_chara()
    result_number = player.get_num()
    res2 = chara.gen_team_pic(result, star_slot_verbose=False)
    res1 = chara.gen_team_pic(result_number, star_slot_verbose=False)
    img = concat_pic([res1, res2])
    charactors = [f'{c.name}' for c in result]
    res_name = ' '.join(charactors)

    await bot.kkr_send(ev, img)
    msg = f'{res_name}\n※发送“选中+角色名称”开始比赛'
    if multi_player:
        msg += '\n※默认需要四人参与才可开始比赛\n※选中后发送指令"开始赛🐴"开始1-3人的比赛'
    await bot.kkr_send(ev, msg, at_sender=False)
    
    # Track
    track = HorseTrack()
    # Status
    g_status_dict[gid] = HorseStatus(gid, track, charactors, multi_player)
    g_uid_dict[gid] = uid

@sv.on_fullmatch(('开始赛马', '开始赛🐴', 'start-horse'))
async def force_start(bot: KokkoroBot, ev: EventInterface):
    gid = ev.get_group_id()
    horse_status: HorseStatus = g_status_dict.get(gid)
    if horse_status == None:
        await bot.kkr_send(ev, f'比赛尚未开始，发送指令"多人赛🐴"发起多人游戏', at_sender=True)
    elif horse_status.is_unselected():
        # single player unselected and multi player unselected
        await bot.kkr_send(ev, f'请至少先选中一匹🐴', at_sender=True)
    else:
        await bot.kkr_send(ev, f'比赛开始')
        res = await horse_status.get_result()
        await bot.kkr_send(ev, f'{res}')
        clean(gid)

    

@sv.on_prefix('选中')
async def _select_(bot: KokkoroBot, ev: EventInterface):
    global g_uid_dict, g_status_dict
    gid = ev.get_group_id()
    uid = ev.get_author_id()
    horse_status: HorseStatus = g_status_dict.get(gid)
    if horse_status == None:
        await bot.kkr_send(ev, f'比赛尚未开始，发送指令"赛🐴"发起新的游戏', at_sender=True)
    elif not horse_status.multi_player and uid != g_uid_dict[gid]:
        await bot.kkr_send(ev, f'仅限比赛发起人进行选择~\n发送指令"多人赛🐴"发起多人游戏')
    else:
        pkey = ev.get_param().remain
        id_ = chara.name2id(pkey)
        s_chara = chara.fromid(id_)
        if s_chara.name not in g_status_dict[gid].charactors:
            await bot.kkr_send(ev, f'所选角色未在参赛角色中')
            return
        success = horse_status.add_player(uid, s_chara.name)
        if not success:
            await bot.kkr_send(ev, f'已经有人选过 {s_chara.name} 了 0x0', at_sender=True)
        elif horse_status.is_finished():
            await bot.kkr_send(ev, f'比赛开始')
            res = await horse_status.get_result()
            await bot.kkr_send(ev, f'{res}')
            # Clean up
            clean(gid)
        else:
            await bot.kkr_send(ev, f'已选择{s_chara.name}', at_sender=True)

def clean(gid):
    g_uid_dict[gid] = None
    g_status_dict[gid] = None