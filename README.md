# image4isbn

A set of tools to find cover images for ISBNs, with the ability to retrieve data from and update images in a Square catalog.

## Tools

### `fetch-items`

Pulls items from a Square catalog and creates a JSONL records file.

Example output with arbitrary configured fields (see Configuration below):

```jsonl
{"id": "item-id-1", "title": "Book Title", "isbn": "9781234567890"}
{"id": "item-id-2", "title": "Another Book", "isbn": "9780987654321"}
```

```bash
fetch-items > records.jsonl
```

### `find-covers`

Makes API calls to find cover images for each item in a records file, adding `images` and `failed_api_calls` to each. At this point only the `isbn` field is required for the API call and other fields pass through.

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

A record for which no image was found:

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
find-covers --source open_library < records.jsonl > records-with-covers.jsonl

# fill gaps with Google Books (requires GOOGLE_BOOKS_API_KEY; 1,000/day free tier)
find-covers --source google --append < records-with-covers.jsonl > records-final.jsonl
```

### `summarize`

Generates an HTML report showing how many covers were found, a sample of the matched images, and a list of ISBNs for which no cover image was found.

```bash
summarize < records-final.jsonl > report.html
open report.html
```

### `attach-images`

Uploads the cover images to Square and attaches them to the matching catalog items.

```bash
attach-images < records-final.jsonl
```

### Example pipeline usage

```bash
fetch-items > records.jsonl
find-covers --source open_library < records.jsonl > records-with-covers.jsonl
summarize < records-with-covers.jsonl > report.html && open report.html
# review report, then:
attach-images < records-with-covers.jsonl
```

### `to-records`

Creates records, one for each line in a list of ISBNs, usable as input for `find-covers`.

```bash
echo "9780802190734" | to-records | find-covers --source open_library | jq .
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

```bash
uv run scripts/fetch_random_isbns.py --count 5 | to-records | \
find-covers --source open_library | summarize > report.html && open report.html
```

<img width="603" height="351" alt="Capture d’écran 2026-05-18 à 08 56 54" src="https://github.com/user-attachments/assets/29f608e5-8bef-43d9-bf33-cbcce4d54451" />


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
| `SQUARE_EXTRA_FIELDS` | Additional attributed to carry along the pipeline (e.g. `"id, title"`) |
| `GOOGLE_BOOKS_API_KEY` | For using `--source google` |

## Installation

```bash
uv tool install -e .
```
