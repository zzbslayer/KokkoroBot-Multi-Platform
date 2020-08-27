import importlib
import os

import matplotlib.font_manager as font_manager

from .__bot__ import *

for module in MODULES_ON:
    try:
        importlib.import_module('kokkoro.config.modules.' + module)
        logger.info(f'Succeeded to load config of "{module}"')
    except ModuleNotFoundError:
        logger.warning(f'Not found config of "{module}"')

for font_file in FONT_PATH.values():
    font_manager.fontManager.addfont(os.path.expanduser(font_file))
