import re
import math
from . import sv
from kokkoro.common_interface import EventInterface

@sv.on_prefix(('合刀计算', '补偿刀计算', 'boss-slayer'))
async def boss_slayer(bot, ev: EventInterface):
    server = re.findall("国服|日服?|台服?|b服?|cn|jp|tw", ev.get_param().remain, re.I)
    # 默认为国服
    if len(server) == 0 or server[0] in ['国服', 'b', 'B', 'b服', 'B服', 'CN', 'cn']:
        servertag = '**国服合刀**'
        ext0 = 100 # 当前版本国服补偿刀10秒起
    else:
        servertag = '**日服/台服合刀**'
        ext0 = 110 # 日服补偿刀20秒起

    remain = ev.get_param().remain
    prm = re.findall("\d+[wW万]", remain)
    if len(prm) == 3:
        hp = int(prm[0][:-1]) * 10000
        dmg1 = int(prm[1][:-1]) * 10000
        dmg2 = int(prm[2][:-1]) * 10000
    else:
        prm = re.findall("\d+", remain)
        if len(prm) == 3:
            hp = int(prm[0])
            dmg1 = int(prm[1])
            dmg2 = int(prm[2])
        else:
            usage = "使用方法：\n合刀计算 [服务器] BOSS剩余血量 伤害1 伤害2"
            await bot.kkr_send(ev, usage, at_sender=True)
            return

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