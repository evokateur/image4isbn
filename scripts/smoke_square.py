import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("SQUARE_ACCESS_TOKEN", "")
headers = {
    "Authorization": f"Bearer {token}",
    "Square-Version": "2026-05-20",
}
print(headers)

response = requests.get(
    "https://connect.squareupsandbox.com/v2/catalog/list", headers=headers
)
print(f"status: {response.status_code}", file=sys.stderr)
print(response.json())
