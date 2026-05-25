from image4isbn.find_covers import should_skip, enrich_item


def test_should_skip_when_has_square_image():
    assert should_skip({"has_square_image": True}, "google", append=False, force=False) is True


def test_force_overrides_has_square_image():
    assert should_skip({"has_square_image": True}, "google", append=False, force=True) is False


def test_should_not_skip_when_no_image_and_no_square_image():
    assert should_skip({"has_square_image": False}, "google", append=False, force=False) is False


def test_enrich_item_deduplicates_images_by_url():
    existing = {"url": "https://example.com/cover.jpg", "source": "open_library"}
    item = {"isbn": "123", "images": [existing]}
    new_image = {"url": "https://example.com/cover.jpg", "source": "google_books"}
    result = enrich_item(item, [new_image], [])
    assert len(result["images"]) == 1
