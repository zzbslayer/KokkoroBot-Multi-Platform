from kokkoro.modules.pcrclanbattle.clanbattle.battlemaster import BattleMaster
from typing import Any, Dict, List, NewType, Optional, Tuple, Union
import time
from datetime import datetime, timedelta
from quart import jsonify

''' route_elucidator side start ---------------------------------------------'''
def hello():
    return ""

def clan_api(group_id, payload):
    bm = BattleMaster(group_id)
    clan = _check_clan(bm)
    if not clan:
        return jsonify(code=20, message="Group dosen't exist")
    zone = bm.get_timezone_num(clan['server'])
    if payload is None:
        return jsonify(code=30, message='Invalid payload')
    action = payload['action']
    if action == 'get_member_list':
        mems = bm.list_member(1)
        members = [{'qqid': m['uid'], 'nickname': m['name']} for m in mems]
        return jsonify(code=0, members=members)
    elif action == 'get_data':
        return jsonify(
            code=0,
            bossData=get_boss_data(bm),
            groupData={
                'group_id': group_id,
                'group_name': "GROUP_NAME", #group.group_name,
                'game_server': "cn", # FIXME
                'level_4': False # FIXME
            },
            selfData={
                'is_admin': False,
                'user_id': "114514",
                'today_sl': False
            }
        )
    elif action == 'get_challenge':
        d = int((datetime.now().timestamp()+(zone-5)*3600)/86400) + 1
        report = get_report(
            bm,
            None,
            None,
            payload['ts'],
        )
        if report is None:
            return jsonofy(code=20, message="Group dosen't exist")
        return jsonify(
            code=0,
            challenges=report,
            today=d,
        )
    elif action == 'update_boss':
        return jsonify(
            code=22,
            message='unfinished action'
        )
    else:
        return jsonify(code=32, message='unknown action')
''' route_elucidator side end -----------------------------------------------'''

''' BattleMaster side start -------------------------------------------------'''
def get_bm(group_id) -> BattleMaster:
    bm = BattleMaster(group_id)
    return bm

def _check_clan(bm:BattleMaster):
    clan = bm.get_clan(1)
    return None if not clan else clan

def get_group(bm:BattleMaster):
    clan = _check_clan(bm)
    if not clan:
        return jsonify(code=20, message="Group dosen't exist")
    return clan

def get_boss_data(bm:BattleMaster):
    clan = _check_clan(bm)
    if not clan:
        return jsonify(code=20, message="Group dosen't exist")
    r, b, hp = bm.get_challenge_progress(1, datetime.now())
    max_hp, score_rate = bm.get_boss_info(r, b, clan['server'])
    boss_data = {
        "challenger": None,
        "challenging_comment": "",
        "cycle": r,
        "num": b,
        "health": hp,
        "full_health": max_hp,
        "lock_type": 1
    }
    return boss_data

def get_member(bm:BattleMaster, uid):
    member = bm.get_member(uid, bm.group)
    return None if not member else member

ClanBattleReport = NewType('ClanBattleReport', List[Dict[str, Any]])

def get_report(bm: BattleMaster,
               battle_id: Union[str, int, None],
               userid: Optional[str] = None,
               ts: Optional[int] = None,
               ) -> ClanBattleReport:
    clan = bm.get_clan(1)
    if not clan:
        return None
    zone = bm.get_timezone_num(clan['server'])
    report = []
    dt = datetime.fromtimestamp(ts) if ts is not None else datetime.now()
    challen = bm.list_challenge_of_day(1, dt, zone)
    for c in challen:
        ctime = int(c['time'].timestamp())
        remain = 0 if bool(c['flag'] & bm.LAST) else c['dmg'] * (-1)
        report.append({
            'battle_id': 0,
            'qqid': c['uid'],
            'challenge_time': ctime,
            'challenge_pcrdate': int(ctime/86400) + 1,
            'challenge_pcrtime': int(ctime%86400),
            'cycle': c['round'],
            'boss_num': c['boss'],
            'health_remain': remain,
            'damage': c['dmg'],
            'is_continue': bool(c['flag'] & bm.EXT),
            'message': None,
            'behalf': None,
            })
    return report

''' BattleMaster side end ---------------------------------------------------'''
