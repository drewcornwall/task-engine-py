from functools import wraps
import time


def skippable(func):
    """Decorator to skip a task if it fails. Does not stop the pipeline."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Skipping task due to error: {e}")
    return wrapper


def check_resource(is_resource_available):
    """Decorator to check if resource is available."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if is_resource_available():
                return func(*args, **kwargs)
            else:
                raise Exception("Resource not available")
        return wrapper
    return decorator


def retries(max_retries):
    """Decorator to retry a task a maximum number of times. retry_handler must return True to retry."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    task = args[0]
                    if not task.retry_handler(e) or attempt == max_retries:
                        raise e
                    time.sleep(1)  # Simple backoff strategy
        return wrapper
    return decorator
