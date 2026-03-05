import requests

API_KEY = "napi_kgwxm8iah53n6jt527kcioqmbkaimlhi37xh7ct6qub583gc5llis4rxe9206brq"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

response = requests.get(
    "https://console.neon.tech/api/v2/projects",
    headers=headers
)

print(response.json())