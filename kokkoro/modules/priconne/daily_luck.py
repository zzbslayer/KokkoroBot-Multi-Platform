# -*- coding: utf-8 -*-
# 作者来自 hoshino群 @Lost℃ 2435994901
# 重构 @zzbslayer
import json
import re
import random
import os
import aiofiles
from PIL import Image, ImageSequence, ImageDraw, ImageFont

import kokkoro
from kokkoro import R
from kokkoro.config import FONT_PATH
from kokkoro.config.modules.priconne import luck
from kokkoro.service import Service
from kokkoro.common_interface import EventInterface, KokkoroBot
from kokkoro.util import DailyNumberLimiter


sv_help = '''
[抽签|人品|运势|抽凯露签]
随机角色/指定凯露预测今日运势
准确率高达114.514%！
'''.strip()
#帮助文本
sv = Service('pcr-luck', help_=sv_help)

lmt = DailyNumberLimiter(1)
#设置每日抽签的次数，默认为1

BASE_LUCK_IMG_DIR = 'priconne/luck'

luck_desc = luck.luck_desc
luck_type = luck.luck_type

async def read_json_config(file):
    if not os.path.exists(file):
        raise Exception(f'json config {file} doesn\'t exist')
    async with aiofiles.open(file, 'r', encoding='utf-8') as f:
        content = await f.read()
    return json.loads(content)

@sv.on_prefix(('抽签', '人品', '运势', 'luck'), only_to_me=True)
async def luck(bot: KokkoroBot, ev: EventInterface):
    uid = ev.get_author_id()
    if not lmt.check(uid):
        await bot.kkr_send(ev, f'你今天已经抽过签了，欢迎明天再来~', at_sender=True)
        return
    lmt.increase(uid)

    #model = 'KYARU'
    model = 'DEFAULT'

    luck_img = generate_luck_image(model)
    await bot.kkr_send(ev, luck_img)


def generate_luck_image(model) -> Image:
    font_path = {
        'title': FONT_PATH["mamelon"],
        'text': FONT_PATH["sakura"]
    }

    
    if model == 'KYARU':
        res_image = get_base_by_name("frame_1.jpg")
    else:
        res_image = random_base()
    
    filename = os.path.basename(res_image.path)
    charaid = filename.lstrip('frame_')
    charaid = charaid.rstrip('.jpg')

    img = res_image.open()
    # Draw title
    draw = ImageDraw.Draw(img)
    text, title = generate_luck_info(charaid)

    text = text['content']
    font_size = 45
    color = '#F5F5F5'
    image_font_center = (140, 99)
    ttfront = ImageFont.truetype(font_path['title'], font_size)
    font_length = ttfront.getsize(title)
    draw.text((image_font_center[0]-font_length[0]/2, image_font_center[1]-font_length[1]/2),
                title, fill=color,font=ttfront)
    # Text rendering
    font_size = 25
    color = '#323232'
    image_font_center = [140, 297]
    ttfront = ImageFont.truetype(font_path['text'], font_size)
    result = decrement(text)
    if not result[0]:
        raise Exception('Unknown error in daily luck') 
    text_vertical = []
    for i in range(0, result[0]):
        font_height = len(result[i + 1]) * (font_size + 4)
        text_vertical = vertical(result[i + 1])
        x = int(image_font_center[0] + (result[0] - 2) * font_size / 2 + 
                (result[0] - 1) * 4 - i * (font_size + 4))
        y = int(image_font_center[1] - font_height / 2)
        draw.text((x, y), text_vertical, fill = color, font = ttfront)

    return img

def get_base_by_name(filename) -> R.ResImg:
    return R.img(os.path.join(BASE_LUCK_IMG_DIR, filename))

def random_base() -> R.ResImg:
    base_dir = R.img(BASE_LUCK_IMG_DIR).path
    random_img = random.choice(os.listdir(base_dir))
    return R.img(os.path.join(BASE_LUCK_IMG_DIR, random_img))

def generate_luck_info(charaid):
    for i in luck_desc:
        if charaid in i['charaid']:
            typewords = i['type']
            desc = random.choice(typewords)
            return desc, get_luck_type(desc)
    raise Exception('luck description not found')

def get_luck_type(desc):
    target_luck_type = desc['good-luck']
    for i in luck_type:
        if i['good-luck'] == target_luck_type:
            return i['name']
    raise Exception('luck type not found')

def decrement(text):
    length = len(text)
    result = []
    cardinality = 9
    if length > 4 * cardinality:
        return [False]
    number_of_slices = 1
    while length > cardinality:
        number_of_slices += 1
        length -= cardinality
    result.append(number_of_slices)
    # Optimize for two columns
    space = ' '
    length = len(text)
    if number_of_slices == 2:
        if length % 2 == 0:
            # even
            fill_in = space * int(9 - length / 2)
            return [number_of_slices, text[:int(length / 2)] + fill_in, fill_in + text[int(length / 2):]]
        else:
            # odd number
            fill_in = space * int(9 - (length + 1) / 2)
            return [number_of_slices, text[:int((length + 1) / 2)] + fill_in,
                                    fill_in + space + text[int((length + 1) / 2):]]
    for i in range(0, number_of_slices):
        if i == number_of_slices - 1 or number_of_slices == 1:
            result.append(text[i * cardinality:])
        else:
            result.append(text[i * cardinality:(i + 1) * cardinality])
    return result

def vertical(str):
    list = []
    for s in str:
        list.append(s)
    return '\n'.join(list)