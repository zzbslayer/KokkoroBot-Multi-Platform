import sqlite3
import pandas as pd
import datetime
from PIL import Image,ImageFont,ImageDraw
from os import path

from ..dao.sqlitedao import DB_PATH

FONT_PATH = "/usr/share/fonts/Microsoft YaHei.ttf" # defined in dockerfile

def add_text(img: Image,text:str,textsize:int,font=FONT_PATH,textfill='white',position:tuple=(0,0)):
    #textsize 文字大小
    #font 字体，默认微软雅黑
    #textfill 文字颜色，默认白色
    #position 文字偏移（0,0）位置，图片左上角为起点
    img_font = ImageFont.truetype(font=font,size=textsize)
    draw = ImageDraw.Draw(img)
    draw.text(xy=position,text=text,font=img_font,fill=textfill)
    return img

def get_data(gid: str, month: int) -> (str,pd.DataFrame):

    conn = sqlite3.connect(DB_PATH)

    now = datetime.datetime.now()
    year = now.year

    month = str(month) if month>=10 else "0"+str(month)

    # get name
    command = f'SELECT * from clan'
    dt = pd.read_sql(command, conn)
    name = dt[dt["gid"]==gid]["name"].iloc[0]

    command = f'SELECT * FROM battle_{gid}_1_{year}{month}'
    dat = pd.read_sql(command, conn)

    conn.close()
    return name,dat

def get_person(gid: str, uid: str, month: int) -> (str,pd.DataFrame):

    name,dat = get_data(gid, month)
    dat = dat[dat["uid"] == uid]

    challenges = dat[["boss","dmg","flag"]]

    return name,challenges





