import json
import os
from datetime import datetime, timedelta
import time
from hashlib import sha256
from typing import Dict, Union
from urllib.parse import urljoin

from .webmaster import WebMaster

from .argparse import ArgParser, ArgHolder, ParseResult
from .argparse.argtype import *
from . import sv, cb_cmd, cb_prefix
from . import cb_cmd
from kokkoro.service import Service
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro import priv, R, util, config

svweb = Service('web')

@svweb.scheduled_job('cron', hour='5')
async def drop_expired_logins():
    now = datetime.now()
    # TODO: delete from DB

@cb_cmd(('登录', 'login'), ArgParser('!登录'))
async def login(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    if False and "this message is from group": # FIXME
        return '请私聊使用'
    reply = get_login_code_url(ev)
    await bot.kkr_send(ev, reply)

@cb_cmd(('重置密码', 'reset-password'), ArgParser('!重置密码'))
async def reset_password(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    if False and "this message is from group": # FIXME
        return '请私聊使用'
    reply = f'您的临时密码是：{_reset_pwd(ev)}'
    await bot.kkr_send(ev, reply)

def get_login_code_url(ev:EventInterface) -> str:
    wm = WebMaster(ev.get_group_id())
    login_code = util.rand_string(6)
    user = wm.get_or_add_user(ev.get_author_id())
    user['login_code'] = login_code
    user['login_code_available'] = True
    user['login_code_expire_time'] = int(time.time()) + 60
    user['deleted'] = False
    wm.mod_user(user)

    url = urljoin(
        config.PUBLIC_ADDRESS, # undefined
        '{}login/c/#uid={}&key={}'.format(
            config.PUBLIC_BASEPATH,
            user['uid'],
            login_code,
        )
    )
    return url

def _reset_pwd(ev:EventInterface):
    return "123456"
