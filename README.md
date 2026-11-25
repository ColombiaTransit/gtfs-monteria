# GTFS Montería

Research and development of a static GTFS feed for public bus transport in Montería, Córdoba, Colombia.

## Scope

Investigate Metrosinú and the wider Movisinú network, including candidate operators Montería Express and Sinumóvil. Operator-to-route assignments and the final GTFS agency structure are not yet confirmed.

## Research inventory (2026-11-25)

- [Source register](research/sources.csv)
- [Candidate route register](research/routes.csv)
- [Official timetable document index](research/timetables.csv)
- [Research notes and backlog](research/README.md)
- [Operational register v1](research/operational-register-v1.csv)
- [V1 modeling assumptions and implementation backlog](research/operational-register-v1.md)

The official Recaudar Sinú homepage links 13 timetable PDFs for eight route names. The documents date from 2024; their current operational validity is unknown. Subsequent API investigation confirmed 18 listed routes and 36 directions, with 17 available KMZ pairs. The operational register is a provisional baseline; actual schedules, current operating assignments and source reuse basis remain unresolved. The additional candidate routes remain research leads.

No GTFS generator or release exists yet. No third-party PDFs or complete datasets are mirrored. Review permissions before redistribution.

Timezone: America/Bogota. Primary sources: Recaudar Sinú, Montería Amable, municipal transport authorities and public GIS datasets.
