import re
import math
from . import sv
from .._pcr_data import total_mana, total_exp

from kokkoro.common_interface import EventInterface

@sv.on_prefix(('角色计算', 'mana-burner'))
async def manaburner(bot, ev: EventInterface):
    prm = re.findall("\d+", ev.get_param().remain)
    if len(prm) == 0 or len(prm) >= 4:
        usage = "使用方法：\n角色计算 [[角色数量] 当前等级 ]目标等级"
        await bot.kkr_send(ev, usage, at_sender=True)
        return
    elif len(prm) == 1:
        n = 1
        l = 1
        r = int(prm[0])
    elif len(prm) == 2:
        n = 1
        l = int(prm[0])
        r = int(prm[1])
    elif len(prm) == 3:
        n = int(prm[0])
        l = int(prm[1])
        r = int(prm[2])
    try:
        mana = (total_mana[r] - total_mana[l]) * n
        exp = (total_exp[r] - total_exp[l]) * n
        bottle = math.ceil(exp/7500)
        buyexp = math.ceil(exp/0.375)
        msg = f"{n}名角色从{l}级升到{r}级需要：\n{mana:,} mana\n{exp:,} 经验\n约{bottle:,}瓶超级经验药水（价值 {buyexp:,} mana）"
    except:
        msg = "0x0 好像超出了等级上限呢"
    await bot.kkr_send(ev, msg, at_sender=True)
