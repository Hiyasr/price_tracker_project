"""
utils/logger.py
---------------
Centralized logging setup for the entire application.

Why a dedicated logger?
  • All logs (scraping, DB errors, price changes) go to one place.
  • Logs are written to BOTH the console AND a rotating file so you
    can review yesterday's run without losing today's output.
  • Every module just does: from utils.logger import get_logger
    and gets a properly configured logger back.

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)

    logger.info("Scraping started")
    logger.warning("Rate limit hit, sleeping...")
    logger.error("Failed to connect to DB", exc_info=True)
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_logger(name: str, log_dir: Path = None) -> logging.Logger:
    """
    Return a logger with console + rotating-file handlers.

    Args:
        name    : Typically pass __name__ so logs show which module they came from.
        log_dir : Directory to write log files. Defaults to project /logs folder.

    Returns:
        A configured logging.Logger instance.
    """
    if log_dir is None:
        # Resolve relative to this file's grandparent (project root)
        log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if this function is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler (INFO and above) ──────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)

    # ── File handler (DEBUG and above, rotates at 5 MB, keeps 7 backups) ──────
    log_file = log_dir / "price_tracker.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
