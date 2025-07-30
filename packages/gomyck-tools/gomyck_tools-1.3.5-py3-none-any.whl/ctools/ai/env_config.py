#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'haoyang'
__date__ = '2025/5/16 16:42'

import json
import os
from typing import Any

from dotenv.main import DotEnv


class Configuration:
  """Manages configuration and environment variables for the MCP client."""

  def __init__(self, dotenv_path: str=".env") -> None:
    """Initialize configuration with environment variables."""
    if not os.path.exists(dotenv_path): raise FileNotFoundError(f"Could not find .env file at {dotenv_path}")
    self.env = DotEnv(dotenv_path=dotenv_path)

  def get_env(self, key: str) -> str:
    value = self.env.get(key)
    return value if value else os.getenv(key)

  def get_llm_api_key(self) -> str:
    api_key = self.get_env("LLM_API_KEY")
    if not api_key: raise ValueError("LLM_API_KEY not found in environment variables")
    return api_key

  def get_mcp_server_config(self) -> dict[str, Any]:
    with open(self.get_env("MCP_CONFIG_PATH"), "r") as f:
      return json.load(f)

