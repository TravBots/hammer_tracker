import logging as logger
import datetime
import os
from threading import Timer
import argparse

# Create a unique filename based on the current timestamp
BASE_LOG_PATH = "../logs/"


def setup_logging(log_level=None):
    # Remove all handlers if exist
    for handler in logger.root.handlers[:]:
        logger.root.removeHandler(handler)

    current_time = datetime.datetime.now()
    log_dir = os.path.join(BASE_LOG_PATH, current_time.strftime("%Y/%m/%d"))
    log_filename = current_time.strftime("%H.log")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_filename)

    # Use provided log_level or default to INFO
    level = log_level if log_level is not None else logger.INFO

    logger.basicConfig(
        level=level,
        format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        handlers=[logger.StreamHandler(), logger.FileHandler(log_path)],
    )


def add_logging_args(parser):
    """Add logging-related command line arguments to an ArgumentParser."""
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )


def periodic_log_check(log_level=None):
    # Check and update log configuration every hour
    setup_logging(log_level)

    # Schedule the next check
    interval = 3600 - (
        datetime.datetime.now().second + (datetime.datetime.now().minute * 60)
    )
    logger.info(f"Next log check in {interval} seconds")
    Timer(interval, periodic_log_check).start()
