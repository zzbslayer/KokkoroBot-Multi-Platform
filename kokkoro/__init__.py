from kokkoro.bot import KokkoroBot
from . import config, log

logger = log.new_logger('KokkoroBot', config.LOG_LEVEL)

kkr_bot = KokkoroBot()