import os
import jinja2
from quart import jsonify, send_file, session, request, url_for
import kokkoro.web.universal_executor as ue
from . import get_app
app = get_app()

''' routing start -----------------------------------------------------------'''
# add route for static files
@app.route("/assets/<path:filename>", methods=["GET"])
async def yobot_static(filename):
    return await send_file(
        os.path.join(os.path.dirname(__file__), "static", filename))

# TODO: session

@app.route('/')
async def hello():
    return "Hello! " + ue.hello()

@app.route('/clan/<group_id>/',
            methods=['GET'])
async def yobot_clan_home(group_id):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template( '404.html', item='公会' ), 404
    #is_member = ue.get_member(bm, uid=session['yobot_user'])
    is_member = None # FIXME
    #if (not is_member and user.authority_group >= 10):
    #if not is_member:
    #    return await render_template('clan/unauthorized.html')
    return await render_template( 'clan/panel.html', is_member=is_member, )

@app.route( '/clan/<group_id>/progress/',
            methods=['GET'])
async def yobot_clan_progress(group_id):
    return await render_template( 'clan/progress.html', )

@app.route( '/clan/<group_id>/statistics/',
            methods=['GET'])
async def yobot_clan_statistics(group_id):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template( '404.html', item='公会' ), 404
    return await render_template(
        'clan/statistics.html',
        )

@app.route( '/clan/<group_id>/statistics/<int:sid>/',
            methods=['GET'])
async def yobot_clan_statistics_details(group_id, sid):
    bm = ue.get_bm(group_id)
    group = ue.get_group(bm)
    if group is None:
        return await render_template( '404.html', item='公会' ), 404
    return await render_template( f'clan/statistics/statistics{sid}.html', )

@app.route('/clan/<group_id>/api/',
            methods=['POST'])
async def yobot_clan_api(group_id):
    payload = await request.get_json()
    return ue.clan_api(group_id, payload)

@app.route( '/clan/<group_id>/statistics/api/',
            methods=['GET'])
async def yobot_clan_statistics_api(group_id):
    apikey = 'apikey' # request.args.get('apikey')
    return await ue.clan_statistics_api(group_id, apikey)
''' routing end -------------------------------------------------------------'''

''' templating start --------------------------------------------------------'''
static_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), './static'))
template_folder = os.path.abspath(os.path.join(
    os.path.dirname(__file__), './template'))

def _vertioned_url_for(endpoint, *args, **kwargs):
    if endpoint == 'yobot_static':
        kwargs['v'] = 'unknown'
    return url_for(endpoint, *args, **kwargs)

_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_folder),
    enable_async=True,
)
_env.globals['session'] = session
_env.globals['url_for'] = _vertioned_url_for

async def render_template(template, **context):
    t = _env.get_template(template)
    return await t.render_async(**context)
''' templating end ----------------------------------------------------------'''
