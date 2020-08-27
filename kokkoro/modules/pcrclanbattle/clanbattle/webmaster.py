from datetime import datetime, timezone, timedelta

from kokkoro import config
from kokkoro.util import rand_string
from .dao.sqlitedao import UserDao, UserLoginDao
from .exception import NotFoundError

class WebMaster(object):
    def __init__(self, group):
        super().__init__()
        self.group = group
        self.userdao = UserDao()
        self.userlogindao = UserLoginDao()
        
    def get_or_add_user(self, uid):
        authority_group = 100
        if uid in config.SUPER_USER:
            authority_group = 1
        return self.userdao.get_or_add(uid, authority_group, rand_string())

    def mod_user(self, user:dict):
        return self.userdao.modify(user)