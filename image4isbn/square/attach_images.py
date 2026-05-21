import json
import os
import sys
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from square import Square
from square.environment import SquareEnvironment

load_dotenv()

IDEMPOTENCY_NAMESPACE = uuid.UUID("7c96ac08-a305-47e8-8785-cf63f3568d91")
RATE_LIMIT_INTERVAL = 60 / 500  # 500 requests/minute max


def square_client():
    env = os.getenv("SQUARE_ENVIRONMENT", "production").lower()
    environment = SquareEnvironment.SANDBOX if env == "sandbox" else SquareEnvironment.PRODUCTION
    return Square(token=os.getenv("SQUARE_ACCESS_TOKEN"), environment=environment)


def make_idempotency_key(item_id: str) -> str:
    return str(uuid.uuid5(IDEMPOTENCY_NAMESPACE, item_id))


def attach(client, item_id: str, image: dict) -> dict:
    local_path = image["local_path"]
    with open(local_path, "rb") as f:
        response = client.catalog.images.create(
            request={
                "idempotency_key": make_idempotency_key(item_id),
                "object_id": item_id,
                "image": {"type": "IMAGE", "id": "#TEMP_IMAGE", "image_data": {}},
                "is_primary": True,
            },
            image_file=(Path(local_path).name, f, "image/jpeg"),
        )
    square_image_id = response.image.id if response.image else None
    return {**image, "attached": {"square_image_id": square_image_id}}


def main():
    client = square_client()
    counts = {"total": 0, "no_item_id": 0, "no_cover": 0, "already_attached": 0, "attached": 0}

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        counts["total"] += 1

        item_id = item.get("id")
        if not item_id:
            counts["no_item_id"] += 1
            print(json.dumps(item))
            continue

        images = item.get("images", [])
        if not images:
            counts["no_cover"] += 1
            print(json.dumps(item))
            continue

        updated = []
        for image in images:
            if image.get("attached"):
                counts["already_attached"] += 1
                updated.append(image)
                continue
            if not image.get("local_path"):
                updated.append(image)
                continue
            updated.append(attach(client, item_id, image))
            counts["attached"] += 1
            time.sleep(RATE_LIMIT_INTERVAL)

        print(json.dumps({**item, "images": updated}))

    print(f"\nTotal items:       {counts['total']:>6}", file=sys.stderr)
    print(f"No item_id:        {counts['no_item_id']:>6}", file=sys.stderr)
    print(f"No cover:          {counts['no_cover']:>6}", file=sys.stderr)
    print(f"Already attached:  {counts['already_attached']:>6}", file=sys.stderr)
    print(f"Images attached:   {counts['attached']:>6}", file=sys.stderr)
