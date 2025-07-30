import inspect
import os
import sys


def get_current_path(subPath: str = '') -> str:
  """
  获取当前文件所在路径
  :param subPath: 子路径
  :return: 当前文件所在路径
  """
  if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
  else:
    caller_frame = inspect.currentframe().f_back
    caller_path = caller_frame.f_globals["__file__"]
    base_path = os.path.dirname(caller_path)
  return os.path.join(base_path, subPath)


def get_app_path(subPath: str = '') -> str:
  """
  获取应用程序工作时所在路径
  :param subPath: 子路径
  :return: 应用程序工作时所在路径
  """
  if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
  else:
    base_path = os.getcwd()
    while not os.path.isfile(os.path.join(base_path, 'README.md')):
      base_path = os.path.dirname(base_path)
  return os.path.join(base_path, subPath)


def get_user_work_path(subPath: str = '', mkdir: bool = False):
  """
  获取用户工作目录
  :param subPath: 拼接的子路径
  :param mkdir: 是否创建目录
  :return: 用户工作目录
  """
  path = os.path.join(os.path.expanduser("~"), subPath)
  if mkdir and not os.path.exists(path): os.makedirs(path, exist_ok=True)
  return path


def get_user_temp_path(subPath: str = '') -> str:
  """
  获取临时文件夹所在路径
  :return: 临时文件夹所在路径
  """
  return os.path.join(os.environ.get('TEMP'), subPath)


def get_Users_path(subPath: str = '') -> str:
  """
  获取用户目录所在路径 C:/Users
  :return: 用户目录所在路径
  """
  return os.path.join(os.path.dirname(os.path.expanduser("~")), subPath)


def get_install_path(subPath: str = '') -> str:
  """
  获取安装包安装的路径
  :return: 安装包安装的路径
  """
  return os.path.join(os.getcwd(), subPath)
