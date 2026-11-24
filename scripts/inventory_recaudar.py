#!/usr/bin/env python3
"""Inventory public route API metadata; never persist raw stop lists or KMZ."""
import io
import json
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

BASE = "https://data.recaudarsinu.com/api/"
SITE = "https://recaudarsinu.com/"
MAX_BYTES = 12_000_000
ALLOWED_HOSTS = {"data.recaudarsinu.com", "recaudarsinu.com", "www.recaudarsinu.com"}
OUT = Path("artifacts/recaudar-inventory.json")
errors = []


def clean_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.hostname or "", p.path, "", ""))


def fetch(url):
    if urlsplit(url).hostname not in ALLOWED_HOSTS or urlsplit(url).scheme != "https":
        raise ValueError("unapproved host or scheme")
    time.sleep(0.3)
    req = Request(url, headers={"User-Agent": "ColombiaTransit-research/1.0",
                                "Accept": "*/*", "Referer": SITE})
    with urlopen(req, timeout=25) as resp:
        if urlsplit(resp.geturl()).hostname not in ALLOWED_HOSTS:
            raise ValueError("redirect outside source hosts")
        body = resp.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("response size limit exceeded")
        return body, resp.status, resp.headers.get("Content-Type", "")


def api(path):
    try:
        body, status, _ = fetch(BASE + path)
        return json.loads(body)
    except Exception as exc:
        errors.append({"path": path, "error": type(exc).__name__,
                       "status": getattr(exc, "code", None)})
        return None


def coord(s):
    try:
        lat, lon = float(s["latitud"]), float(s["longitud"])
        return -90 <= lat <= 90 and -180 <= lon <= 180 and (lat, lon) != (0, 0)
    except (KeyError, TypeError, ValueError):
        return False


def kml_metadata(blob):
    if zipfile.is_zipfile(io.BytesIO(blob)):
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            members = [m for m in z.infolist()
                       if m.filename.lower().endswith(".kml") and not m.is_dir()]
            if not members or sum(m.file_size for m in members) > MAX_BYTES:
                return {"format": "kmz", "error": "missing or oversized KML"}
            docs = [z.read(m) for m in members]
        fmt = "kmz"
    else:
        docs, fmt = [blob], "kml"
    counts = {}
    for doc in docs:
        root = ET.fromstring(doc)
        if root.tag.split("}")[-1] != "kml":
            raise ValueError("not KML")
        for el in root.iter():
            name = el.tag.split("}")[-1]
            if name in {"Placemark", "Point", "LineString", "MultiGeometry", "Track"}:
                counts[name] = counts.get(name, 0) + 1
    return {"format": fmt, "kml_documents": len(docs), "geometry_counts": counts}


def kmz(value):
    if not isinstance(value, str) or not value.strip():
        return {"reference_present": False}
    # Resolve explicit URLs and root-relative paths only. Bare filenames
    # require the actual frontend's resource base; do not guess directories.
    value = value.strip()
    p = urlsplit(value)
    if p.scheme:
        urls = [value]
    elif value.startswith("/") and not value.startswith("//"):
        urls = [urljoin(BASE, value), urljoin(SITE, value)]
    else:
        return {"reference_present": True, "reference_kind": "relative",
                "reference_suffix": Path(p.path).suffix,
                "status": "frontend base unresolved"}
    attempts = []
    for url in dict.fromkeys(urls):
        item = {"url": clean_url(url)}
        try:
            body, status, ct = fetch(url)
            item.update(status=status, content_type=ct, bytes=len(body))
            item.update(kml_metadata(body))
            attempts.append(item)
            break
        except Exception as exc:
            item.update(error=type(exc).__name__)
            if getattr(exc, "code", None):
                item["status"] = exc.code
            attempts.append(item)
    return {"reference_present": True, "attempts": attempts}


def main():
    report = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "routes": [], "errors": errors}
    routes = api("rutas")
    if not isinstance(routes, list):
        errors.append({"path": "rutas", "error": "expected list"})
        routes = []
    report["route_count"] = len(routes)
    all_ids, occurrences = set(), 0
    for route in routes[:30]:
        if not isinstance(route, dict) or type(route.get("id")) is not int:
            continue
        rid = route["id"]
        row = {"route_id": rid, "type": route.get("tipo"),
               "kmz": kmz(route.get("kmz_file")), "directions": []}
        report["routes"].append(row)
        directions = api(f"sentidos/{rid}")
        if not isinstance(directions, list):
            continue
        for d in directions[:10]:
            if not isinstance(d, dict) or type(d.get("id")) is not int:
                continue
            did = d["id"]
            result = {"direction_id": did, "route_link_matches": d.get("ruta_id") == rid}
            row["directions"].append(result)
            stops = api(f"paradas/{did}")
            if not isinstance(stops, list):
                continue
            stops = [s for s in stops if isinstance(s, dict)]
            ids = [s.get("id") for s in stops if type(s.get("id")) is int]
            all_ids.update(ids)
            occurrences += len(stops)
            result.update(stop_count=len(stops), coordinate_count=sum(coord(s) for s in stops),
                          missing_coordinate_count=sum(not coord(s) for s in stops),
                          unique_stop_ids=len(set(ids)),
                          named_count=sum(bool(s.get("parada")) for s in stops),
                          pivot_matches=sum(isinstance(s.get("pivot"), dict) and
                                            s["pivot"].get("sentido_id") == did and
                                            s["pivot"].get("parada_id") == s.get("id") for s in stops),
                          pivot_fields=sorted({k for s in stops if isinstance(s.get("pivot"), dict)
                                               for k in s["pivot"]}),
                          record_fields=sorted({k for s in stops for k in s}))
    report["summary"] = {"route_count_inspected": len(report["routes"]),
                         "directions": sum(len(r["directions"]) for r in report["routes"]),
                         "stop_occurrences": occurrences, "unique_stop_ids": len(all_ids),
                         "coordinates_present": sum(d.get("coordinate_count", 0)
                            for r in report["routes"] for d in r["directions"]),
                         "kmz_geometry_verified": sum(any("geometry_counts" in a for a in r["kmz"].get("attempts", []))
                            for r in report["routes"])}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print("API errors:", len(errors))


if __name__ == "__main__":
    main()
