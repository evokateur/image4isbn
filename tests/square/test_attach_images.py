from image4isbn.square.attach_images import make_idempotency_key


def test_idempotency_key_is_deterministic():
    assert make_idempotency_key("ABC123", "https://example.com/cover.jpg") == make_idempotency_key("ABC123", "https://example.com/cover.jpg")


def test_different_urls_produce_different_keys():
    assert make_idempotency_key("ABC123", "https://example.com/a.jpg") != make_idempotency_key("ABC123", "https://example.com/b.jpg")


def test_different_item_ids_produce_different_keys():
    assert make_idempotency_key("ABC123", "https://example.com/cover.jpg") != make_idempotency_key("XYZ999", "https://example.com/cover.jpg")
