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

def clan_api(bm:BattleMaster, payload):
    try:
        clan = check_clan(bm)
        zone = bm.get_timezone_num(clan['server'])
        action = payload['action']
        if payload['uid'] == 0:
              # 允许游客查看
              if action not in ['get_member_list', 'get_challenge']:
                  return jsonify(code=10, message='Not logged in')
        if action == 'get_member_list':
            mems = bm.list_member()
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
                    'level_4': False
                },
                selfData={
                    'is_admin': False,
                    'user_id': payload['uid'],
                    'today_sl': False
                }
            )
        elif action == 'get_challenge':
            d = int((datetime.now().timestamp()+(zone-5)*3600)/86400) + 1
            report = get_report(bm, None, payload['ts'])
            if report is None:
                return jsonofy(code=20, message="Group dosen't exist")
            return jsonify(
                code=0,
                challenges=report,
                today=d,
            )
        elif action == 'get_user_challenge':
            report = get_report(bm, payload['target_uid'], 0)
            try:
                visited_user = get_member(bm, payload['target_uid'])
            except:
                return jsonify(code=20, message='user not found')
            return jsonify(
                code=0,
                challenges=report,
                game_server=SERVER_NAME[clan['server']],
                user_info={
                    'uid': payload['target_uid'],
                    'nickname': visited_user['name']
                }
            )
        elif action == 'send_remind':

            return jsonify(code=0, notice='发送成功')
        else:
            return jsonify(code=32, message='unknown action')
    except KeyError as e:
        logger.error(e)
        return jsonify(code=31, message='missing key: '+str(e))
    except Exception as e:
        logger.exception(e)
        return jsonify(code=40, message='server error')

async def clan_statistics_api(bm:BattleMaster, apikey):
    try:
        clan = check_clan(bm)
        report = get_report(bm, None, 0)
        mems = bm.list_member()
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

def clan_setting_api(bm:BattleMaster, payload):
    try:
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
                privacy=3,
                notification=1023,
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
    clan = bm.get_clan()
    return None if not clan else clan

def get_group(bm:BattleMaster):
    clan = check_clan(bm)
    if not clan:
        return jsonify(code=20, message="Group dosen't exist")
    return clan

def list_group_by_member(bm:BattleMaster, uid):
    return bm.list_clan_by_uid(uid)

def get_boss_data(bm:BattleMaster):
    clan = check_clan(bm)
    if not clan:
        return jsonify(code=20, message="Group dosen't exist")
    r, b, hp = bm.get_challenge_progress(datetime.now())
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
    member = bm.get_member(uid)
    return None if not member else member

def mod_member(bm:BattleMaster, uid, new_name, new_sl, new_auth):
    return bm.mod_member(uid, new_name, new_sl, new_auth)

def get_report(bm: BattleMaster,
               userid: str = None,
               ts: int = None,
               ) -> ClanBattleReport:
    clan = bm.get_clan()
    if not clan:
        return None
    zone = bm.get_timezone_num(clan['server'])
    report = []
    if userid is None:
        if ts == 0: # get all of the challenge
            dt = datetime.now()
            challen = bm.list_challenge(dt)
        else:       # get challenge of one day
            dt = datetime.fromtimestamp(ts) if ts is not None else datetime.now()
            challen = bm.list_challenge_of_day(dt, zone)
    else:
        if ts == 0: # get all challenge of the user
            dt = datetime.now()
            challen = bm.list_challenge_of_user(userid, dt)
        else:       # get challenge of the user of one day
            dt = datetime.fromtimestamp(ts) if ts is not None else datetime.now()
            challen = bm.list_challenge_of_user_of_day(userid, dt, zone)
    for c in challen:
        ctime = int(c['time'].timestamp())
        report.append({
            'battle_id': 0,
            'uid': c['uid'],
            'challenge_time': ctime,
            'challenge_pcrdate': int(ctime/86400) + 1,
            'challenge_pcrtime': int(ctime%86400),
            'cycle': c['round'],
            'boss_num': c['boss'],
            'damage': c['dmg'],
            'health_remain': c['remain'],
            'is_continue': bool(c['flag'] & bm.EXT),
            'message': None,
            'behalf': None,
            })
    return report

''' BattleMaster side end -------------------------------------------------- '''

''' WebMaster side start --------------------------------------------------- '''
def get_wm():
    return WebMaster()

''' WebMaster side end ----------------------------------------------------- '''
