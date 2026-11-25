#!/usr/bin/env python3
"""Fetch official KMZs as a temporary research reference, not a published feed."""
import csv
import hashlib
import json
from pathlib import Path
from shapely.geometry import mapping
from shapely.ops import transform
from pyproj import Transformer
from compare_spatial import shapes

def main():
    back = Transformer.from_crs(32618, 4326, always_xy=True)
    features, errors = [], []
    with open("research/api-route-inventory.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rid = int(row["api_route_id"])
            url = row["kmz_url"]
            if not url:
                continue
            try:
                lines, points = shapes(url)
                for i, (name, geom) in enumerate(lines, 1):
                    features.append({"type":"Feature","properties":{"route_id":rid,"line_index":i,"name":name,"source_url":url},"geometry":mapping(transform(back.transform,geom))})
            except Exception as exc:
                errors.append({"route_id":rid,"error":str(exc)[:200]})
    out=Path("artifacts/kmz-reference.geojson")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"type":"FeatureCollection","features":features},ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    print(json.dumps({"lines":len(features),"routes":len({f["properties"]["route_id"] for f in features}),"errors":errors,"sha256":hashlib.sha256(out.read_bytes()).hexdigest()}))
    if errors or len(features)!=34:
        raise SystemExit("Reference differs from the verified 34-line baseline; review before comparing")
if __name__ == "__main__":
    main()
