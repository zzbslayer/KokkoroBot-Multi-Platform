import asyncio
from kokkoro.service import Service, BroadcastTag
from .spider import *

svtw = Service('pcr-news-tw', help_='台服官网新闻')
svbl = Service('pcr-news-bili', help_='B服官网新闻')

async def news_poller(spider:BaseSpider, sv:Service, bc_tag, LOG_TAG, send=True):
    if not spider.item_cache:
        await spider.get_update()
        sv.logger.info(f'{LOG_TAG}新闻缓存为空，已加载至最新')
        return
    news = await spider.get_update()
    if not news:
        sv.logger.info(f'未检索到{LOG_TAG}新闻更新')
        return
    sv.logger.info(f'检索到{len(news)}条{LOG_TAG}新闻更新！')
    if send:
        await sv.broadcast(spider.format_items(news), bc_tag)

async def _async_init():
    await news_poller(BiliAllSpider, svbl, BroadcastTag.cn_broadcast, 'B服官网')

#asyncio.run(_async_init())

@svtw.scheduled_job('cron', minute='*/10', jitter=20)
async def sonet_news_poller():
    await news_poller(SonetSpider, svtw, BroadcastTag.tw_broadcast, '台服官网')

@svbl.scheduled_job('cron', minute='*/10', jitter=20)
async def bili_news_poller():
    await news_poller(BiliAllSpider, svbl, BroadcastTag.cn_broadcast, 'B服官网')

    


async def send_news(bot, ev, spider:BaseSpider, max_num=5):
    if not spider.item_cache:
        await spider.get_update()
    news = spider.item_cache
    news = news[:min(max_num, len(news))]
    await bot.kkr_send(ev, spider.format_items(news), at_sender=True)

@svtw.on_fullmatch(('台服新闻'))
async def send_sonet_news(bot, ev):
    await send_news(bot, ev, SonetSpider)

@svbl.on_fullmatch(('b服新闻', '国服新闻', 'B服新闻'))
async def send_bili_news(bot, ev):
    await send_news(bot, ev, BiliAllSpider)
