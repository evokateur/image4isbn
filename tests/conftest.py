import pytest
from square.types.catalog_custom_attribute_value import CatalogCustomAttributeValue
from square.types.catalog_item import CatalogItem
from square.types.catalog_object import CatalogObject_Item, CatalogObject_ItemVariation

ISBN_VALUE = "9780140434088"


@pytest.fixture
def catalog_item():
    variation = CatalogObject_ItemVariation(
        type="ITEM_VARIATION",
        id="GBGREKFIHSX56YP7JRMJ6KDT",
        custom_attribute_values={
            "Square:e71073f7-a1fb-47fa-a241-ed51bc7795f4": CatalogCustomAttributeValue(
                name="ISBN",
                string_value=ISBN_VALUE,
            ),
        },
    )
    return CatalogObject_Item(
        type="ITEM",
        id="Q6O257AKWZXONAM33IDHVJDS",
        item_data=CatalogItem(
            name="The Moonstone",
            variations=[variation],
        ),
    )
