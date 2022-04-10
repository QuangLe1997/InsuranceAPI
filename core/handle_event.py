import logging

from configs import setup_logging

log = logging.getLogger(__name__)
telegram_logger = logging.getLogger("critical")


async def handle_app_startup():
    """Start app"""
    setup_logging()
    log.info("Start server ...")
    telegram_logger.info("service api start success")
    log.info("End starting app ...")


async def handle_app_shutdown():
    """Shutdown app"""
    log.info("Shutting down API")
    telegram_logger.info("service api shutdown")
