.PHONY: install reinstall uninstall test

install:
	uv tool install --editable .

reinstall:
	uv tool install --editable --reinstall .

uninstall:
	uv tool uninstall download-covers, find-covers, square-attach-images, square-fetch-items, summarize, to-items

test:
	uv run pytest
