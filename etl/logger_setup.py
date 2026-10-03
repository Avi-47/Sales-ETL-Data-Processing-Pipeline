"""
LOGGER SETUP
------------
Configures logging to both console and a rotating log file.
"""

import logging
import os
from datetime import datetime


def setup_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Configure and return the root logger.

    Args:
        log_dir: Directory to store log files.

    Returns:
        Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)

    log_filename = os.path.join(
        log_dir,
        f"etl_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger("sales_etl")
    logger.info(f"Logger initialized. Log file: {log_filename}")
    return logger
