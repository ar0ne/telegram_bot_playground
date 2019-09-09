# import time
# import threading
#
#
# from datetime import datetime, timedelta
# from functools import wraps
#
#
# def throttle(seconds: float = 0, minutes: float = 0, hours: float = 0, time_of_last_call: datetime = datetime.min):
#     throttle_period = timedelta(seconds=seconds, minutes=minutes, hours=hours)
#     def throttle_decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             nonlocal time_of_last_call
#             now = datetime.now()
#             if now > time_of_last_call + throttle_period:
#                 res = func(*args, **kwargs)
#                 time_of_last_call = datetime.now()
#                 return res, time_of_last_call
#             else:
#                 time.sleep((throttle_period - (now - time_of_last_call)).seconds)
#
#         return wrapper
#
#     return throttle_decorator
#
#
# @throttle(seconds=5)
# def test_func():
#     print('test_func starting...')
#     time.sleep(10)
#     print('test_func finished...')
#
#
#
#
# if __name__ == '__main__':
#     print('start application')
#     # t1 = threading.Thread(target=test_func, args=[])
#     # t2 = threading.Thread(target=test_func, args=[])
#     # t1.start()
#     # t2.start()
#     # print('finished application')
#     # time.sleep(10)
#     _, last_call = test_func()
