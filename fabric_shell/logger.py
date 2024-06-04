import sys

from loguru import logger

from .config import config

logger.remove()
logger.add(sys.stdout, level=config.logging.level)
# TODO add one more logger for errors (sink=sys.stderr)
