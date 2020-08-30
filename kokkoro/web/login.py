import os
from quart import Response, jsonify, make_response, redirect, request, send_file, session, url_for
from urllib.parse import urljoin
from kokkoro import config
from kokkoro.util import rand_string, add_salt_and_hash
import kokkoro.web.universal_executor as ue
from . import get_app
app = get_app()

from .templating import render_template, static_folder, template_folder

PATH = config.PUBLIC_BASEPATH
MAX_TRY_TIMES = 3
EXPIRED_TIME = 7 * 24 * 60 * 60  # 7 days
LOGIN_AUTH_COOKIE_NAME = 'yobot_login'

class ExceptionWithAdvice(RuntimeError):
    def __init__(self, reason: str, advice=''):
        super(ExceptionWithAdvice, self).__init__(reason)
        self.reason = reason
        self.advice = advice

def check_pwd(user, pwd) -> bool:
    if not user or not user['password'] or not user['salt']:
        raise ExceptionWithAdvice(
            'uid错误 或 您尚未设置密码',
            '请私聊机器人“!登录”后，再次选择[修改密码]修改'
        )
    if user['privacy'] >= MAX_TRY_TIMES:
        raise ExceptionWithAdvice(
            '密码错误次数过多，账号已锁定',
            '请私聊机器人“!重置密码”后，重新登录'
        )
    if not user['password'] == add_salt_and_hash(pwd, user['salt']):
        user['privacy'] += 1
        ue.mod_user(user)
        raise ExceptionWithAdvice(
            '密码错误',
            '如果忘记密码，请私聊机器人“!登录”后，再次选择[修改密码]修改，' + \
            '或私聊机器人“!重置密码”后，重新登录'
        )
    return True

def check_key(user, key):
    now = ue.now()
    if user is None or user['login_code'] != key:
        raise ExceptionWithAdvice(
            '无效的登录地址',
            '请检查登录地址是否完整且为最新'
        )
    if user['login_code_expire_time'] < now:
        raise ExceptionWithAdvice(
            '这个登录地址已过期',
            '请私聊机器人“!登录”获取新登录地址'
        )
    if not user['login_code_available']:
        raise ExceptionWithAdvice(
            '这个登录地址已被使用',
            '请私聊机器人“!登录”获取新登录地址'
        )
    return True

def recall_from_cookie(auth_cookie):
    advice = '请私聊机器人“!登录” 或 重新登录'
    if not auth_cookie:
        raise ExceptionWithAdvice('登录已过期', advice)
    s = auth_cookie.split(':')
    if len(s) != 2:
        raise ExceptionWithAdvice('Cookie异常', advice)
    uid, auth = s

    user = ue.get_user(uid)
    advice = '请先加入一个公会 或 私聊机器人“!登录”'
    if user is None:
        raise ExceptionWithAdvice('用户不存在', advice)
    salty_cookie = add_salt_and_hash(auth, user['salt'])
    userlogin = ue.get_login(uid, salty_cookie)
    if userlogin is None:
        raise ExceptionWithAdvice('Cookie异常', advice)
    now = ue.now()
    if userlogin['auth_cookie_expire_time'] < now:
        raise ExceptionWithAdvice('登录已过期', advice)
    user['last_login_time'] = now
    user['last_login_ipaddr'] = request.headers.get('X-Real-IP', request.remote_addr)
    ue.mod_user(user)

    return user

def set_auth_info(user:dict, res: Response = None, save_user=True):
    now = ue.now()
    session['yobot_user'] = user['uid']
    session['csrf_token'] = rand_string(16)
    session['last_login_time'] = user['last_login_time']
    session['last_login_ipaddr'] = user['last_login_ipaddr']
    user['last_login_time'] = now
    user['last_login_ipaddr'] = request.headers.get('X-Real-IP', request.remote_addr)
    if res:
        new_key = rand_string(32)
        ue.add_login(
            uid=user['uid'],
            auth_cookie=add_salt_and_hash(new_key, user['salt']),
            auth_cookie_expire_time=now + EXPIRED_TIME
        )
        new_cookie = f"{user['uid']}:{new_key}"
        res.set_cookie(LOGIN_AUTH_COOKIE_NAME, new_cookie, max_age=EXPIRED_TIME)
    if save_user:
        ue.mod_user(user)

@app.route( urljoin(PATH, 'login/'),
            methods=['GET', 'POST'])
