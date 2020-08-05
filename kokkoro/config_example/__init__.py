import importlib
from .__bot__ import *

for module in MODULES_ON:
    try:
        importlib.import_module('kokkoro.config.modules' + module)
        logger.info(f'Succeeded to load config of "{module}"')
    except ModuleNotFoundError:
        logger.warning(f'Not found config of "{module}"')
