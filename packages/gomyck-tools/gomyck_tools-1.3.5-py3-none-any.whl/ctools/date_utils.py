import time
from datetime import datetime, timedelta

def get_date():
  return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def get_time():
  return time.strftime('%H-%M-%S', time.localtime(time.time()))

def get_date_time(fmt="%Y-%m-%d %H:%M:%S"):
  return time.strftime(fmt, time.localtime(time.time()))

def str_to_datetime(val: str, fmt="%Y-%m-%d %H:%M:%S"):
  return time.strptime(val, fmt)

def str_to_timestamp(val: str, fmt="%Y-%m-%d %H:%M:%S"):
  return time.mktime(time.strptime(val, fmt))

def timestamp_to_str(timestamp: int=time.time(), fmt="%Y-%m-%d %H:%M:%S"):
  return time.strftime(fmt, time.localtime(timestamp))

def get_today_start_end(now: datetime.now()):
  start = datetime(now.year, now.month, now.day, 0, 0, 0)
  end = datetime(now.year, now.month, now.day, 23, 59, 59)
  return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")

def get_week_start_end(now: datetime.now()):
  start = now - timedelta(days=now.weekday())  # 本周一
  end = start + timedelta(days=6)  # 本周日
  return start.strftime("%Y-%m-%d 00:00:00"), end.strftime("%Y-%m-%d 23:59:59")

def time_diff_in_seconds(sub_head: str=get_date_time(), sub_end: str=get_date_time()):
  start_ts = str_to_timestamp(sub_head)
  end_ts = str_to_timestamp(sub_end)
  return int(start_ts - end_ts)

def opt_time(base_time=None, days=0, hours=0, minutes=0, seconds=0, weeks=0, fmt="%Y-%m-%d %H:%M:%S"):
  if base_time is None:
    base_time = datetime.now()
  elif isinstance(base_time, str):
    base_time = datetime.strptime(base_time, fmt)
  new_time = base_time + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds, weeks=weeks)
  return new_time.strftime(fmt)
