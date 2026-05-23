import json
import os

from dotenv import load_dotenv
from square import Square
from square.environment import SquareEnvironment

load_dotenv()

ISBN_ATTRIBUTE_NAME = os.getenv("SQUARE_ISBN_ATTRIBUTE_NAME", "isbn")
OTHER_ATTRIBUTE_NAMES = [f.strip() for f in os.getenv("SQUARE_OTHER_ATTRIBUTE_NAMES", "").split(",") if f.strip()]


def square_client():
    env = os.getenv("SQUARE_ENVIRONMENT", "production").lower()
    environment = SquareEnvironment.SANDBOX if env == "sandbox" else SquareEnvironment.PRODUCTION
    return Square(token=os.getenv("SQUARE_ACCESS_TOKEN"), environment=environment)


def find_attribute_by_name(catalog_object, name: str):
    name_lower = name.lower()
    for variation in (catalog_object.item_data and catalog_object.item_data.variations or []):
        for attr in (variation.custom_attribute_values or {}).values():
            if attr.name and attr.name.lower() == name_lower:
                return attr
    for attr in (catalog_object.custom_attribute_values or {}).values():
        if attr.name and attr.name.lower() == name_lower:
            return attr
    return None


def extract_isbn(catalog_object) -> str | None:
    attr = find_attribute_by_name(catalog_object, ISBN_ATTRIBUTE_NAME)
    return attr.string_value if attr else None


def has_image(catalog_object) -> bool:
    if catalog_object.image_id:
        return True
    item_data = catalog_object.item_data
    return bool(item_data and item_data.image_ids)


def to_item(catalog_object) -> dict:
    item = {
        "id": catalog_object.id,
        "isbn": extract_isbn(catalog_object),
        "has_square_image": has_image(catalog_object),
    }
    for name in OTHER_ATTRIBUTE_NAMES:
        attr = find_attribute_by_name(catalog_object, name)
        if attr:
            item[name.lower()] = attr.string_value
    return item


def main():
    client = square_client()
    for catalog_object in client.catalog.list(types="ITEM"):
        print(json.dumps(to_item(catalog_object)))
