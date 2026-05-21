# image4isbn

A set of tools to find cover images for ISBNs, with the ability to retrieve data from and update images in a Square catalog.

## Tools

Composable into pipelines connected by a stream of items as JSONL data. Schema is append-only. Fields are added as the item moves through the pipeline. Nothing is ever removed or mutated.

### `square-fetch-items`

Fetches items from a Square catalog, emitting JSONL.

```jsonl
{"id": "item-id-1", "isbn": "9781234567890"}
{"id": "item-id-2", "isbn": "9780987654321"}
```

```sh
square-fetch-items > items.jsonl
```

### `find-covers`

Makes API calls to find cover images for each item.

Reads: `isbn`; Appends: `images`, `failed_api_calls`

An pretty-printed item for which an image was found (will be flattened in the JSONL):

```json
{
  "id": "item-id-1",
  "title": "Book Title",
  "isbn": "9781234567890",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9781234567890-L.jpg"
    }
  ],
  "failed_api_calls": []
}
```

An item for which an image was NOT found:

```json
{
  "id": "item-id-2",
  "title": "Another Book",
  "isbn": "9780987654321",
  "images": [],
  "failed_api_calls": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780987654321-L.jpg",
      "status": 404,
      "result": "not_found"
    }
  ]
}
```

```sh
find-covers --source open_library < items.jsonl > items-covers.jsonl
```

### `summarize`

Generates an HTML report showing how many covers were found, a sample of the matched images, and a list of ISBNs for which no cover image was found.

```sh
summarize < items-covers.jsonl > report.html
open report.html
```

### `download-covers`

Downloads each image to a directory as `<isbn>.jpg`.

Reads: `images[].url`; Appends: `images[].local_path`

```json
{
  "id": "item-id-1",
  "title": "Book Title",
  "isbn": "9781234567890",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9781234567890-L.jpg",
      "local_path": "covers/9781234567890.jpg"
    }
  ],
  "failed_api_calls": []
}
```

```sh
download-covers --dir ./covers < items-covers.jsonl > items-downloaded.jsonl
```

### `square-attach-images`

Uploads each record's image to Square, attaching it to the matching catalog item, and adding additional fields... *waves hands*

Reads: `id`, `images[].local_path`; Appends: ?

```sh
square-attach-images < items-downloaded.jsonl > items-attached.jsonl
```

### Example pipeline usage

```sh
square-fetch-items > items.jsonl
find-covers --source open_library < items.jsonl > items-ol.jsonl
find-covers --source google --append < items-ol.jsonl > items-covers.jsonl
download-covers --dir ./covers < items-covers.jsonl > items-downloaded.jsonl
square-attach-images < items-downloaded.jsonl > items-attached.jsonl
```

### `to-items`

Creates an item with an ISBN for each line in a stream, suitable for input to `find-covers`

```sh
echo "9780802190734" | to-items | find-covers --source open_library | jq .
```

```json
{
  "isbn": "9780802190734",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780802190734-L.jpg",
      "api_call": {
        "url": "https://covers.openlibrary.org/b/isbn/9780802190734-L.jpg",
        "called_at": "2026-05-18T15:36:08Z",
        "status": 200
      }
    }
  ],
  "failed_api_calls": []
}
```

```sh
uv run scripts/fetch_random_isbns.py --count 5 | to-items | \
find-covers --source open_library | summarize > report.html && open report.html
```

<img width="603" height="351" alt="Capture d'écran 2026-05-18 à 08 56 54" src="https://github.com/user-attachments/assets/29f608e5-8bef-43d9-bf33-cbcce4d54451" />

## Configuration

Copy `.env.example` to `.env` and fill in the values.

```sh
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SQUARE_ACCESS_TOKEN` | Square Developer access token |
| `SQUARE_ENVIRONMENT` | `sandbox` for testing, `production` for the real catalog |
| `SQUARE_ISBN_FIELD` | The catalog attribute key where ISBNs are stored |
| `SQUARE_EXTRA_FIELDS` | Additional attributes (comma separated) to carry along the pipeline (e.g. `name, description`) |
| `COVERS_DIR` | Directory for downloaded cover images (default: `covers`) |
| `GOOGLE_BOOKS_API_KEY` | For using `--source google` |

## Installation

```sh
uv tool install -e .
```
