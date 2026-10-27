# Field catalog — Agentic-Job-Matching-Standard (AJMS), Community Draft v0.1

This catalog explains the **shared criteria**: where each one sits in a CandidateProfile and a JobProfile, which units and reference values it uses, and how missing information is handled. Every property with its type is listed in the generated [property index](property-index.md).

## 1. Statement classes

AJMS keeps statements that serve different purposes structurally apart:

| Separation | Candidate side | Job side |
|---|---|---|
| **Facts and self-reports** vs. **evidenced statements** | `provenance.basis`: `SELF_REPORTED`, `DOCUMENT_EVIDENCED`, `THIRD_PARTY_CONFIRMED`, `ESTIMATED`, `DERIVED` | `provenance.basis`: `ORGANIZATION_STATED` (employer-published) or `DERIVED` (extracted by a third party or agent) |
| **Evidenced statements** and **their evidence** | `evidence[]` (document references, `verificationStatus`), linked via `provenance.evidenceRefs` | — |
| **Requirements** vs. **offers** | — | `requirements` (input to Hiring-Fit) vs. `offer` (input to Career-Fit) |
| **Capabilities** vs. **wishes** | `capabilities` (what the candidate brings) vs. `jobPreferences` (what the candidate looks for) | — |
| **Wishes** vs. **hard conditions** | Each preference block has `hardCondition` and/or `wish` | Each requirement has `requirementLevel`: `REQUIRED` (hard) or `PREFERRED` |
| **Profile data** vs. **evaluation weights** | Weights never appear in a profile; they live in a separate `MatchPolicy` | same |

AJMS **records** evidence references. It does not verify them. `verificationStatus: VERIFIED_BY_THIRD_PARTY` only states that someone (named in `verifiedBy`) claims to have checked the evidence.

## 2. Unknown, not applicable, not met

| State | How it is expressed | Meaning |
|---|---|---|
| **UNKNOWN** | the field or block is **absent** | Nobody has stated a value. Never treated as 0, as "no", or as a failed requirement. |
| **NOT_DISCLOSED** | `{"state": "NOT_DISCLOSED"}` in place of a criterion block | A value exists but is deliberately withheld (e.g. "salary on request"). Treated like UNKNOWN in matching, but documented as a choice. |
| **NOT_APPLICABLE** | `{"state": "NOT_APPLICABLE"}` | The criterion does not apply (e.g. remote share for bedside nursing). Excluded from matching. |
| **NOT_MET** | only in a `MatchResult` | A stated value falls short of a stated condition. Requires values on **both** sides. |

`StatedAbsence` is allowed at the level of criterion blocks (`jobPreferences.*`, `offer.*`). A candidate's capability that is not listed is UNKNOWN, not absent. A profile is a selection, not an exhaustive inventory.

## 3. Shared criteria

