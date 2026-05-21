import json
import os

from dotenv import load_dotenv
from square import Square
from square.environment import SquareEnvironment

load_dotenv()

ISBN_FIELD = os.getenv("SQUARE_ISBN_FIELD", "isbn")
EXTRA_FIELDS = [f.strip() for f in os.getenv("SQUARE_EXTRA_FIELDS", "").split(",") if f.strip()]


def square_client():
    env = os.getenv("SQUARE_ENVIRONMENT", "production").lower()
    environment = SquareEnvironment.SANDBOX if env == "sandbox" else SquareEnvironment.PRODUCTION
    return Square(token=os.getenv("SQUARE_ACCESS_TOKEN"), environment=environment)


def extract_isbn(catalog_object) -> str | None:
    # TODO: implement after running square-discover against the client's catalog
    raise NotImplementedError


def has_image(catalog_object) -> bool:
    if catalog_object.image_id:
        return True
    item_data = catalog_object.item_data
    return bool(item_data and item_data.image_ids)


def to_item(catalog_object) -> dict:
    item = {"item_id": catalog_object.id, "isbn": extract_isbn(catalog_object)}
    item_data = catalog_object.item_data
    for field in EXTRA_FIELDS:
        if item_data and hasattr(item_data, field):
            item[field] = getattr(item_data, field)
    return item


def main():
    client = square_client()
    for catalog_object in client.catalog.list(types="ITEM"):
        if has_image(catalog_object):
            continue
        print(json.dumps(to_item(catalog_object)))
