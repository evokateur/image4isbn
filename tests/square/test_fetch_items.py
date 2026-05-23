from image4isbn.square.fetch_items import find_attribute_by_name, to_item
from tests.conftest import ISBN_VALUE


def test_find_attribute_by_name_is_case_insensitive(catalog_item):
    assert find_attribute_by_name(catalog_item, "ISBN") is not None
    assert find_attribute_by_name(catalog_item, "isbn") is not None
    attr = find_attribute_by_name(catalog_item, "isbn")
    assert attr is not None
    assert attr.string_value == ISBN_VALUE


def test_to_item_has_square_image_false(catalog_item):
    assert to_item(catalog_item)["has_square_image"] is False


def test_to_item_has_square_image_true(catalog_item_with_image):
    assert to_item(catalog_item_with_image)["has_square_image"] is True
