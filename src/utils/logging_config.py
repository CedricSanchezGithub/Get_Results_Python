import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_CONFIGURED = False


def configure_logging(level=None, log_dir: str = "logs", filename: str = "scraper.log"):
    global _LOG_CONFIGURED
    if _LOG_CONFIGURED:
        return

    os.makedirs(log_dir, exist_ok=True)
    logfile_path = os.path.join(log_dir, filename)

    logger = logging.getLogger()
    # Default level
    logger.setLevel(level if level is not None else logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(logfile_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for container stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Reduce verbosity of noisy libs
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    _LOG_CONFIGURED = True
