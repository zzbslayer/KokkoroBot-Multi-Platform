import os
import asyncio
import nest_asyncio
from tomon_sdk import bot
from io import BytesIO
import httpx
import time


from random import choice
from string import ascii_letters

import kokkoro
from kokkoro.service import BroadcastTag
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.typing import overrides, Image, Figure
from kokkoro.bot.tomon.tomon_adaptor import *
from kokkoro.bot.tomon.tomon_util import at
from kokkoro.bot.tomon import get_scheduler_loop

nest_asyncio.apply()
loop = asyncio.get_event_loop()

DEFAULT_CD = 5*60 # 5 minute

def rand_temp_file():
    rand_name = ''.join(choice(ascii_letters) for i in range(10)) + '.png'
    dst = os.path.join("/var/tmp/", rand_name)
    return dst

class KokkoroTomonBot(KokkoroBot):
    def __init__(self, config):
        self.config = config
        super().kkr_load_modules(self.config)

        def on_message(data):
            if data.get('e') == 'MESSAGE_CREATE':
                raw_event = data.get('d')
                if raw_event.get('author') == None:
                    return # ignore system msg
                loop.run_until_complete(self.kkr_on_message(raw_event))

        self._bot = bot.Bot()
        self._bot.on(bot.OpCodeEvent.DISPATCH, on_message)

        self._channels_cache = {}
        self._channels_cache_lock = asyncio.Lock(loop=get_scheduler_loop())

    def get_raw_bot(self):
        return self._bot

    @overrides(KokkoroBot)
    def kkr_event_adaptor(self, raw_event) -> TomonEvent:
        return TomonEvent(raw_event)
    
    @overrides(KokkoroBot)
    async def kkr_send(self, ev: TomonEvent, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        if isinstance(msg, str) and at_sender:
            at_info = self.kkr_at(ev.get_author_id())
            msg = f'{msg} {at_info}'

        cid = ev.get_channel_id()
        await self._send_by_channel(cid, msg, filename)
        

    async def _send_by_channel(self, cid, msg: SupportedMessageType, filename="image.png"):
        if isinstance(msg, str):
            payload = {}
            payload['content'] = msg
            await self._bot.api().route(f'/channels/{cid}/messages').post(data=payload)
        elif isinstance(msg, ResImg):
            if kokkoro.config.RES_PROTOCOL == 'http':
                async with httpx.AsyncClient() as client:
                    r = await client.get(url)
                    with BytesIO(r) as fp:
                        path=rand_temp_file()
                        with open(path,'wb') as temp: 
                            temp.write(fp.read())

                await self._bot.api().route(f'/channels/{cid}/messages').post(data={}, files=[path])

            elif kokkoro.config.RES_PROTOCOL == 'file':
                await self._bot.api().route(f'/channels/{cid}/messages').post(data={}, files=[msg.path])
            else:
                raise NotImplementedError
        elif isinstance(msg, RemoteResImg):
            
            async with httpx.AsyncClient() as client:
                r = await client.get(msg.url)
                with BytesIO(r.content) as fp:
                    path=rand_temp_file()
                    with open(path,'wb') as temp: 
                        temp.write(fp.read())

            await self._bot.api().route(f'/channels/{cid}/messages').post(data={}, files=[path])

        elif isinstance(msg, Image.Image):
            with BytesIO() as fp:
                msg.save(fp, format='PNG')
                fp.seek(0)
                path=rand_temp_file()
                with open(path,'wb') as temp: 
                    temp.write(fp.read())

            await self._bot.api().route(f'/channels/{cid}/messages').post(data={}, files=[path])
        elif isinstance(msg, Figure):
            with BytesIO() as fp:
                msg.savefig(fp, format='PNG')
                fp.seek(0)
                path=rand_temp_file()
                with open(path,'wb') as temp: 
                    temp.write(fp.read())

            await self._bot.api().route(f'/channels/{cid}/messages').post(data={}, files=[path])
        else:
            raise NotImplementedError

    @overrides(KokkoroBot)
    def kkr_run(self):
        self._bot.start(kokkoro.config.bot.tomon.TOMON_TOKEN)

    @overrides(KokkoroBot)
    def kkr_at(self, uid):
        return at(uid)

    @overrides(KokkoroBot)
    async def kkr_send_by_group(self, gid, msg: SupportedMessageType, tag=BroadcastTag.default, filename='image.png'):
        channels = await self.get_channels_by_gid(gid)

        sent_channels = []
        for channel in channels:
            if tag in channel.get('name'):
                cid = channel.get('id')
                if cid in sent_channels:
                    continue
                await self._send_by_channel(cid, msg, filename=filename)
                sent_channels.append(cid)
                #return
        kokkoro.logger.warning(f"Guild <{gid}> doesn't contains any channel named as <{tag}>")

    async def get_channels_by_gid(self, gid):
        await self._channels_cache_lock.acquire()
        try:
            ch_time_tuple = self._channels_cache.get(gid)
            if ch_time_tuple == None: # no cache
                raw_channels = await self.request_channels_by_gid(gid)
            else:
                raw_channels, next_time = ch_time_tuple
                if time.time() >= next_time: # cache expire
                    raw_channels = await self.request_channels_by_gid(gid)
        finally:
            self._channels_cache_lock.release()
        return raw_channels
    
    async def request_channels_by_gid(self, gid):
        kokkoro.logger.debug(f'Requesting for /guilds/{gid}/channels')
        raw_channels = await self._bot.api().route(f'/guilds/{gid}/channels').get()
        if raw_channels == None:
            raise Exception('No channels')
        next_time = time.time() + DEFAULT_CD
        self._channels_cache[gid] = (raw_channels, next_time)
        return raw_channels
    
    @overrides(KokkoroBot)
    def get_groups(self) -> List[TomonGroup]:
        raw_groups = asyncio.run(self._bot.api().route(f'/users/@me/guilds').get())
        return TomonGroup.from_raw_groups(raw_groups)

    @overrides(KokkoroBot)
    def get_members_in_group(self, gid) -> List[TomonUser]:
        raw_members = asyncio.run(self._bot.api().route(f'/guilds/{gid}/members').get())
        return TomonUser.from_raw_members(raw_members)

    def get_group_by_id(self, gid) -> TomonGroup:
        raw_group = asyncio.run(self._bot.api().route(f'/guilds/{gid}').get())
        return TomonGroup(raw_group)
    
    def get_roles_by_group(self, gid):
        raw_roles = asyncio.run(self._bot.api().route(f'/guilds/{gid}/roles').get())
        return raw_roles