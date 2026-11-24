# Montería public transport research

Last reviewed: 2026-11-24.

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

## Work backlog

- [ ] Inspect public route portal frontend and normal public network requests; identify route/stop/shape endpoints and any usage restrictions.
- [ ] Confirm route IDs, names, directions, variants, active status and operating company.
- [ ] Retrieve ANSV SETP GIS layer; inspect metadata, pagination and license; validate route alignment.
- [ ] Investigate Montería Amable and municipal transport decisions for stops, frequencies, operating windows and fares.
- [ ] Verify timetable validity and day types; obtain reuse permission or independently licensed schedules before storing full transcriptions in this public repository.
- [ ] Collect OSM stop and geometry references with proper attribution; use GraphHopper for missing shapes or estimated running times when necessary, clearly labeling estimates.
- [ ] Build GTFS generator with verified routes and explicit calendar exceptions using Python holidays for Colombia.
- [ ] Add MobilityData validator, tests, and fixed-name release workflow after data is ready.
- [ ] Keep Moovit as a later comparison source rather than a primary source.
