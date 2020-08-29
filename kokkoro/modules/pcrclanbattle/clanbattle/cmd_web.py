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
from kokkoro import config
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.service import Service
from kokkoro.util import rand_string, add_salt_and_hash

svweb = Service('web')
@svweb.scheduled_job('cron', hour='5')
async def drop_expired_logins():
    now = datetime.now()
    wm = WebMaster()
    wm.del_login_by_time(now)

EXPIRED_TIME = 7 * 24 * 60 * 60  # 7 days
LOGIN_AUTH_COOKIE_NAME = 'yobot_login'
# this need be same with static/password.js
FRONTEND_SALT = '14b492a3-a40a-42fc-a236-e9a9307b47d2'


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
    reply = f'您的临时密码是：{reset_pwd(ev)}'
    await bot.kkr_send(ev, reply)

def get_login_code_url(ev:EventInterface) -> str:
    wm = WebMaster()
    login_code = rand_string(6)
    user = wm.get_or_add_user(ev.get_author_id())
    user['login_code'] = login_code
    user['login_code_available'] = True
    user['login_code_expire_time'] = int(time.time()) + 60
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

def reset_pwd(ev:EventInterface):
    wm = WebMaster()
    raw_pwd = rand_string(8)
    user = wm.get_or_add_user(ev.get_author_id())
    frontend_salted_pwd = add_salt_and_hash(raw_pwd + user['uid'], FRONTEND_SALT)
    user['password'] = add_salt_and_hash(frontend_salted_pwd, user['salt'])
    user['privacy'] = 0
    user['must_change_password'] = 1
    wm.mod_user(user)
    wm.del_login(user['uid'])
    return raw_pwd
