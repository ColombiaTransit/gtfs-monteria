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

## Spatial probe (2026-11-25)

[Run 45553609709](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45553609709), job 139000306078: the ANSV service is accessible from GitHub Actions. Layer 0 Propuesta_PEP has 11 proposed points; layer 1 Municipio_PEP has 13 municipal points (fields id, tipo, zona); layer 5 Municipio_Rutas_SETP has 30 polyline features (id, tipo, num, shape_leng). Service has 13 layers in total. No explicit license or description is provided in inspected metadata. Municipal points are candidates, not verified active boarding positions.

All 18 API route names are now resolved in [kmz-endpoints.csv](kmz-endpoints.csv). Missing KMZ route 17 is FURATENA. All 17 KMZ pairs have two named points at the line endpoints within rounded 1 m. These are geographic termini, not verified boarding positions. Tambo's two lines are both digitized MOCARI to TAMBO; the 14.193 km line needs reversal if assigned to the return trip. Sabanal and Rancho Grande labels disagree with coordinate orientation. Panzenú has an anomalous second line name. Match directions using evidence rather than line order or naming alone.

Added spatial comparison to check bidirectional line overlap at 50 m, rank ArcGIS candidates, find PEP points near KMZ lines and endpoints, and compare first/last API stop names with KMZ endpoints. An unmatched ArcGIS line is not proof of Furatena; route identification needs independent evidence. No full third-party geometries are committed.

## Spatial comparison (2026-11-25)

[Run 45553848333](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45553848333), job 139001087468: all 30 ArcGIS polylines, 24 PEP points, 34 KMZ lines and 36 API directions inspected; no reported errors. See [arcgis-route-comparison.csv](arcgis-route-comparison.csv), [arcgis-pep-comparison.csv](arcgis-pep-comparison.csv) and [direction-endpoint-audit.csv](direction-endpoint-audit.csv).

- No full-route matches at the chosen 50 m buffer and harmonic bidirectional coverage threshold of 0.85. Highest score 0.7113: ArcGIS object 8, expresa 27, against Tambo KMZ line 2. All 30 ArcGIS id values are zero. There are 20 expresa and 10 alimentadora features; they appear to describe partial corridors or another network design. Do not substitute any as Furatena without independent evidence.
- 11 of 13 Municipio_PEP points and all 11 Propuesta_PEP points are within 50 m of at least one KMZ line. Propuesta_PEP contains five PEP Existente and six PEP Propuesto objects; the latter are not verified active stops. No PEP point is within 50 m of a KMZ terminus. Nearest is municipal object 30 (objectid_1 9), 250.6 m from PEP UPB. Proximity alone does not establish boarding service, names, uniqueness or correct side of the road.
- Only Mogambo directions 29 and 30 have exact normalized names matching the oriented KMZ endpoints. For the other 32 directions with KMZ, assess name aliases and actual endpoint discrepancies, not just string similarity. Some endpoints differ materially (e.g. Santa Lucía and KM30 API list UPB vs KMZ 41K4; KM15 lists KR3/CL41 vs KMZ 27K4). Do not silently replace official stop names with KMZ labels.
- Furatena (route 17) directions 33 and 34 run between Br. El Privilegio and UPB. Other KMZ files contain candidate endpoint anchors: Santander for El Privilegio, Dorado and Rancho Grande for PEP UPB. UPB and PEP UPB are not yet established as the same boarding location. Obtain intermediate route evidence and geolocate anchors before GraphHopper reconstruction.
- Keep the 17 KMZ route pairs as primary geometry evidence; government PEP points are supplementary candidates. Seek the municipal LP-001-2018 infrastructure location annex and current official stops. Do not treat planned infrastructure as operational.

The threshold is a diagnostic chosen for this comparison, not an official standard. No full route geometry has been published in this repository; reuse and operational verification remain pending.
