# Match result

- **Candidate profile:** `urn:uuid:8f73559a-b25b-56dd-a91d-cf81a2926480` (2026-10-27T11:00:00+01:00)
- **Job profile:** `urn:uuid:5d2671cc-7e2b-5f18-8444-4ff63d11b269` (2026-10-27T10:15:00+01:00)

> Demonstration output. Weights are UNCALIBRATED and illustrative. UNKNOWN means information is missing or not comparable; it is not a negative result. Not suitable for automated decisions about people.

## Hiring-Fit (does the candidate meet the job's requirements?)

- **Hard conditions:** UNRESOLVED
- **Indicative score (soft criteria, known only):** 1.00
- **Known weight coverage:** 75%
- **Weights:** demo-hiring-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 4, UNKNOWN 2

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `competencies/sql` | HARD | MET | SQL: proficiency ADVANCED vs required ADVANCED (basis not stated) |
| `competencies/python` | SOFT | MET | Python: proficiency ADVANCED vs required INTERMEDIATE (basis not stated) |
| `languages/de` | HARD | MET | de: NATIVE vs required C1 |
| `languages/en` | HARD | MET | en: C1 vs required B2 |
| `domainExperience/supply-chain-planning` | HARD | **UNKNOWN** | Supply-Chain-Planung: not stated |
| `careerLevel` | SOFT | **UNKNOWN** | candidate's current career level not stated |

## Career-Fit (does the job meet the candidate's conditions and wishes?)

- **Hard conditions:** NONE_DEFINED
- **Indicative score (soft criteria, known only):** 1.00
- **Known weight coverage:** 100%
- **Weights:** demo-career-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 3

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `archetypes/wish` | SOFT | MET | job archetype demand-planner: the job has an included value |
| `location/wish` | SOFT | MET | Hamburg: 0.0 km straight line (+/-20.0 km) vs max 40.0 km |
| `workingTime/wish` | SOFT | MET | schedule FULL_TIME |

_Generated deterministically by the AJMS reference implementation. Synthetic data._
