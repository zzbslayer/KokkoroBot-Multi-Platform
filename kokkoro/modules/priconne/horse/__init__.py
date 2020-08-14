# 本模块来自 HoshinoBot 群友
import os
import random
import json
from collections import defaultdict

import kokkoro
from kokkoro import R
from kokkoro.common_interface import EventInterface
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


g_result_dict = defaultdict(lambda:[], {})

g_uid_dict = defaultdict(lambda :[], {})


def save_player(gid, result_name):
    if result_name != []:
        global g_result_dict
        g_result_dict[gid] = [f'{c}' for c in result_name]
    else:
        g_result_dict[gid] = []
        return


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


#逻辑有待优化
async def compe(bot, ev: EventInterface, p:str):
    global g_result_dict
    gid = ev.get_group_id()
    r = 15
    result = []
    msg = f'========================\n'
    pa = genl(r)
    pb = genl(r)
    pc = genl(r)
    pd = genl(r)
    pri = []
    r_pri = []
    stone = [500, 400, 300, 250]
    a = b = c = d = 0
    await bot.kkr_send(ev, f'{gen_w(pa, 1)}\n{gen_w(pb, 2)}\n{gen_w(pc, 3)}\n{gen_w(pd, 4)}')
    for _ in range(r):
        a += step(pa, _)
        b += step(pb, _)
        c += step(pc, _)
        d += step(pd, _)
        if a >= r:
            pri.append(g_result_dict[gid][0])
        if b >= r:
            pri.append(g_result_dict[gid][1])
        if c >= r:
            pri.append(g_result_dict[gid][2])
        if d >= r:
            pri.append(g_result_dict[gid][3])
    pri_r = [a, b, c, d]
    pri_r = sorted(pri_r, reverse=True)
    for _ in pri_r:
        if a == _:
            pri.append(g_result_dict[gid][0])
        if b == _:
            pri.append(g_result_dict[gid][1])
        if c == _:
            pri.append(g_result_dict[gid][2])
        if d == _:
            pri.append(g_result_dict[gid][3])
    for k in pri:
        if k not in r_pri:
            r_pri.append(k)
    for i in range(0, 4):
        msg += f'第{i+1}位：{r_pri[i]}\n'
    for j in range(4):
        if p == r_pri[j]:
            msg += f'恭喜获得第{j+1}位奖励，宝石×{stone[j]}\n========================'
    await bot.kkr_send(ev, msg)
    save_player(gid, result)




async def select_player(bot, ev: EventInterface, pkey):
    global g_result_dict, g_uid_dict
    gid = ev.get_group_id()
    id_ = chara.name2id(pkey)
    p = chara.fromid(id_)
    if p.name not in g_result_dict[gid]:
        await bot.kkr_send(ev, f'所选角色未在参赛角色中')
        return
    await bot.kkr_send(ev, f'已选择{p.name},比赛开始', at_sender=True)
    await compe(bot, ev, p.name)
    g_uid_dict[gid] = 0



@sv.on_fullmatch(('赛跑', '赛马', '兰德索尔杯', 'horse'), only_to_me=False)
async def pcr_comp(bot, ev: EventInterface):
    global g_result_dict, g_uid_dict
    gid = ev.get_group_id()
    uid = ev.get_author_id()
    if not lmt.check(uid):
        await bot.kkr_send(ev, '今天已经赛过5次力', at_sender=True)
        return
    if g_result_dict[gid] != []:
        await bot.kkr_send(ev, '上一场比赛尚未结束，请等待', at_sender=True)
        return
    lmt.increase(uid)
    await bot.kkr_send(ev, f'第○届兰德索尔杯比赛开始！', at_sender=True)
    player = Player(_group_pool[gid])
    result = player.get_chara()
    result_number = player.get_num()
    res2 = chara.gen_team_pic(result, star_slot_verbose=False)
    res1 = chara.gen_team_pic(result_number, star_slot_verbose=False)
    res = concat_pic([res1, res2])
    result_name = [f'{c.name}' for c in result]
    res_name = ' '.join(result_name)
    if sv.bot.config.ENABLE_IMAGE:
        await bot.kkr_send(ev, res)
        await bot.kkr_send(ev, f'{res_name}\n※发送“选中+角色名称”开始比赛', at_sender=False)
    else:
        await bot.kkr_send(ev, f'Image is disabled')
    save_player(gid, result_name)
    g_uid_dict[gid] = uid

@sv.on_prefix('选中')
async def _select_(bot, ev: EventInterface):
    global g_uid_dict, g_result_dict
    gid = ev.get_group_id()
    uid = ev.get_author_id()
    if uid != g_uid_dict[gid] and g_result_dict[gid] != []:
        await bot.kkr_send(ev, f'仅限比赛发起人进行选择~')
    elif uid != g_uid_dict[gid] and g_result_dict[gid] == []:
        await bot.kkr_send(ev, f'上一场比赛已经结束，您可以用“@bot赛跑模拟”发起新的比赛', at_sender=True)
    elif uid == g_uid_dict[gid]:
        await select_player(bot, ev,  ev.get_param().remain)
    else:
        await bot.kkr_send(ev, f'出现错误，请联系维护组嘤嘤嘤')
