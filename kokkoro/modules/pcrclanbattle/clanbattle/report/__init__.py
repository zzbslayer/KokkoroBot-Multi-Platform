'''
该插件由 HoshinoBot 群友提供
以下是作者相关信息：

倚栏待月——基础代码编写
明见——背景图片与字体提供
qq3193377836
魔法の書——增强显示效果
'''

本插件以GPL-v3协议开源。

from io import BytesIO
import os
import requests
from PIL import Image

import matplotlib.pyplot as plt
from .data_source import add_text, get_data, get_person
import base64
import pandas as pd
import numpy as np
import datetime

from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro.service import Service
from kokkoro.util import FreqLimiter
from kokkoro import R

from .. import sv, cb_cmd

_time_limit = 30*60
_lmt = FreqLimiter(_time_limit)

b_constellations = ["摩羯","水瓶","双鱼","白羊","金牛","双子","巨蟹","狮子","处女","天秤","天蝎","射手"] #国服的（预测）

background1 = R.img('priconne/公会离职报告模板.jpg')
background2 = R.img('priconne/公会本期报告模板.jpg')

REPORT_RESIGN = 0
REPORT_NORMAL = 1
REPORT_UNDECLARED = -1

sv = Service('clanbattle-retire')

@sv.on_fullmatch('离职报告')
async def send_resign_report(bot:KokkoroBot, event:EventInterface):
    await send_report(bot, event, type=REPORT_RESIGN)

@sv.on_fullmatch('会战报告')
async def send_normal_report(bot:KokkoroBot, event:EventInterface):
    await send_report(bot, event, type=REPORT_NORMAL)


async def send_report(bot:KokkoroBot, event:EventInterface, type=REPORT_UNDECLARED):

    if type not in (REPORT_RESIGN,REPORT_NORMAL):
        await bot.kkr_send(event, "类型错误！", at_sender=True)
        return

    uid = event.get_author_id()
    nickname = event.get_author().get_nick_name()
    gid = event.get_group_id()

    if not _lmt.check(uid):
        await bot.kkr_send(event, f'每{int(_time_limit/60)}分钟仅能生成一次报告', at_sender=True)
        return
    _lmt.start_cd(uid)

    now = datetime.datetime.now()
    year = now.year
    month = now.month-1
    if month==0:
        year -= 1
        month = 12
    constellation = b_constellations[month-1]

    try:
        clanname, challenges = get_person(gid,uid,month)
    except Exception as e:
        await bot.kkr_send(event, f"出现错误: {str(e)}\n请联系开发组调教。")
        return

    if challenges.shape[0] == 0:
        await bot.kkr_send(event, "您没有参加本次公会战。请再接再厉！", at_sender=True)
        return

    total_chl = 0
    miss_chl = 0
    damage_to_boss: list = [0 for i in range(5)]
    times_to_boss: list = [0 for i in range(5)]
    truetimes_to_boss: list = [0 for i in range(5)]
    total_damage = 0

    for idx,chl in challenges.iterrows():
        total_damage += chl['dmg']
        times_to_boss[chl['boss']-1] += 1
        if chl['flag'] == 0:
            damage_to_boss[chl['boss']-1] += chl['dmg']
            truetimes_to_boss[chl['boss']-1] += 1
        if chl['flag'] != 1:
            total_chl += 1
        if chl['dmg'] == 0:
        	miss_chl += 1

    avg_day_damage = int(total_damage/6)
    df=pd.DataFrame({'a':damage_to_boss,'b':truetimes_to_boss})
    result=(df.a/df.b).replace(np.inf,0).fillna(0)
    avg_boss_damage = list(result)
    if total_chl >= 18:
        disable_chl = 0
        attendance_rate = 100
    else:
        disable_chl = 18 - total_chl
        attendance_rate = round(total_chl/18*100,2)

    #日期转字符串
    year=str(year)
    month=str(month)
    
    #设置中文字体
    plt.rcParams['font.family'] = ['Microsoft YaHei']
    x = [f'{x}王' for x in range(1,6)]
    y = times_to_boss
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制刀数柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x()+0.1, h, f'{int(times_to_boss[i])}刀',fontdict={"size":12})
    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img1 = Image.open(buf)
    #清空图
    plt.clf()

    x = [f'{x}王' for x in range(1,6)]
    y = avg_boss_damage
    plt.figure(figsize=(4.3,2.8))
    ax = plt.axes()

    #设置标签大小
    plt.tick_params(labelsize=15)

    #设置y轴不显示刻度
    plt.yticks([])

    #绘制均伤柱状图
    recs = ax.bar(x,y,width=0.618,color=['#fd7fb0','#ffeb6b','#7cc6f9','#9999ff','orange'],alpha=0.4)

    #删除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    #设置数量显示
    for i in range(0,5):
        rec = recs[i]
        h = rec.get_height()
        plt.text(rec.get_x(), h, f'{int(avg_boss_damage[i]/10000)}万',fontdict={"size":12})

    buf = BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=120)
    bar_img2 = Image.open(buf)

    #将饼图和柱状图粘贴到模板图,mask参数控制alpha通道，括号的数值对是偏移的坐标
    current_folder = os.path.dirname(__file__)
    img = background1.open() if type==REPORT_RESIGN else background2.open()
    R
    img.paste(bar_img1, (580,950), mask=bar_img1.split()[3])
    img.paste(bar_img2, (130,950), mask=bar_img2.split()[3])

    #添加文字到img
    row1 = f'''
    {total_chl}

    {disable_chl}

    {total_damage}
    '''
    row2 = f'''
    {attendance_rate}%

    {miss_chl}

    {avg_day_damage}
    '''
    
    add_text(img, row1, position=(380,630), textsize=35, textfill='black')
    add_text(img, row2, position=(833,630), textsize=35, textfill='black')
    add_text(img, year, position=(355,438), textsize=40, textfill='black')
    add_text(img, month, position=(565,438), textsize=40, textfill='black')
    add_text(img, constellation, position=(710,438), textsize=40, textfill='black')
    if len(clanname) <= 7:
        add_text(img, clanname, position=(300+(7-len(clanname))/2*40, 515), textsize=40, textfill='black')
    else:
        add_text(img, clanname, position=(300+(10-len(clanname))/2*30, 520), textsize=30, textfill='black')
    add_text(img, nickname, position=(280,365), textsize=35, textfill='white')
    #输出
    await bot.kkr_send(event, img)
    plt.close('all')


