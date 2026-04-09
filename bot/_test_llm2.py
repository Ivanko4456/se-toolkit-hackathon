import asyncio, sys
from llm_client import extract_link_data, LLM_MODEL, LLM_API_KEY, LLM_API_BASE_URL

print(f"MODEL: {LLM_MODEL}")
print(f"KEY len: {len(LLM_API_KEY)}")
print(f"BASE: {LLM_API_BASE_URL}")

result = asyncio.run(extract_link_data("https://habr.com/ru/articles/871678/"))
print(f"Result: {result}")
