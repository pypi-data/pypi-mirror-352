import logging

from .._common.config import ModeSetting

logger = logging.getLogger()

def log_config(level = logging.INFO, quiet = False):
    global logger
    logger.setLevel(level=level)
    ModeSetting.write_mode(quiet)
