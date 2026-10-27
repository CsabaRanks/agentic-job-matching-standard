# Conversion report: linkedin-data-export-csv → CandidateProfile

Adapter `ajms-adapters`, rules `linkedin-csv-1`. Deterministic, no network, no language model. Synthetic input.

## 1. Source data

- **Format:** `linkedin-data-export-csv` (structured fields, mapped directly)
- **Source reference:** urn:sha256:86b2b5dd879cd18c015ce1efd06bfd1d9cca110beb4f08370c86bcaf8d6cb1cb (file `export`)
- **Retrieved / provided:** 2026-10-27T11:05:00+01:00
- **SHA-256:** `86b2b5dd879cd18c015ce1efd06bfd1d9cca110beb4f08370c86bcaf8d6cb1cb`

`Certifications.csv`:

```text
Name,Url,Authority,Started On,Finished On,License Number
Python for Data Analysis,https://example.org/certificates/abc123,Example Academy,May 2023,May 2028,ABC-123
```

`Connections.csv`:

```text
First Name,Last Name,URL,Email Address,Company,Position,Connected On
```

`Education.csv`:

```text
School Name,Start Date,End Date,Notes,Degree Name,Activities
Example University,2017,2019,,Master of Science - MS Logistics,Student consulting club
Example University,2014,2017,,Bachelor of Science - BS Business Administration,
```

`Languages.csv`:

```text
Name,Proficiency
German,Native or bilingual proficiency
English,Full professional proficiency
Spanish,
```

`Positions.csv`:

```text
Company Name,Title,Description,Location,Started On,Finished On
Example Foods GmbH,Supply Chain Analyst,Build and maintain statistical demand forecasts; monthly S&OP reporting,"Hamburg, Germany",Oct 2020,
Example Logistics AG,Logistics Trainee,Rotation through planning and warehouse operations,"Bremen, Germany",Sep 2019,Sep 2020
```

`Profile.csv`:

```text
First Name,Last Name,Maiden Name,Address,Birth Date,Headline,Summary,Industry,Zip Code,Geo Location,Twitter Handles,Websites,Instant Messengers
Jordan,Example,,Musterstraße 1,"Jan 1, 1990",Supply Chain Analyst | Demand Forecasting,"Synthetic example profile. Forecasting and S&OP reporting in consumer goods.",Food and Beverage Manufacturing,21073,"Hamburg, Germany",,[https://example.org/jordan],
```

`Skills.csv`:

```text
Name
Demand Forecasting
SQL
Python
Sales and Operations Planning (S&OP)
```

## 2. Structural checks

- **Status:** PASSED
- Certifications.csv: header has all expected columns, 1 rows
- Connections.csv: not imported (DATA_MINIMISATION)
- Education.csv: header has all expected columns, 2 rows
- Languages.csv: header has all expected columns, 3 rows
- Positions.csv: header has all expected columns, 2 rows
- Profile.csv: header has all expected columns, 1 rows
- Skills.csv: header has all expected columns, 4 rows

## 3. Field mapping

