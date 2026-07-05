"""File logging for frozen builds (console=False hides errors)."""

import logging
import sys

from app_paths import app_dir, is_frozen


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("livesubs")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    if is_frozen():
        log_file = app_dir() / "livesubs.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
