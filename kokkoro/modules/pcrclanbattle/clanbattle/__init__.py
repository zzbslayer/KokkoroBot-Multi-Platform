# 公主连接Re:Dive会战管理插件
# clan == クラン == 戰隊（直译为氏族）（CLANNAD的CLAN（笑））

from .argparse import ArgParser
from .exception import *

from kokkoro.typing import *
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.service import Service
from kokkoro.util import join_iterable

sv = Service('clanbattle')
SORRY = 'ごめんなさい！嘤嘤嘤(〒︿〒)'

def cb_prefix(cmds):
    if isinstance(cmds, str):
        cmds = (cmds, )
    return join_iterable(('!', '！'), cmds)

def cb_cmd(prefixes, parser:ArgParser) -> Callable:
    prefixes = cb_prefix(prefixes)
    if not isinstance(prefixes, Iterable):
        raise ValueError('`name` of cb_cmd must be `str` or `Iterable[str]`')
    
    def deco(func):
        async def wrapper(bot: KokkoroBot, ev: EventInterface):
            try:
                args = parser.parse(ev.get_param().args, ev)
            except ParseError as e:
                await bot.kkr_send(ev, e.message, at_sender=True)
                return
            try:
                return await func(bot, ev, args)
            except ClanBattleError as e:
                await bot.kkr_send(ev, e.message, at_sender=True)
            except Exception as e:
                await bot.kkr_send(ev, f'{SORRY} 发生未知错误', at_sender=True)
                raise e
        sv.on_prefix(prefixes)(wrapper)
        return wrapper
    return deco


from .cmdv2 import *


QUICK_START = f'''
======================
- Kokkoro 会战管理v2.0 -
======================
快速开始指南
【必读事项】
※会战系命令均以感叹号!开头，半全角均可
※命令与参数之间必须以【空格】隔开
※下面以使用场景-使用例给出常用指令的说明
【群初次使用】
！建会 N自警団（カォン） Sjp
！建会 N哞哞自衛隊 Stw
！建会 N自卫团 Scn
【公会成员】
！入会 祐树
！入会 佐树 @123456789
！退会 @123456789
！查看成员
！一键入会
！清空成员
【会战进行时】
！出刀 514w
！收尾
！补时刀 114w
！删刀 E1
！补偿刀计算 50W 60W
！挂树
【锁定Boss】
！锁定
！解锁
【会战信息查询】
！进度
！查刀
！催刀
！出刀记录
！出刀记录 @123456789
！查树
【预约Boss】
！预约 5 M留言
！取消预约 5
【统计信息】
！分数统计
！伤害统计
【国服排名查询】
※！排名

※前往 t.cn/A6wBzowv 查看完整命令一览表
※如有问题请先阅读一览表底部的FAQ
※使用前请务必【逐字】阅读开头的必读事项
'''.rstrip()

@sv.on_fullmatch(cb_prefix(('帮助', '幫助', 'help')), only_to_me=False)
async def cb_help(bot: KokkoroBot, ev:EventInterface):
    await bot.kkr_send(ev, QUICK_START, at_sender=True)
    # msg = MessageSegment.share(url='https://github.com/Ice-Cirno/HoshinoBot/blob/master/hoshino/modules/pcrclanbattle/clanbattle/README.md',
    #                            title='Hoshino会战管理v2',
    #                            content='命令一览表')
    # await session.send(msg)

from . import report