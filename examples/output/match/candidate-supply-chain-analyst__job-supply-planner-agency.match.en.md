# Match result

- **Candidate profile:** `urn:uuid:dcde3cca-c19a-55b6-8354-1d988ad1eb21` (2026-10-20T09:00:00+02:00)
- **Job profile:** `urn:uuid:c4d5e6f7-1a2b-4c3d-9e8f-7a6b5c4d3e2f` (2026-10-22T08:15:00+02:00)

> Demonstration output. Weights are UNCALIBRATED and illustrative. UNKNOWN means information is missing or not comparable; it is not a negative result. Not suitable for automated decisions about people.

## Hiring-Fit (does the candidate meet the job's requirements?)

- **Hard conditions:** UNRESOLVED
- **Indicative score (soft criteria, known only):** 1.00
- **Known weight coverage:** 100%
- **Weights:** demo-hiring-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 3, UNKNOWN 1

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `competencies/sap-mm` | HARD | **UNKNOWN** | SAP MM: not stated in the candidate profile |
| `languages/de` | HARD | MET | de: NATIVE vs required C1 |
| `totalExperience` | HARD | MET | 74 months vs required 24 |
| `careerLevel` | SOFT | MET | job PROFESSIONAL, candidate currently PROFESSIONAL (step +0) |

## Career-Fit (does the job meet the candidate's conditions and wishes?)

- **Hard conditions:** NOT_MET
- **Indicative score (soft criteria, known only):** 0.20
- **Known weight coverage:** 38%
- **Weights:** demo-career-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 3, PARTIALLY_MET 1, NOT_MET 6, UNKNOWN 9

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `archetypes/hard` | HARD | **NOT_MET** | job archetype supply-planner: none of the job's values is included |
| `archetypes/wish` | SOFT | **NOT_MET** | job archetype supply-planner: none of the job's values is included |
| `careerLevel/hard` | HARD | MET | job level PROFESSIONAL |
| `careerLevel/wish` | SOFT | **NOT_MET** | job level PROFESSIONAL |
| `industries/hard` | HARD | MET | job industry NACE-REV2 C21: no excluded value present |
| `industries/wish` | SOFT | MET | job industry NACE-REV2 C21: the job has an included value |
| `organization/wish` | SOFT | **UNKNOWN** | size not stated |
| `tasks/wish` | SOFT | PARTIALLY_MET | 1 of 2 desired tasks present |
| `compensation/hard` | HARD | **UNKNOWN** | job compensation not disclosed |
| `compensation/wish` | SOFT | **UNKNOWN** | job compensation not disclosed |
| `location/hard` | HARD | **NOT_MET** | Bremen: 89.1 km straight line (+/-10.0 km) vs max 40.0 km |
| `location/wish` | SOFT | **UNKNOWN** | Bremen: travel time limit 45 MIN needs routing or timetable data; not derived from distance |
| `workModel/hard` | HARD | **UNKNOWN** | arrangement HYBRID; travel share not stated |
| `workModel/wish` | SOFT | **UNKNOWN** | remote share not stated (HYBRID without extent) |
| `workingTime/hard` | HARD | **UNKNOWN** | schedule FULL_TIME; weekly hours not stated; shiftWork not stated |
| `contract/hard` | HARD | **NOT_MET** | TEMPORARY_AGENCY_WORK; 12 months vs at least 24 |
| `contract/wish` | SOFT | **NOT_MET** | TEMPORARY_AGENCY_WORK |
| `development/wish` | SOFT | **UNKNOWN** | job paths: not stated |
| `domainCriteria/org.example.supplychain.planning_tool_budget` | SOFT | **UNKNOWN** | Budget for planning tool licences available: no value stated on the other side |

_Generated deterministically by the AJMS reference implementation. Synthetic data._
