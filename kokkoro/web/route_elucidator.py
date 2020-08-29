import os
from urllib.parse import urljoin
from quart import send_file, send_from_directory, session
from kokkoro import config
import kokkoro.web.universal_executor as ue
from . import get_app
app = get_app()

from .templating import render_template, static_folder, template_folder

PATH = config.PUBLIC_BASEPATH

''' routing start ---------------------------------------------------------- '''
# add route for static files
@app.route("/assets/<path:filename>", methods=["GET"])
async def yobot_static(filename):
    return await send_file(os.path.join(static_folder, filename))

from .clan import *
from .login import *
from .settings import *

@app.route(PATH, ["GET"])
async def yobot_homepage():
    return await render_template(
        "homepage.html",
        # verinfo=self.setting["verinfo"]["ver_name"],
        # show_icp=self.setting["show_icp"],
        # icp_info=self.setting["icp_info"],
        # gongan_info=self.setting["gongan_info"],
    )

@app.route( urljoin(PATH, 'about/'),
        methods=['GET'])
async def yobot_about():
    return await render_template(
        "about.html",
        # verinfo=self.setting["verinfo"]["ver_name"],
    )

@app.route("/favicon.ico", ["GET"])
async def yobot_favicon():
    return await send_from_directory(static_folder, "small.ico")

@app.route( urljoin(PATH, 'help/'),
            methods=['GET'])
async def yobot_help():
    return await send_from_directory(template_folder, "help.html")

@app.route( urljoin(PATH, 'manual/'),
            methods=['GET'])
async def yobot_manual():
    return await send_from_directory(template_folder, "manual.html")

@app.route( urljoin(PATH, 'api/ip-location/'),
            methods=['GET'])
async def yobot_api_iplocation():
    if 'yobot_user' not in session:
        return jsonify(['unauthorized'])
    ip = request.args.get('ip')
    if ip is None:
        return jsonify(['unknown'])
    try:
        location = await ue.ip_location(ip)
    except:
        location = ['unknown']
    return jsonify(location)

''' routing end ------------------------------------------------------------ '''
