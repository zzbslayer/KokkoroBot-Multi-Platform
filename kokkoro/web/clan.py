from quart import jsonify, redirect, request, session, url_for
from urllib.parse import urljoin
from kokkoro import config
import kokkoro.web.universal_executor as ue
from . import get_app
app = get_app()

from .templating import render_template, static_folder, template_folder

PATH = config.PUBLIC_BASEPATH

@app.route( urljoin(PATH, 'clan/<group_id>/'),
            methods=['GET'])
async def yobot_clan(group_id):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template( '404.html', item='公会' ), 404
    is_member = ue.get_member(bm, uid=session['yobot_user'])
    if (not is_member and user.authority_group >= 10):
        return await render_template('clan/unauthorized.html')
    return await render_template( 'clan/panel.html', is_member=is_member, )

@app.route( urljoin(PATH, 'clan/<group_id>/subscribers/'),
            methods=['GET'])
async def yobot_clan_subscribers(group_id):
    return '敬请期待'

@app.route( urljoin(PATH, 'clan/<group_id>/progress/'),
            methods=['GET'])
async def yobot_clan_progress(group_id):
    return await render_template( 'clan/progress.html', )

@app.route( urljoin(PATH, 'clan/<group_id>/statistics/'),
            methods=['GET'])
async def yobot_clan_statistics(group_id):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template( '404.html', item='公会' ), 404
    return await render_template(
        'clan/statistics.html',
        )

@app.route( urljoin(PATH, 'clan/<group_id>/statistics/<int:sid>/'),
            methods=['GET'])
async def yobot_clan_statistics_details(group_id, sid):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template( '404.html', item='公会' ), 404
    return await render_template( f'clan/statistics/statistics{sid}.html', )

@app.route( urljoin(PATH, 'clan/<group_id>/my/'),
            methods=['GET'])
async def yobot_clan_user_auto(group_id):
    if 'yobot_user' not in session:
        return redirect(url_for('yobot_login', callback=request.path))
    return redirect(url_for(
        'yobot_clan_user',
        group_id=group_id,
        uid=session['yobot_user'],
    ))

@app.route( urljoin(PATH, 'clan/<group_id>/<uid>/'),
            methods=['GET'])
async def yobot_clan_user(group_id, uid):
    if 'yobot_user' not in session:
        return redirect(url_for('yobot_login', callback=request.path))
    user = ue.get_user(session['yobot_user'])
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template('404.html', item='公会'), 404
    is_member = ue.get_member(bm, uid=session['yobot_user'])
    if (not is_member and user['authority_group'] >= 10):
        return await render_template('clan/unauthorized.html')
    return await render_template(
        'clan/user.html',
        uid=uid,
    )

@app.route( urljoin(PATH, 'clan/<group_id>/setting/'),
            methods=['GET'])
async def yobot_clan_setting(group_id):
    if 'yobot_user' not in session:
        return redirect(url_for('yobot_login', callback=request.path))
    user = ue.get_user(session['yobot_user'])
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template('404.html', item='公会'), 404
    is_member = ue.get_member(bm, uid=session['yobot_user'])
    if (not is_member):
        return await render_template(
            'unauthorized.html',
            limit='本公会成员',
            uath='无')
    if (user['authority_group'] >= 100):
        return await render_template(
            'unauthorized.html',
            limit='公会战管理员',
            uath='成员')
    return await render_template('clan/setting.html')

@app.route( urljoin(PATH, 'clan/<group_id>/api/'),
            methods=['POST'])
async def yobot_clan_api(group_id):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return jsonify(code=20, message='Group not exists')
    if 'yobot_user' not in session:
        if not(False and 'privacy'):
            return jsonify(code=10, message='Not logged in')
        uid = 0
    else:
        uid = session['yobot_user']
        user = ue.get_user(uid)
        is_member = ue.get_member(bm, uid=uid)
        if (user['authority_group'] >= 100 or not is_member):
            return jsonify(code=11, message='Insufficient authority')
    payload = await request.get_json()
    return ue.clan_api(bm, payload)

@app.route( urljoin(PATH, 'clan/<group_id>/statistics/api/'),
            methods=['GET'])
async def yobot_clan_statistics_api(group_id):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return jsonify(code=20, message="Group dosen't exist")
    apikey = request.args.get('apikey') or 'apikey'
    return await ue.clan_statistics_api(bm, apikey)

@app.route( urljoin(PATH, 'clan/<group_id>/setting/api/'),
            methods=['POST'])
async def yobot_clan_setting_api(group_id):
    if 'yobot_user' not in session:
        return jsonify(code=10, message='Not logged in')
    uid = session['yobot_user']
    user = ue.get_user(uid)
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return jsonify(code=20, message='Group not exists')
    is_member = ue.get_member(bm, uid=uid)
    if (user['authority_group'] >= 100 or not is_member):
        return jsonify(code=11, message='Insufficient authority')
    payload = await request.get_json()
    return ue.clan_setting_api(bm, payload)

