import base64
import os
import time
import unicodedata
import pytz
import zhconv
import json
import re
import importlib

from collections import defaultdict
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from PIL import Image
from io import BytesIO

import discord
import kokkoro
from kokkoro import config

def load_config(inbuilt_file_var):
    """
    Just use `config = load_config(__file__)`,
    you can get the config.json as a dict.
    """
    filename = os.path.join(os.path.dirname(inbuilt_file_var), 'config.json')
    try:
        with open(filename, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        kokkoro.logger.exception(e)
        return {}

def only_to_me(msg: discord.Message) -> bool:
    members = msg.mentions
    if len(members) != 1:
        return False
    if members[0].id == config.BOT_ID:
        return True
    return False

def pic2b64(pic:Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def fig2b64(plt:plt) -> str:
    buf = BytesIO()
    plt.savefig(buf, format='PNG', dpi=100)
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def concat_pic(pics, border=5) -> Image:
    num = len(pics)
    w, h = pics[0].size
    des = Image.new('RGBA', (w, num * h + (num-1) * border), (255, 255, 255, 255))
    for i, pic in enumerate(pics):
        des.paste(pic, (0, i * (h + border)), pic)
    return des


def normalize_str(string) -> str:
    """
    规范化unicode字符串 并 转为小写 并 转为简体
    """
    string = unicodedata.normalize('NFKC', string)
    string = string.lower()
    string = zhconv.convert(string, 'zh-hans')
    return string

class FreqLimiter:
    def __init__(self, default_cd_seconds):
        self.next_time = defaultdict(float)
        self.default_cd = default_cd_seconds

    def check(self, key) -> bool:
        return bool(time.time() >= self.next_time[key])

    def start_cd(self, key, cd_time=0):
        self.next_time[key] = time.time() + (cd_time if cd_time > 0 else self.default_cd)

    def left_time(self, key) -> float:
        return self.next_time[key] - time.time()


class DailyNumberLimiter:
    tz = pytz.timezone('Asia/Shanghai')
    
    def __init__(self, max_num):
        self.today = -1
        self.count = defaultdict(int)
        self.max = max_num

    def check(self, key) -> bool:
        now = datetime.now(self.tz)
        day = (now - timedelta(hours=5)).day
        if day != self.today:
            self.today = day
            self.count.clear()
        return bool(self.count[key] < self.max)

    def get_num(self, key):
        return self.count[key]

    def increase(self, key, num=1):
        self.count[key] += num

    def reset(self, key):
        self.count[key] = 0

async def silence(ev: discord.Message, ban_time, skip_su=True):
    pass

def load_module(module_path: str):
    try:
        module = importlib.import_module(module_path)
        kokkoro.logger.info(f'Succeeded to import "{module_path}"')
        return module
    except Exception as e:
        kokkoro.logger.error(f'Failed to import "{module_path}", error: {e}')
        kokkoro.logger.exception(e)

def load_modules(module_dir, module_prefix):
    for name in os.listdir(module_dir):
        path = os.path.join(module_dir, name)
        if os.path.isfile(path) and (name.startswith('_') or not name.endswith('.py')):
            continue
        if os.path.isdir(path) and (name.startswith('_') or not os.path.exists(os.path.join(path, '__init__.py'))):
            continue

        m = re.match(r'([_A-Z0-9a-z]+)(.py)?', name)
        if not m:
            continue

        load_module(f'{module_prefix}.{m.group(1)}')

