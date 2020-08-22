import os
import base64

from io import BytesIO
from PIL import Image

from kokkoro.util import join_iterable
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

_meme = ['表情包', '表情']
show_meme_prefix = join_iterable(_meme, ['列表']) + join_iterable(['查看'], _meme) + ('meme-list',)
@sv.on_fullmatch(show_meme_prefix)
async def show_memes(bot: KokkoroBot, event: EventInterface):
	msg = "当前表情有："
	for meme in img_name:
		msg += "\n" + meme
	await bot.kkr_send(event, msg, at_sender=True)

_refresh = ['刷新', '更新']
refresh_meme_prefix = join_iterable(_meme, _refresh) + join_iterable(_refresh, _meme) + ('meme-refresh',)
@sv.on_fullmatch(refresh_meme_prefix)
async def reload_memes(bot: KokkoroBot, event: EventInterface):
	load_images()
	await bot.kkr_send(event, f"表情列表更新成功，现在有{len(img)}张表情")

def parse_alias(alias):
	alias_dict = MemeGenerator.alias
	for item in alias_dict.items():
		if alias in item[1]:
			return item[0]
	return alias

_gen=['生成']
gen_meme_prefix = join_iterable(_meme, _gen) + join_iterable(_refresh, _gen) + ('meme-gen',)
@sv.on_prefix(gen_meme_prefix)
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
