import os
import random
import json
from collections import defaultdict

from kokkoro import priv, util, R
from kokkoro.service import Service
from kokkoro.common_interface import *
from kokkoro.util import DailyNumberLimiter, concat_pic, pic2b64, silence

from .. import chara
from .gacha import Gacha

sv = Service('gacha')

POOL = ('MIX', 'JP', 'TW', 'BL')
DEFAULT_POOL = POOL[0]

_pool_config_file = os.path.expanduser('~/.kokkoro/group_pool_config.json')
_group_pool = {}
try:
    with open(_pool_config_file, encoding='utf8') as f:
        _group_pool = json.load(f)
except FileNotFoundError as e:
    sv.logger.warning('group_pool_config.json not found, will create when needed.')
_group_pool = defaultdict(lambda: DEFAULT_POOL, _group_pool)

def dump_pool_config():
    with open(_pool_config_file, 'w', encoding='utf8') as f:
        json.dump(_group_pool, f, ensure_ascii=False)

_gacha_10_aliases = ('抽十连', '十连', '十连！', '十连抽', '来个十连', '来发十连', '来次十连', '抽个十连', '抽发十连', '抽次十连', '十连扭蛋', '扭蛋十连',
                    '10连', '10连！', '10连抽', '来个10连', '来发10连', '来次10连', '抽个10连', '抽发10连', '抽次10连', '10连扭蛋', '扭蛋10连')
_gacha_1_aliases = ('单抽', '单抽！', '来发单抽', '来个单抽', '来次单抽', '扭蛋单抽', '单抽扭蛋')
_gacha_300_aliases = ('抽一井', '来一井', '来发井', '抽发井', '天井扭蛋', '扭蛋天井')

en_10 = ('gacha-10', 'gacha10', '10gacha')
en_1 = ('gacha-1', 'gacha1', '1gacha')
en_300 = ('gacha-300', 'gacha300', '300gacha', 'tenjo')

gacha_10_aliases = _gacha_10_aliases + en_10
gacha_1_aliases = _gacha_1_aliases + en_1
gacha_300_aliases = _gacha_300_aliases + en_300

@sv.on_fullmatch(('卡池资讯', '查看卡池', '看看卡池', '康康卡池', '卡池資訊', '看看up', '看看UP', 'gacha-info'))
async def gacha_info(bot:KokkoroBot, ev: EventInterface):
    gid = ev.get_group_id()
    gacha = Gacha(_group_pool[gid])
    up_chara = gacha.up
    up_chara_imgs = map(lambda x: (chara.fromname(x, star=3).icon), up_chara)
    for img in up_chara_imgs:
        await bot.kkr_send(ev, img)
    await bot.kkr_send(ev, f"本期卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob/10):.1f}% 3★出率={(gacha.s3_prob)/10:.1f}%")


POOL_NAME_TIP = '请选择以下卡池\n> 切换卡池jp\n> 切换卡池tw\n> 切换卡池b\n> 切换卡池mix'
@sv.on_prefix(('切换卡池', '选择卡池', 'switch-pool'))
async def set_pool(bot:KokkoroBot, ev: EventInterface):
    if not priv.check_priv(ev.get_author(), priv.ADMIN):
        await bot.kkr_send(ev, '只有群管理才能切换卡池', at_sender=True)
        return
    name = util.normalize_str(ev.get_param().remain)
    if not name:
        await bot.kkr_send(ev, POOL_NAME_TIP)
        return
    elif name in ('国', '国服', 'cn'):
        await bot.kkr_send(ev, '请选择以下卡池\n> 选择卡池 b服\n> 选择卡池 台服', at_sender=True)
        return
    elif name in ('b', 'b服', 'bl', 'bilibili'):
        name = 'BL'
    elif name in ('台', '台服', 'tw', 'sonet'):
        name = 'TW'
    elif name in ('日', '日服', 'jp', 'cy', 'cygames'):
        name = 'JP'
    elif name in ('混', '混合', 'mix'):
        name = 'MIX'
    else:
        await bot.kkr_send(ev, f'未知服务器地区 {POOL_NAME_TIP}', at_sender=True)
        return
    gid = ev.get_group_id()
    _group_pool[gid] = name
    dump_pool_config()
    await bot.kkr_send(ev, f'卡池已切换为{name}池', at_sender=True)

