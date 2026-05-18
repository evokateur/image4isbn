import sys
import json
import argparse
import time
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

MIN_COVER_BYTES = 1000
OPEN_LIBRARY_REQUEST_INTERVAL = 0.5  # 2 requests/second


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def lookup_google(isbn, api_key=None):
    params = {"q": f"isbn:{isbn}"}
    if api_key:
        params["key"] = api_key
    called_at = now_iso()
    resp = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
    api_call = {"url": resp.url, "called_at": called_at, "status": resp.status_code}

    if resp.status_code != 200:
        return [], [{**api_call, "result": "error"}]

    data = resp.json()
    if data.get("totalItems", 0) == 0:
        return [], [{**api_call, "result": "no_cover"}]

    image_links = (
        data.get("items", [{}])[0]
        .get("volumeInfo", {})
        .get("imageLinks", {})
    )
    if not image_links:
        return [], [{**api_call, "result": "no_cover"}]

    images = [
        {"source": "google_books", "url": img_url, "size": size, "api_call": api_call}
        for size, img_url in image_links.items()
    ]
    return images, []


def lookup_open_library(isbn):
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    called_at = now_iso()
    resp = requests.get(url)
    api_call = {"url": url, "called_at": called_at, "status": resp.status_code}

    if resp.status_code == 404:
        return [], [{**api_call, "result": "not_found"}]
    if resp.status_code != 200:
        return [], [{**api_call, "result": "error"}]
    if len(resp.content) < MIN_COVER_BYTES:
        return [], [{**api_call, "result": "placeholder"}]

    return [{"source": "open_library", "url": url, "api_call": api_call}], []


def lookup_image(isbn, source):
    if source == "google":
        return lookup_google(isbn, api_key=os.getenv("GOOGLE_BOOKS_API_KEY"))
    if source == "open_library":
        return lookup_open_library(isbn)
    raise ValueError(f"Unknown source: {source}")


def source_tag(source):
    if source == "google":
        return "google_books"
    return source


def enrich_record(record, images, failed_calls):
    return {
        **record,
        "images": record.get("images", []) + images,
        "failed_api_calls": record.get("failed_api_calls", []) + failed_calls,
    }


def should_skip(record, source, append, force):
    if force:
        return False
    existing = record.get("images", [])
    if append:
        return any(img.get("source") == source_tag(source) for img in existing)
    return bool(existing)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, choices=["google", "open_library"])
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.append and args.force:
        parser.error("--append and --force are mutually exclusive")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"expected a JSON object, got: {line.strip()!r}")

        if should_skip(record, args.source, args.append, args.force):
            print(json.dumps(record))
            continue

        isbn = record.get("isbn")
        if not isbn:
            print(json.dumps(record))
            continue

        images, failed_calls = lookup_image(isbn, args.source)
        print(json.dumps(enrich_record(record, images, failed_calls)))

        if args.source == "open_library":
            time.sleep(OPEN_LIBRARY_REQUEST_INTERVAL)
