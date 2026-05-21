from image4isbn.square.fetch_items import find_attribute_by_name
from tests.conftest import ISBN_VALUE


def test_find_attribute_by_name_is_case_insensitive(catalog_item):
    assert find_attribute_by_name(catalog_item, "ISBN") is not None
    assert find_attribute_by_name(catalog_item, "isbn") is not None
    attr = find_attribute_by_name(catalog_item, "isbn")
    assert attr is not None
    assert attr.string_value == ISBN_VALUE
