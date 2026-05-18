# image4isbn

The main idea is to fetch book cover images by ISBN. The gravy will be attaching them to items in a Square catalog.

## Setup

```bash
cp .env.example .env  # fill in credentials
uv tool install -e .
```

## Discovery

Before running against the client's catalog, identify which Square catalog field holds the ISBN:

```bash
discover
```

Set `SQUARE_ISBN_FIELD` in `.env` based on the output.

## Usage

Full pipeline:

```bash
fetch-items | find-covers --source open_library | attach-images
```

With Google Books as a gap-filler (1,000 req/day limit):

```bash
fetch-items > records.jsonl
find-covers --source open_library < records.jsonl > records-ol.jsonl
find-covers --source google --append < records-ol.jsonl > records-final.jsonl
attach-images < records-final.jsonl
```

Test `find-covers` without Square credentials:

```bash
cat isbns.txt | to-records | find-covers --source open_library
```

## Flags

`find-covers --source <source> [--append] [--force]`

- default: skip records that already have any image
- `--append`: skip records that already have an image from this source; use to augment with a second source
- `--force`: process all records regardless

## Sources

- `open_library` — no daily quota; throttled to 2 req/s; primary source for bulk runs
- `google` — requires `GOOGLE_BOOKS_API_KEY`; 1,000 req/day free tier
