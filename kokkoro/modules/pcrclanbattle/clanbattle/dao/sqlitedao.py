import sqlite3
import os
import datetime
from kokkoro import logger
from ..exception import DatabaseError

DB_PATH = os.path.expanduser('~/.kokkoro/clanbattle.db')

class SqliteDao(object):
    def __init__(self, table, columns, fields):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self._dbpath = DB_PATH
        self._table = table
        self._columns = columns
        self._fields = fields
        self._create_table()


    def _create_table(self):
        sql = "CREATE TABLE IF NOT EXISTS {0} ({1})".format(self._table, self._fields)
        with self._connect() as conn:
            conn.execute(sql)


    def _connect(self):
        # detect_types 中的两个参数用于处理datetime
        return sqlite3.connect(self._dbpath, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)



class ClanDao(SqliteDao):

    SERVER_JP = 0x00
    SERVER_TW = 0x01
    SERVER_CN = 0x02

    def __init__(self):
        super().__init__(
            table='clan',
            columns='gid, name, server',
            fields='''
            gid TEXT NOT NULL PRIMARY KEY,
            name TEXT NOT NULL,
            server INT NOT NULL
            ''')


    @staticmethod
    def row2item(r):
        return {'gid': r[0], 'name': r[1], 'server': r[2]} if r else None


    def add(self, clan):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?)
                    '''.format(self._table, self._columns),
                    (clan['gid'], clan['name'], clan['server']) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[ClanDao.add] {e}')
                raise DatabaseError('添加公会失败')


    def delete(self, gid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE gid=?
                    '''.format(self._table),
                    (gid,) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[ClanDao.delete] {e}')
                raise DatabaseError('删除公会失败')


    def modify(self, clan):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET name=?, server=? WHERE gid=?
                    '''.format(self._table),
                    (clan['name'], clan['server'], clan['gid']) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[ClanDao.modify] {e}')
                raise DatabaseError('修改公会失败')


    def find_one(self, gid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE gid=?
                    '''.format(self._table, self._columns),
                    (gid,) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[ClanDao.find_one] {e}')
                raise DatabaseError('查找公会失败')


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0}
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[ClanDao.find_all] {e}')
                raise DatabaseError('查找公会失败')


    def find_by_uid(self, uid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT M.uid, C.gid, C.name
                    FROM MEMBER M INNER JOIN CLAN C
                    ON M.alt = C.gid
                    WHERE M.uid=?
                    ''',
                    (uid,) ).fetchall()
                return [
                    {'uid': r[0], 'gid': r[1], 'name': r[2]}
                    if r else None
                    for r in ret
                ]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_by_uid] {e}')
                raise DatabaseError('查找成员及公会失败')



class MemberDao(SqliteDao):
    def __init__(self):
        super().__init__(
            table='member',
            columns='uid, gid, name, last_sl, ' + \
                    'authority_group, last_login_time, last_login_ipaddr, ' + \
                    'login_code, login_code_available, login_code_expire_time, ' + \
                    'must_change_password, password, privacy, salt',
            fields='''
            uid TEXT NOT NULL,
            gid TEXT NOT NULL,
            name TEXT NOT NULL,
            last_sl INT,
            authority INT,
            last_login_time INT,
            last_login_ipaddr INT,
            login_code CHAR(6),
            login_code_available INT DEFAULT 0,
            login_code_expire_time INT DEFAULT 0,
            must_change_password INT DEFAULT 1,
            password CHAR(64),
            privacy INT DEFAULT 0,
            salt VARCHAR(16) NOT NULL,
            PRIMARY KEY (uid, gid)
            ''')

    @staticmethod
    def row2item(r, full=False):
        if full:
            return {
                'uid': r[0],
                'gid': r[1],
                'name': r[2],
                'last_sl': r[3],
                'authority_group': r[4],
                'last_login_time': r[5],
                'last_login_ipaddr': r[6],
                'login_code': r[7],
                'login_code_available': r[8],
                'login_code_expire_time': r[9],
                'must_change_password': r[10],
                'password': r[11],
                'privacy': r[12],
                'salt': r[13]
            } if r else None
        else:
            return {
                'uid': r[0],
                'gid': r[1],
                'name': r[2],
                'last_sl': r[3]
            } if r else None


    def get_or_add(self, uid, gid, name, authority_group, salt):
        with self._connect() as conn:
            try:
                ret = self.find_by(uid=uid, full=True)
                if 0 == len(ret):
                    conn.execute('''
                        INSERT INTO {0} ({1}) VALUES (?, ?, ?, ?, ?)
                        '''.format(self._table, 'uid, gid, name, authority_group, salt'),
                        (uid, gid, name, authority_group, salt)
                    )
                else:
                    r = ret[0]
                    conn.execute('''
                        INSERT OR IGNORE INTO {0} ({1}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        '''.format(self._table, self._columns),
                        (
                            uid, gid, name, r[3], authority_group,
                            r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]
                        )
                    )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.get_or_add] {e}')
                raise DatabaseError('添加成员失败')
        return self.find_one(uid, gid)


    def find_one(self, uid, gid, full=False):
        with self._connect() as conn:
            try:
                if full:
                    ret = conn.execute('''
                        SELECT {1} FROM {0} WHERE uid=? AND gid=?
                        '''.format(self._table, self._columns),
                        (uid, gid) ).fetchone()
                else:
                    ret = conn.execute('''
                        SELECT {1} FROM {0} WHERE uid=? AND gid=?
                        '''.format(self._table, 'uid, gid, name, last_sl'),
                        (uid, gid) ).fetchone()
                return self.row2item(ret, full)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_one] {e}')
                raise DatabaseError('查找成员失败')


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0}
                    '''.format(self._table, 'uid, gid, name, last_sl'),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_all] {e}')
                raise DatabaseError('查找成员失败')


    def find_by(self, uid=None, gid=None, full=False):
        cond_str = []
        cond_tup = []
        if not gid is None:
            cond_str.append('gid=?')
            cond_tup.append(gid)
        if not uid is None:
            cond_str.append('uid=?')
            cond_tup.append(uid)

        if 0 == len(cond_tup):
            return self.find_all()

        cond_str = " AND ".join(cond_str)

        target_columns = self._columns if full else 'uid, gid, name, last_sl'

        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2}
                    '''.format(self._table, target_columns, cond_str),
                    cond_tup ).fetchall()
                return [self.row2item(r, full) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_by] {e}')
                raise DatabaseError('查找成员失败')


    def modify(self, member, full=False, only_by_uid=False):
        with self._connect() as conn:
            try:
                if full:
                    if only_by_uid:
                        conn.execute('''
                            UPDATE {0} SET
                                last_login_time=?, last_login_ipaddr=?,
                                login_code=?, login_code_available=?, login_code_expire_time=?,
                                must_change_password=?, password=?, privacy=?, salt=?
                            WHERE uid=?
                            '''.format(self._table),
                            (
                                 member['last_login_time'], member['last_login_ipaddr'],
                                 member['login_code'], member['login_code_available'], member['login_code_expire_time'],
                                 member['must_change_password'], member['password'], member['privacy'], member['salt'],
                                 member['uid']
                            )
                        )
                    else:
                        conn.execute('''
                            UPDATE {0} SET
                                name=?, last_sl=?, authority_group=?,
                                last_login_time=?, last_login_ipaddr=?,
                                login_code=?, login_code_available=?, login_code_expire_time=?,
                                must_change_password=?, password=?, privacy=?, salt=?
                            WHERE uid=? AND gid=?
                            '''.format(self._table),
                            (
                                 member['name'], member['last_sl'], member['authority_group'],
                                 member['last_login_time'], member['last_login_ipaddr'],
                                 member['login_code'], member['login_code_available'], member['login_code_expire_time'],
                                 member['must_change_password'], member['password'], member['privacy'], member['salt'],
                                 member['uid'], member['gid']
                            )
                        )
                else:
                    conn.execute('''
                        UPDATE {0} SET name=?, last_sl=? WHERE uid=? AND gid=?
                        '''.format(self._table),
                        (member['name'], member['last_sl'], member['uid'], member['gid']) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.modify] {e}')
                raise DatabaseError('修改成员失败')


    def delete(self, uid, gid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE uid=? AND gid=?
                    '''.format(self._table),
                    (uid, gid) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.delete] {e}')
                raise DatabaseError('删除成员失败')


    def delete_by(self, uid=None, gid=None):
        cond_str = []
        cond_tup = []
        if not gid is None:
            cond_str.append('gid=?')
            cond_tup.append(gid)
        if not uid is None:
            cond_str.append('uid=?')
            cond_tup.append(uid)

        if 0 == len(cond_tup):
            raise DatabaseError('删除成员的条件有误')

        cond_str = " AND ".join(cond_str)

        with self._connect() as conn:
            try:
                cur = conn.execute('''
                    DELETE FROM {0} WHERE {1}
                    '''.format(self._table, cond_str),
                    cond_tup )
                return cur.rowcount
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.delete_by] {e}')
                raise DatabaseError('删除成员失败')


