import inspect
import os
import sys


def path(subPath: str = '') -> str:
  if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
  else:
    caller_frame = inspect.currentframe().f_back
    caller_path = caller_frame.f_globals["__file__"]
    base_path = os.path.dirname(caller_path)
  return base_path + os.path.sep + subPath
