import random, itertools

from kokkoro.service import Service
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro import R, priv, util

sv = Service('chat', visible=False)

@sv.on_fullmatch(('老婆', 'waifu', 'laopo'), only_to_me=True)
async def chat_waifu(bot: KokkoroBot, ev: EventInterface):
    await bot.kkr_send(ev, '?')

# ============================================ #


@sv.on_keyword(('确实', '有一说一', 'u1s1', 'yysy'))
async def chat_queshi(bot: KokkoroBot, ev: EventInterface):
    cmd = ev.get_param().plain_text
    if cmd in ['确实.jpg'] or random.random() < 0.05:
        await bot.kkr_send(ev, R.img('确实.jpg'))


_neigui = ['内鬼']
_image_suffix = ['.jpg', '.png', '.gif']

@sv.on_keyword(tuple(_neigui))
async def chat_neigui(bot: KokkoroBot, ev: EventInterface):
    cmd = ev.get_param().plain_text
    if cmd in util.join_iterable(_neigui, _image_suffix) or random.random() < 0.05:
        await bot.kkr_send(ev, R.img('内鬼.png'))

_africa = ['非酋', '非洲', '脸黑', '非洲人']
@sv.on_keyword(tuple(_africa))
async def africa(bot: KokkoroBot, ev: EventInterface):
    cmd = ev.get_param().plain_text
    if cmd in util.join_iterable(_africa, _image_suffix) or random.random() < 0.05:
        await bot.kkr_send(ev, R.img('非洲人.png'))

nyb_player = f'''
正在播放：New Year Burst
──●━━━━ 1:05/1:30
⇆ ㅤ◁ ㅤㅤ❚❚ ㅤㅤ▷ ㅤ↻
'''.strip()

_ch = ('春黑', '新黑')
@sv.on_keyword(_ch)
async def new_year_burst(bot: KokkoroBot, ev: EventInterface):
    cmd = ev.get_param().plain_text
    if cmd in util.join_iterable(_ch, _image_suffix) or random.random() < 0.02:
        await bot.kkr_send(ev, R.img('newyearburst.gif'))
        await bot.kkr_send(ev, nyb_player)

_ue_sorry = ['ue对不起', '优衣对不起']
@sv.on_keyword(tuple(_ue_sorry))
async def new_year_burst(bot: KokkoroBot, ev: EventInterface):
    cmd = ev.get_param().plain_text
    if cmd in util.join_iterable(_ue_sorry, _image_suffix) or random.random() < 0.02:
        await bot.kkr_send(ev, R.img('ue_sorry.jpg'))
