import os
import base64

from io import BytesIO
from PIL import Image

from kokkoro.service import Service
from kokkoro.common_interface import *
from kokkoro.config.modules.groupmaster import MemeGenerator

from .memeutil import draw_meme

img_dir = os.path.join(os.path.expanduser(kokkoro.config.RES_DIR), 'img', 'meme')

img = []
img_name = []

def load_images():
	global img,img_name,img_dir
	img = os.listdir(img_dir)
	img_name = [''.join(s.split('.')[:-1]) for s in img]

load_images()

sv = Service('meme-generator')

@sv.on_fullmatch(('表情包列表', '表情列表','查看表情列表', 'meme-list'))
async def show_memes(bot: KokkoroBot, event: EventInterface):
	msg = "当前表情有："
	for meme in img_name:
		msg += "\n" + meme
	await bot.kkr_send(event, msg, at_sender=True)

@sv.on_fullmatch(('更新表情', '更新表情包', '刷新表情', '刷新表情包', '更新表情列表','刷新表情列表', 'meme-refresh'))
async def reload_memes(bot: KokkoroBot, event: EventInterface):
	load_images()
	await bot.kkr_send(event, f"表情列表更新成功，现在有{len(img)}张表情")

def parse_alias(alias):
	alias_dict = MemeGenerator.alias
	for item in alias_dict.items():
		if alias in item[1]:
			return item[0]
	return alias

@sv.on_prefix(('生成表情','生成表情包', 'meme-gen'))
async def generate_meme(bot: KokkoroBot, event: EventInterface):
	msg = event.get_param().remain.split(' ')

	if len(msg) == 1:
		await bot.kkr_send(event, 'Usage: 生成表情 <表情名> <文字>')
		return

	sel = msg[0]
	sel = parse_alias(sel)
	if sel not in img_name:
		await bot.kkr_send(event,f'没有找到表情<{sel}> 0x0',at_sender=True)
		return

	idx = img_name.index(sel)
	image = Image.open(os.path.join(img_dir,img[idx]))
	message = " ".join(msg[1:])
	message = message.replace("\r","\n")
	meme = draw_meme(image,message)

	await bot.kkr_send(event, meme)
