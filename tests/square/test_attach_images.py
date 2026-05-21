from image4isbn.square.attach_images import make_idempotency_key


def test_idempotency_key_is_deterministic():
    assert make_idempotency_key("ABC123") == make_idempotency_key("ABC123")
