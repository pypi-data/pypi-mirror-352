import sched
import threading
import time
from functools import wraps

# annotation
def once(func):
  """
  decorator to initialize a function once
  :param func: function to be initialized
  :return: the real decorator for return the result
  """
  initialized = False
  res = None

  def wrapper(*args, **kwargs):
    nonlocal initialized, res
    if not initialized:
      res = func(*args, **kwargs)
      initialized = True
      return res
    else:
      return res

  return wrapper

# annotation
def init(func):
  """
  decorator to initialize a function automic
  :param func: function to be initialized
  :return: the real decorator for return the result
  """
  res = func()

  def wrapper():
    return res

  return wrapper

# annotation
def schd(interval_seconds, start_by_call: bool = False):
  start_flag = False
  run_flag = False
  scheduler = sched.scheduler(time.time, time.sleep)

  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      nonlocal start_flag
      if start_by_call and not start_flag:
        start_flag = True
        threading.Thread(target=wrapper, args=args, kwargs=kwargs, daemon=True).start()
        return

      def job():
        func(*args, **kwargs)
        scheduler.enter(interval_seconds, 1, job)

      nonlocal run_flag
      if not run_flag:
        scheduler.enter(interval_seconds, 1, job)
        run_flag = True
        scheduler.run()
      else:
        func(*args, **kwargs)

    if not start_by_call: threading.Thread(target=wrapper, daemon=True).start()
    return wrapper

  return decorator
