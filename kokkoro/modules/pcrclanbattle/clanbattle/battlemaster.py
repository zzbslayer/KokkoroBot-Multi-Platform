from datetime import datetime, timezone, timedelta

from kokkoro import config
from .dao.sqlitedao import ClanDao, MemberDao, BattleDao
from .exception import NotFoundError

def get_config():
    return config.modules.pcrclanbattle.boss_config


class BattleMaster(object):

    NORM    = BattleDao.NORM
    LAST    = BattleDao.LAST
    EXT     = BattleDao.EXT
    TIMEOUT = BattleDao.TIMEOUT

    SERVER_JP = ClanDao.SERVER_JP
    SERVER_TW = ClanDao.SERVER_TW
    SERVER_CN = ClanDao.SERVER_CN

    SERVER_JP_NAME = ('jp', 'JP', 'Jp', '日', '日服', str(SERVER_JP))
    SERVER_TW_NAME = ('tw', 'TW', 'Tw', '台', '台服', str(SERVER_TW))
    SERVER_CN_NAME = ('cn', 'CN', 'Cn', '国', '国服', 'B', 'B服', str(SERVER_CN))

    def __init__(self, group):
        super().__init__()
        self.group = group
        self.clandao = ClanDao()
        self.memberdao = MemberDao()
        self.config = get_config()


    @staticmethod
    def get_timezone_num(server):
        return 9 if BattleMaster.SERVER_JP == server else 8


    @staticmethod
    def get_yyyymmdd(time, zone_num:int=8):
        '''
        返回time对应的会战年月日。
        其中，年月为该期会战的年月；日为刷新周期对应的日期。
        会战为每月最后一星期，编程时认为mm月的会战一定在mm月20日至mm+1月10日之间，每日以5:00 UTC+8为界。
        注意：返回的年月日并不一定是自然时间，如2019年9月2日04:00:00我们认为对应2019年8月会战，日期仍为1号，将返回(2019,8,1)
        '''
        # 日台服均为当地时间凌晨5点更新，故减5
        time = time.astimezone(timezone(timedelta(hours=zone_num-5)))
        yyyy = time.year
        mm = time.month
        dd = time.day
        if dd < 20:
            mm = mm - 1
        if mm < 1:
            mm = 12
            yyyy = yyyy - 1
        return (yyyy, mm, dd)


    @staticmethod
    def next_boss(round_:int, boss:int):
        return (round_, boss + 1) if boss < 5 else (round_ + 1, 1)


    @staticmethod
    def get_stage(round_, server):
        if server == BattleMaster.SERVER_CN:
            y, m, _ = BattleMaster.get_yyyymmdd(datetime.now(), 8)
            if y == 2020:
                if m < 9:
                    return 5 if round_ == 1 else 6
                elif m < 12:
                    return 7 if round_ <= 3 else 8
        # All other situation
        return 4 if round_ >= 35 else 3 if round_ >= 11 else 2 if round_ >= 4 else 1


    def get_boss_info(self, round_, boss, server):
        """@return: boss_max_hp, score_rate"""
        stage = BattleMaster.get_stage(round_, server)
        config = self.config
        boss_hp = config[ config["BOSS_HP"][server] ][ stage-1 ][ boss-1 ]
        score_rate = config[ config["SCORE_RATE"][server] ][ stage-1 ][ boss-1 ]
        return boss_hp, score_rate


    def get_boss_hp(self, round_, boss, server):
        stage = BattleMaster.get_stage(round_, server)
        config = self.config
        return config[ config["BOSS_HP"][server] ][ stage-1 ][ boss-1 ]


    def get_score_rate(self, round_, boss, server):
        stage = BattleMaster.get_stage(round_, server)
        config = self.config
        return config[ config["SCORE_RATE"][server] ][ stage-1 ][ boss-1 ]


    @staticmethod
    def int2kanji(x):
        if 0 <= x <= 50:
            return '零一二三四五六七八九十⑪⑫⑬⑭⑮⑯⑰⑱⑲廿㉑㉒㉓㉔㉕㉖㉗㉘㉙卅㉛㉜㉝㉞㉟㊱㊲㊳㊴㊵㊶㊷㊸㊹㊺㊻㊼㊽㊾㊿'[x]
        raise ValueError("'x' should in range [0, 50]")

    @staticmethod
    def get_server_code(server_name):
        if server_name in BattleMaster.SERVER_JP_NAME:
            return BattleMaster.SERVER_JP
        elif server_name in BattleMaster.SERVER_TW_NAME:
            return BattleMaster.SERVER_TW
        elif server_name in BattleMaster.SERVER_CN_NAME:
            return BattleMaster.SERVER_CN
        else:
            return -1


    def get_battledao(self, time):
        clan = self.get_clan()
        zone_num = self.get_timezone_num(clan['server'])
        yyyy, mm, _ = self.get_yyyymmdd(time, zone_num)
        return BattleDao(self.group, yyyy, mm)


    def add_clan(self, name, server):
        return self.clandao.add({'gid': self.group, 'name': name, 'server': server})
    def get_clan(self):
        return self.clandao.find_one(self.group)
    def has_clan(self):
        return True if self.clandao.find_one(self.group) else False
    def list_clan(self):
        return [self.clandao.find_one(self.group)]
    def list_clan_by_uid(self, uid):
        return self.clandao.find_by_uid(uid)
    def mod_clan(self, name, server):
        return self.clandao.modify({'gid': self.group, 'name': name, 'server': server})
    def del_clan(self):
        return self.clandao.delete(self.group)


    def add_member(self, uid, name):
        return self.memberdao.add({'uid': uid, 'gid': self.group, 'name': name})
    def get_member(self, uid):
        mem = self.memberdao.find_one(uid, self.group)
        return mem if mem else None
    def has_member(self, uid):
        mem = self.memberdao.find_one(uid, self.group)
        return True if mem else False
    def list_member(self):
        return self.memberdao.find_by(gid=self.group)
    def list_account(self, uid):
        return self.memberdao.find_by(gid=self.group, uid=uid)
    def mod_member(self, uid, new_name, new_sl, new_auth):
        return self.memberdao.modify(
            {
                'uid': uid,
                'gid': self.group,
                'name': new_name,
                'last_sl': new_sl,
                'authority_group': new_auth
            }
        )
    def del_member(self, uid):
        return self.memberdao.delete(uid, self.group)
    def clear_member(self):
        return self.memberdao.delete_by(gid=self.group)


    def add_challenge(self, uid, round_, boss, dmg, flag, time):
        mem = self.get_member(uid)
        if not mem or mem['gid'] != self.group:
            raise NotFoundError('未找到成员')
        challenge = {
            'uid':   uid,
            'time':  time,
            'round': round_,
            'boss':  boss,
            'dmg':   dmg,
            'flag':  flag
        }
        dao = self.get_battledao(time)
        return dao.add(challenge)

    def get_challenge(self, eid, time):
        dao = self.get_battledao(time)
        return dao.find_one(eid)

    def list_challenge(self, time):
        dao = self.get_battledao(time)
        return dao.find_all()

    def list_challenge_of_user(self, uid, gid, time):
        mem = self.memberdao.find_one(uid, gid)
        if not mem or mem['gid'] != self.group:
            return []
        dao = self.get_battledao(time)
        return dao.find_by(uid=uid)

    def mod_challenge(self, eid, uid, round_, boss, dmg, flag, time):
        mem = self.get_member(uid)
        if not mem or mem['gid'] != self.group:
            raise NotFoundError('未找到成员')
        challenge = {
            'eid':   eid,
            'uid':   uid,
            'time':  time,
            'round': round_,
            'boss':  boss,
            'dmg':   dmg,
            'flag':  flag
        }
        dao = self.get_battledao(time)
        return dao.modify(challenge)

    def del_challenge(self, eid, time):
        dao = self.get_battledao(time)
        return dao.delete(eid)


    @staticmethod
    def filt_challenge_of_day(challenge_list, time, zone_num:int=8):
        _, _, day = BattleMaster.get_yyyymmdd(time, zone_num)
        return list(filter(lambda challen: day == BattleMaster.get_yyyymmdd(challen['time'], zone_num)[2], challenge_list))


    def list_challenge_of_day(self, time, zone_num:int=8):
        return self.filt_challenge_of_day(self.list_challenge(time), time, zone_num)


    def list_challenge_of_user_of_day(self, uid, time, zone_num:int=8):
        return self.filt_challenge_of_day(self.list_challenge_of_user(uid, self.group, time), time, zone_num)


    def stat_challenge(self, time, only_one_day=True, zone_num:int=8):
        '''
        统计每个成员的出刀
        return [(member, [challenge])]
        '''
        ret = []
        mem = self.list_member()
        dao = self.get_battledao(time)
        for m in mem:
            challens = dao.find_by(uid=m['uid'])
            if only_one_day:
                challens = self.filt_challenge_of_day(challens, time, zone_num)
            ret.append((m, challens))
        return ret


    def stat_damage(self, time):
        '''
        统计各成员的本月各Boss伤害总量
        :return: [(uid, name, [total_dmg, dmg1, ..., dmg5])]
        '''
        clan = self.get_clan()
        if not clan:
            raise NotFoundError(f'未找到公会')
        server = clan['server']
        stat = self.stat_challenge(time, only_one_day=False, zone_num=self.get_timezone_num(server))
        ret = []
        for mem, challens in stat:
            dmgs = [0] * 6
            for ch in challens:
                d = ch['dmg']
                dmgs[0] += d
                dmgs[ch['boss']] += d
            ret.append((mem['uid'], mem['name'], dmgs))
        return ret


    def stat_score(self, time):
        '''
        统计各成员的本月总分数
        :return: [(uid,name,score)]
        '''
        clan = self.get_clan()
        if not clan:
            raise NotFoundError(f'未找到公会')
        server = clan['server']
        stat = self.stat_challenge(time, only_one_day=False, zone_num=self.get_timezone_num(server))
        ret = [
            (mem['uid'], mem['name'], sum(map(lambda ch: round(self.get_score_rate(ch['round'], ch['boss'], server) * ch['dmg']), challens)))
            for mem, challens in stat
        ]
        return ret


    def list_challenge_remain(self, time):
        '''
        return [(uid,name,remain_n,remain_e)]

        norm + timeout + last == 3 - remain_n       // 正常出刀数 == 3 - 余刀数
        last - ext == remain_e                      // 尾刀数 - 补时刀数 == 补时余刀
        challen_cnt == norm + last + ext + timeout  // 列表长度 == 所有出刀
        故有==>
        remain_n = 3 - (norm + timeout + last)
        remain_e = last - ext
        '''
        def count(challens):
            norm = 0
            last = 0
            ext = 0
            timeout = 0
            for ch in challens:
                f = ch['flag']
                if f & BattleMaster.EXT:
                    ext = ext + 1
                elif f & BattleMaster.LAST:
                    last = last + 1
                elif f & BattleMaster.TIMEOUT:
                    timeout = timeout + 1
                else:
                    norm = norm + 1
            return norm, last, ext, timeout

        clan = self.get_clan()
        if not clan:
            raise NotFoundError(f'未找到公会')
        ret = []
        stat = self.stat_challenge(time, only_one_day=True, zone_num=self.get_timezone_num(clan['server']))
        for mem, challens in stat:
            norm, last, ext, timeout = count(challens)
            r = (
                mem['uid'],
                mem['name'],
                3 - (norm + timeout + last),
                last - ext,
            )
            ret.append(r)
        return ret


    def get_challenge_progress(self, time):
        '''
        return (round, boss, remain_hp)
        '''
        clan = self.get_clan()
        if not clan:
            return None
        server = clan['server']
        dao = self.get_battledao(time)
        challens = dao.find_all()
        if not len(challens):
            return ( 1, 1, self.get_boss_hp(1, 1, server) )
        round_ = challens[-1]['round']
        boss = challens[-1]['boss']
        remain_hp = self.get_boss_hp(round_, boss, server)
        for challen in reversed(challens):
            if challen['round'] == round_ and challen['boss'] == boss:
                remain_hp = remain_hp - challen['dmg']
            else:
                break
        if remain_hp <= 0:
            round_, boss = self.next_boss(round_, boss)
            remain_hp = self.get_boss_hp(round_, boss, server)
        return (round_, boss, remain_hp)
