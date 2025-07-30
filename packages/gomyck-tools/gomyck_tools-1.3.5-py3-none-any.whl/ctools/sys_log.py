import logging
import os
import sys
import time
import traceback

from ctools import call, work_path

clog: logging.Logger = None
flog: logging.Logger = None

neglect_keywords = [
  "OPTIONS",
]


# 文件日志
@call.once
def _file_log(sys_log_path: str = './', log_level: int = logging.INFO, mixin: bool = False) -> logging:
  try:
    os.mkdir(sys_log_path)
  except Exception:
    pass
  log_file = sys_log_path + os.path.sep + "log-" + time.strftime("%Y-%m-%d-%H", time.localtime(time.time())) + ".log"
  if mixin:
    handlers = [logging.FileHandler(filename=log_file, encoding='utf-8'), logging.StreamHandler()]
  else:
    handlers = [logging.FileHandler(filename=log_file, encoding='utf-8')]
  logging.basicConfig(level=log_level,
                      format='%(asctime)s-%(levelname)s-%(thread)d-%(module)s(%(funcName)s:%(lineno)d) %(message)s',
                      datefmt='%Y%m%d%H%M%S',
                      handlers=handlers)
  logger = logging.getLogger('ck-flog')
  return logger


# 控制台日志
@call.once
def _console_log(log_level: int = logging.INFO) -> logging:
  handler = logging.StreamHandler()
  logging.basicConfig(level=log_level,
                      format='%(asctime)s-%(levelname)s-%(thread)d-%(module)s(%(funcName)s:%(lineno)d) %(message)s',
                      datefmt='%Y%m%d%H%M%S',
                      handlers=[handler])
  logger = logging.getLogger('ck-clog')
  return logger


class GlobalLogger(object):
  def __init__(self, logger):
    sys.stdout = self
    sys.stderr = self
    sys.excepthook = self.handle_exception
    self.log = logger

  def write(self, message):
    if message == '\n' or message == '\r\n': return
    global neglect_keywords
    for neglect_keyword in neglect_keywords:
      if neglect_keyword in message: return
    try:
      stack = traceback.extract_stack(limit=3)
      caller = stack[-2]
      location = f"{os.path.splitext(os.path.basename(caller.filename))[0]}({caller.name}:{caller.lineno})"
      self.log.info(f"{location} {message.strip()}")
    except Exception:
      self.log.info(message.strip())

  def handle_exception(self, exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
      sys.__excepthook__(exc_type, exc_value, exc_traceback)
      return
    formatted_exception = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    self.log.error(f"An error occurred:\n{formatted_exception.strip()}")

  def flush(self):
    pass

  def fileno(self):
    return sys.__stdout__.fileno()


@call.init
def _init_log() -> None:
  global flog, clog
  flog = _file_log(sys_log_path='{}/ck-py-log/'.format(work_path.get_user_work_path()), mixin=True, log_level=logging.DEBUG)
  clog = _console_log()
  GlobalLogger(flog)

def setLevel(log_level=logging.INFO):
  flog.setLevel(log_level)
  clog.setLevel(log_level)
