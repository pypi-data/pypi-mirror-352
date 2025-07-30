import logging
from functools import wraps

class StatsLogger:

    @classmethod
    def exception_log(cls, default_return=None, level='error'):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log_fn = getattr(logging, level, logging.error)
                    log_fn(
                        f"{func.__name__} failed | args={args}, kwargs={kwargs} | error={e}",
                        exc_info=True
                    )
                    return default_return
            return wrapper
        return decorator