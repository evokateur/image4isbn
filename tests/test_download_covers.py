import pytest
from pathlib import Path
from image4isbn.download_covers import download


def test_does_not_redownload_existing_file(tmp_path):
    sentinel = b"original content"
    cover = tmp_path / "9780743273565.jpg"
    cover.write_bytes(sentinel)

    item = {"isbn": "9780743273565", "images": [{"url": "https://invalid.invalid/cover.jpg"}]}
    result = download(item, tmp_path)

    assert cover.read_bytes() == sentinel
    assert result["images"][0]["local_path"] == str(cover)


def test_sets_local_path_when_image_has_none(tmp_path):
    cover = tmp_path / "9780743273565.jpg"
    cover.write_bytes(b"data")

    item = {"isbn": "9780743273565", "images": [{"url": "https://invalid.invalid/cover.jpg"}]}
    result = download(item, tmp_path)

    assert result["images"][0]["local_path"] == str(cover)


def test_passes_through_image_with_local_path_already_set(tmp_path):
    item = {"isbn": "123", "images": [{"url": "https://example.com/cover.jpg", "local_path": "/already/set.jpg"}]}
    result = download(item, tmp_path)
    assert result["images"][0]["local_path"] == "/already/set.jpg"
