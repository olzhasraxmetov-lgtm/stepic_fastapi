import sys
from loguru import logger

def setup_logging():
    logger.remove()


    logger.add(
        sys.stdout,
        format="<cyan>{time:YYYY-MM-DD HH:mm:ss}</cyan> <level>{level: <5}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    logger.add(
        'app/logs/app.log',
        rotation="20 mb",
        retention="7 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        compression="zip",
    )