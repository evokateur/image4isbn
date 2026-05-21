import json
import os
import sys

from dotenv import load_dotenv
from square import Square
from square.environment import SquareEnvironment

load_dotenv()

SAMPLE_SIZE = 25


def square_client():
    env = os.getenv("SQUARE_ENVIRONMENT", "production").lower()
    environment = SquareEnvironment.SANDBOX if env == "sandbox" else SquareEnvironment.PRODUCTION
    return Square(token=os.getenv("SQUARE_ACCESS_TOKEN"), environment=environment)


def main():
    client = square_client()
    count = 0
    for catalog_object in client.catalog.list(types="ITEM"):
        print(json.dumps(catalog_object.model_dump(mode="json", exclude_none=True)))
        count += 1
        if count >= SAMPLE_SIZE:
            break
    print(f"{count} items shown.", file=sys.stderr)
