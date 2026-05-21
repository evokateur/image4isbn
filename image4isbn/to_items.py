import sys
import json


def main():
    for line in sys.stdin:
        isbn = line.strip()
        if isbn:
            print(json.dumps({"isbn": isbn}))
