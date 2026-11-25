# Timetable processing v1 — 2026-11-25

All twelve indexed 2024 timetable PDFs for the seven API routes were reviewed using public text representations of the exact document URLs in timetables.csv. Direct PDF downloads failed DNS in the analysis runtime; web PDF screenshots failed or were unavailable. The original page layouts have NOT been reverified. The following is a provisional text-based extraction summary, not a verified present-day schedule.

| Timetable ID | Timing point A (count, span) | Timing point B (count, span) | Intermediate | Status |
|---|---|---|---|---|
| aguas_vivas_habil | Aguas Vivas 13, 06:15–18:15 | 41K4 11, 07:15–17:16 | — | Text grouped, Hábil day label |
| aguas_vivas_fest | Aguas Vivas 4, 09:00–17:30 | 41K4 4, 09:58–18:28 | — | Text grouped |
| carrizal_habil | Carrizal 7, 05:57–17:17 | 41K4 6, 06:34–16:20 | — | Monday–Saturday; check Parque Catedral itinerary |
| carrizal_fest | Carrizal 6, 07:46–17:38 | 41K4 5, 08:36–16:40 | — | Same endpoint check |
| cano_viejo_habil | Unassigned | Unassigned | — | 9 times recovered; flattened layout prevents reliable column assignment |
| cano_viejo_fest | 41K4 3, 06:50–15:30 | C. Viejo 3, 07:50–16:30 | — | Table grouped; confirm KMZ Palotal match |
| km30_habil | KM30 24, 06:00–18:05 | 41K4 21, 06:00–16:59 | — | Afternoon normalization and column grouping inferred; check page |
| km30_fest | KM30 10, 08:30–18:05 | 41K4 10, 07:19–16:59 | — | Table grouped |
| km15_habil | KM15 33, 06:10–18:36 | Parque 29, 06:50–17:44 | — | Afternoon normalization; Parque differs from KMZ 27K4; itinerary includes KM30 fragment |
| leticia_habil | 41K4 4, 05:20–15:10 | Tronco 4, 06:40–16:40 | Granero Colón 4 | Likely intermediate outbound point; validate direction and arrivals/departures |
| leticia_fest | 41K4 3, 06:50–15:50 | Tronco 3, 08:10–17:20 | Granero Colón 3 | Same |
| santa_lucia_habil | S. Lucía 19, 05:33–17:56 | 41K4 20, 06:28–18:20 | — | Afternoon normalization inferred; check page |

258 printed time entries total, matching the twelve-document index. 249 associated with named timing points, of which 242 are endpoint candidates and seven are intermediate candidates. Nine unassigned Caño Viejo weekday entries. These are NOT 258 distinct trips. No direction ID or trip pairing is asserted by the draft. User receives a local CSV with one record per printed time, explicit normalization/review status and unresolved rows. Do not commit complete third-party schedule transcriptions until reuse basis established.

## Focused checks before generation

- Obtain actual PDF page images for all twelve documents, particularly Caño Viejo Hábil, KM15, KM30 Hábil and Santa Lucía. Do not infer missing directional assignments.
- Preserve source day labels: five pairs of Hábil/Lunes–Sábado and Festivos; only Aguas Vivas uses Hábil among these five. Saturday not confirmed for Aguas Vivas. Festivos as Sunday is a provisional model choice, not a source statement. KM15 and Santa Lucía have no holiday/Sunday timetable in current index.
- Explicit AM/PM normalized to 24-hour notation; unmarked afternoon values inferred from chronology in Santa Lucía/KM15/KM30 Hábil; Leticia's inconsistent 15:30 pm interpreted as 15:30. No trip is generated from a standalone intermediate timing point.
- Match departure timing points to verified geographic stops and shape orientation. The PDF does not establish running times merely by listing times in neighboring columns. Do not create duplicate services from round-trip rows.
- Original 2024 tariffs and present validity remain unverified. Source reuse gate unchanged. No generator or public feed built by this step.
