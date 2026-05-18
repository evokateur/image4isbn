import sys
import json
from datetime import datetime, timezone
from html import escape

SAMPLE_SIZE = 50

STYLE = """
* { box-sizing: border-box; }
body {
  font-family: sans-serif;
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1.5rem;
  color: #222;
  background: #f9f9f9;
}
h1 { margin: 0 0 0.25rem; font-size: 1.5rem; }
.generated { color: #999; font-size: 0.8rem; margin-bottom: 2rem; }
h2 { font-size: 1rem; text-transform: uppercase; letter-spacing: 0.05em; color: #888; margin: 2rem 0 0.75rem; }

.stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem 1.5rem;
  flex: 1;
}
.stat .number { font-size: 2rem; font-weight: 600; line-height: 1; }
.stat .label { font-size: 0.8rem; color: #888; margin-top: 0.25rem; }
.stat.found .number { color: #2a7a2a; }
.stat.missing .number { color: #b04040; }

.sources { display: flex; gap: 0.5rem; margin-bottom: 2rem; flex-wrap: wrap; }
.source-badge {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 0.3rem 0.75rem;
  font-size: 0.85rem;
}
.source-badge strong { margin-right: 0.4rem; }

.sample-note { font-size: 0.8rem; color: #999; margin-bottom: 0.75rem; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 0.75rem;
  margin-bottom: 2rem;
}
.card {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.card img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
  background: #f0f0f0;
}
.card .isbn {
  font-size: 0.65rem;
  color: #888;
  padding: 0.35rem 0.5rem;
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card .src {
  font-size: 0.6rem;
  color: #bbb;
  padding: 0 0.5rem 0.35rem;
}

.no-cover-list {
  columns: 4;
  column-gap: 1rem;
  margin-bottom: 2rem;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem 1.25rem;
}
.no-cover-list p {
  font-size: 0.8rem;
  font-family: monospace;
  margin: 0.2rem 0;
  break-inside: avoid;
}
"""


def pct(n, total):
    return f"{100 * n / total:.1f}%" if total else "—"


def render(records):
    covered = [r for r in records if r.get("images")]
    no_cover = [r for r in records if not r.get("images") and r.get("failed_api_calls")]
    skipped = [r for r in records if not r.get("images") and not r.get("failed_api_calls")]
    total = len(records)

    source_counts = {}
    for r in covered:
        for img in r["images"]:
            src = img.get("source", "unknown")
            source_counts[src] = source_counts.get(src, 0) + 1

    source_badges = "".join(
        f'<div class="source-badge"><strong>{count:,}</strong>{escape(src)}</div>'
        for src, count in sorted(source_counts.items(), key=lambda x: -x[1])
    )

    sample = covered[:SAMPLE_SIZE]
    sample_note = (
        f"Showing {len(sample):,} of {len(covered):,}"
        if len(covered) > SAMPLE_SIZE
        else f"Showing all {len(covered):,}"
    )

    cards = "".join(
        f"""<div class="card">
          <img src="{escape(r['images'][0]['url'])}" loading="lazy" alt="{escape(r.get('isbn', ''))}">
          <div class="isbn">{escape(r.get('isbn', ''))}</div>
          <div class="src">{escape(r['images'][0].get('source', ''))}</div>
        </div>"""
        for r in sample
    )

    missing_items = "".join(
        f"<p>{escape(r.get('isbn', '(no isbn)'))}</p>"
        for r in no_cover
    )

    no_cover_section = (
        f'<div class="no-cover-list">{missing_items}</div>'
        if no_cover
        else "<p>None.</p>"
    )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Cover Image Report</title>
  <style>{STYLE}</style>
</head>
<body>
  <h1>Cover Image Report</h1>
  <p class="generated">Generated {generated}</p>

  <div class="stats">
    <div class="stat">
      <div class="number">{total:,}</div>
      <div class="label">Total records</div>
    </div>
    <div class="stat found">
      <div class="number">{len(covered):,}</div>
      <div class="label">Cover found ({pct(len(covered), total)})</div>
    </div>
    <div class="stat missing">
      <div class="number">{len(no_cover):,}</div>
      <div class="label">No cover ({pct(len(no_cover), total)})</div>
    </div>
    <div class="stat">
      <div class="number">{len(skipped):,}</div>
      <div class="label">Skipped</div>
    </div>
  </div>

  <h2>Sources</h2>
  <div class="sources">{source_badges}</div>

  <h2>Sample covers</h2>
  <p class="sample-note">{sample_note}</p>
  <div class="grid">{cards}</div>

  <h2>No cover found ({len(no_cover):,})</h2>
  {no_cover_section}
</body>
</html>"""


def main():
    records = [json.loads(line) for line in sys.stdin if line.strip()]
    print(render(records))
