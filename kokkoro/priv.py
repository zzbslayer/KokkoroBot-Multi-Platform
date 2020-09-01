from datetime import datetime

import kokkoro

BLACK = -999
DEFAULT = 0
NORMAL = 1
PRIVATE = 10
ADMIN = 21
OWNER = 22
WHITE = 51
SUPERUSER = 999

#===================== block list =======================#
_black_group = {}  # Dict[group_id, expr_time]
_black_user = {}  # Dict[user_id, expr_time]

def is_super_user(user_id):
    return user_id in kokkoro.config.SUPER_USER

def set_block_group(group_id, time):
    _black_group[group_id] = datetime.now() + time


def set_block_user(user_id, time):
    if not is_super_user(user_id):
        _black_user[user_id] = datetime.now() + time


def check_block_group(group_id):
    if group_id in _black_group and datetime.now() > _black_group[group_id]:
        del _black_group[group_id]  # 拉黑时间过期
        return False
    return bool(group_id in _black_group)


def check_block_user(user_id):
    if user_id in _black_user and datetime.now() > _black_user[user_id]:
        del _black_user[user_id]  # 拉黑时间过期
        return False
    return bool(user_id in _black_user)


#========================================================#


def get_user_priv(user):
    if check_block_user(user.get_id()):
        return BLACK
    return user.get_priv()

def check_priv(user, require: int) -> bool:
    return get_user_priv(user) >= require