| # | Criterion | CandidateProfile | JobProfile | Units and reference values |
|---|---|---|---|---|
| 1 | **Compensation** | `jobPreferences.compensation.{hardCondition,wish}.atLeast` | `offer.compensation[]` | One `CompensationAmount` = one `component` × one `currency` (ISO 4217) × one `period` (`HOUR`…`YEAR`) × `grossOrNet`; optional `hoursPerWeekBasis` (hours basis) and `paymentsPerYear`. Point value **or** interval; estimates (`informationKind: ESTIMATED`) must be intervals. Variable pay is never folded into base salary. |
| 2 | **Company and industry** | `jobPreferences.organization` (types, size classes), `jobPreferences.industries` | `hiringOrganization` (`name`, `organizationType`, `industries[]`, `sizeClass`), `intermediary` | Industries as `ClassificationCode` (`NACE-REV2`, `WZ-2008`, `ISIC-REV4`, `NAICS`, …). A code covers its sub-codes (`C10` covers `C10.1`). Size classes by headcount. |
| 3 | **Job archetype** | `capabilities.archetypes[]`, `jobPreferences.archetypes` | `archetype` | `archetypeId` (stable identifier) plus optional `occupationCodes` (`ISCO-08`, `ESCO`, `KLDB-2010`, `ONET-SOC`). |
| 4 | **Career level** | `capabilities.currentCareerLevel`, `jobPreferences.careerLevel` | `careerLevel`, `leadership` | Ordered scale `ENTRY < JUNIOR < PROFESSIONAL < SENIOR < LEAD < HEAD < DIRECTOR < EXECUTIVE`; leadership separately as `NONE`, `FUNCTIONAL`, `DISCIPLINARY` and `directReports` range. |
| 5 | **Task content** | `experienceHistory[].tasks[]`, `jobPreferences.tasks` (include / exclude) | `tasks[]` | `Task` with `taskId`, `label`, optional `category` code and `shareOfTimePercent` (0–100 % of working time). |
| 6 | **Competencies, experience, qualifications** | `capabilities.competencies[]`, `.languages[]`, `.qualifications[]`, `.domainExperience[]`, `.totalExperienceMonths`, `.leadershipExperience` | `requirements.competencies[]`, `.languages[]`, `.qualifications[]`, `.domainExperience[]`, `.totalExperienceMonths`, `.leadershipExperience` | Proficiency `BASIC < INTERMEDIATE < ADVANCED < EXPERT`; languages BCP 47 + CEFR (`A1`…`C2`, `NATIVE`); qualifications with EQF level 1–8; experience in **months**. |
| 7 | **Work location and commute** | `jobPreferences.location.{hardCondition,wish}` → `commute` (`origin`, `maxOneWayDistance`, `maxOneWayDuration`, `transportModes`, `relocationPossible`), `places[]` | `offer.locations[]` (`Place` with optional `geo`) | **Commute distance and commute time are different criteria.** Distance: `value` + `unitCode` (`KMT` km, `SMI` mile) + `measurement` (`STRAIGHT_LINE` or `ROUTE`). Time: `value` + `unitCode` (`MIN`, `HUR`), one way. Coordinates carry `precisionKm` (deliberate coarseness). |
| 8 | **Work model and remote share** | `jobPreferences.workModel` → `arrangements`, `remoteShareAtLeast`, `travelShareAtMost` | `offer.workModel` → `arrangement`, `remoteShare`, `onsiteDays`, `travelShare`, `remoteCountries` | Shares are **percent of contractual working time with a `referencePeriod`** (`WEEK`, `MONTH`, `YEAR`); on-site days are a count per reference period. `HYBRID` without a share leaves the share UNKNOWN. |
| 9 | **Working time and weekly hours** | `jobPreferences.workingTime` → `schedules`, `weeklyHours`, `shiftWorkAcceptable`, `onCallDutyAcceptable` | `offer.workingTime` → `schedule`, `weeklyHours`, `shiftWork`, `onCallDuty`, `flexibleHours` | `weeklyHours` in **hours per week** (range). `schedule` is `FULL_TIME` / `PART_TIME`, kept separate from the contract type. |
| 10 | **Contract type and fixed term** | `jobPreferences.contract` → `contractTypes`, `fixedTermMonthsAtLeast` | `offer.contract` → `contractType`, `fixedTermMonths`, `permanentConversionPossible`, `probationMonths` | Contract types incl. `TEMPORARY_AGENCY_WORK`; durations in **months**. |
| 11 | **Development perspectives** | `jobPreferences.development` → `paths` | `offer.development` → `paths`, `trainingDaysPerYear`, `description` | Paths: `LEADERSHIP`, `EXPERT`, `PROJECT`, `INTERNATIONAL`, `CROSS_FUNCTIONAL`, `FURTHER_EDUCATION`; training in **days per year**. |
| 12 | **Availability / start date** | `availability` (`immediate`, `earliestStartDate`, `noticePeriod`) | `requirements.startTiming` (`earliestStartDate`, `latestStartDate`, `immediate`) | ISO 8601 dates; notice period `value` + `unitCode` (`WEE` week, `MON` month). A notice period alone does not give a start date (no implicit "today"). |
| 13 | **Optional domain-specific criteria** | `capabilities.domainCriteria[]` (facts), `jobPreferences.domainCriteria.{hardCondition,wish}[]` (conditions) | `requirements.domainCriteria[]` (`criterion` + `requirementLevel`), `offer.domainCriteria[]` (facts) | See section 4. |

