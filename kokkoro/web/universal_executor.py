from kokkoro.modules.pcrclanbattle.clanbattle.battlemaster import BattleMaster
from typing import Any, Dict, List, NewType, Optional, Tuple, Union
import time
from datetime import datetime, timedelta
from quart import jsonify


ClanBattleReport = NewType('ClanBattleReport', List[Dict[str, Any]])

def hello():
    return "骑士君~"

def clan_home(group_id):
    pass

def clan_api(group_id, payload):
    bm = BattleMaster(group_id)
    clan = bm.get_clan(1)
    if not clan:
        return jsonify(code=20, message="Group dosen't exist")
    zone = bm.get_timezone_num(clan['server'])

    # TODO: session

    if payload is None:
        return jsonify(code=30, message='Invalid payload')
    action = payload['action']
    if action == 'get_member_list':
        mems = bm.list_member(1)
        members = [{'qqid': m['uid'], 'nickname': m['name']} for m in mems]
        return jsonify(code=0, members=members)
    elif action == 'get_data':
        pass
    elif action == 'get_challenge':
        d = int(datetime.now().timestamp() + (zone-5)*3600 ) / 86400 + 1
        report = get_report(
            bm,
            None,
            None,
            payload['ts'],
        )
        return jsonify(
            code=0,
            challenges=report,
            today=d,
        )
    else:
        return jsonify(code=32, message='unknown action')

def get_report(bm: BattleMaster,
               battle_id: Union[str, int, None],
               userid: Optional[str] = None,
               ts: Optional[int] = None,
               ) -> ClanBattleReport:
    clan = bm.get_clan(1)
    if not clan:
        return jsonofy(code=20, message="Group dosen't exist")
    zone = bm.get_timezone_num(clan['server'])
    report = []
    dt = datetime.fromtimestamp(ts) if ts is not None else datetime.now()
    challen = bm.list_challenge_of_day(1, dt, zone)
    for c in challen:
        ctime = int(c['time'].timestamp())
        report.append({
            'battle_id': 0,
            'qqid': c['uid'],
            'challenge_time': c['time'].isoformat(),
            'challenge_pcrdate': int(ctime/86400) + 1,
            'challenge_pcrtime': int(ctime%86400),
            'cycle': c['round'],
            'boss_num': c['boss'],
            'health_ramain': 0,
            'damage': c['dmg'],
            'is_continue': 1 if c['flag'] & bm.EXT else 0,
            'message': "",
            'behalf': 0,
            })
    return report
