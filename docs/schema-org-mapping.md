# schema.org mapping

Checked against schema.org release **V30.1 (2026-09-16)**, pages retrieved 2026-10-27 (see [sources](sources.md)).

AJMS does **not** claim support by schema.org, Google or any ATS vendor. The mapping states which schema.org terms AJMS uses and how. It does not say that any consumer interprets AJMS documents.

## Categories

| Category | Meaning |
|---|---|
| **Adopted** | The AJMS key maps directly to the schema.org IRI in the JSON-LD context. The AJMS value has the type schema.org expects. |
| **Transformed** | The information exists in schema.org, but in a different shape. `ajms export-schemaorg` converts it when a public JobProfile is exported as `JobPosting`. Inside AJMS documents the key uses the `ajms:` namespace. |
| **Extended** | No suitable schema.org term exists. The key is defined in the `ajms:` namespace. |
| **Not mappable** | The information cannot be expressed in schema.org without losing its meaning. It is left out of the export. |

## Adopted (same IRI in the AJMS context)

| AJMS key | schema.org term | Note |
|---|---|---|
| `title` | `schema:title` | JobPosting title; a language-tagged literal via `text`/`language` → `@value`/`@language` |
| `label`, `name`, `displayName` | `schema:name` | |
| `summary`, `description` | `schema:description` | |
| `benefits` | `schema:jobBenefits` | Text |
| `hiringOrganization` | `schema:hiringOrganization` | |
| `industries` | `schema:industry` | expected `DefinedTerm` or Text; AJMS uses a code node (scheme + code) |
| `datePosted`, `validThrough` | `schema:datePosted`, `schema:validThrough` | typed `xsd:date` |
| `updatedAt` | `schema:dateModified` | typed `xsd:dateTime` |
| `url`, `postingUrl` | `schema:url` | IRI |
| `countryCode`, `region`, `locality`, `postalCode` | `schema:addressCountry`, `schema:addressRegion`, `schema:addressLocality`, `schema:postalCode` | |
| `geo`, `latitude`, `longitude` | `schema:geo`, `schema:latitude`, `schema:longitude` | `precisionKm` is extended |
| `currency`, `min`, `max`, `value`, `unitCode` | `schema:currency`, `schema:minValue`, `schema:maxValue`, `schema:value`, `schema:unitCode` | `unitCode` uses UN/CEFACT Common Code, as schema.org specifies |
| `residence` | `schema:homeLocation` | private views only |
| `defaultLanguage` | `schema:inLanguage` | |

## Transformed (`ajms export-schemaorg`, JobProfile → JobPosting)

| AJMS | schema.org JobPosting | Transformation |
|---|---|---|
| `offer.compensation[]` with `component: BASE_SALARY`, `GROSS`, `STATED` | `baseSalary` (`MonetaryAmount` + `QuantitativeValue` with `unitText` = period) | first matching entry; hours basis and payments per year have no schema.org place and are dropped |
| same with `informationKind: ESTIMATED` | `estimatedSalary` | |
| `VARIABLE_TARGET` entries | `incentiveCompensation` (Text) | |
| `tasks[]` | `responsibilities` (Text) and `description` (HTML) | `description` is required by Google's documentation; AJMS assembles it from tasks |
| `requirements.competencies[]` | `skills` (`DefinedTerm`) | proficiency and REQUIRED/PREFERRED are lost |
| `requirements.qualifications[]` (DEGREE) | `educationRequirements` (`EducationalOccupationalCredential`, `educationalLevel` "EQF level n") | |
| `experienceInPlaceOfEducation` | `experienceInPlaceOfEducation` | |
| `requirements.domainExperience[]`, `.totalExperienceMonths` | `experienceRequirements` (`OccupationalExperienceRequirements.monthsOfExperience`) | maximum of the stated minimums; the domain is lost |
| `requirements.workAuthorization` | `eligibilityToWorkRequirement` (Text) | |
| `requirements.startTiming` | `jobStartDate`, `jobImmediateStart` | |
| `offer.locations[]` | `jobLocation` (`Place` + `PostalAddress` + `GeoCoordinates`) | |
| `offer.workModel.arrangement = REMOTE` | `jobLocationType: TELECOMMUTE`, `applicantLocationRequirements` (`Country`) | only fully remote jobs; HYBRID has no schema.org value |
| `offer.workingTime.schedule`, `offer.contract.contractType` | `employmentType` (`FULL_TIME`, `PART_TIME`, `TEMPORARY`, `CONTRACTOR`, `INTERN`, `OTHER`) | AJMS separates schedule and contract; schema.org combines them in one list |
| `offer.workingTime.weeklyHours` | `workHours` (Text, e.g. "38 hours per week") | |
| `archetype.occupationCodes` (ISCO-08) | `occupationalCategory` (`CategoryCode`) | |
| `hiringOrganization.industries` | `industry` (`DefinedTerm`) | |
| `profileId` | `identifier` (`PropertyValue`) | |