async def yobot_login():
    def get_params(k: str) -> str:
        return request.args.get(k) \
            if request.method == "GET" \
            else (form and k in form and form[k])

    if request.method == "POST":
        form = await request.form

    try:
        uid = get_params('uid')
        key = get_params('key')
        pwd = get_params('pwd')
        callback_page = get_params('callback') or url_for('yobot_user')
        auth_cookie = request.cookies.get(LOGIN_AUTH_COOKIE_NAME)

        if not uid and not auth_cookie:
            return await render_template(
                'login.html',
                advice=f'请私聊机器人“!登录”获取登录地址 ',
            )
        key_failure = None
        if uid:
            user = ue.get_user(uid)
            if key:
                try:
                    check_key(user, key)
                except ExceptionWithAdvice as e:
                    if auth_cookie:
                        uid = None
                        key_failure = e
                    else:
                        raise e from e
            if pwd:
                check_pwd(user, pwd)
        if auth_cookie and not uid:
            # 可能用于用cookie寻回session

            if 'yobot_user' in session:
                # 会话未过期
                return redirect(callback_page)
            try:
                user = recall_from_cookie(auth_cookie)
            except ExceptionWithAdvice as e:
                if key_failure is not None:
                    raise key_failure
                else:
                    raise e from e
            set_auth_info(user)
            if user['must_change_password']:
                callback_page = url_for('yobot_reset_pwd')
            return redirect(callback_page)
        if not key and not pwd:
            raise ExceptionWithAdvice(
                "无效的登录地址",
                "请检查登录地址是否完整"
            )
        if user['must_change_password']:
            callback_page = url_for('yobot_reset_pwd')
        res = await make_response(redirect(callback_page))
        set_auth_info(user, res, save_user=False)
        ue.mod_user(user)
        return res
    except ExceptionWithAdvice as e:
        return await render_template(
            'login.html',
            reason=e.reason,
            advice=e.advice or '请私聊机器人“!登录”获取登录地址 ',
        )

@app.route( urljoin(PATH, 'login/c/'),
            methods=['GET', 'POST'])
async def yobot_login_code():
    return await send_file(os.path.join(template_folder, "login-code.html"))

@app.route( urljoin(PATH, 'logout/'),
            methods=['GET', 'POST'])
async def yobot_logout():
    session.clear()
    res = await make_response(redirect(url_for('yobot_login')))
    res.delete_cookie(LOGIN_AUTH_COOKIE_NAME)
    return res

@app.route( urljoin(PATH, 'user/'),
    endpoint='yobot_user',
    methods=['GET'])
@app.route( urljoin(PATH, 'admin/'),
    endpoint='yobot_admin',
    methods=['GET'])
async def yobot_user():
    if 'yobot_user' not in session:
        return redirect(url_for('yobot_login', callback=request.path))
    user = ue.get_user_with_clan(session['yobot_user'])
    bm = ue.get_bm(user['gid'])
    groups = ue.list_group_by_member(bm, user['uid'])
    return await render_template(
        'user.html',
        user=user,
        clan_groups=[{
            'group_id': g['gid'],
            'group_name': g['name'] or g['gid']
        } for g in groups],
    )

@app.route(
    urljoin(PATH, 'user/<uid>/'),
    methods=['GET'])
async def yobot_user_info(uid):
    if 'yobot_user' not in session:
        return redirect(url_for('yobot_login', callback=request.path))
    if session['yobot_user'] == uid:
        visited_user_info = ue.get_user_with_member(uid)
    else:
        visited_user = ue.get_user_with_member(uid)
        if visited_user is None:
            return '没有此用户', 404
        visited_user_info = visited_user
    return await render_template(
        'user-info.html',
        user=visited_user_info,
        visitor=ue.get_user_with_member(session['yobot_user']),
    )

@app.route(
    urljoin(PATH,
            'user/<uid>/api/'),
    methods=['GET', 'PUT'])
async def yobot_user_info_api(uid):
    if 'yobot_user' not in session:
        return jsonify(code=10, message='未登录')
    user = ue.get_user(session['yobot_user'])
    if user['uid'] != uid and user['authority_group'] >= 100:
        return jsonify(code=11, message='权限不足')
    user_data = ue.get_user_with_clan(uid)
    if user_data is None:
        return jsonify(code=20, message='用户不存在')
    if request.method == 'GET':
        return jsonify(
            code=0,
            nickname=user_data['name'],
            authority_group=user_data['authority_group'],
            clan_group_id=user_data['gid'],
            last_login_time=user_data['last_login_time'],
            last_login_ipaddr=user_data['last_login_ipaddr'],
        )
    new_setting = await request.get_json()
    if new_setting is None:
        return jsonify(code=30, message='消息体格式错误')
    new_nickname = new_setting.get('nickname')
    if new_nickname is None:
        return jsonify(code=32, message='消息体内容错误')
    bm = ue.get_bm(user_data['gid'])
    ue.mod_member(bm, user_data['uid'], user_data['gid'], new_nickname, 1)
    return jsonify(code=0, message='success')

@app.route(
    urljoin(PATH, 'user/reset-password/'),
    methods=['GET', 'POST'])
async def yobot_reset_pwd():
    try:
        if 'yobot_user' not in session:
            return redirect(url_for('yobot_login', callback=request.path))
        if request.method == "GET":
            return await render_template('password.html')

        uid = session['yobot_user']
        user = ue.get_user(uid)
        if user is None:
            raise Exception("请先加公会")
        form = await request.form
        pwd = form["pwd"]
        user['password'] = add_salt_and_hash(pwd, user['salt'])
        user['privacy'] = 0
        user['must_change_password'] = False
        ue.mod_user(user)
        # 踢掉过去的登录
        ue.del_login(uid)
        return await render_template(
            'password.html',
            success="密码设置成功",
        )
    except Exception as e:
        return await render_template(
            'password.html',
            error=str(e)
        )