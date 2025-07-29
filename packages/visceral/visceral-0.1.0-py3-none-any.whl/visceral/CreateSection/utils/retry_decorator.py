import functools
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_on_json_error(func=None, *, max_retries=3, delay=1):
    if func is None:
        return functools.partial(retry_on_json_error, max_retries=max_retries, delay=delay)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                return func(*args, **kwargs)  # Try executing the function
            except Exception as e:  # Catch ANY exception
                last_error = e
                retry_count += 1
                logger.warning(f"Retry {retry_count}/{max_retries} due to error: {e}")

                if retry_count < max_retries:
                    time.sleep(delay)  # Wait before retrying
                else:
                    logger.error(f"Function {func.__name__} failed after {max_retries} attempts.")
                    raise last_error  # Raise last error after max retries

    return wrapper
