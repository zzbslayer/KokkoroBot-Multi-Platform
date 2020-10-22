from datetime import datetime, timezone, timedelta

from kokkoro.common_interface import EventInterface
from .dao.sqlitedao import ClanDao, MemberDao, UserDao, LoginDao
from .exception import NotFoundError

class WebMaster():
    def __init__(self):
        super().__init__()
        self.clandao = ClanDao()
        self.memberdao = MemberDao()
        self.userdao = UserDao()
        self.logindao = LoginDao()


    def get_clan(self, gid):
        return self.clandao.findone(gid)
    def get_clan_by_uid(self, uid):
        return self.clandao.find_by_uid(uid)


    def get_member(self, uid, gid):
        mem = self.memberdao.find_one(uid, gid)
        return mem if mem else None
    def get_member_by_uid(self, uid):
        mems = self.memberdao.find_by(uid=uid)
        return mems if mems else None
    def mod_member(self, member:dict):
        return self.memberdao.modify(member)


    def get_or_add_user(self, uid, salt):
        return self.userdao.get_or_add(uid, salt)
    def get_user(self, uid):
        return self.userdao.find_one(uid)
    def mod_user(self, user:dict):
        return self.userdao.modify(user)


    def add_login(self, uid, auth_cookie, auth_cookie_expire_time):
        return self.logindao.add(uid, auth_cookie, auth_cookie_expire_time)
    def get_login(self, uid, auth_cookie):
        return self.logindao.find_one(uid, auth_cookie)
    def mod_login(self, login:dict):
        return self.logindao.modify(login)
    def del_login(self, uid):
        return self.logindao.delete(uid)
    def del_login_by_time(self, time):
        return self.logindao.delete_by_time(self, time)
