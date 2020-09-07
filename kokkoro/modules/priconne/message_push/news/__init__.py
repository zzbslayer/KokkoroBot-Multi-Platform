import asyncio
from kokkoro.service import Service, BroadcastTag, BroadcastService
from .spider import *

svtw = BroadcastService('pcr-news-tw', broadcast_tag=BroadcastTag.tw_broadcast, help_='台服官网新闻')
svbl = BroadcastService('pcr-news-bili', broadcast_tag=BroadcastTag.cn_broadcast, help_='B服官网新闻')

async def news_poller(spider:BaseSpider, sv:Service, LOG_TAG, send=True):
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
        await sv.broadcast(spider.format_items(news))

async def _async_init():
    await news_poller(BiliAllSpider, svbl, 'B服官网')

#asyncio.run(_async_init())

@svtw.scheduled_job('cron', minute='*/20', jitter=20)
async def sonet_news_poller():
    await news_poller(SonetSpider, svtw, '台服官网')

@svbl.scheduled_job('cron', minute='*/20', jitter=20)
async def bili_news_poller():
    await news_poller(BiliAllSpider, svbl,'B服官网')

    


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
