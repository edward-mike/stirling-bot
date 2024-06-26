import logging
import time
from functools import wraps

from config.settings import LOG_DIR, setup_logger

# setup logging
setup_logger(LOG_DIR)


def time_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        logging.info(f"Execution time of {func.__name__}: {execution_time:.4f} sec.")
        return result

    return wrapper
