import os
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
payload = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Xin chào"}],
    "temperature": 0.7
}

response = requests.post("https://api.deepseek.com/v1/chat/completions",
                         headers=headers, json=payload)

print(response.status_code)
print(response.text)
