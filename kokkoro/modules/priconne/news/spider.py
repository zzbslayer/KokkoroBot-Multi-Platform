"""Ref: https://github.com/yuudi/yobot/blob/master/src/client/ybplugins/spider
GPLv3 Licensed. Thank @yuudi for his contribution!
"""

import abc
from dataclasses import dataclass
from typing import List, Union

from bs4 import BeautifulSoup
from kokkoro import aiorequests


@dataclass
class Item:
    idx: Union[str, int]
    content: str = ""

    def __eq__(self, other):
        return self.idx == other.idx


class BaseSpider(abc.ABC):
    url = None
    src_name = None
    idx_cache = set()
    item_cache = []

    @classmethod
    async def get_response(cls) -> aiorequests.AsyncResponse:
        resp = await aiorequests.get(cls.url)
        resp.raise_for_status()
        return resp

    @staticmethod
    @abc.abstractmethod
    async def get_items(resp: aiorequests.AsyncResponse) -> List[Item]:
        raise NotImplementedError

    @classmethod
    async def get_update(cls) -> List[Item]:
        resp = await cls.get_response()
        items = await cls.get_items(resp)
        updates = [ i for i in items if i.idx not in cls.idx_cache ]
        if updates:
            cls.idx_cache = set(i.idx for i in items)
            cls.item_cache = items
        return updates

    @classmethod
    def format_items(cls, items) -> str:
        return f'{cls.src_name}\n' + '\n'.join(map(lambda i: i.content, items))



class SonetSpider(BaseSpider):
    url = "http://www.princessconnect.so-net.tw/news/"
    src_name = "台服官网"

    @staticmethod
    async def get_items(resp:aiorequests.AsyncResponse):
        soup = BeautifulSoup(await resp.text, 'lxml')
        return [
            Item(idx=dd.a["href"],
                 content=f"{dd.text}\n▲www.princessconnect.so-net.tw{dd.a['href']}"
            ) for dd in soup.find_all("dd")
        ]

NEWS_TYPE={
    "ANNOUCEMENT": 1,
    "NEWS": 2,
    "EVENT": 4,
    "NOTE": 6,
    "ALL": ''
}

bili_url = lambda news_type: f"http://api.biligame.com/news/list?gameExtensionId=267&positionId=2&pageNum=1&pageSize=5&typeId={news_type}"
bili_detail_url = lambda id : f"http://game.bilibili.com/pcr/news.html#news_detail_id={id}"

class AbstractBiliSpider(BaseSpider):
    @staticmethod
    async def get_items(resp:aiorequests.AsyncResponse):
        content = await resp.json()
        items = [
            Item(idx=n["id"],
                 content="{title}\n▲game.bilibili.com/pcr/news.html#news_detail_id={id}".format_map(n)
            ) for n in content["data"]
        ]
        print(items[0])
        return items

class BiliAllSpider(AbstractBiliSpider):
    url = bili_url(NEWS_TYPE["ALL"])
    src_name = "国服新闻一览"

class BiliNoteSpider(AbstractBiliSpider):
    url = bili_url(NEWS_TYPE["NOTE"])
    src_name = "本地化笔记"

class BiliEventSpider(AbstractBiliSpider):
    url = bili_url(NEWS_TYPE["EVENT"])
    src_name = "国服活动"