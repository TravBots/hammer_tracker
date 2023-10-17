import logging as logger
import datetime
import os

# Create a unique filename based on the current timestamp
filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_logfile.log'
LOG_PATH = '../logs/' + filename

# Ensure the parent directory exists
if not os.path.exists('../logs/'):
    os.makedirs('../logs/')

# Set up basic logging configuration
logger.basicConfig(level=logger.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[
                       logger.StreamHandler(),  # Console logging
                       logger.FileHandler(LOG_PATH)  # File logging
                   ])