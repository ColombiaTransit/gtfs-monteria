#!/usr/bin/env python3
"""Compare SETP lines against official KMZ; report only evidence and scores."""
import csv
import io
import json
import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from probe_spatial import ROOT, API, get, js, attempt, coords, LIMIT

PROJECT = Transformer.from_crs("EPSG:4326", "EPSG:32618", always_xy=True)
BUFFER_M = 50


def xy(coord):
    return PROJECT.transform(*coord[:2])


def normalize(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return re.sub(r"[^a-z0-9]", "", s.encode("ascii", "ignore").decode().lower())


def features(layer_id):
    base = f"{ROOT}/{layer_id}/query"
    count = js(base, where="1=1", returnCountOnly="true", f="json")["count"]
    data = js(base, where="1=1", outFields="*", returnGeometry="true", outSR=4326, f="json")
    result = data["features"]
    if len(result) != count or data.get("exceededTransferLimit"):
        raise RuntimeError(f"Layer {layer_id}: incomplete download")
    return result


def shapes(url):
    lines, points = [], []
    with zipfile.ZipFile(io.BytesIO(get(url))) as z:
        members = [i for i in z.infolist() if i.filename.lower().endswith(".kml")]
        if sum(i.file_size for i in members) > LIMIT:
            raise ValueError("KML too large")
        for member in members:
            root = ET.fromstring(z.read(member))
            for pm in root.findall(".//{*}Placemark"):
                name = pm.findtext("{*}name", "")
                for item in pm.findall(".//{*}LineString"):
                    c = coords(item)
                    if len(c) >= 2:
                        lines.append((name, LineString([xy(p) for p in c])))
                for item in pm.findall(".//{*}Point"):
                    c = coords(item)
                    if c:
                        points.append((name, Point(xy(c[0]))))
    return lines, points


def main():
    report = {"buffer_m": BUFFER_M, "arcgis_lines": [], "pep": [], "directions": [], "errors": []}
    known = []
    endpoints = []
    with open("research/api-route-inventory.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rid = int(r["api_route_id"])
            if r["kmz_url"]:
                try:
                    lines, points = shapes(r["kmz_url"])
                    for index, (name, geom) in enumerate(lines, 1):
                        known.append({"route_id": rid, "line_index": index, "name": name, "geom": geom})
                    endpoints.extend((rid, name, p) for name, p in points)
                except Exception as e:
                    report["errors"].append({"route_id": rid, "kmz_error": type(e).__name__})
            # Check actual first and last API names against KMZ endpoints, not all names.
            dirs = attempt(lambda: js(API + f"sentidos/{rid}"))
            if not isinstance(dirs, list):
                report["errors"].append({"route_id": rid, "directions": dirs})
                continue
            for d in dirs:
                did = d["id"]
                stops = attempt(lambda: js(API + f"paradas/{did}"))
                item = {"route_id": rid, "direction_id": did, "direction_name": d.get("sentido")}
                if isinstance(stops,list) and stops:
                    a,b = stops[0].get("parada"),stops[-1].get("parada")
                    item.update(first_stop=a,last_stop=b,stop_count=len(stops))
                    for k,n in (("first_stop",a),("last_stop",b)):
                        item[k+"_endpoint_exact_name_match"] = [name for rr,name,p in endpoints if rr==rid and normalize(name)==normalize(n)]
                    # Identify lines by geometry rather than trusting names.
                    candidates=[]
                    for l in known:
                        if l["route_id"]!=rid:
                            continue
                        c=l["geom"].coords
                        local=[(name,p) for rr,name,p in endpoints if rr==rid]
                        if not local:
                            continue
                        start=min(local,key=lambda np:np[1].distance(Point(c[0])))[0]
                        end=min(local,key=lambda np:np[1].distance(Point(c[-1])))[0]
                        candidates.append({"line_index":l["line_index"],"start":start,"end":end,
                            "orientation_matches_api_names":normalize(start)==normalize(a) and normalize(end)==normalize(b),
                            "reverse_matches_api_names":normalize(end)==normalize(a) and normalize(start)==normalize(b)})
                    item["line_candidates"]=candidates
                else:
                    item["stop_error"]=stops
                report["directions"].append(item)
    for feat in features(5):
        a=feat["attributes"]
        paths=(feat.get("geometry") or {}).get("paths",[])
        segments=[LineString([xy(p) for p in path]) for path in paths if len(path)>=2]
        if not segments:
            continue
        geom=unary_union(segments)
        candidates=[]
        for l in known:
            g=l["geom"]
            # Both directional coverage measures prevent short shared corridors
            # from being mistaken for full-route matches.
            arc_cover=geom.intersection(g.buffer(BUFFER_M)).length/geom.length if geom.length else 0
            kmz_cover=g.intersection(geom.buffer(BUFFER_M)).length/g.length if g.length else 0
            score=2*arc_cover*kmz_cover/(arc_cover+kmz_cover) if arc_cover+kmz_cover else 0
            candidates.append({"route_id":l["route_id"],"line_index":l["line_index"],
                "arc_coverage":round(arc_cover,4),"kmz_coverage":round(kmz_cover,4),"score":round(score,4)})
        candidates.sort(key=lambda x:x["score"],reverse=True)
        report["arcgis_lines"].append({"attributes":{k:a.get(k) for k in ("objectid_1","id","tipo","num")},
            "length_km":round(geom.length/1000,3),"path_count":len(segments),"best_matches":candidates[:3]})
    for layer in (0,1):
        for f in features(layer):
            g=f.get("geometry") or {}
            if not all(k in g for k in ("x","y")):
                continue
            p=Point(xy((g["x"],g["y"])))
            matches=sorted(({"route_id":r,"endpoint":n,"distance_m":round(p.distance(q),1)}
                for r,n,q in endpoints),key=lambda x:x["distance_m"])[:3]
            close=[{"route_id":l["route_id"],"line_index":l["line_index"],"distance_m":round(p.distance(l["geom"]),1)}
                   for l in known if p.distance(l["geom"])<=BUFFER_M]
            a=f["attributes"]
            report["pep"].append({"layer_id":layer,"attributes":{k:a.get(k) for k in ("objectid","objectid_1","id","tipo","zona","name") if k in a},
                 "nearest_endpoints":matches,"lines_within_50m":close})
    report["summary"]={"kmz_lines":len(known),"kmz_endpoint_records":len(endpoints),
        "arcgis_lines":len(report["arcgis_lines"]),"pep_points":len(report["pep"]),
        "directions":len(report["directions"]),
        "arcgis_strong_candidates":sum(bool(r["best_matches"]) and r["best_matches"][0]["score"]>=0.85 for r in report["arcgis_lines"])}
    out=Path("artifacts/spatial-comparison.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))


if __name__=="__main__":
    main()
