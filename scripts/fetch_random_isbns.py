# /// script
# requires-python = ">=3.11"
# dependencies = ["requests"]
# ///
import sys
import argparse
import requests

OPEN_LIBRARY_SEARCH = "https://openlibrary.org/search.json"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="fiction")
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()

    resp = requests.get(OPEN_LIBRARY_SEARCH, params={
        "q": args.query,
        "limit": args.count * 2,
        "fields": "isbn",
    })
    resp.raise_for_status()

    seen = set()
    isbns = []
    for doc in resp.json().get("docs", []):
        for isbn in doc.get("isbn", []):
            if len(isbn) == 13 and isbn not in seen:
                seen.add(isbn)
                isbns.append(isbn)
                if len(isbns) >= args.count:
                    break
        if len(isbns) >= args.count:
            break

    for isbn in isbns:
        print(isbn)

    if len(isbns) < args.count:
        print(f"warning: found {len(isbns)} ISBNs, requested {args.count}", file=sys.stderr)
