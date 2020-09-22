import importlib
from kokkoro import log

logger = log.new_logger('config')

BOT_TYPE="discord"
ENABLE_WEB=False

try:
    platform_config = importlib.import_module('kokkoro.config.bot.' + BOT_TYPE)
    logger.info(f'Succeeded to load config of "{BOT_TYPE}"')
except ModuleNotFoundError as e:
    logger.error(f'Not found config of "{BOT_TYPE}"')
    raise e


BOT_ID = platform_config.BOT_ID
SUPER_USER = platform_config.SUPER_USER
ENABLED_GROUP = platform_config.ENABLED_GROUP

DEFAULT_BROADCAST_TAG = "broadcast"

LOG_LEVEL="DEBUG"

NICK_NAME = ['可可萝', '妈', 'kkr', 'kokkoro']

RES_PROTOCOL = 'file'
RES_DIR = '~/.kokkoro/res/'
RES_URL = '0.0.0.0'

def get_font_path(font_file):
    return os.path.expanduser(os.path.join(RES_DIR, 'fonts', font_file))

FONT_PATH = {
    "msyh": get_font_path('Microsoft YaHei.ttf'),# 微软雅黑
    "simhei": get_font_path('simhei.ttf'), # 黑体
    "mamelon": get_font_path('Mamelon.otf'), 
    "sakura": get_font_path('sakura.ttf'),
}

MODULES_ON = [
    "arknights",
    "botmanage",
    "groupmaster",
    "priconne",
    "pcrclanbattle",
    "weibo"
]
