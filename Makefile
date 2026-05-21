.PHONY: install reinstall test

install:
	uv tool install --editable .

reinstall:
	uv tool install --editable --reinstall .

test:
	uv run pytest
