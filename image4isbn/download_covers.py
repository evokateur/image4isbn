import sys
import json
import argparse
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()


def download(item, output_dir):
    images = item.get("images", [])
    if not images:
        return item

    isbn = item.get("isbn", "unknown")
    updated = []

    for i, image in enumerate(images):
        if image.get("local_path"):
            updated.append(image)
            continue

        url = image.get("url")
        if not url:
            updated.append(image)
            continue

        filename = f"{isbn}.jpg" if i == 0 else f"{isbn}-{i}.jpg"
        local_path = output_dir / filename

        if not local_path.exists():
            resp = requests.get(url)
            resp.raise_for_status()
            local_path.write_bytes(resp.content)

        updated.append({**image, "local_path": str(local_path)})

    return {**item, "images": updated}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=os.getenv("COVERS_DIR", "covers"))
    args = parser.parse_args()

    output_dir = Path(args.dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if not isinstance(item, dict):
            raise ValueError(f"expected a JSON object, got: {line!r}")
        print(json.dumps(download(item, output_dir)))
