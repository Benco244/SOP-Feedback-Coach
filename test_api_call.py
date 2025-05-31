import httpx
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    "HTTP-Referer": "https://sopcoach.local",  # Optional
    "X-Title": "SOP Coach Test"                # Optional
}

payload = {
    "model": "deepseek/deepseek-r1",  # ✅ Correct model ID
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Can you help me write my statement of purpose?"}
    ]
}

response = httpx.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

if response.status_code == 200:
    print(response.json()["choices"][0]["message"]["content"])
else:
    print("❌ Error:")
    print(response.status_code)
    print(response.json())
