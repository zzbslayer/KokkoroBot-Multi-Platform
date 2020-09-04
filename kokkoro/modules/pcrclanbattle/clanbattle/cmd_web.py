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
from kokkoro.priv import ADMIN, SUPERUSER
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

    wm = WebMaster()
    uid = ev.get_author_id()
    gid = ev.get_group_id()
    auth = ev.get_author().get_priv()

    member = wm.get_member(uid, gid)
    if member is None:
        await bot.kkr_send(ev, '请先加入公会')
        return
    member['authority_group'] = 100
    if auth == SUPERUSER:
        member['authority_group'] = 1
    elif auth == ADMIN:
        member['authority_group'] = 10
    wm.mod_member(member)

    user = wm.get_or_add_user(uid, rand_string(16))
    login_code = rand_string(6)
    user['login_code'] = login_code
    user['login_code_available'] = True
    user['login_code_expire_time'] = int(time.time()) + 60
    wm.mod_user(user)

    url = urljoin(
        config.PUBLIC_ADDRESS,
        '{}login/c/#uid={}&key={}'.format(
            config.PUBLIC_BASEPATH,
            user['uid'],
            login_code,
        )
    )
    await bot.kkr_send(ev, url)

@cb_cmd(('重置密码', 'reset-password'), ArgParser('!重置密码'))
async def reset_password(bot:KokkoroBot, ev:EventInterface, args:ParseResult):
    if False and "this message is from group": # FIXME
        return '请私聊使用'
    reply = f'您的临时密码是：{reset_pwd(ev)}'
    await bot.kkr_send(ev, reply)

def reset_pwd(ev:EventInterface):
    wm = WebMaster()
    user = wm.get_or_add_user(ev.get_author_id(), rand_string(16))
    raw_pwd = rand_string(8)
    frontend_salted_pwd = add_salt_and_hash(raw_pwd + user['uid'], FRONTEND_SALT)
    user['password'] = add_salt_and_hash(frontend_salted_pwd, user['salt'])
    user['privacy'] = 0
    user['must_change_password'] = 1
    wm.mod_user(user)
    wm.del_login(user['uid'])
    return raw_pwd
