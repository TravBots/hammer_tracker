import logging as logger
import datetime
import os
from threading import Timer

# Create a unique filename based on the current timestamp
BASE_LOG_PATH = "../logs/"


def setup_logging():
    # Remove all handlers if exist
    for handler in logger.root.handlers[:]:
        logger.root.removeHandler(handler)

    current_time = datetime.datetime.now()
    log_dir = os.path.join(BASE_LOG_PATH, current_time.strftime("%Y/%m/%d"))
    log_filename = current_time.strftime("%H.log")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_filename)

    logger.basicConfig(
        level=logger.DEBUG,
        format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
        handlers=[logger.StreamHandler(), logger.FileHandler(log_path)],
    )


def periodic_log_check():
    # Check and update log configuration every hour
    setup_logging()

    # Schedule the next check
    interval = 3600 - (
        datetime.datetime.now().second + (datetime.datetime.now().minute * 60)
    )
    logger.info(f"Next log check in {interval} seconds")
    Timer(interval, periodic_log_check).start()