## Extended (`ajms:` namespace)

`CandidateProfile`, `JobProfile`, `ProfileReference`, `profileView`, `schemaVersion`, `capabilities`, `jobPreferences`, `hardCondition`, `wish`, `include`, `exclude`, `requirements`, `offer`, `requirementLevel`, `provenance`, `basis`, `evidence`, `evidenceRefs`, `verificationStatus`, `competencies`, `proficiency`, `cefrLevel`, `eqfLevel`, `domainExperience`, `months`, `archetype`, `occupationCodes`, `careerLevel`, `leadership`, `tasks`, `shareOfTimePercent`, `workModel`, `arrangement`, `remoteShare`, `onsiteDays`, `travelShare`, `referencePeriod`, `percent`, `workingTime`, `weeklyHours`, `schedule`, `shiftWork`, `contract`, `contractType`, `fixedTermMonths`, `development`, `paths`, `commute`, `maxOneWayDistance`, `maxOneWayDuration`, `measurement`, `precisionKm`, `compensation`, `component`, `grossOrNet`, `hoursPerWeekBasis`, `paymentsPerYear`, `informationKind`, `domainCriteria`, `criterionId`, `dataType`, `comparator`, `availability`, `noticePeriod`, `profileUrl`, `accessMethod`, `contentDigest` and the further terms listed in [`ajms.context.jsonld`](../context/v0.1/ajms.context.jsonld).

## Not mappable

| Information | Why |
|---|---|
| **Candidate wishes and hard conditions** (`jobPreferences`) | schema.org has no type for a person's job search criteria. A wish is not an advertised job, so `JobPosting` would be wrong (Google's documentation also disallows `JobPosting` markup on pages that do not list a job). `Person.seeks` expects `Demand`, defined as an announcement to seek goods or services; using it for job-search criteria would stretch that definition. AJMS therefore keeps candidate preferences in its own namespace and offers no candidate export. |
| Hard condition vs. wish, REQUIRED vs. PREFERRED | no schema.org concept |
| Statement provenance and evidence verification state | no schema.org concept for "self-reported vs. evidenced" |
| Remote share with reference period, on-site days, travel share | `jobLocationType` knows only `TELECOMMUTE` (fully remote) |
| Commute limits (distance vs. time, measurement method) | no schema.org concept |
| Compensation hours basis and payments per year | `MonetaryAmount` has no place for them |
| Domain criteria with data type, unit and comparator | `JobPosting` has no generic property bag (`additionalProperty` is not defined for JobPosting) |
| UNKNOWN / NOT_APPLICABLE / NOT_DISCLOSED | schema.org has no "stated absence" |

## Relation to other formats (not mappings)

| Format | Relation |
|---|---|
| **JSON Resume** v1.7.0 (Draft-07 JSON Schema, MIT) | Covers CV content (`basics`, `work`, `education`, `skills`, `languages`, `certificates`). It has no job-search preferences, hard conditions, provenance or job side. An importer from JSON Resume into `capabilities`/`experienceHistory` is on the roadmap. |
| **HR Open Standards** (HR-JSON; Recruiting workgroup with `Candidate` and `PositionOpening`) | The specifications are offered for download after accepting the HR Open IP agreement. They were **not downloaded or inspected in detail** for this draft, so no field-level mapping is claimed. A comparison is an open task. |
| **Bundesagentur für Arbeit** profile | Uses its own occupation taxonomy (KldB 2010); AJMS supports `KLDB-2010` as a classification scheme. |
