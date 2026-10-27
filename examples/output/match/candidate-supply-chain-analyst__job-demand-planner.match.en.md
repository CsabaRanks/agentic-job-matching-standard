# Match result

- **Candidate profile:** `urn:uuid:dcde3cca-c19a-55b6-8354-1d988ad1eb21` (2026-10-20T09:00:00+02:00)
- **Job profile:** `urn:uuid:9b2e4d71-0c3a-4f5e-8d6b-1a2b3c4d5e6f` (2026-10-18T14:30:00+02:00)

> Demonstration output. Weights are UNCALIBRATED and illustrative. UNKNOWN means information is missing or not comparable; it is not a negative result. Not suitable for automated decisions about people.

## Hiring-Fit (does the candidate meet the job's requirements?)

- **Hard conditions:** ALL_MET
- **Indicative score (soft criteria, known only):** 0.90
- **Known weight coverage:** 83%
- **Weights:** demo-hiring-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 11, PARTIALLY_MET 1, UNKNOWN 1

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `competencies/demand-forecasting` | HARD | MET | Demand forecasting: proficiency ADVANCED vs required ADVANCED; 5 years vs required 3 (SELF_REPORTED) |
| `competencies/sql` | SOFT | MET | SQL: proficiency ADVANCED vs required INTERMEDIATE (SELF_REPORTED) |
| `competencies/python` | SOFT | PARTIALLY_MET | Python: proficiency INTERMEDIATE vs required ADVANCED (DOCUMENT_EVIDENCED) |
| `competencies/stakeholder-facilitation` | SOFT | **UNKNOWN** | Facilitating cross-functional meetings: not stated in the candidate profile |
| `languages/de` | HARD | MET | de: NATIVE vs required C1 |
| `languages/en` | HARD | MET | en: C1 vs required B2 |
| `qualifications/q-degree` | HARD | MET | Degree in logistics, business or a related field: EQF 7 vs required 6; field of study not compared automatically |
| `domainExperience/supply-chain-planning` | HARD | MET | Supply chain planning: 72 months vs required 36 |
| `careerLevel` | SOFT | MET | job SENIOR, candidate currently PROFESSIONAL (step +1) |
| `workAuthorization` | HARD | MET | DE: authorized |
| `startTiming` | SOFT | MET | candidate from 2027-01-01, job latest 2027-03-01 |
| `domainCriteria/org.example.supplychain.erp_systems` | HARD | MET | ERP systems: all of ["SAP_IBP", "SAP_S4HANA"] present |
| `domainCriteria/org.example.logistics.drivers_license_b` | SOFT | MET | Driving licence class B: stated true, condition EQUALS true |

## Career-Fit (does the job meet the candidate's conditions and wishes?)

- **Hard conditions:** ALL_MET
- **Indicative score (soft criteria, known only):** 0.91
- **Known weight coverage:** 85%
- **Weights:** demo-career-fit-v0.1 (UNCALIBRATED)
- **Outcome:** MET 15, PARTIALLY_MET 1, NOT_MET 1, UNKNOWN 2

| Criterion | Type | Outcome | Explanation |
|---|---|---|---|
| `archetypes/hard` | HARD | MET | job archetype demand-planner: the job has an included value |
| `archetypes/wish` | SOFT | MET | job archetype demand-planner: the job has an included value |
| `careerLevel/hard` | HARD | MET | job level SENIOR |
| `careerLevel/wish` | SOFT | MET | job level SENIOR |
| `industries/hard` | HARD | MET | job industry NACE-REV2 C11: no excluded value present |
| `industries/wish` | SOFT | **NOT_MET** | job industry NACE-REV2 C11: none of the job's values is included |
| `organization/wish` | SOFT | MET | size EMPLOYEES_250_999 |
| `tasks/wish` | SOFT | MET | 2 of 2 desired tasks present |
| `compensation/hard` | HARD | MET | job 67,368-77,895 EUR/year vs at least 62,000; scaled from 38 h to 40 h per week |
| `compensation/wish` | SOFT | PARTIALLY_MET | job 67,368-77,895 EUR/year vs at least 70,000; scaled from 38 h to 40 h per week |
| `location/hard` | HARD | MET | Hamburg: 9.1 km straight line (+/-5.5 km) vs max 40.0 km |
| `location/wish` | SOFT | **UNKNOWN** | Hamburg: travel time limit 45 MIN needs routing or timetable data; not derived from distance |
| `workModel/hard` | HARD | MET | arrangement HYBRID; travel share up to 5 % vs at most 20 % |
| `workModel/wish` | SOFT | MET | remote share 40-60 % vs at least 40 % |
| `workingTime/hard` | HARD | MET | schedule FULL_TIME; 38-38 h/week vs acceptable 35-40; shiftWork no |
| `contract/hard` | HARD | MET | PERMANENT_EMPLOYMENT |
| `contract/wish` | SOFT | MET | PERMANENT_EMPLOYMENT |
| `development/wish` | SOFT | MET | job paths: EXPERT, PROJECT |
| `domainCriteria/org.example.supplychain.planning_tool_budget` | SOFT | **UNKNOWN** | Budget for planning tool licences available: no value stated on the other side |

_Generated deterministically by the AJMS reference implementation. Synthetic data._
