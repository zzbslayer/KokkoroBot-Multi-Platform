from kokkoro.modules.pcrclanbattle.clanbattle.battlemaster import BattleMaster
from kokkoro.modules.pcrclanbattle.clanbattle.webmaster import WebMaster
from kokkoro import logger
from typing import Any, Dict, List, NewType, Optional, Tuple, Union
import time
from datetime import datetime, timedelta
from quart import jsonify, make_response

SERVER_NAME = { 0x00: 'jp', 0x01: 'tw', 0x02: 'cn' }
ClanBattleReport = NewType('ClanBattleReport', List[Dict[str, Any]])


''' route_elucidator side start -------------------------------------------- '''
def now():
    return int(time.time())

def clan_api(bm:BattleMaster, uid, payload):
    try:
        clan = check_clan(bm)
        zone = bm.get_timezone_num(clan['server'])
        if payload is None:
            return jsonify(code=30, message='Invalid payload')
        action = payload['action']
        if action == 'get_member_list':
            mems = bm.list_member(1)
            members = [{'uid': m['uid'], 'nickname': m['name']} for m in mems]
            return jsonify(code=0, members=members)
        elif action == 'get_data':
            return jsonify(
                code=0,
                bossData=get_boss_data(bm),
                groupData={
                    'group_id': bm.group,
                    'group_name': clan['name'],
                    'game_server': SERVER_NAME[clan['server']],
                    'level_4': False # FIXME
                },
                selfData={
                    'is_admin': False,
                    'user_id': uid,
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
    except KeyError as e:
        logger.error(e)
        return jsonify(code=31, message='missing key: '+str(e))
    except Exception as e:
        logger.exception(e)
        return jsonify(code=40, message='server error')

async def clan_statistics_api(bm:BattleMaster, apikey, ):
    try:
        clan = check_clan(bm)
        report = get_report(bm, None, None, 0)
        mems = bm.list_member(1)
        members = [{'uid': m['uid'], 'nickname': m['name']} for m in mems]
        groupinfo = {
            'group_id': bm.group,
            'group_name': clan['name'],
            'game_server': SERVER_NAME[clan['server']],
            'battle_id': 0,
        }
        response = await make_response(jsonify(
            code=0,
            message='OK',
            api_version=1,
            challenges=report,
            groupinfo=groupinfo,
            members=members,
        ))
        #if (group.privacy & 0x2):
        #    response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    except KeyError as e:
        logger.error(e)
        return jsonify(code=31, message='missing key: '+str(e))
    except Exception as e:
        logger.exception(e)
        return jsonify(code=40, message='server error')

async def clan_statistics_api(bm, payload):
    try:
        if payload is None:
            return jsonify(code=30, message='Invalid payload')
        if payload.get('csrf_token') != session['csrf_token']:
            return jsonify(code=15, message='Invalid csrf_token')
        action = payload['action']
        clan = check_clan(bm)
        if action == 'get_setting':
            return jsonify(
                code=0,
                groupData={
                    'group_name': clan['name'],
                    'game_server': SERVER_NAME[clan['server']],
                    'battle_id': 0,
                },
                #privacy=group.privacy,
                #notification=group.notification,
            )
        elif action == 'put_setting':
            # clan['server'] = payload['game_server']
            # clan['notification = payload['notification']
            # clan['privacy'] = payload['privacy']
            # clan.save()
            # logger.info('网页 成功 {} {} {}'.format(
            #     uid, group_id, action))
            # return jsonify(code=0, message='success')
            return jsonify(code=22, message='unfinished action')
        elif action == 'get_data_slot_record_count':
            # counts = self.get_data_slot_record_count(group_id)
            # logger.info('网页 成功 {} {} {}'.format(
            #     uid, group_id, action))
            # return jsonify(code=0, message='success', counts=counts)
            return jsonify(code=22, message='unfinished action')
        # elif action == 'new_data_slot':
        #     self.new_data_slot(group_id)
        #     logger.info('网页 成功 {} {} {}'.format(
        #         uid, group_id, action))
        #     return jsonify(code=0, message='success')
        elif action == 'clear_data_slot':
            # battle_id = payload.get('battle_id')
            # self.clear_data_slot(group_id, battle_id)
            # logger.info('网页 成功 {} {} {}'.format(
            #     uid, group_id, action))
            # return jsonify(code=0, message='success')
            return jsonify(code=22, message='unfinished action')
        elif action == 'switch_data_slot':
            # battle_id = payload['battle_id']
            # self.switch_data_slot(group_id, battle_id)
            # logger.info('网页 成功 {} {} {}'.format(
            #     uid, group_id, action))
            # return jsonify(code=0, message='success')
            return jsonify(code=22, message='unfinished action')
        else:
            return jsonify(code=32, message='unknown action')
    except KeyError as e:
        logger.error(e)
        return jsonify(code=31, message='missing key: '+str(e))
    except Exception as e:
        logger.exception(e)
        return jsonify(code=40, message='server error')

''' route_elucidator side end ---------------------------------------------- '''

''' BattleMaster side start ------------------------------------------------ '''
def get_bm(group_id) -> BattleMaster:
    bm = BattleMaster(group_id)
    return bm

def check_clan(bm:BattleMaster):
    clan = bm.get_clan(1)
    return None if not clan else clan

def get_group(bm:BattleMaster):
    clan = check_clan(bm)
    if not clan:
        return jsonify(code=20, message="Group dosen't exist")
    return clan

def get_boss_data(bm:BattleMaster):
    clan = check_clan(bm)
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

def mod_member(bm:BattleMaster, uid, alt, new_name, new_cid):
    return bm.mod_member(uid, alt, new_name, new_cid)

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
    if ts == 0: # get all of the challenge
        dt = datetime.now()
        challen = bm.list_challenge(1, dt)
    else:       # get challenge of one day
        dt = datetime.fromtimestamp(ts) if ts is not None else datetime.now()
        challen = bm.list_challenge_of_day(1, dt, zone)
    for c in challen:
        ctime = int(c['time'].timestamp())
        remain = 0 if bool(c['flag'] & bm.LAST) else c['dmg'] * (-1)
        report.append({
            'battle_id': 0,
            'uid': c['uid'],
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

''' BattleMaster side end -------------------------------------------------- '''

''' WebMaster side start --------------------------------------------------- '''
def get_user(uid):
    wm = WebMaster()
    return wm.get_user(uid)

def get_user_with_member(uid):
    wm = WebMaster()
    return wm.get_user_with_member(uid)

def get_user_with_clan(uid):
    wm = WebMaster()
    return wm.get_user_with_clan(uid)

def mod_user(user:dict):
    wm = WebMaster()
    return wm.mod_user(user)

def add_login(uid, auth_cookie, auth_cookie_expire_time):
    wm = WebMaster()
    return wm.add_login(uid, auth_cookie, auth_cookie_expire_time)
def get_login(uid, auth_cookie):
    wm = WebMaster()
    return wm.get_login(uid, auth_cookie)
def del_login(uid):
    wm = WebMaster()
    return wm.del_login(uid)

''' WebMaster side end ----------------------------------------------------- '''