class BattleDao(SqliteDao):
    NORM    = 0x00
    LAST    = 0x01
    EXT     = 0x02
    TIMEOUT = 0x04

    def __init__(self, gid, cid, yyyy, mm):
        super().__init__(
            table=self.get_table_name(gid, cid, yyyy, mm),
            columns='eid, uid, alt, time, round, boss, dmg, flag',
            fields='''
            eid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            alt INT NOT NULL,
            time TIMESTAMP NOT NULL,
            round INT NOT NULL,
            boss  INT NOT NULL,
            dmg   INT NOT NULL,
            flag  INT NOT NULL
            ''')


    @staticmethod
    def get_table_name(gid, cid, yyyy, mm):
        return 'battle_%s_%d_%04d%02d' % (gid, cid, yyyy, mm)


    @staticmethod
    def row2item(r):
        return {
            'eid':  r[0], 'uid':   r[1], 'alt':  r[2],
            'time': r[3], 'round': r[4], 'boss': r[5],
            'dmg':  r[6], 'flag':  r[7] } if r else None


    def add(self, challenge):
        with self._connect() as conn:
            try:
                cur = conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (challenge['uid'], challenge['alt'], challenge['time'], challenge['round'], challenge['boss'], challenge['dmg'], challenge['flag']) )
                return cur.lastrowid
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.add] {e}')
                raise DatabaseError('添加记录失败')


    def delete(self, eid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE eid=?
                    '''.format(self._table),
                    (eid, ) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.delete] {e}')
                raise DatabaseError('删除记录失败')


    def modify(self, challenge):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET uid=?, alt=?, time=?, round=?, boss=?, dmg=?, flag=? WHERE eid=?
                    '''.format(self._table),
                    (challenge['uid'], challenge['alt'], challenge['time'], challenge['round'], challenge['boss'], challenge['dmg'], challenge['flag'], challenge['eid']) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.modify] {e}')
                raise DatabaseError('修改记录失败')


    def find_one(self, eid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE eid=?
                    '''.format(self._table, self._columns),
                    (eid, ) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.find_one] {e}')
                raise DatabaseError('查找记录失败')


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} ORDER BY round, boss, eid
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.find_all] {e}')
                raise DatabaseError('查找记录失败')


    def find_by(self, uid=None, alt=None, order_by_user=False):
        cond_str = []
        cond_tup = []
        order = 'round, boss, eid' if not order_by_user else 'uid, alt, round, boss, eid'
        if not uid is None:
            cond_str.append('uid=?')
            cond_tup.append(uid)
        if not alt is None:
            cond_str.append('alt=?')
            cond_tup.append(alt)
        if 0 == len(cond_tup):
            return self.find_all()

        cond_str = " AND ".join(cond_str)

        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2} ORDER BY {3}
                    '''.format(self._table, self._columns, cond_str, order), 
                    cond_tup ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.find_by] {e}')
                raise DatabaseError('查找记录失败')


