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

BROADCAST_CHANNEL="broadcast"

LOG_LEVEL="DEBUG"
ENABLE_IMAGE=True

NICK_NAME = ['可可萝', '妈']

RES_PROTOCOL = 'file'
RES_DIR = '~/.kokkoro/res/'
RES_URL = '0.0.0.0'

MODULES_ON = [
    "botmanage",
    "priconne",
    "pcrclanbattle"
]