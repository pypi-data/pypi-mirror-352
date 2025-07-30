import logging
import os
import sys

import httpx

from ctools import sys_log, cjson

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("mcp.client.sse").setLevel(logging.WARNING)

log = sys_log.flog

def process_SSE(line):
  if not line: return None
  if line.startswith("data: "):
    data = line[6:]
    if data == "[DONE]":
      return "DONE"
    return data

class LLMClient:
  """Manages communication with the LLM provider."""

  def __init__(self, api_key: str=os.getenv("LLM_API_KEY"), llm_url: str="https://api.siliconflow.cn/v1/", model_name: str="Qwen/Qwen3-235B-A22B", temperature: float=1, stream: bool=True, thinking: bool=True, thinking_budget: int=4096, max_tokens: int=8192) -> None:
    self.api_key = api_key
    self.llm_url = llm_url
    self.model_name = model_name
    self.temperature = temperature
    self.stream = stream
    self.thinking = thinking
    self.thinking_budget = thinking_budget
    self.max_tokens = max_tokens

  async def model_completion(self, messages: list[dict[str, str]]):
    self.no_think_compatible(messages)
    url = self.llm_url
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {self.api_key}",
    }
    payload = {
      "messages": messages,
      "model": self.model_name,
      "temperature": self.temperature,
      "max_tokens": self.max_tokens,
      "top_p": 0.5,
      "top_k": 50,
      "frequency_penalty": 0.7,
      "stream": self.stream,
      "enable_thinking": self.thinking,
      "thinking_budget": self.thinking_budget
    }
    try:
      req_url = "chat/completions"
      if self.stream:
        async with httpx.AsyncClient(timeout=None, base_url=url) as client:
          async with client.stream("POST", req_url, headers=headers, json=payload) as response:
            response.raise_for_status()
            # 兼容 DS QWEN 的思维链
            start_think: bool = False
            end_think: bool = False
            start_token: str = "<think>"
            end_token: str = "</think>"
            # 兼容 DS QWEN 的思维链
            async for line in response.aiter_lines():
              data = process_SSE(line)
              if not data: continue
              if data == "DONE":
                continue
              choice = cjson.loads(data)["choices"][0]
              if "message" in choice:
                content = choice["message"]["content"]
              else:
                content = choice["delta"].get("content", "")
                # 兼容 DS QWEN 的思维链
                reasoning_content = choice["delta"].get("reasoning_content", "")
                if not start_think and not content and reasoning_content:
                  content = f"{start_token}{reasoning_content}"
                  start_think = True
                if not end_think and start_think and not reasoning_content:
                  content = f"{end_token}{content}"
                  end_think = True
                if not content: content = reasoning_content
                if not content: continue
                # 兼容 DS QWEN 的思维链
              yield content
      else:
        async with httpx.AsyncClient(timeout=None, base_url=url) as client:
          response = await client.post(req_url, headers=headers, json=payload)
          response.raise_for_status()
          content = response.json()["choices"][0]["message"]["content"]
          yield content
    except httpx.RequestError as e:
      error_message = f"Error getting LLM response: {str(e)}"
      log.error(error_message)
      if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code
        log.error(f"Status code: {status_code}")
        log.error(f"Response details: {e.response.text}")
      yield f"I encountered an error: {error_message}. Please try again or rephrase your request."

  def no_think_compatible(self, messages):
    if not self.thinking and "qwen3" in self.model_name:
      for msg in messages:
        if (msg.get("role") == "user" or msg.get("role") == "system") and "/no_think" not in msg.get("content", ""):
          msg["content"] += " /no_think"

# if __name__ == '__main__':
#   from env_config import Configuration
#
#   config = Configuration()
#   # llm = LLMClient(config.get_llm_api_key(), llm_url="http://192.168.3.73:8000/v1/", stream=True, model_name="deepseek-r1:7b", thinking=False, verbose=True)
#   llm = LLMClient(config.get_llm_api_key(), stream=True, model_name="Qwen/Qwen3-32B", thinking=False, verbose=True)
#   res = []
#   for chunk in llm.get_response([{"role": "user", "content": "写一个大概三百字的开心故事"}]):
#     res.append(chunk)
#   print("".join(res))

