import httpx, os, sys
try:
    r = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer " + os.getenv("LLM_API_KEY"),
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "LinkSaver",
        },
        json={"model": os.getenv("LLM_MODEL"), "messages": [{"role": "user", "content": "Say hello"}]},
        timeout=10,
    )
    print("Status:", r.status_code)
    print("Body:", r.text[:300])
except Exception as e:
    print("Error:", type(e).__name__, e)
