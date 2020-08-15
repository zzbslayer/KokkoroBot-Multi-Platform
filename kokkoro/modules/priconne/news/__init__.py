import asyncio
from kokkoro.service import Service
from .spider import *

svtw = Service('pcr-news-tw', help_='台服官网新闻')
svbl = Service('pcr-news-bili', help_='B服官网新闻')

async def news_poller(spider:BaseSpider, sv:Service, TAG, send=True):
    if not spider.item_cache:
        await spider.get_update()
        sv.logger.info(f'{TAG}新闻缓存为空，已加载至最新')
        return
    news = await spider.get_update()
    if not news:
        sv.logger.info(f'未检索到{TAG}新闻更新')
        return
    sv.logger.info(f'检索到{len(news)}条{TAG}新闻更新！')
    if send:
        await sv.broadcast(spider.format_items(news), TAG, interval_time=0.5)

async def _async_init():
    await news_poller(BiliAllSpider, svbl, 'B服官网')
    await news_poller(BiliNoteSpider, svbl, 'B服本地化笔记', send=False)
    await news_poller(BiliEventSpider, svbl, 'B服活动', send=False)

asyncio.get_event_loop().run_until_complete(_async_init())

@svtw.scheduled_job('cron', minute='*/10', jitter=20)
async def sonet_news_poller():
    await news_poller(SonetSpider, svtw, '台服官网')

@svbl.scheduled_job('cron', minute='*/10', jitter=20)
async def bili_news_poller():
    await news_poller(BiliAllSpider, svbl, 'B服官网')
    await news_poller(BiliNoteSpider, svbl, 'B服本地化笔记', send=False)
    await news_poller(BiliEventSpider, svbl, 'B服活动', send=False)
    


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

@svbl.on_fullmatch(('本地化笔记', 'b服本地化笔记', 'B服本地化笔记', '国服本地化笔记'))
async def send_bili_news(bot, ev):
    await send_news(bot, ev, BiliNoteSpider)

@svbl.on_fullmatch(('B服活动', 'b服活动', '国服活动'))
async def send_bili_news(bot, ev):
    await send_news(bot, ev, BiliEventSpider)