| Target field (JSON Pointer) | Value | Statement | Source excerpt | Method | Note |
|---|---|---|---|---|---|
| `/capabilities/competencies/0/competencyId` | demand-forecasting | DERIVED | Demand Forecasting | slug-of-label |  |
| `/capabilities/competencies/0/label` | Demand Forecasting | EXPLICIT | Demand Forecasting | – |  |
| `/capabilities/competencies/1/competencyId` | sql | DERIVED | SQL | slug-of-label |  |
| `/capabilities/competencies/1/label` | SQL | EXPLICIT | SQL | – |  |
| `/capabilities/competencies/2/competencyId` | python | DERIVED | Python | slug-of-label |  |
| `/capabilities/competencies/2/label` | Python | EXPLICIT | Python | – |  |
| `/capabilities/competencies/3/competencyId` | sales-and-operations-planning-s-op | DERIVED | Sales and Operations Planning (S&OP) | slug-of-label |  |
| `/capabilities/competencies/3/label` | Sales and Operations Planning (S&OP) | EXPLICIT | Sales and Operations Planning (S&OP) | – |  |
| `/capabilities/languages/0/cefrLevel` | NATIVE | DERIVED | Native or bilingual proficiency | linkedin-proficiency-to-cefr |  |
| `/capabilities/languages/0/languageCode` | de | NORMALIZED | German | language-name-en-to-bcp47 |  |
| `/capabilities/languages/1/cefrLevel` | C1 | DERIVED · lossy | Full professional proficiency | linkedin-proficiency-to-cefr | no official equivalence between LinkedIn 'Full professional proficiency' and CEFR C1 |
| `/capabilities/languages/1/languageCode` | en | NORMALIZED | English | language-name-en-to-bcp47 |  |
| `/capabilities/qualifications/0/eqfLevel` | 7 | DERIVED | Master of Science - MS Logistics | degree-keyword-to-eqf |  |
| `/capabilities/qualifications/0/issuerName` | Example University | EXPLICIT | Example University | – |  |
| `/capabilities/qualifications/0/label` | Master of Science - MS Logistics | EXPLICIT | Master of Science - MS Logistics | – |  |
| `/capabilities/qualifications/0/qualificationType` | DEGREE | DERIVED | – | education-row-is-degree |  |
| `/capabilities/qualifications/1/eqfLevel` | 6 | DERIVED | Bachelor of Science - BS Business Administration | degree-keyword-to-eqf |  |
| `/capabilities/qualifications/1/issuerName` | Example University | EXPLICIT | Example University | – |  |
| `/capabilities/qualifications/1/label` | Bachelor of Science - BS Business Administration | EXPLICIT | Bachelor of Science - BS Business Administration | – |  |
| `/capabilities/qualifications/1/qualificationType` | DEGREE | DERIVED | – | education-row-is-degree |  |
| `/capabilities/qualifications/2/completedOn` | 2023-05 | NORMALIZED | May 2023 | linkedin-month-year | 'Started On' read as issue month |
| `/capabilities/qualifications/2/issuerName` | Example Academy | EXPLICIT | Example Academy | – |  |
| `/capabilities/qualifications/2/label` | Python for Data Analysis | EXPLICIT | Python for Data Analysis | – |  |
| `/capabilities/qualifications/2/provenance` | basis=DOCUMENT_EVIDENCED | DERIVED | – | certificate-url-is-evidence-reference |  |
| `/capabilities/qualifications/2/qualificationType` | CERTIFICATION | DERIVED | – | certification-row |  |
| `/capabilities/qualifications/2/validUntil` | 2028-05-31 | DERIVED · lossy | May 2028 | month-to-last-day | month-precision expiry mapped to the last day of that month |
| `/evidence/0/documentUrl` | https://example.org/certificates/abc123 | EXPLICIT | https://example.org/certificates/abc123 | – |  |
| `/evidence/0/verificationStatus` | UNVERIFIED | DERIVED | – | nothing-verified-on-import |  |
| `/experienceHistory/0/ongoing` | True | DERIVED | – | empty-finished-on-means-current |  |
| `/experienceHistory/0/organization/name` | Example Foods GmbH | EXPLICIT | Example Foods GmbH | – |  |
| `/experienceHistory/0/roleTitle` | Supply Chain Analyst | EXPLICIT | Supply Chain Analyst | – |  |
| `/experienceHistory/0/startMonth` | 2020-10 | NORMALIZED | Oct 2020 | linkedin-month-year |  |
| `/experienceHistory/0/tasks/0/label` | Build and maintain statistical demand forecasts; monthly S&OP reporting | EXPLICIT · lossy | Build and maintain statistical demand forecasts; monthly S&OP reporting | – | the whole description becomes one task |
| `/experienceHistory/1/endMonth` | 2020-09 | NORMALIZED | Sep 2020 | linkedin-month-year |  |
| `/experienceHistory/1/organization/name` | Example Logistics AG | EXPLICIT | Example Logistics AG | – |  |
| `/experienceHistory/1/roleTitle` | Logistics Trainee | EXPLICIT | Logistics Trainee | – |  |
| `/experienceHistory/1/startMonth` | 2019-09 | NORMALIZED | Sep 2019 | linkedin-month-year |  |
| `/experienceHistory/1/tasks/0/label` | Rotation through planning and warehouse operations | EXPLICIT · lossy | Rotation through planning and warehouse operations | – | the whole description becomes one task |
| `/headline` | Supply Chain Analyst \| Demand Forecasting | EXPLICIT | Supply Chain Analyst \| Demand Forecasting | – |  |
| `/identity/displayName` | Jordan Example | NORMALIZED | Jordan | join-first-and-last-name | First Name and Last Name joined |
| `/identity/residence/countryCode` | DE | NORMALIZED | Germany | country-name-to-iso3166 |  |
| `/identity/residence/geo` | latitude=53.55, longitude=9.99, precisionKm=10 | DERIVED | Hamburg | gazetteer-city-centroid | city centroid, precision 10 km |
| `/identity/residence/locality` | Hamburg | EXPLICIT | Hamburg | – |  |
| `/summary` | Synthetic example profile. Forecasting and S&OP reporting in consumer goods. | EXPLICIT | Synthetic example profile. Forecasting and S&OP reporting in consumer goods. | – |  |

Explicit, normalized, derived: EXPLICIT 20, NORMALIZED 8, DERIVED 16; with loss of meaning: 4.

## 4. Conversion result

Profile: [`synthetic-supply-chain-analyst.candidateprofile.json`](synthetic-supply-chain-analyst.candidateprofile.json) (`CandidateProfile`, `profileView` FULL_PRIVATE).

**Not carried into the profile** (field names only, values are not stored):

