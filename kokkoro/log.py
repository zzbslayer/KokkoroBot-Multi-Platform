import logging
import os
import sys

os.makedirs('./log', exist_ok=True)
_error_log_file = os.path.expanduser('./log/error.log')
_critical_log_file = os.path.expanduser('./log/critical.log')

formatter = logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')
default_handler = logging.StreamHandler(sys.stdout)
default_handler.setFormatter(formatter)
error_handler = logging.FileHandler(_error_log_file, encoding='utf8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
critical_handler = logging.FileHandler(_critical_log_file, encoding='utf8')
critical_handler.setLevel(logging.CRITICAL)
critical_handler.setFormatter(formatter)

level_dict = {
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG
}
def new_logger(name, level="INFO"):
    logger = logging.getLogger(name)
    logger.addHandler(default_handler)
    logger.addHandler(error_handler)
    logger.addHandler(critical_handler)
    logger.setLevel(level_dict.get(level, logging.INFO))
    return logger
