import requests

response = requests.get('http://localhost:8000/api/company-profile/8/financial?year=2024')
print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"\nRaw Response:")
print(response.text[:500])
