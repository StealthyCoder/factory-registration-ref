import logging
import os

from config.settings import Settings

logging.basicConfig(level=logging.INFO)


async def log_device(uuid: str, pubkey: str) -> None:
    # Keep a log of created devices
    with open(os.path.join(Settings.DEVICES_DIR, uuid), "w") as log_file:
        log_file.write(pubkey)


async def log_msg(msg: str, name: str) -> None:
    logger = logging.getLogger(name)
    logger.info(msg)


async def log_error(msg: str, name: str) -> None:
    logger = logging.getLogger(name)
    logger.error(msg)
