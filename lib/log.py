import sys
import logging
import inspect

logging.basicConfig(level=logging.INFO, filename='logs.log', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def get_log(name: str):
    """
    Get logger with name as Test123

    format: 2019-11-06 22:39:38,498 - INFO - Test123 - log this
    """

    logger = logging.getLogger(name)
    return logger

def log_message(message: str) -> str:
    calling_function_name = inspect.currentframe().f_back.f_code.co_name
    return f'Function name: {calling_function_name} | message: {message}'