- `Connections.csv` — DATA_MINIMISATION: personal data of third parties; never imported
- `Profile.csv:Address` — DATA_MINIMISATION: a full address is not needed for matching
- `Profile.csv:Birth Date` — PROTECTED_CHARACTERISTIC_NOT_MAPPED: age is not represented in AJMS; value not stored
- `Profile.csv:Industry` — NO_AJMS_FIELD: current industry without duration; experience by industry needs months
- `Profile.csv:Zip Code` — DATA_MINIMISATION: postal code of the residence is not needed for matching
- `Profile.csv:Websites` — NO_AJMS_FIELD
- `Positions.csv row 1:Location` — NO_AJMS_FIELD: experience entries have no location in AJMS v0.1
- `Positions.csv row 2:Location` — NO_AJMS_FIELD: experience entries have no location in AJMS v0.1
- `Education.csv row 1:End Date` — MISSING_REQUIRED_DETAIL: year without month; completion month stays unknown
- `Education.csv row 1:Activities` — NO_AJMS_FIELD
- `Education.csv row 2:End Date` — MISSING_REQUIRED_DETAIL: year without month; completion month stays unknown
- `Certifications.csv row 1:License Number` — DATA_MINIMISATION
- `Languages.csv row 3:Proficiency` — MISSING_REQUIRED_DETAIL: no proficiency stated; AJMS requires a level, so the language is not mapped

**Unknown** (absent from the source, therefore absent from the profile):

- current career level (`/capabilities/currentCareerLevel`)
- practised job archetypes (`/capabilities/archetypes`)
- experience by domain (months) (`/capabilities/domainExperience`)
- total experience (months) (`/capabilities/totalExperienceMonths`)
- work authorization (`/capabilities/workAuthorizations`)
- wished job archetypes (`/jobPreferences/archetypes`)
- wished career level (`/jobPreferences/careerLevel`)
- industry preferences (`/jobPreferences/industries`)
- compensation expectation (`/jobPreferences/compensation`)
- location / commute (`/jobPreferences/location`)
- work model / remote share (`/jobPreferences/workModel`)
- working time (`/jobPreferences/workingTime`)
- contract preferences (`/jobPreferences/contract`)
- development wishes (`/jobPreferences/development`)
- availability / start date (`/availability`)
- search status (`/searchStatus`)

## 5. AJMS validation

- **JSON Schema + semantic rules:** valid
- **JSON-LD:** ok, 359 RDF statements

## 6. Human-readable output (en)

### Candidate profile: Supply Chain Analyst | Demand Forecasting

- **Profile ID:** `urn:uuid:1f969c0f-9978-5a35-9ad7-cf4a80bb7e3f`
- **View:** FULL_PRIVATE
- **Updated:** 2026-10-27T11:05:00+01:00
- **Schema version:** 0.1.0
- **Search status:** unknown
- **Source:** linkedin-data-export-csv, urn:sha256:86b2b5dd879cd18c015ce1efd06bfd1d9cca110beb4f08370c86bcaf8d6cb1cb, retrieved 2026-10-27T11:05:00+01:00

#### Identity

- **Name:** Jordan Example

#### Summary

Synthetic example profile. Forecasting and S&OP reporting in consumer goods.

#### Capabilities

- **Current career level:** unknown
- **Job archetypes:** unknown
- **Total experience:** unknown
- **Leadership experience:** unknown
- **Work authorization:** unknown

##### Competencies

| Competencies | Proficiency | years | basis |
|---|---|---|---|
| Demand Forecasting | unknown | unknown | – |
| SQL | unknown | unknown | – |
| Python | unknown | unknown | – |
| Sales and Operations Planning (S&OP) | unknown | unknown | – |

##### Languages

| Languages | CEFR | basis |
|---|---|---|
| de | NATIVE | – |
| en | C1 | – |

##### Qualifications

| Qualifications | Type | EQF | basis |
|---|---|---|---|
| Master of Science - MS Logistics | DEGREE | 7 | – |
| Bachelor of Science - BS Business Administration | DEGREE | 6 | – |
| Python for Data Analysis | CERTIFICATION | unknown | DOCUMENT_EVIDENCED (ev-cert-1) |

#### Experience history

- **Supply Chain Analyst** — Example Foods GmbH, 2020-10 – today (–)
  - Build and maintain statistical demand forecasts; monthly S&OP reporting
- **Logistics Trainee** — Example Logistics AG, 2019-09 – 2020-09 (–)
  - Rotation through planning and warehouse operations

#### Evidence

| ID | Kind | Evidence | Verification |
|---|---|---|---|
| ev-cert-1 | CERTIFICATION | Python for Data Analysis | UNVERIFIED |

#### Job preferences

| Criterion | Hard condition | Wish |
|---|---|---|
| Job archetypes | unknown | unknown |
| Career level | unknown | unknown |
| Industry | unknown | unknown |
| Organization | unknown | unknown |
| Tasks | unknown | unknown |
| Compensation | unknown | unknown |
| Location | unknown | unknown |
| Work model | unknown | unknown |
| Working time | unknown | unknown |
| Contract | unknown | unknown |
| Development | unknown | unknown |

#### Availability

unknown

_Generated deterministically by the AJMS reference implementation. Synthetic data._
