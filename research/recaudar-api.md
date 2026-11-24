# Recaudar Sinú public API investigation

Observation: 2026-11-24, [GitHub Actions run 45487996948](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45487996948), artifact 14965176424. Job succeeded on Ubuntu 24.04; navigation HTTP 200; 10 fetch/XHR responses, 15 scripts, one DOM snapshot. The only recorded failed request was Google Analytics (aborted).

## Verified public GET endpoints

| URL | HTTP | Observed data |
|---|---|---|
| https://data.recaudarsinu.com/api/info | 200 | company and navs arrays, both empty |
| https://data.recaudarsinu.com/api/rutas | 200 | 18 route records, 2712 bytes |
| https://data.recaudarsinu.com/api/rutas/1 | 200 | one route record, 157 bytes |
| https://data.recaudarsinu.com/api/sentidos/1 | 200 | two direction records, 287 bytes |

Route schema: id (int), ruta (str), embled (null in observed first item), kmz_file (str), tipo (str), visual (null), created_at (null), updated_at (null).

Direction schema: id (int), ruta_id (int), sentido (str), created_at (str), updated_at (str).

No scalar values were retained by this probe, so the mapping between API IDs and route names remains unverified. The kmz_file field suggests a geometry resource, but its URL, contents, availability and license have not been verified.

## Frontend

Gatsby/React/webpack, with Google Maps. Route-specific chunk observed:
https://recaudarsinu.com/component---src-pages-rutas-tsx-81c61176d01e59c67ab9.js

Gatsby page data:
https://recaudarsinu.com/page-data/rutas/page-data.json

The initial DOM snapshot had no stop count label and no visible direction switch. Stop requests and KMZ retrieval were not observed. The initial probe may have sampled before the page finished rendering; inspect the route-specific chunk for endpoint fragments and wait for the actual direction response before taking a second snapshot.

No full database copies or third-party JS are stored. Reuse conditions remain unresolved.

## Second browser probe

[Run 45488327174](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45488327174), artifact 14965750912, 2026-11-24: successful. Confirmed an additional public GET endpoint:

- https://data.recaudarsinu.com/api/paradas/1 — HTTP 200, 28 records, 4911 bytes.
- First item schema: id (int), parada (str), longitud (null), latitud (null), created_at (str), updated_at (str), pivot (sentido_id int, parada_id int).
- The direction ID parameter is inferred from the pivot relationship and still needs validation across other directions. Stop ordering semantics and coordinate coverage are not yet verified.
- The route-specific JS chunk was retrieved (22765 bytes), but the literal scan only found /rutas. Browser network observation supplied the stop endpoint.
- No visible direction switch or stop count in the captured DOM snapshot; only analytics request failures. Do not interpret missing DOM labels as missing API data.

Next: bounded public API inventory of route/direction relationships, stop counts and coordinate completeness, and KMZ metadata, with no publication of raw stop lists or third-party geometry.
