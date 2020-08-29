from quart import Response, jsonify, make_response, redirect, request, send_file, session, url_for
from urllib.parse import urljoin
from kokkoro import config
from kokkoro.util import rand_string, add_salt_and_hash
import kokkoro.web.universal_executor as ue
from . import get_app
app = get_app()

from .templating import render_template, static_folder, template_folder

PATH = config.PUBLIC_BASEPATH

@app.route( urljoin(PATH, 'admin/setting/'),
            methods=['GET'])
async def yobot_setting():
    return "敬请期待"

@app.route( urljoin(PATH, 'admin/setting/api/'),
            methods=['GET', 'PUT'])
async def yobot_setting_api():
    return "敬请期待"

@app.route( urljoin(PATH, 'admin/users/'),
        methods=['GET'])
async def yobot_users_managing():
    return "敬请期待"

@app.route( urljoin(PATH, 'admin/users/api/'),
        methods=['POST'])
async def yobot_users_api():
    return "敬请期待"

@app.route( urljoin(PATH, 'admin/groups/'),
        methods=['GET'])
async def yobot_groups_managing():
    return "敬请期待"

@app.route( urljoin(PATH, 'admin/groups/api/'),
        methods=['POST'])
async def yobot_groups_api():
    return "敬请期待"
