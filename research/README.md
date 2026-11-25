# Montería public transport research

Last reviewed: 2026-11-25.

## Evidence and scope

- `sources.csv`: official links and candidate GIS sources, with access status.
- `routes.csv`: 22 provisional route records, including eight names independently supported by timetable documents. Codes, current operating status and operating company are not verified. Candidate IDs are internal research identifiers, not public GTFS IDs.
- `timetables.csv`: all 13 documents linked by the official homepage, visually reviewed across 14 pages. Dates range from March to September 2024. Printed time counts count entries at published timing points, not distinct trips; intermediate timing points can describe the same vehicle journey. Historical fares are not valid 2026 fares without further evidence.

The prior research reported a dynamic route listing with ordered stops and a Pradera/P1 example of 28 stops in one direction. The current retrieved page instead displays no routes. Neither the route list nor the stop coordinates have been archived or independently reconfirmed. Candidate route codes and secondary leads need traceable source URLs. The Aeropuerto–Terminal schedule is a research lead, not a verified timetable.

Candidate operators: Metrosinú S.A.S., Montería Express S.A. and Sinumóvil S.A.S. Recaudar Sinú identifies itself as the technology and fare collection operator. Confirm the operating entities and the Movisinú network structure before assigning agencies.

## Timetable interpretation

- Five route names have both Hábil and Festivos documents: Aguas Vivas, Carrizal, Caño Viejo, KM30 and Leticia.
- KM15, Santa Lucía and Villa Caribe currently have one linked Hábil document each.
- Do not infer that Hábil necessarily includes Saturday when the PDF does not state this. Do not infer that every Festivos timetable covers Sunday without confirmation.
- For Leticia, Granero Colón may be an intermediate timing point; do not create a separate trip for every time entry.
- Villa Caribe lists times at Monterroble and UPB on separate pages. Confirm whether this is a circular service.
- KM15 contains an itinerary fragment mentioning KM30. Confirm whether this is a shared segment, a through service or a layout error before generating shapes.
- Some documents use 12-hour clocks without AM/PM or inconsistent suffixes; normalize only after checking chronological order.
- The previously reported 2026 urban fare of COP 3500 is an unverified lead; obtain the applicable decree and separate rural fares.

## Reuse and publication

The repository is public. [Recaudar Sinú terms of use](https://recaudarsinu.com/terminos-y-condiciones), section 6, restrict reproduction without authorization. Keep source references, factual research summaries and independently licensed data separate from third-party content. Do not mirror the PDF artwork, bulk-copy the route database or publish a feed derived from it until the applicable reuse basis is established. No third-party PDFs or full timetable transcriptions are committed. Investigate municipal open data and request permission or an openly licensed feed where needed.

## Work backlog (updated 2026-11-25)

### Completed research
- [x] Inspect public route portal; verify route, direction and stop API endpoints.
- [x] Resolve 18 API route names, 36 directions, 148 distinct API stop IDs and 639 stop occurrences; no usable stop coordinates in the API.
- [x] Inspect 17 KMZ route pairs and compare the ANSV GIS route and PEP layers. Keep KMZ as primary geometry evidence; ArcGIS lines are partial matches only.
- [x] Identify 2018 and 2026 stop infrastructure procurements and inspect the supplied 2026 contractor final report (322 caption records). See [stop-procurement.md](stop-procurement.md).

### Next research priorities
- [ ] Extract service windows, departure times and frequencies from official Recaudar Sinú timetable PDFs; verify 2024 validity, day types, timing points and coverage of missing routes.
- [ ] Search Alcaldía de Montería, Secretaría de Tránsito/Movilidad and Montería Ciudad Amable for route authorizations, operational plans, resolutions, frequency and service-hour tables, fare decrees and actual boarding rules.
- [ ] Investigate Movisinú app public functionality and public data sources; check whether it provides stop coordinates, direction itineraries or schedule data beyond the web portal.
- [ ] Investigate operator websites and official public announcements (Metrosinú, Montería Express, Sinumóvil, and Monteriana Móvil if operational role confirmed).
- [ ] Review 2026 supervisor report, contract and completion record if available; seek the original digital stop inventory/artwork and 2018 plans and annexes. SECOP document downloads returned HTTP 403; avoid redundant retries.
- [ ] Verify Vallejo (VA), Canta Claro–Villacielo (CC), Villa Caribe, and Furatena against current service evidence; establish whether these are separate active routes, variants or historical names.
- [ ] Resolve API/KMZ endpoint discrepancies and Furatena missing geometry using independent evidence; GraphHopper reconstruction only after the itinerary is supported.
- [ ] Confirm operators and agency structure; establish source reuse basis before publishing.
- [ ] Build GTFS generator with verified schedules, Python holidays for Colombia, MobilityData validator, tests and fixed-name release workflow when data is ready.

### Parked by user request
- [ ] **PARKED: stop geocoding.** Geocode the 144 Bandera captions and 16 PEP locations using Photon/OSM and verified street/landmark evidence; compare with KMZ lines and correct road side. Do not start geocoding until user resumes this work. Keep the 74 M10 and 88 Colombina photo-label extraction, route-sign associations, duplicate code CO071 and seven explicit infrastructure exceptions as related stop-inventory review tasks. No fabricated coordinates or proximity-only route assignments.
- [ ] Moovit remains a later comparison source, not a primary research source.

## Public portal technical investigation (2026-11-24)

- Indexed source: https://recaudarsinu.com/rutas — 18 route names, Pradera P1 with 28 stops in one direction, a direction toggle and urban classification. A fresh text retrieval instead returned an empty route list. This is consistent with asynchronous frontend loading, but is not proof of the underlying implementation.
- https://recaudarsinu.com/nosotros also lists Monteriana Móvil SAS as a fourth MOVISINÚ member; the SIU description names only the other three. Confirm the fourth member's operational role.
- https://recaudarsinu.com/politica-de-datos identifies the Android package as `com.recaudarsinu.movisinu`.
- Direct HTTP retrieval in the analysis runtime failed at DNS resolution; no raw frontend JavaScript or API response has been inspected yet.
- `scripts/probe_recaudar.py` uses Chromium to observe ordinary public frontend traffic, record sanitized URL paths and query parameter names, JSON response structure, script filenames and route-related URL literals. It tests the initial page, a direction switch and one alternate route, if available. No login, credentials, full response bodies, or bulk database copies are retained.
- Workflow: `.github/workflows/probe-recaudar.yml`. It can run manually or on pushes affecting the probe. Download the `recaudar-probe` artifact and inspect its JSON before designing the collector. A successful workflow does not by itself establish that the portal returned data.
- Next: identify actual route/stop/geometry endpoints, response schemas, relationships and any access/reuse conditions. No guessed endpoints are treated as verified.
