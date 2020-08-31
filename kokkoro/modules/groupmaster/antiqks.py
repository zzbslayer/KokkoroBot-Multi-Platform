import aiohttp
from kokkoro.service import Service
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro import R, util

sv = Service('antiqks', help_='识破骑空士的阴谋')

qks_url = ["granbluefantasy.jp"]
qksimg = R.img('antiqks.jpg')

@sv.on_keyword(qks_url)
async def qks_keyword(bot: KokkoroBot, ev: EventInterface):
    await bot.kkr_send(ev, qksimg, at_sender=True)
    await util.silence(ev, 60)

# 有潜在的安全问题
# @sv.on_rex(r'[a-zA-Z0-9\.]{4,12}\/[a-zA-Z0-9]+')
async def qks_rex(bot: KokkoroBot, ev: EventInterface):
    match = ev.get_param().match
    msg = f'骑空士爪巴远点\n{qksimg}'
    res = 'http://'+match.group(0)
    async with aiohttp.TCPConnector(verify_ssl=False) as connector:
        async with aiohttp.request(
            'GET',
            url=res,
            allow_redirects=False,
            connector=connector,
        ) as resp:
            h = resp.headers
            s = resp.status
    if s == 301 or s == 302:
        if 'granbluefantasy.jp' in h['Location']:
            await bot.kkr_send(ev, msg, at_sender=True)
            await util.silence(ev, 60)
