# image4isbn

A set of tools to find cover images for ISBNs, with the ability to retrieve data from and update images in a Square catalog.

## Tools

### `square-discover` (unfinished)

Fetches a sample of catalog items from Square and prints their raw JSON structure. Run this first to identify where ISBNs are stored in the catalog before running `square-fetch-items`.

```bash
square-discover
```

### `square-fetch-items` (unfinished)

Pulls items from a Square catalog and creates a JSONL items file.

Example output with arbitrary additional attributes (see Configuration below):

```jsonl
{"id": "item-id-1", "title": "Book Title", "isbn": "9781234567890"}
{"id": "item-id-2", "title": "Another Book", "isbn": "9780987654321"}
```

```bash
square-fetch-items > items.jsonl
```

### `to-items`

Creates JSON records, one for each line in a stream of ISBNs, usable as input for `find-covers`

Can be used by piping in a file or even:

```bash
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

Look at those pipes!

```bash
uv run scripts/fetch_random_isbns.py --count 5 | to-items | \
find-covers --source open_library | summarize > report.html && open report.html
```

<img width="603" height="351" alt="Capture d'écran 2026-05-18 à 08 56 54" src="https://github.com/user-attachments/assets/29f608e5-8bef-43d9-bf33-cbcce4d54451" />

### `find-covers`

Makes API calls to find cover images for each item in a items file, adding `images` and `failed_api_calls` to each. At this point only the `isbn` field is required for the API call and other fields pass through.

A record for which an image was found (will be flattened in the `.jsonl`):

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

A record for which an image was NOT found:

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

```bash
find-covers --source open_library < items.jsonl > items-covers.jsonl

# fill gaps with Google Books (requires GOOGLE_BOOKS_API_KEY; 1,000/day free tier)
find-covers --source google --append < items-covers.jsonl > records-final.jsonl
```

### `summarize`

Generates an HTML report showing how many covers were found, a sample of the matched images, and a list of ISBNs for which no cover image was found.

```bash
summarize < items-covers.jsonl > report.html
open report.html
```

### `download-covers`

Downloads each cover image to disk as `<isbn>.jpg` and adds a `local_path` to each record.

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

```bash
download-covers < items-covers.jsonl > items-downloaded.jsonl
```

### `square-attach-images` (unfinished)

Reads each record's local image file and uploads it to Square, attaching it to the matching catalog item. Square does not accept image URLs — it requires file uploads.

```bash
square-attach-images < items-downloaded.jsonl
```

### Example pipeline usage

```bash
square-fetch-items > items.jsonl
find-covers --source open_library < items.jsonl > items-covers.jsonl
summarize < items-covers.jsonl > report.html && open report.html
# review report, then:
download-covers < items-covers.jsonl > items-downloaded.jsonl
square-attach-images < items-downloaded.jsonl
```

## Configuration

Copy `.env.example` to `.env` and fill in the values.

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SQUARE_ACCESS_TOKEN` | Square Developer access token |
| `SQUARE_ENVIRONMENT` | `sandbox` for testing, `production` for the real catalog |
| `SQUARE_ISBN_FIELD` | The catalog attribute key where ISBNs are stored |
| `SQUARE_EXTRA_FIELDS` | Additional attributes (comma separated) to carry along the pipeline (e.g. `id, title`) |
| `COVERS_DIR` | Directory for downloaded cover images (default: `covers`) |
| `GOOGLE_BOOKS_API_KEY` | For using `--source google` |

## Installation

```bash
uv tool install -e .
```
