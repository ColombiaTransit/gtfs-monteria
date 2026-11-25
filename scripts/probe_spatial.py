#!/usr/bin/env python3
"""Inspect government GIS layers and official KMZ endpoint geometry."""
import csv
import io
import json
import math
import zipfile
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = "https://srvansvargweb.ansv.gov.co/server/rest/services/Hosted/MapaBaseMonteria/FeatureServer"
API = "https://data.recaudarsinu.com/api/"
LIMIT = 12_000_000
HOSTS = {"srvansvargweb.ansv.gov.co", "data.recaudarsinu.com", "recaudarsinu.com", "www.recaudarsinu.com"}


def get(url):
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname not in HOSTS:
        raise ValueError("Unexpected source")
    req = Request(url, headers={"User-Agent": "ColombiaTransit-research/1.0", "Accept": "*/*"})
    with urlopen(req, timeout=25) as r:
        if urlsplit(r.geturl()).hostname not in HOSTS:
            raise ValueError("Unexpected redirect")
        b = r.read(LIMIT + 1)
        if len(b) > LIMIT:
            raise ValueError("Response too large")
        return b


def js(url, **params):
    data = json.loads(get(url + ("?" + urlencode(params) if params else "")))
    if isinstance(data, dict) and "error" in data:
        raise ValueError(str(data["error"])[:300])
    return data


def attempt(fn):
    try:
        return fn()
    except Exception as e:
        return {"error": type(e).__name__, "detail": str(e)[:300]}


def layer(i):
    base = f"{ROOT}/{i}"
    m = attempt(lambda: js(base, f="json"))
    count = attempt(lambda: js(base + "/query", where="1=1", returnCountOnly="true", f="json"))
    sample = attempt(lambda: js(base + "/query", where="1=1", outFields="*", returnGeometry="true", outSR=4326, resultRecordCount=5, f="json"))
    return {"id": i, "metadata": {k: m.get(k) for k in ("name", "geometryType", "description", "copyrightText", "extent", "objectIdField", "fields") if k in m} if "error" not in m else m,
            "count": count,
            "sample_summary": {"feature_count": len(sample.get("features", [])), "geometry_type": sample.get("geometryType"),
                               "geometry_keys": sorted({k for f in sample.get("features", []) for k in (f.get("geometry") or {})}),
                               "attribute_keys": sorted({k for f in sample.get("features", []) for k in (f.get("attributes") or {})})} if "error" not in sample else sample}


def distance(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 12742000 * math.asin(min(1, math.sqrt(h)))


def coords(el):
    t = el.find(".//{*}coordinates")
    return [tuple(map(float, p.split(",")[:2])) for p in (t.text or "").split()] if t is not None else []


def kmz(url):
    with zipfile.ZipFile(io.BytesIO(get(url))) as z:
        members = [i for i in z.infolist() if i.filename.lower().endswith(".kml")]
        if sum(i.file_size for i in members) > LIMIT:
            raise ValueError("KML too large")
        roots = [ET.fromstring(z.read(i)) for i in members]
    points, lines = [], []
    for root in roots:
        for pm in root.findall(".//{*}Placemark"):
            name = pm.findtext("{*}name", "")
            for p in pm.findall(".//{*}Point"):
                c = coords(p)
                if c:
                    points.append((name, c[0]))
            for l in pm.findall(".//{*}LineString"):
                c = coords(l)
                if len(c) >= 2:
                    lines.append((name, c))
    return {"point_names": [n for n, _ in points],
            "lines": [{"name": n, "vertices": len(c),
                       "length_km": round(sum(distance(a,b) for a,b in zip(c,c[1:]))/1000, 3),
                       "point_to_start_end_m": [{"point_name": pn, "start": round(distance(p,c[0])), "end": round(distance(p,c[-1]))} for pn,p in points]}
                      for n,c in lines]}


def main():
    service = attempt(lambda: js(ROOT, f="json"))
    report = {"arcgis_service": {k:service.get(k) for k in ("layers","serviceItemId","copyrightText","description","fullExtent") if k in service} if "error" not in service else service,
              "arcgis_layers": [layer(i) for i in (0,1,5)], "kmz": []}
    route_list = attempt(lambda: js(API+"rutas"))
    names = {str(r["id"]): r.get("ruta") for r in route_list if isinstance(r,dict) and "id" in r} if isinstance(route_list,list) else {}
    if isinstance(route_list,dict):
        report["route_api_error"] = route_list
    with open("research/api-route-inventory.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rid = row["api_route_id"]
            result = {"route_id": rid, "route_name": names.get(rid)}
            url = row["kmz_url"]
            result["geometry"] = attempt(lambda: kmz(url)) if url else {"missing": True}
            report["kmz"].append(result)
    path = Path("artifacts/spatial-probe.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
