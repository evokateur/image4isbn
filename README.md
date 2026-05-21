# image4isbn

A set of tools to find cover images for ISBNs, with the ability to retrieve items and update images in a Square catalog.

## Tools

Composable into pipelines connected by a stream of items as JSONL data. Schema is append-only. Fields are added as the item moves through the pipeline. Nothing is ever removed or mutated.

### `square-fetch-items`

Fetches items from a Square catalog, emitting JSONL

Reads: nothing; Appends: `id`, `isbn`, and attributes specified in `SQUARE_OTHER_ATTRIBUTE_NAMES`)

```sh
√ ~ $ square-fetch-items | jq .
{
  "id": "Q6O257AKWZXONAM33IDHVJDS",
  "isbn": "9780140434088",
  "title": "The Moonstone",
  "author": "Wilkie Collins"
}
{
  "id": "BVOI6U7ULAOQ6NSCGSOZUHOP",
  "isbn": "9780816628773",
  "title": "The Practice of Everyday Life, Vol. 2: Living and Cooking",
  "author": "Michel de Certeau"
}
{
  "id": "KITW7KPCX5QGP5Q2ET34FXZA",
  "isbn": "9780517414248",
  "title": "Mary Queen of Scots",
  "author": "Antonia Fraser"
}
```

### `find-covers`

Makes API calls to find cover images for each item.

Reads: `isbn`; Appends: `images`, `failed_api_calls`

```sh
√ ~ $ square-fetch-items | find-covers --source open_library | jq .
{
  "id": "Q6O257AKWZXONAM33IDHVJDS",
  "isbn": "9780140434088",
  "title": "The Moonstone",
  "author": "Wilkie Collins",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780140434088-L.jpg",
      "api_call": {
        "url": "https://covers.openlibrary.org/b/isbn/9780140434088-L.jpg",
        "called_at": "2026-05-21T21:02:52Z",
        "status": 200
      }
    }
  ],
  "failed_api_calls": []
}
{
  "id": "BVOI6U7ULAOQ6NSCGSOZUHOP",
  "isbn": "9780816628773",
  "title": "The Practice of Everyday Life, Vol. 2: Living and Cooking",
  "author": "Michel de Certeau",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780816628773-L.jpg",
      "api_call": {
        "url": "https://covers.openlibrary.org/b/isbn/9780816628773-L.jpg",
        "called_at": "2026-05-21T21:02:53Z",
        "status": 200
      }
    }
  ],
  "failed_api_calls": []
}
{
  "id": "KITW7KPCX5QGP5Q2ET34FXZA",
  "isbn": "9780517414248",
  "title": "Mary Queen of Scots",
  "author": "Antonia Fraser",
  "images": [],
  "failed_api_calls": [
    {
      "url": "https://covers.openlibrary.org/b/isbn/9780517414248-L.jpg",
      "called_at": "2026-05-21T21:03:00Z",
      "status": 200,
      "result": "placeholder"
    }
  ]
}
```

### `summarize`

Generates an HTML report showing how many covers were found, a sample of the matched images, and a list of ISBNs for which no cover image was found.

```sh
√ ~ $ square-fetch-items | find-covers --source open_library | summarize > report.html
√ ~ $ open report.html
```

<img width="576" height="458" alt="sample-cover-image-report" src="https://github.com/user-attachments/assets/696f3fbf-535e-49ee-bbcb-a1964cc614c5" />

### `download-covers`

Downloads each image to a directory as `<isbn>.jpg`.

Reads: `images[].url`; Appends: `images[].local_path`

```sh
{
  "id": "Q6O257AKWZXONAM33IDHVJDS",
  "isbn": "9780140434088",
  "title": "The Moonstone",
  "author": "Wilkie Collins",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780140434088-L.jpg",
      "api_call": {
        "url": "https://covers.openlibrary.org/b/isbn/9780140434088-L.jpg",
        "called_at": "2026-05-21T21:24:40Z",
        "status": 200
      },
      "local_path": "docs/covers/9780140434088.jpg"
    }
  ],
  "failed_api_calls": []
}
{
  "id": "BVOI6U7ULAOQ6NSCGSOZUHOP",
  "isbn": "9780816628773",
  "title": "The Practice of Everyday Life, Vol. 2: Living and Cooking",
  "author": "Michel de Certeau",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780816628773-L.jpg",
      "api_call": {
        "url": "https://covers.openlibrary.org/b/isbn/9780816628773-L.jpg",
        "called_at": "2026-05-21T21:24:40Z",
        "status": 200
      },
      "local_path": "docs/covers/9780816628773.jpg"
    }
  ],
  "failed_api_calls": []
}
{
  "id": "KITW7KPCX5QGP5Q2ET34FXZA",
  "isbn": "9780517414248",
  "title": "Mary Queen of Scots",
  "author": "Antonia Fraser",
  "images": [],
  "failed_api_calls": [
    {
      "url": "https://covers.openlibrary.org/b/isbn/9780517414248-L.jpg",
      "called_at": "2026-05-21T21:24:41Z",
      "status": 200,
      "result": "placeholder"
    }
  ]
}
```

### `square-attach-images`

Uploads each item's cover image to Square, attaching it to the matching catalog item.

Reads: `id`, `images[].local_path`; Appends: `images[].attached.square_image_id`

```sh
√ ~ $ square-fetch-items | find-covers --source open_library | download-covers | square-attach-images | jq .
Total items:            3
No item_id:             0
No cover:               1
Already attached:       0
Images attached:        2
```

```json
{
  "id": "Q6O257AKWZXONAM33IDHVJDS",
  "isbn": "9780140434088",
  "title": "The Moonstone",
  "author": "Wilkie Collins",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780140434088-L.jpg",
      "local_path": "covers/9780140434088.jpg",
      "attached": {
        "square_image_id": "WF5PEFDHAEGJ64TRY2K2KI3C"
      }
    }
  ],
  "failed_api_calls": []
}
{
  "id": "BVOI6U7ULAOQ6NSCGSOZUHOP",
  "isbn": "9780816628773",
  "title": "The Practice of Everyday Life, Vol. 2: Living and Cooking",
  "author": "Michel de Certeau",
  "images": [
    {
      "source": "open_library",
      "url": "https://covers.openlibrary.org/b/isbn/9780816628773-L.jpg",
      "local_path": "covers/9780816628773.jpg",
      "attached": {
        "square_image_id": "2TFHAT3L4EBJSWKTF4QROXM7"
      }
    }
  ],
  "failed_api_calls": []
}
{
  "id": "KITW7KPCX5QGP5Q2ET34FXZA",
  "isbn": "9780517414248",
  "title": "Mary Queen of Scots",
  "author": "Antonia Fraser",
  "images": [],
  "failed_api_calls": [
    {
      "url": "https://covers.openlibrary.org/b/isbn/9780517414248-L.jpg",
      "status": 200,
      "result": "placeholder"
    }
  ]
}
```

### `to-items`

Creates an item for each ISBN in the input stream, which can then be piped to `find-covers`  

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
| `SQUARE_ISBN_ATTRIBUTE_NAME` | Name of the custom attribute where ISBNs are stored. Only needed if it is not `isbn`, which is assumed. |
| `SQUARE_OTHER_ATTRIBUTE_NAMES` | Names of other custom attributes to carry along the pipeline, comma-separated (e.g. `title, author`) |
| `COVERS_DIR` | Directory for downloaded cover images (default: `covers`) |
| `GOOGLE_BOOKS_API_KEY` | For using `--source google` |

## Installation

```sh
uv tool install -e .
```