Additional fields without a matching counterpart: `capabilities.workAuthorizations[]` ↔ `requirements.workAuthorization` (Hiring-Fit), `offer.benefits[]` (informational), `searchStatus`, `headline`, `summary`.

## 4. Domain-specific extensions

A `DomainCriterion` has:

| Property | Rule |
|---|---|
| `criterionId` | Stable identifier in reverse-DNS form, owned by whoever defines it: `org.example.healthcare.night_shifts_per_month`. Pattern `^[a-z0-9]+(\.[a-z0-9-]+)+\.[a-z][a-z0-9_]*$`. Never re-use an identifier with a different meaning. |
| `label` | Human-readable label with language. |
| `definitionUrl` | Optional link to the definition. |
| `dataType` | `BOOLEAN`, `INTEGER`, `NUMBER`, `TEXT`, `CODE`, `CODE_LIST`; the schema enforces the matching JSON type of `value`. |
| `unitCode` | UN/CEFACT Common Code for quantities (e.g. `HUR` hours). Values with different units are not compared. |
| `comparator` | Required on condition/requirement side: `EQUALS`, `AT_LEAST`, `AT_MOST`, `ANY_OF`, `ALL_OF` (allowed set depends on `dataType`). |

**Any number of domain criteria may be used, including none.** The examples show two (supply chain) and four (intensive care nursing). The concept drafts' rule of "minimum 2, maximum 4" was not adopted: a minimum forces invented criteria.

| Example | Side | dataType | Comparator |
|---|---|---|---|
| `org.example.supplychain.erp_systems` | job requirement / candidate fact | `CODE_LIST` | `ALL_OF` |
| `org.example.logistics.drivers_license_b` | job requirement (preferred) / candidate fact | `BOOLEAN` | `EQUALS` |
| `org.example.healthcare.professional_registration` | job requirement / candidate fact | `BOOLEAN` | `EQUALS` |
| `org.example.healthcare.specialties` | job requirement / candidate fact | `CODE_LIST` | `ANY_OF` |
| `org.example.healthcare.ventilation_hours` | job requirement / candidate fact | `NUMBER`, `HUR` | `AT_LEAST` |
| `org.example.healthcare.night_shifts_per_month` | candidate hard condition / job fact | `INTEGER` | `AT_MOST` |

## 5. Imported profiles

| Property | Meaning |
|---|---|
| `source.sourceUrl`, `sourceFileName`, `sourceRecordId` | where the data came from (`urn:sha256:<digest>` for files without URL) |
| `source.retrievedAt` | when the data was retrieved or provided |
| `source.sourceFormat`, `source.inputKind` | adapter format; `STRUCTURED` (fields mapped directly) or `TEXT` (values extracted) |
| `source.textDigest` | SHA-256 of the original data |
| `source.extractionQuality` | `PASSED` / `REVIEW`, recognized share, checks |
| `source.unmapped[]` | source fields not carried, with reason; never their values |
| `fieldStatements[]` | per field: `EXPLICIT`, `NORMALIZED`, `DERIVED`, `sourceExcerpt`, `method`, `lossy`, `note` |

Details: [import-adapters.md](import-adapters.md).

## 6. Profile envelope

| Property | CandidateProfile | JobProfile | Meaning |
|---|---|---|---|
| `@context` | required | required | AJMS JSON-LD context URL (or array starting with it) |
| `@type` | `CandidateProfile` | `JobProfile` | document type |
| `profileId` | required | required | `urn:uuid:…` or `https://…`; must not encode personal data |
| `schemaVersion` | `0.1.0` | `0.1.0` | specification version |
| `updatedAt` | required | required | RFC 3339 date-time with offset |
| `profileView` | `FULL_PRIVATE`, `SHARED_VIEW`, `PUBLIC_MINIMAL` | `PUBLIC`, `SHARED_VIEW`, `FULL_PRIVATE` | which representation this document is |
