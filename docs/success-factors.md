# Shared success factors and what they mean to both sides

A job change succeeds when **both** perspectives fit: the candidate meets the job's requirements (Hiring-Fit) and the job meets the candidate's conditions and wishes (Career-Fit). The factors below are the same criteria seen from both sides. They come from the ten job evaluation factors of the MyCareerAgent project (prof-v0.3, F1–F10; see [prior-work-and-deviations.md](prior-work-and-deviations.md)). Factors that were implicit there are made explicit here.

AJMS provides the **data** for each factor. It does not prescribe weights, a scale or a ranking. MyCareerAgent used a 0–4 scale with UNKNOWN as a separate state ("never 0, never an average") and no weights. AJMS keeps that principle: unknown stays visible.

| # | Factor | Meaning for the candidate | Meaning for the employer / agency | AJMS data (candidate ↔ job) | Origin |
|---|---|---|---|---|---|
| 1 | **Compensation** | minimum acceptable (hard) and target (wish), comparable only per component, period and hours basis | budget range; transparent ranges prevent late drop-outs in the process | `jobPreferences.compensation` ↔ `offer.compensation[]` | F5 Vergütungsfit |
| 2 | **Industry** | preferred and excluded industries | relevance of industry experience, culture | `jobPreferences.industries` ↔ `hiringOrganization.industries`; `capabilities.domainExperience` | F1 Branchenfit |
| 3 | **Company** | employer type and size, own or agency employment | employer attractiveness; agencies must disclose that they are intermediaries | `jobPreferences.organization` ↔ `hiringOrganization`, `intermediary` | F2 Unternehmensfit |
| 4 | **Job archetype** | the kind of job the candidate wants to do | the kind of job to be filled; occupation codes make it comparable | `capabilities.archetypes`, `jobPreferences.archetypes` ↔ `archetype` | F3 Job-Archetypfit |
| 5 | **Career direction and tasks** | do the tasks lead where the candidate wants to go? | do the tasks match what the candidate has done and wants to do (motivation, retention)? | `jobPreferences.tasks`, `experienceHistory[].tasks` ↔ `tasks[]` | F4 Careerfit (career direction) |
| 6 | **Career level** | the next step, not a step back and not an overreach | seniority and leadership scope of the role | `capabilities.currentCareerLevel`, `jobPreferences.careerLevel` ↔ `careerLevel`, `leadership` | F6 Karrierelevelfit |
| 7 | **Commute** | load depends on distance or travel time **and** on how many days per week are on site | catchment area of the location; on-site needs | `jobPreferences.location.commute` ↔ `offer.locations[]`, `offer.workModel.onsiteDays` | F7 Pendeldistanzfit (weekly commute = 2 × distance × on-site days) |
| 8 | **Requirements fit** | can the candidate do the job, with evidence? | the core of Hiring-Fit: competencies, experience, qualifications, languages, authorization | `capabilities.*`, `evidence` ↔ `requirements.*` | F8 Hiringfit |
| 9 | **Remote share** | share of working time away from the site, per reference period | collaboration model; "hybrid" without extent is not information | `jobPreferences.workModel` ↔ `offer.workModel` | F9 (remote / home office share) |
| 10 | **Working time** | weekly hours, schedule, shift work, on-call duty | staffing need and working-time model | `jobPreferences.workingTime` ↔ `offer.workingTime` | implicit in the hard filters (full-time/contract) |
| 11 | **Contract security** | permanent vs. fixed-term, agency work, minimum term | flexibility needs; conversion options | `jobPreferences.contract` ↔ `offer.contract` | implicit in the hard filters |
| 12 | **Development** | expert, leadership or project path; training | retention and growth of the role | `jobPreferences.development` ↔ `offer.development` | part of F4 |
| 13 | **Start timing** | earliest start, notice period | when the job must be filled | `availability` ↔ `requirements.startTiming` | new in AJMS |
| 14 | **Domain-specific factors** | e.g. night shifts per month, licences | e.g. professional registration, specialties | `domainCriteria` on both sides | F10 "Sonstiges 2" (unused there), generalised |

## Principles carried over

1. **Two separate judgements.** Hiring-Fit and Career-Fit are reported separately. A strong result in one does not compensate for a failed hard condition in the other.
2. **Unknown is a state, not a score.** An unknown factor is shown as unknown, with the share of weight it would have carried.
3. **Hard conditions are not weighted.** They pass, fail or remain unresolved.
4. **Evidence over assertion.** Requirements fit distinguishes self-reported from evidenced statements, so the recipient can decide how much to trust them.
5. **No hidden calibration.** Any weights are published with the result and marked as calibrated or not.
