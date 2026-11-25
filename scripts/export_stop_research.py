#!/usr/bin/env python3
"""Temporary research extract of public passenger stop metadata."""
import csv
import json
from pathlib import Path
from probe_spatial import API, js

def main():
    rows=[]
    errors=[]
    for route in js(API+"rutas"):
        rid=route["id"]
        try:
            for direction in js(API+f"sentidos/{rid}"):
                did=direction["id"]
                for sequence, stop in enumerate(js(API+f"paradas/{did}"),1):
                    rows.append({"route_id":rid,"route_name":route.get("ruta"),"direction_id":did,"direction_name":direction.get("sentido"),"sequence":sequence,"api_stop_id":stop["id"],"stop_name":stop.get("parada"),"latitude":stop.get("latitud"),"longitude":stop.get("longitud")})
        except Exception as e:
            errors.append({"route_id":rid,"error":str(e)[:150]})
    out=Path("artifacts/api-stop-research.csv")
    out.parent.mkdir(exist_ok=True)
    if not rows:
        raise RuntimeError("No stop records")
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({"occurrences":len(rows),"ids":len({r["api_stop_id"] for r in rows}),"directions":len({r["direction_id"] for r in rows}),"errors":errors}))
    if errors:
        raise SystemExit("Incomplete extract")
if __name__=="__main__":
    main()
