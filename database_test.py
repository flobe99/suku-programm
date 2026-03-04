import requests
import json

NEON_API_KEY = "DEIN_API_KEY"
NEON_PROJECT_ENDPOINT = "https://ep-square-cloud-aia2lc9m.apirest.c-4.us-east-1.aws.neon.tech/neondb/rest/v1"

query = {
    "query": "SELECT NOW();"
}

response = requests.post(
    NEON_PROJECT_ENDPOINT,
    headers={
        "Authorization": f"Bearer {NEON_API_KEY}",
        "Content-Type": "application/json"
    },
    data=json.dumps(query)
)

print(response.json())