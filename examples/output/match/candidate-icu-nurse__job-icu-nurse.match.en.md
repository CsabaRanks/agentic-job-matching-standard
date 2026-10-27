# Match result

- **Candidate profile:** `urn:uuid:5a6b7c8d-9e0f-4a1b-8c2d-3e4f5a6b7c8d` (2026-10-15T18:00:00+02:00)
- **Job profile:** `urn:uuid:0e1f2a3b-4c5d-4e6f-a7b8-c9d0e1f2a3b4` (2026-10-19T10:00:00+02:00)

> Demonstration output. Weights are UNCALIBRATED and illustrative. UNKNOWN means information is missing or not comparable; it is not a negative result. Not suitable for automated decisions about people.

## Hiring-Fit (does the candidate meet the job's requirements?)

- **Hard conditions:** ALL_MET
- **Indicative score (soft criteria, known only):** 1.00
- **Known weight coverage:** 100%
- **Weights:** demo-hiring-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 7

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `languages/de` | HARD | MET | de: NATIVE vs required B2 |
| `qualifications/q-nursing` | HARD | MET | Abgeschlossene Pflegeausbildung: EQF 4 vs required 4; field of study not compared automatically |
| `domainExperience/icu-care` | SOFT | MET | Intensivpflege: 96 months vs required 24 |
| `careerLevel` | SOFT | MET | job SENIOR, candidate currently SENIOR (step +0) |
| `domainCriteria/org.example.healthcare.professional_registration` | HARD | MET | Berufserlaubnis Pflege: stated true, condition EQUALS true |
| `domainCriteria/org.example.healthcare.specialties` | HARD | MET | Fachgebiet: stated ["ICU", "ANESTHESIA"], condition ANY_OF ["ICU"] |
| `domainCriteria/org.example.healthcare.ventilation_hours` | SOFT | MET | Erfahrung Beatmungspflege: stated 800, condition AT_LEAST 500 |

## Career-Fit (does the job meet the candidate's conditions and wishes?)

- **Hard conditions:** NOT_MET
- **Indicative score (soft criteria, known only):** 0.00
- **Known weight coverage:** 100%
- **Weights:** demo-career-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 3, PARTIALLY_MET 1, NOT_MET 2, UNKNOWN 1, NOT_APPLICABLE 1

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `archetypes/hard` | HARD | MET | job archetype icu-nurse: the job has an included value |
| `compensation/hard` | HARD | PARTIALLY_MET | job 3,849-4,356 EUR/month vs at least 3,900; job pays 13 times per year; compared per month; scaled from 38.5 h to 39 h per week |
| `location/hard` | HARD | **UNKNOWN** | Leipzig: travel time limit 40 MIN needs routing or timetable data; not derived from distance |
| `workModel` | SOFT | NOT_APPLICABLE | candidate marked this as not applicable |
| `workingTime/hard` | HARD | MET | 38.5-38.5 h/week vs acceptable 30-39; shiftWork yes |
| `workingTime/wish` | SOFT | **NOT_MET** | schedule FULL_TIME |
| `contract/hard` | HARD | MET | PERMANENT_EMPLOYMENT |
| `domainCriteria/org.example.healthcare.night_shifts_per_month` | HARD | **NOT_MET** | Nachtdienste pro Monat: stated 6, condition AT_MOST 4 |

_Generated deterministically by the AJMS reference implementation. Synthetic data._
