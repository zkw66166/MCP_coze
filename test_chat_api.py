import requests
import json

# Test calling /api/chat endpoint directly
url = "http://localhost:8000/api/chat"
payload = {
    "question": "测试保存功能",
    "company_id": None,
    "enable_routing": True,
    "show_chart": True,
    "response_mode": "detailed"
}

print(f"Sending POST to {url}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, json=payload, stream=True, timeout=30)
    print(f"Status: {response.status_code}")
    
    # Read stream response
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:
            print(chunk.decode('utf-8', errors='ignore'))
            
except Exception as e:
    print(f"Error: {e}")
