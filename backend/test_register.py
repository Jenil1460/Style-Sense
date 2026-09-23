import urllib.request
import json

url = "http://localhost:8000/api/v1/auth/register"
payload = json.dumps({
    "email": "testuser_debug3@example.com",
    "password": "Password123!",
    "first_name": "Test",
    "last_name": "User"
}).encode('utf-8')

req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Exception:", e)
