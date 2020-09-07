import math, sqlite3, os, random, asyncio, time

from kokkoro.service import Service
from kokkoro.common_interface import EventInterface, KokkoroBot
from kokkoro.modules.priconne import chara, _pcr_data

import kokkoro


sv = Service('avatarguess', help_='''
猜头像 | 猜猜机器人随机发送的头像的一小部分来自哪位角色
猜头像群排行 | 显示猜头像小游戏猜对次数的群排行榜(只显示前十名)
'''.strip())


PIC_SIDE_LENGTH = 25 
ONE_TURN_TIME = 20
EXPIRE_TIME = 120
DB_PATH = os.path.expanduser(f'~/.kokkoro/pcr_avatar_guess_winning_counter.db')
BLACKLIST_ID = [
    1072, 1908, 4031, 9000, 1000,
    9601, 9602, 9603, 9604, # horse
    ]

class WinnerJudger:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_chara_id = {}
    
    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)
        
    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''
        
    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False
    
    def set_correct_chara_id(self, gid, cid):
        self.correct_chara_id[gid] = cid
    
    def get_correct_chara_id(self, gid):
        return self.correct_chara_id[gid] if self.correct_chara_id.get(gid) is not None else chara.UNKNOWN
    
    def turn_on(self, gid):
        self.on[gid] = True
        
    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_chara_id[gid] = chara.UNKNOWN


winner_judger = WinnerJudger()


class WinningCounter:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._create_table()


    def _connect(self):
        return sqlite3.connect(DB_PATH)


    def _create_table(self):
        try:
            self._connect().execute('''CREATE TABLE IF NOT EXISTS WINNINGCOUNTER
                          (GID             STR    NOT NULL,
                           UID             STR    NOT NULL,
                           COUNT           INT    NOT NULL,
                           PRIMARY KEY(GID, UID));''')
        except:
            raise Exception('创建表发生错误')
    
    
    def _record_winning(self, gid, uid):
        try:
            winning_number = self._get_winning_number(gid, uid)
            conn = self._connect()
            conn.execute("INSERT OR REPLACE INTO WINNINGCOUNTER (GID,UID,COUNT) \
                                VALUES (?,?,?)", (gid, uid, winning_number+1))
            conn.commit()       
        except:
            raise Exception('更新表发生错误')


    def _get_winning_number(self, gid, uid):
        try:
            r = self._connect().execute("SELECT COUNT FROM WINNINGCOUNTER WHERE GID=? AND UID=?",(gid,uid)).fetchone()        
            return 0 if r is None else r[0]
        except:
            raise Exception('查找表发生错误')

@sv.on_fullmatch(('猜头像排行榜', '猜头像群排行'))
async def description_guess_group_ranking(bot: KokkoroBot, ev: EventInterface):
    members = ev.get_members_in_group()
    card_winningcount_dict = {}
    winning_counter = WinningCounter()
    for member in members:
        if member.get_id() != ev.get_author_id():
            card_winningcount_dict[member.get_nick_name()] = winning_counter._get_winning_number(ev.get_group_id(), member.get_id())
    group_ranking = sorted(card_winningcount_dict.items(), key = lambda x:x[1], reverse = True)
    msg = '猜头像小游戏此群排行为:\n'
    for i in range(min(len(group_ranking), 10)):
        if group_ranking[i][1] != 0:
            msg += f'第{i+1}名: {group_ranking[i][0]}, 猜对次数: {group_ranking[i][1]}次\n'
    await bot.kkr_send(ev, msg.strip())

'''
wait           show answer and new round           new round
---------next_time--------------------expire_time--------->
'''
start_time_dict = {}
@sv.on_fullmatch('猜头像')
async def avatar_guess(bot: KokkoroBot, ev: EventInterface):
    try:
        gid = ev.get_group_id()
        if winner_judger.get_on_off_status(gid):
            start = start_time_dict[gid]
            next_time = start + ONE_TURN_TIME
            expire_time = start + EXPIRE_TIME
            now = time.time()
            if now < next_time:
                msg = f'{int(next_time - now)}秒后才能够结束本轮猜头像0x0'
                await bot.kkr_send(ev, msg)
                return
            elif next_time <= now and now <= expire_time:
                correct_id = winner_judger.get_correct_chara_id(gid)
                c = chara.fromid(correct_id)
                msg =  f'正确答案是: {c.name}\n很遗憾，没有人答对~'
                # winner_judger.turn_off(gid) # finally turn on
                await bot.kkr_send(ev, msg)
                await bot.kkr_send(ev, c.icon)
            # else:
            ## do nothing. just a new round
               
                
        winner_judger.turn_on(gid)
        chara_id_list = list(_pcr_data.CHARA_NAME.keys())
        while True:
            random.shuffle(chara_id_list)
            if chara_id_list[0] not in BLACKLIST_ID: break
        winner_judger.set_correct_chara_id(gid, chara_id_list[0])
        dir_path = os.path.join(os.path.expanduser(kokkoro.config.RES_DIR), 'img', 'priconne', 'unit')
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        c = chara.fromid(chara_id_list[0])
        img = c.icon.open()
        left = math.floor(random.random()*(129-PIC_SIDE_LENGTH))
        upper = math.floor(random.random()*(129-PIC_SIDE_LENGTH))
        cropped_img = img.crop((left, upper, left+PIC_SIDE_LENGTH, upper+PIC_SIDE_LENGTH))
        
        msg = f'猜猜这个图片是哪位角色头像的一部分?\n回答时请加前缀 ag\n示例：ag 可可萝'
        await bot.kkr_send(ev, msg)
        await bot.kkr_send(ev, cropped_img)

        start_time_dict[gid] = time.time()
        
    except Exception as e:
        winner_judger.turn_off(gid)
        raise e

@sv.on_fullmatch('公布答案')
async def avatar_guess(bot: KokkoroBot, ev: EventInterface):   
    gid = ev.get_group_id()
    if winner_judger.get_on_off_status(gid):
        correct_id = winner_judger.get_correct_chara_id(gid)
        c = chara.fromid(correct_id)
        msg =  f'正确答案是: {c.name}\n很遗憾，没有人答对~'
        await bot.kkr_send(ev, msg)
        await bot.kkr_send(ev, c.icon)

        winner_judger.turn_off(gid)
    else:
        await bot.kkr_send(ev, "尚未开始猜头像0x0")
        
@sv.on_prefix(('ag'))
async def on_input_chara_name(bot: KokkoroBot, ev: EventInterface):
    gid = ev.get_group_id()
    uid = ev.get_author_id()
    if winner_judger.get_on_off_status(gid):
        s = ev.get_param().remain
        cid = chara.name2id(s)
        correct_id = winner_judger.get_correct_chara_id(gid)
        if cid != chara.UNKNOWN and cid == correct_id and winner_judger.get_winner(gid) == '':
            winner_judger.record_winner(gid, uid)
            winning_counter = WinningCounter()
            winning_counter._record_winning(gid, uid)
            winning_count = winning_counter._get_winning_number(gid, uid)
            nick = ev.get_author().get_nick_name()
            msg_part = f'{nick}猜对了，真厉害！TA已经猜对{winning_count}次了~'
            c = chara.fromid(correct_id)
            msg =  f'正确答案是: {c.name}'
            await bot.kkr_send(ev, msg)
            await bot.kkr_send(ev, c.icon)
            await bot.kkr_send(ev, msg_part)

            winner_judger.turn_off(gid)
            del start_time_dict[gid]