@sv.on_fullmatch(gacha_1_aliases, only_to_me=True)
async def gacha_1(bot:KokkoroBot, ev: EventInterface):
    gid = ev.get_group_id()
    gacha = Gacha(_group_pool[gid])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    #silence_time = hiishi * 60

    res = f'{chara.name} {"★"*chara.star}'

    img = chara.icon
    await bot.kkr_send(ev, img)

    if chara.star == 3:
        await silence(ev, 60)
    await bot.kkr_send(ev, f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_fullmatch(gacha_10_aliases, only_to_me=True)
async def gacha_10(bot:KokkoroBot, ev: EventInterface):
    SUPER_LUCKY_LINE = 170
    
    gid = ev.get_group_id()
    gacha = Gacha(_group_pool[gid])
    result, hiishi = gacha.gacha_ten()
    silence_time = hiishi * 6 if hiishi < SUPER_LUCKY_LINE else hiishi * 60

    res1 = chara.gen_team_pic(result[:5], star_slot_verbose=False)
    res2 = chara.gen_team_pic(result[5:], star_slot_verbose=False)
    img = concat_pic([res1, res2])
    await bot.kkr_send(ev, img, filename="gacha10.png")
    result = [f'{c.name}{"★"*c.star}' for c in result]
    res1 = ' '.join(result[0:5])
    res2 = ' '.join(result[5:])
    res = f'{res1}\n{res2}'

    # result = [f'{c.name}{"★"*c.star}' for c in result]
    # res1 = ' '.join(result[0:5])
    # res2 = ' '.join(result[5:])
    # res = f'{res1}\n{res2}' # text version

    if hiishi >= SUPER_LUCKY_LINE:
        await bot.kkr_send(ev, '恭喜海豹！おめでとうございます！')
    await bot.kkr_send(ev, f'素敵な仲間が増えますよ！\n{res}', at_sender=True)


@sv.on_fullmatch(gacha_300_aliases, only_to_me=True)
async def gacha_300(bot, ev: EventInterface):

    gid = ev.get_group_id()
    gacha = Gacha(_group_pool[gid])
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])

    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    if lenth <= 0:
        res = "竟...竟然没有3★？！"
    else:
        step = 4
        pics = []
        for i in range(0, lenth, step):
            j = min(lenth, i + step)
            pics.append(chara.gen_team_pic(res[i:j], star_slot_verbose=False))
        img = concat_pic(pics)
        await bot.kkr_send(ev, img, "gacha300.png")

    msg = [
        f"\n素敵な仲間が増えますよ！",
        f"★★★×{up+s3} ★★×{s2} ★×{s1}",
        f"获得记忆碎片×{100*up}与女神秘石×{50*(up+s3) + 10*s2 + s1}！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得女神秘石{50*(up+s3) + 10*s2 + s1}个！"
    ]

    if up == 0 and s3 == 0:
        msg.append("太惨了，咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("这位酋长，梦幻包考虑一下？")
    elif up == 0:
        msg.append("据说天井的概率只有12.16%")
    elif up <= 2:
        if result['first_up_pos'] < 50:
            msg.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
        elif result['first_up_pos'] < 100:
            msg.append("已经可以了，您已经很欧了")
        elif result['first_up_pos'] > 290:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > 250:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！多出30等专武～")
    elif up >= 4:
        msg.append("记忆碎片一大堆！您是托吧？")
    
    await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
    silence_time = ((100*up + 50*(up+s3)) / 3) * 1 #+ 10*s2 + s1) * 1
    if silence_time >= 5 * 60:
        await silence(ev, 5 * 60)


@sv.on_prefix('氪金')
async def kakin(bot, ev: EventInterface):
    if ev.get_author_id not in bot.config.SUPERUSERS:
        return
    count = 0
    members = ev.get_mentions()
    for m in members:
        uid = m.get_id()
        jewel_limit.reset(uid)
        tenjo_limit.reset(uid)
        count += 1
    if count:
        await bot.kkr_send(ev, f"已为{count}位用户充值完毕！谢谢惠顾～")