class LoginDao(SqliteDao):
    def __init__(self):
        super().__init__(
            table='login',
            columns='uid, auth_cookie, auth_cookie_expire_time',
            fields='''
            uid TEXT NOT NULL,
            auth_cookie CHAR(64) NOT NULL,
            auth_cookie_expire_time INT NOT NULL,
            PRIMARY KEY(uid, auth_cookie)
            ''')

    @staticmethod
    def row2item(r):
        return {'uid': r[0], 'auth_cookie': r[1], 'auth_cookie_expire_time': r[2]} if r else None

    def add(self, uid, auth_cookie, auth_cookie_expire_time):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?)
                    '''.format(self._table, self._columns),
                    (uid, auth_cookie, auth_cookie_expire_time) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[LoginDao.add] {e}')
                raise DatabaseError('添加登录状态失败')

    def find_one(self, uid, auth_cookie):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE uid=? AND auth_cookie=?
                    '''.format(self._table, self._columns),
                    (uid, auth_cookie) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[LoginDao.find_one] {e}')
                raise DatabaseError('查找登录状态失败')

    def modify(self, login:dict):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    UPDATE {0} SET auth_cookie_expire_time=?
                    WHERE uid=? AND auth_cookie=?
                    '''.format(self._table),
                    (login['auth_cookie_expire_time'], login['uid'], login['auth_cookie']) )
                ret = conn.execute('''
                    UPDATE member SET last_login_time=?, last_login_ipaddr=?
                    WHERE uid=?
                    ''',
                    (login['last_login_time'], login['last_login_ipaddr']) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[LoginDao.find_one] {e}')
                raise DatabaseError('修改登录状态失败')

    def delete(self, uid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE uid=?
                    '''.format(self._table),
                    (uid,) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[LoginDao.delete] {e}')
                raise DatabaseError('删除登录状态失败')


    def delete_by_time(self, time):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE auth_cookie_expire_time<?
                    '''.format(self._table),
                    (time,) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[LoginDao.delete_by_time] {e}')
                raise DatabaseError('删除登录状态失败')

