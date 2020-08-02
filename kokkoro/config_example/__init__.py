import importlib
import os
from kokkoro import log
from .__bot__ import *

# check correctness
#RES_DIR = os.path.expanduser(RES_DIR)
#assert RES_PROTOCOL in ('http', 'file', 'base64')

# load module configs
logger = log.new_logger('config')
for module in MODULES_ON:
    try:
        importlib.import_module('kokkoro.config.' + module)
        logger.info(f'Succeeded to load config of "{module}"')
    except ModuleNotFoundError:
        logger.warning(f'Not found config of "{module}"')
