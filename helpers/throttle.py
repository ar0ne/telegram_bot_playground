import time

from datetime import datetime, timedelta


def throttling(seconds: float = 0, minutes: float = 0, hours: float = 0):
    def throttle_wrapper(func):
        def wrapper(*args, **kwargs):
            nonlocal last_time_call
            now = datetime.now()
            delta = timedelta(seconds=seconds, minutes=minutes, hours=hours)
            if not last_time_call or now > last_time_call + delta:
                res = func(*args, **kwargs)
                last_time_call = datetime.now()
                return res
            else:
                time.sleep((delta - (now - last_time_call)).seconds)

        last_time_call: datetime = None
        return wrapper

    return throttle_wrapper
