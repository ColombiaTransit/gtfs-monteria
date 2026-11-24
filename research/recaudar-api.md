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

## Full network metadata inventory

[Run 45489221168](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45489221168), artifact 14966175280, 2026-11-24. See [api-route-inventory.csv](api-route-inventory.csv).

- 18 routes, 36 directions, 639 stop occurrences, 148 distinct stop IDs.
- All 36 direction-to-route links and all 639 stop-to-direction pivot links match; all 639 occurrences have names.
- Zero occurrences have usable coordinates. A stop ID is not necessarily one physical roadside boarding position, especially if reused in both directions. Do not construct stops.txt directly from these IDs without geolocation and direction checks.
- 17 routes are typed urbana. Route 17 has no type and no KMZ reference; its directions 33 and 34 contain 23 and 25 stops respectively.
- 17 valid KMZ files are served by https://recaudarsinu.com/rutas/ (not the data subdomain, which returned 404). Each contains two LineString and two Point elements in one KML document. In total: 34 lines and 34 points. The two points are likely route endpoints, not a complete stop inventory; validate their meanings and line orientation.
- No explicit stop sequence field is present in the pivot schema. Verify array ordering against the portal and geometry.
- Route ID-to-name mapping is still pending. Do not join candidate IDs by row number.

Next: compare the named stops with independently sourced OSM and municipal stops, determine whether source IDs denote stop areas or boarding points, validate direction-to-line assignment, and identify route 17. If stop positions cannot be supported by evidence, consider continuous pickup/drop-off only where that boarding practice is confirmed. Reuse permission for official source data remains unresolved.
