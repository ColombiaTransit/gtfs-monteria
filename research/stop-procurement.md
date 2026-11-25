# Stop infrastructure procurement research

2026-11-25. Research leads, not verified stop coordinates.

## LP-001-2018 / SECOP I 18-1-193585

- [Official project](https://www.monteriaamable.gov.co/index.php/es/setp/infraestructura/obras-en-ejecucion/paraderos)
- [Procurement index](https://colombialicita.com/licitacion/109543468)
- [SECOP I process URL candidate](https://www.contratos.gov.co/consultas/detalleProceso.do?numConstancia=18-1-193585)
- [Official SECOP I open data](https://www.datos.gov.co/resource/f789-7hwg.json)
- Montería Ciudad Amable S.A.S.; Consorcio Paraderos Montería 2018; COP 4 billion. The secondary index records liquidation on 2019-12-19.
- Project scope: 70 M10, 150 totem, 390 colombina (610 planned units, not a verified active stop count).
- Index lists PLANOS, ANEXOS, ESPECIFICACIONES TECNICAS, PRESUPUESTO, DISEÑO GRAFICO, PLAN DE MANEJO AMBIENTAL, and prior studies dated 2018-07-23. Prioritize plans and annexes, then actual acceptance/liquidation records.

## SI-MCA-002-2026 / SECOP II

- Contract: CO1.PCCNTR.9318841. Related process IDs: CO1.REQ.9479470 (earlier phase), CO1.REQ.9771263 (selected phase).
- [Contract index, 2026-07-08](https://buscasecop.com/contract/CO1.PCCNTR.9318841/2026%2F07%2F08%2F11%2F26%2F09)
- [Official document archive 2026](https://www.datos.gov.co/en/Estad-sticas-Nacionales/SECOP-II-Archivos-Descarga-Historico-2026/dmgg-8hin)
- Update of stop information/signage; contracted COP 199,183,390. The July 8 snapshot records full payment and a final date of May 25.
- Final report: INFORME DE GESTION FINAL BIG.pdf, 38 MB, document record 804228578.
- Final execution record: ACTA DE EJECUCION FINAL BIGSIGNS.pdf, 804228575.
- Bilateral liquidation record: ACTA DE LIQUIDACION BILATERAL BIGSIGNS.pdf, 804228571.
- These records are indexed, but underlying document contents have not yet been retrieved. Prefer actual installation inventory and locations in these recent files if present.

## Other evidence

[Operator observations on paraderos](https://es.scribd.com/document/444049343/OBSERVACIONES-A-PARADEROS-DE-MONTERIA), undated in inspected text, attributed to Montería Express and SOPROAS, reports a detailed historical stop inventory and references BD, CO and M10 codes. The document includes some address-based descriptions of missing stops, not a verified active stop coordinate list. Do not import missing or proposed locations as active. A 2020 upload date must not be confused with an inspection date. Seek the original inventory or official annex rather than redistributing the Scribd document.

## Next steps

The browser could see indexed metadata but opening document indexes and filtered Socrata endpoints failed. The new workflow uses the official document index and ordinary public HTML links, downloads selected technical documents temporarily, reports document formats, ZIP member names, PDF text coverage and candidate page numbers, then discards the originals. No full PDFs or text transcriptions are committed or published. Review the resulting page candidates and flag image-only files for later analysis. Coordinates and route associations must be validated against current KMZ and route directions; no new stop locations confirmed yet.

## First procurement probe

[Run 45555285310](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45555285310) completed successfully but obtained no document links or files. Socrata metadata and queries worked. The SECOP II contract field is actually `n_mero_de_contrato`; the initial filter omitted it and returned zero rows for the process IDs. SECOP I returned 278 records under the overly broad process reference OR filter; its official process page returned HTTP 403. The BuscaSECOP document pages returned TLS errors. No stop coordinates or locations were extracted.

The second probe corrects the contract filter, adds a separate type-aware document-ID filter, narrows SECOP I to the exact constancia and tries the public SECOP II RetrieveFile URL pattern for the three known document IDs. Those direct links remain candidates until a PDF or ZIP is actually returned. TLS verification remains enabled.

## Second procurement probe

[Run 45555489946](https://github.com/ColombiaTransit/gtfs-monteria/actions/runs/45555489946) completed successfully. The corrected `n_mero_de_contrato` query returned 25 official document records; the separate document-ID query confirmed all three known priority records. Exact SECOP I constancia returned one record. See [secop-2026-documents.csv](secop-2026-documents.csv) for the complete official 2026 document index, URLs and download status.

All seven attempted document downloads (four distinct documents plus three duplicate URL variants) returned HTTP 403; SECOP I also returned HTTP 403. No PDF content or additional stop locations have been retrieved. The newly identified supervisor final report (804228560) and contract (747859448) are high-priority candidates but were not downloaded by this run. Prefer normal public browser access or an official copy from the contracting entity; do not repeatedly retry identical blocked URLs. No document contents or coordinates inferred from filenames.

## Final contractor report supplied by user (2026-11-25)

Source: SECOP II document 804228578, INFORME DE GESTION FINAL BIG.pdf, 194 pages, SHA-256 3d066da9cba658a8c460ef219193c5d55bf72ced546fad160d8760dfed686659. Final report dated 2026-05-25, contract SI-MCA-002-2026. Page numbers below are PDF page numbers.

| Section | Contract quantity (p. 19) | Caption records | Pages |
|---|---:|---:|---|
| Bandera | 148 | 144 | 20–91 |
| M10 | 79 | 74 | 92–128 |
| Colombina | 93 | 88 | 129–176 |
| PEP | 17 | 16 | 177–193 |
| Total | 337 | 322 | |

The first 306 records have 305 distinct printed codes; CO071 appears in two sections. The M10 section includes unusual code 210D05 and CO071. PEP captions have names but no explicit stop codes. The 15-record difference is between contract quantities and caption inventory, not proof of missing operational stops. The record count includes exceptions.

Explicit exceptions: BD085 (printed/stolen, p.50), BD120 (pending construction, p.59), BD146 (not found, p.70), BD148 (park under construction, p.70), BD168 (not found, p.77), BD189 (not found, p.85), M1068 (stolen, p.121). CO034 has a note about a missing front photo (p.137). Preserve all as research records; do not infer current service status.

The local extraction yielded a 322-row CSV with source page and review status. GPS fields and route assignments are blank. No coordinate keywords found in the extracted caption text (pp.20–194); no EXIF GPS tag in 497 distinct embedded image objects, and no attached files. No GPS locations established by this inspection.

PEP UPB photo (p.192) shows a route information panel including Vallejo and Canta Claro–Villacielo, absent from the 18-route API list. These are candidates requiring operational verification. Carrizal is not visibly listed on this specific board; do not infer discontinuation. Several panel route labels differ from the API names, including Pradera 27, Mogambo 22, and Aeropuerto/Santa Elena. Individual stop signage can provide route associations and street names, subject to image legibility and directional verification.

Priorities: obtain original digital inventory or artwork if possible; geocode Bandera addresses with OSM/Photon and match to KMZ, inspect PEP route panels and QR destinations, extract M10/Colombina names and route codes from legible photo regions, resolve duplicate CO071 and exceptions. No fabricated coordinates or automated proximity-only service assignments. Full report contains unrelated financial and personal administrative information; do not commit the original or such data to the public repo.
