#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/5/19 16:45'

import re

def extract_json_from_text(text):
  """
  从混杂文本中提取第一个完整的 JSON 对象
  """
  import json

  # 方法1：尝试直接解析
  try:
    return json.loads(text)
  except json.JSONDecodeError:
    pass

  # 方法2：字符级括号匹配提取 JSON
  start = None
  brace_count = 0
  for i, char in enumerate(text):
    if char == '{':
      if start is None:
        start = i
      brace_count += 1
    elif char == '}':
      brace_count -= 1
      if brace_count == 0 and start is not None:
        json_candidate = text[start:i + 1]
        try:
          return json.loads(json_candidate)
        except json.JSONDecodeError:
          start = None  # 重置继续寻找下一个可能的 JSON

  # 方法3：尝试 JSONP 格式
  match = re.search(r'\((\{[\s\S]*\})\)', text)
  if match:
    try:
      return json.loads(match.group(1))
    except json.JSONDecodeError:
      pass

  return None

