from image4isbn.find_covers import should_skip


def test_should_skip_when_has_square_image():
    assert should_skip({"has_square_image": True}, "google", append=False, force=False) is True


def test_force_overrides_has_square_image():
    assert should_skip({"has_square_image": True}, "google", append=False, force=True) is False


def test_should_not_skip_when_no_image_and_no_square_image():
    assert should_skip({"has_square_image": False}, "google", append=False, force=False) is False
