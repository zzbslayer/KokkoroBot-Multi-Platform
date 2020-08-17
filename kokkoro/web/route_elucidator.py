import os
from quart import send_file, request, jsonify
from .templating import render_template
import kokkoro.web.universal_executor as ue
from . import get_app
app = get_app()

# add route for static files
@app.route("/assets/<path:filename>", methods=["GET"])
async def yobot_static(filename):
    return await send_file(
        os.path.join(os.path.dirname(__file__), "static", filename))

@app.route('/')
async def hello():
    return "Hello! " + ue.hello()


@app.route( '/clan/<group_id>/progress/',
            methods=['GET'])
async def yobot_clan_progress(group_id):
    return await render_template( 'clan/progress.html', )

@app.route('/clan/<group_id>/api/',
            methods=['POST'])
async def yobot_clan_api(group_id):
    payload = await request.get_json()
    return ue.clan_api(group_id, payload)
