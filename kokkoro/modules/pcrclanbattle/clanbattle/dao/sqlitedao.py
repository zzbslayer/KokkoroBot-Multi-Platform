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
                    ON M.gid = C.gid
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



class MemberDao(SqliteDao):
    def __init__(self):
        super().__init__(
            table='member',
            columns='uid, gid, name, last_sl, authority_group',
            fields='''
            uid TEXT NOT NULL,
            gid TEXT NOT NULL,
            name TEXT NOT NULL,
            last_sl INT,
            authority_group INT,
            PRIMARY KEY (uid, gid)
            ''')

    @staticmethod
    def row2item(r):
        return {
            'uid': r[0],
            'gid': r[1],
            'name': r[2],
            'last_sl': r[3],
            'authority_group': r[4]
        } if r else None


    def add(self, member):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (member['uid'], member['gid'], member['name'], None, None)
                )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.add] {e}')
                raise DatabaseError('添加成员失败')


    def find_one(self, uid, gid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE uid=? AND gid=?
                    '''.format(self._table, self._columns),
                    (uid, gid) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_one] {e}')
                raise DatabaseError('查找成员失败')


    def find_all(self):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0}
                    '''.format(self._table, self._columns),
                    ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_all] {e}')
                raise DatabaseError('查找成员失败')


    def find_by(self, uid=None, gid=None):
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

        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE {2}
                    '''.format(self._table, self._columns, cond_str),
                    cond_tup ).fetchall()
                return [self.row2item(r) for r in ret]
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[MemberDao.find_by] {e}')
                raise DatabaseError('查找成员失败')


    def modify(self, member):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET name=?, last_sl=?, authority_group=? WHERE uid=? AND gid=?
                    '''.format(self._table),
                    (member['name'], member['last_sl'], member['authority_group'],
                     member['uid'], member['gid']) )
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

    def __init__(self, gid, yyyy, mm):
        super().__init__(
            table=self.get_table_name(gid, yyyy, mm),
            columns='eid, uid, time, round, boss, dmg, flag',
            fields='''
            eid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            time TIMESTAMP NOT NULL,
            round INT NOT NULL,
            boss  INT NOT NULL,
            dmg   INT NOT NULL,
            flag  INT NOT NULL
            ''')


    @staticmethod
    def get_table_name(gid, yyyy, mm):
        return 'battle_%s_%04d%02d' % (gid, yyyy, mm)


    @staticmethod
    def row2item(r):
        return {
            'eid':  r[0], 'uid':   r[1],
            'time': r[2], 'round': r[3], 'boss': r[4],
            'dmg':  r[5], 'flag':  r[6] } if r else None


    def add(self, challenge):
        with self._connect() as conn:
            try:
                cur = conn.execute('''
                    INSERT INTO {0} ({1}) VALUES (NULL, ?, ?, ?, ?, ?, ?)
                    '''.format(self._table, self._columns),
                    (challenge['uid'], challenge['time'], challenge['round'], challenge['boss'], challenge['dmg'], challenge['flag']) )
                return cur.lastrowid
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.add] {e}')
                raise DatabaseError('添加记录失败')


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


    def find_by(self, uid=None, order_by_user=False):
        cond_str = []
        cond_tup = []
        order = 'round, boss, eid' if not order_by_user else 'uid, round, boss, eid'
        if not uid is None:
            cond_str.append('uid=?')
            cond_tup.append(uid)
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


    def modify(self, challenge):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET uid=?, time=?, round=?, boss=?, dmg=?, flag=? WHERE eid=?
                    '''.format(self._table),
                    (challenge['uid'], challenge['time'], challenge['round'], challenge['boss'], challenge['dmg'], challenge['flag'], challenge['eid']) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[BattleDao.modify] {e}')
                raise DatabaseError('修改记录失败')


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


class UserDao(SqliteDao):
    def __init__(self):
        super().__init__(
            table='user',
            columns='uid, last_login_time, last_login_ipaddr, ' + \
                    'login_code, login_code_available, login_code_expire_time, ' + \
                    'must_change_password, password, privacy, salt',
            fields='''
            uid TEXT NOT NULL PRIMARY KEY,
            last_login_time INT,
            last_login_ipaddr INT,
            login_code CHAR(6),
            login_code_available INT DEFAULT 0,
            login_code_expire_time INT DEFAULT 0,
            must_change_password INT DEFAULT 1,
            password CHAR(64),
            privacy INT DEFAULT 0,
            salt VARCHAR(16) NOT NULL,
            ''')

    @staticmethod
    def row2item(r):
        return {
            'uid': r[0],
            'last_login_time': r[1],
            'last_login_ipaddr': r[2],
            'login_code': r[3],
            'login_code_available': r[4],
            'login_code_expire_time': r[5],
            'must_change_password': r[6],
            'password': r[7],
            'privacy': r[8],
            'salt': r[9]
        } if r else None


    def get_or_add(self, uid, salt):
        with self._connect() as conn:
            try:
                conn.execute('''
                    INSERT OR IGNORE INTO {0} (uid, salt) VALUES (?, ?)
                    '''.format(self._table),
                    (uid, salt) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[UserDao.get_or_add] {e}')
                raise DatabaseError('添加用户失败')
        return self.find_one(uid)


    def find_one(self, uid):
        with self._connect() as conn:
            try:
                ret = conn.execute('''
                    SELECT {1} FROM {0} WHERE uid=?
                    '''.format(self._table, self._columns),
                    (uid,) ).fetchone()
                return self.row2item(ret)
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[UserDao.find_one] {e}')
                raise DatabaseError('查找用户失败')


    def modify(self, user:dict):
        with self._connect() as conn:
            try:
                conn.execute('''
                    UPDATE {0} SET  last_login_time=?, last_login_ipaddr=?,
                    login_code=?, login_code_available=?, login_code_expire_time=?,
                    must_change_password=?, password=?, privacy=?, salt=?
                    WHERE uid=?
                    '''.format(self._table),
                    (
                        user['last_login_time'], user['last_login_ipaddr'],
                        user['login_code'], user['login_code_available'], user['login_code_expire_time'],
                        user['must_change_password'], user['password'], user['privacy'],
                        user['salt'], user['uid'])
                    )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[UserDao.modify] {e}')
                raise DatabaseError('修改用户失败')


    def delete(self, uid):
        with self._connect() as conn:
            try:
                conn.execute('''
                    DELETE FROM {0} WHERE uid=?
                    '''.format(self._table),
                    (uid,) )
            except (sqlite3.DatabaseError) as e:
                logger.error(f'[UserDao.delete] {e}')
                raise DatabaseError('删除用户失败')


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
        return {
            'uid': r[0],
            'auth_cookie': r[1],
            'auth_cookie_expire_time': r[2]
        } if r else None

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
                    UPDATE user SET last_login_time=?, last_login_ipaddr=? WHERE uid=?
                    ''',
                    (login['last_login_time'], login['last_login_ipaddr'], login['uid']) )
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

