import sys
import logging

logging.basicConfig(level=logging.INFO, filename='logs.log', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def getLog(name):
    """
    Get logger with name as Test123

    format: 2019-11-06 22:39:38,498 - INFO - Test123 - log this
    """

    logger = logging.getLogger(name)
    return logger
