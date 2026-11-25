# Municipal stop matching — 2026-11-25

Sources: contractor final report INFORME DE GESTION FINAL BIG.pdf (SECOP 804228578, May 25 2026), locally extracted 322 captions, and [API export run 45569268491](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45569268491). Export completed successfully, 639 stop occurrences / 148 distinct API IDs across the observed network. No shared municipal code field; API numeric IDs and municipal BD/CO/M10 codes are different identifiers. No coordinates in the API export.

## First pass

144 Bandera and 16 PEP captions contain location labels. 74 M10 and 88 Colombina records have no extracted location name in captions; their photos require further review. Normalize diacritics, whitespace, punctuation, CRA/KR and CLL/CL; compare names, then limited prefix aliases (PEP, Br., Urb.) and explicitly reviewed landmark candidates. Street-token matching is a separate weak signal, not a stop identity. No geocoding done.

- Exact normalized names: 8 API IDs, 40 occurrences, including one generic street KR25 (BD011). Seven non-street exact name IDs, 36 occurrences.
- Prefix aliases: 5 IDs, 32 occurrences.
- Manually selected landmark candidates: 6 IDs, 14 occurrences, 7 pairs (Suricentro has two candidate signs).
- Photo label candidate: API 30 Clínica de Traumas y Fracturas, municipal 210D05, page 92, 4 occurrences.
- Combined excluding street-only and KR25: 19 distinct API IDs / 86 occurrences / 20 candidate pairs. No physical stop identity or direction validated. Additional street token results: 82 pairs for 30 IDs / 110 occurrences; not counted as named landmark matches. This pass is conservative and incomplete, not a final coverage measurement. Comfacor code BD184 matches multiple differently named API locations; Pradera neighborhood vs PEP Pradera also ambiguous. 
- Examples: API 44 Cai Garzones ↔ BD001; API 37 Cai Ribera ↔ BD052; API 15 Ara Costa de Oro ↔ BD126; API 74 SENA ↔ BD130; API 77 C.C. Alamedas ↔ BD158; API 83 I.E. Guillermo Valencia ↔ BD134; API 85 I.E. Mercedes Abrego ↔ BD137; API 4 UPB ↔ PEP UPB. These are location candidates, not boarding-side confirmation.
- API 81 Suricentro ↔ BD131/BD132; API 47 T. Transporte ↔ PEP Terminal; API 104 Coliseo Miguel Happy Lora ↔ PEP Coliseo; API 114 Villa Mellisa ↔ PEP Villa Melisa. Inspect photo route labels, directions and adjacent API entries before accepting. No full raw source copies in repository. Local candidate CSV provided to user.

## Boarding practice and transition

User reports current flag-down boarding and stop-button alighting along the route. Treat as local operational observation, not proof of permission everywhere. [2019 local reporting](https://larazon.co/paraderos-unicos-puntos-autorizados-para-dejar-y-recoger-pasajeros/) says designated stops were promoted as authorized points. [2021 Universidad de Córdoba fieldwork](https://repositorio.unicordoba.edu.co/bitstream/handle/ucordoba/6486/velasquezsanchezluisfelipe.pdf?isAllowed=y&sequence=1), pp.60–64, fig.10 and 11: 23 physical stops surveyed in comuna 2 and 94.61% of respondents did not use a designated stop. Not representative of whole city; figure 10 map is a new geographic lead, screenshot unavailable through web. [24 November 2026 campaign](https://gsnoticias.com/monteria-inicio-campana-de-cultura-de-movilidad-segura-con-el-setp/) promotes designated stop use ahead of January 2027 implementation. Formal rules and actual transition date still need verification. GTFS Schedule continuous_pickup/drop_off=0 only where service actually offers unrestricted boarding/alighting and is appropriate for public guidance; use segment overrides for exceptions, no claim that all roads permit stopping. Keep physical stops and named landmarks distinct.

## Additional sources

- 2021 comuna 2 study above: 23 stop locations map and three named locations with route-use evidence; obtain original GIS if available.
- [Javeriana 2019 operating diagnosis](https://redcol.minciencias.gov.co/Record/JAVERIANA_b72c6570709686458150f25f54d221da): mapped 300 m stop catchments in secondary text; seek original thesis and GIS annex.
- [ArcGIS POT item 31b4bfbed9c7486d9efdcf50678c7c83](https://www.arcgis.com/home/item.html?id=31b4bfbed9c7486d9efdcf50678c7c83): municipal supplied POT layers according to metadata, item data/service URLs not yet retrieved.
- [IGAC 1:1000 base map 2024](https://mapas2.igac.gov.co/server3/rest/services/carto/carto1000monteria23001000/MapServer): municipal mapping from 2023 aerial imagery; street and landmark evidence, stop layer not confirmed.
- [Montería and Montería_PMG_JEJC public FeatureServers](https://services5.arcgis.com/85aFYYEQ9koK4ueu/ArcGIS/rest/services): published layer lists contain road classes and neighborhoods, no stop layer. 
- [Terminal manual V2](https://www.terminaldemonteria.com/files/MANUAL-OPERATIVO-TERMINAL-DE-TRANSPORTE-DE-MONTERIA-V2.pdf) indexed text specifies urban boarding at external stop on Calle 41 and drop-off in terminal; retrieve current V4 to verify. 
- [Busser historic operator page](https://metrosinu.wordpress.com/busser/) and ministry BusApp reporting: separate historical leads, no APK/backend probing resumed.
- SECOP 2018 plans and 2024 consultant product B/F remain high-value; seek original 2026 signage artwork/digital inventory from Montería Amable. No duplicate blocked SECOP retries.

Next: visually transcribe 162 unnamed M10/Colombina records and route badges as legible; compare route-direction context and repeated landmarks. Keep geocoding parked until user resumes it. No GTFS published, no GPS matches confirmed.
