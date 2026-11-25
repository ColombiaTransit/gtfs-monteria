#!/usr/bin/env python3
"""Collect the indexed official timetable PDFs for a one-off visual review."""
import csv
import hashlib
import json
import re
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import fitz
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts"
MAX_BYTES = 25 * 1024 * 1024

def main():
    with (ROOT / "research/timetables.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    # Include Villa Caribe too: it is already indexed and has a published timetable.
    if len(rows) != 13 or len({r["timetable_id"] for r in rows}) != 13:
        raise ValueError("Expected 13 distinct indexed timetables; review any inventory change")
    OUT.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/pdf,*/*;q=0.8",
        "Referer": "https://recaudarsinu.com/",
    })
    session.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"], respect_retry_after_header=True)))
    results, files, errors = [], {}, []
    for row in rows:
        ident = row["timetable_id"]
        url = row["url"]
        try:
            parsed = urlsplit(url)
            if parsed.scheme != "https" or parsed.hostname != "recaudarsinu.com" or not parsed.path.startswith("/assets/horarios/"):
                raise ValueError("Unexpected source URL")
            if not re.fullmatch(r"[a-z0-9_]+", ident):
                raise ValueError("Invalid timetable ID")
            with session.get(url, timeout=(15, 60), stream=True, allow_redirects=False) as response:
                if response.status_code != 200:
                    raise ValueError(f"HTTP {response.status_code}")
                data = bytearray()
                for chunk in response.iter_content(65536):
                    data.extend(chunk)
                    if len(data) > MAX_BYTES:
                        raise ValueError("PDF exceeds size limit")
            raw = bytes(data)
            if not raw.startswith(b"%PDF-"):
                raise ValueError("Response is not a PDF")
            with fitz.open(stream=raw, filetype="pdf") as doc:
                if doc.needs_pass or doc.page_count != int(row["pages"]):
                    raise ValueError("Encrypted or unexpected page count")
                for page in doc:
                    page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
                pages = doc.page_count
            filename = ident + ".pdf"
            files[filename] = raw
            results.append({"timetable_id": ident, "file": filename, "source": url,
                            "document_date": row["document_date"], "day_label": row["source_day_label"],
                            "pages": pages, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
            print(f"OK {ident}: {pages} page(s), {len(raw)} bytes", flush=True)
        except Exception as exc:
            errors.append({"timetable_id": ident, "source": url, "error": str(exc)})
            print(f"ERROR {ident}: {exc}", file=sys.stderr, flush=True)
        time.sleep(0.5)
    manifest = {"collected_at": datetime.now(timezone.utc).isoformat(), "expected": len(rows),
                "downloaded": len(files), "documents": results, "errors": errors}
    (OUT / "timetable-download-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if errors or len(files) != len(rows):
        raise SystemExit("Incomplete collection: no release archive created")
    target = OUT / "monteria-timetables.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for name, raw in sorted(files.items()):
            z.writestr(name, raw)
        z.write(OUT / "timetable-download-manifest.json", "manifest.json")
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
    print(f"Complete: {len(files)} PDFs, {sum(r['pages'] for r in results)} pages")

if __name__ == "__main__":
    main()
