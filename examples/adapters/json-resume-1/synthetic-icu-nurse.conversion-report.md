# Conversion report: json-resume-1 → CandidateProfile

Adapter `ajms-adapters`, rules `json-resume-1`. Deterministic, no network, no language model. Synthetic input.

## 1. Source data

- **Format:** `json-resume-1` (structured fields, mapped directly)
- **Source reference:** urn:sha256:25e8efa2154c6dc368f360e80e87e5dd59f11b74c4aace37cc36e8d200d336fa (file `synthetic-icu-nurse.resume.json`)
- **Retrieved / provided:** 2026-10-27T11:10:00+01:00
- **SHA-256:** `25e8efa2154c6dc368f360e80e87e5dd59f11b74c4aace37cc36e8d200d336fa`

`synthetic-icu-nurse.resume.json`:

```text
{
  "basics": {
    "name": "Sam Example",
    "label": "Intensive care nurse",
    "email": "sam.example@example.org",
    "url": "https://example.org/sam",
    "summary": "Synthetic example resume. Eight years in intensive care with ventilation experience.",
    "location": { "address": "Beispielweg 2", "postalCode": "04109", "city": "Leipzig", "countryCode": "DE", "region": "Sachsen" },
    "profiles": [ { "network": "ExampleNet", "username": "sam", "url": "https://example.org/net/sam" } ]
  },
  "work": [
    {
      "name": "Example Hospital",
      "position": "Intensive care nurse",
      "startDate": "2018-04-01",
      "summary": "Care of ventilated patients in a surgical ICU",
      "highlights": [ "Practical instructor for new colleagues" ]
    },
    {
      "name": "Example Clinic",
      "position": "Nurse",
      "startDate": "2015-10",
      "endDate": "2018-03",
      "location": "Leipzig"
    }
  ],
  "education": [
    { "institution": "Example Nursing School", "area": "Nursing", "studyType": "Vocational training", "startDate": "2012-10", "endDate": "2015-09" }
  ],
  "certificates": [
    { "name": "Specialist training in intensive care and anaesthesia nursing", "date": "2020-06-30", "issuer": "Example Academy", "url": "https://example.org/certificates/icu" }
  ],
  "skills": [
    { "name": "Ventilation care", "level": "Advanced", "keywords": [ "invasive ventilation", "weaning" ] },
    { "name": "Patient monitoring", "level": "Expert" }
  ],
  "languages": [
    { "language": "German", "fluency": "Native speaker" },
    { "language": "English", "fluency": "Conversational" }
  ],
  "interests": [ { "name": "Hiking" } ],
  "references": [ { "name": "A colleague", "reference": "Synthetic reference text." } ],
  "meta": { "version": "v1.0.0" }
}
```

## 2. Structural checks

- **Status:** PASSED
- valid JSON object; known sections have the expected JSON types
- not validated against the official JSON Resume schema

## 3. Field mapping

| Target field (JSON Pointer) | Value | Statement | Source excerpt | Method | Note |
|---|---|---|---|---|---|
| `/capabilities/competencies/0/competencyId` | ventilation-care | DERIVED | Ventilation care | slug-of-label |  |
| `/capabilities/competencies/0/label` | Ventilation care | EXPLICIT | Ventilation care | – |  |
| `/capabilities/competencies/0/proficiency` | ADVANCED | NORMALIZED | Advanced | json-resume-level-words |  |
| `/capabilities/competencies/1/competencyId` | patient-monitoring | DERIVED | Patient monitoring | slug-of-label |  |
| `/capabilities/competencies/1/label` | Patient monitoring | EXPLICIT | Patient monitoring | – |  |
| `/capabilities/competencies/1/proficiency` | EXPERT | NORMALIZED | Expert | json-resume-level-words |  |
| `/capabilities/languages/0/cefrLevel` | NATIVE | DERIVED | Native speaker | json-resume-fluency-to-cefr |  |
| `/capabilities/languages/0/languageCode` | de | NORMALIZED | German | language-name-en-to-bcp47 |  |
| `/capabilities/languages/1/cefrLevel` | B1 | DERIVED · lossy | Conversational | json-resume-fluency-to-cefr | free-text fluency 'Conversational' has no official CEFR equivalence |
| `/capabilities/languages/1/languageCode` | en | NORMALIZED | English | language-name-en-to-bcp47 |  |
| `/capabilities/qualifications/0/completedOn` | 2015-09 | NORMALIZED | 2015-09 | iso-date-to-month |  |
| `/capabilities/qualifications/0/fieldOfStudy` | Nursing | EXPLICIT | Nursing | – |  |
| `/capabilities/qualifications/0/issuerName` | Example Nursing School | EXPLICIT | Example Nursing School | – |  |
| `/capabilities/qualifications/0/label` | Vocational training, Nursing | NORMALIZED | Vocational training | join-study-type-and-area |  |
| `/capabilities/qualifications/0/qualificationType` | VOCATIONAL_QUALIFICATION | DERIVED | Vocational training | study-type-keyword |  |
| `/capabilities/qualifications/1/completedOn` | 2020-06 | NORMALIZED · lossy | 2020-06-30 | iso-date-to-month | day of month dropped |
| `/capabilities/qualifications/1/issuerName` | Example Academy | EXPLICIT | Example Academy | – |  |
| `/capabilities/qualifications/1/label` | Specialist training in intensive care and anaesthesia nursing | EXPLICIT | Specialist training in intensive care and anaesthesia nursing | – |  |
| `/capabilities/qualifications/1/provenance` | basis=DOCUMENT_EVIDENCED | DERIVED | – | certificate-url-is-evidence-reference |  |
| `/capabilities/qualifications/1/qualificationType` | CERTIFICATION | DERIVED | – | certificates-section |  |
| `/evidence/0/documentUrl` | https://example.org/certificates/icu | EXPLICIT | https://example.org/certificates/icu | – |  |
| `/evidence/0/verificationStatus` | UNVERIFIED | DERIVED | – | nothing-verified-on-import |  |
| `/experienceHistory/0/ongoing` | True | DERIVED | – | missing-end-date-means-current |  |
| `/experienceHistory/0/organization/name` | Example Hospital | EXPLICIT | Example Hospital | – |  |
| `/experienceHistory/0/roleTitle` | Intensive care nurse | EXPLICIT | Intensive care nurse | – |  |
| `/experienceHistory/0/startMonth` | 2018-04 | NORMALIZED · lossy | 2018-04-01 | iso-date-to-month | day of month dropped |
| `/experienceHistory/0/tasks/0/label` | Care of ventilated patients in a surgical ICU | EXPLICIT | Care of ventilated patients in a surgical ICU | – |  |
| `/experienceHistory/0/tasks/1/label` | Practical instructor for new colleagues | EXPLICIT | Practical instructor for new colleagues | – |  |
| `/experienceHistory/1/endMonth` | 2018-03 | NORMALIZED | 2018-03 | iso-date-to-month |  |
| `/experienceHistory/1/organization/name` | Example Clinic | EXPLICIT | Example Clinic | – |  |
| `/experienceHistory/1/roleTitle` | Nurse | EXPLICIT | Nurse | – |  |
| `/experienceHistory/1/startMonth` | 2015-10 | NORMALIZED | 2015-10 | iso-date-to-month |  |
| `/headline` | Intensive care nurse | EXPLICIT | Intensive care nurse | – |  |
| `/identity/contactPoints/0/contactValue` | sam.example@example.org | EXPLICIT | sam.example@example.org | – |  |
| `/identity/contactPoints/1/contactValue` | https://example.org/sam | EXPLICIT | https://example.org/sam | – |  |
| `/identity/displayName` | Sam Example | EXPLICIT | Sam Example | – |  |
| `/identity/residence/countryCode` | DE | EXPLICIT | DE | – |  |
| `/identity/residence/geo` | latitude=51.34, longitude=12.37, precisionKm=10 | DERIVED | Leipzig | gazetteer-city-centroid | city centroid, precision 10 km |
| `/identity/residence/locality` | Leipzig | EXPLICIT | Leipzig | – |  |
| `/identity/residence/postalCode` | 04109 | EXPLICIT | 04109 | – |  |
| `/identity/residence/region` | Sachsen | EXPLICIT | Sachsen | – |  |
| `/summary` | Synthetic example resume. Eight years in intensive care with ventilation experience. | EXPLICIT | Synthetic example resume. Eight years in intensive care with ventilation experience. | – |  |

Explicit, normalized, derived: EXPLICIT 22, NORMALIZED 10, DERIVED 10; with loss of meaning: 3.

## 4. Conversion result

Profile: [`synthetic-icu-nurse.candidateprofile.json`](synthetic-icu-nurse.candidateprofile.json) (`CandidateProfile`, `profileView` FULL_PRIVATE).

**Not carried into the profile** (field names only, values are not stored):

- `interests` — NO_AJMS_FIELD: private interests are not matching criteria
- `references` — DATA_MINIMISATION: statements by third parties; never imported
- `meta` — REDUNDANT: metadata of the resume document
- `basics.location.address` — DATA_MINIMISATION: a street address is not needed for matching
- `basics.profiles` — NO_AJMS_FIELD: social network profile links
- `work[1].location` — NO_AJMS_FIELD
- `skills[0].keywords` — NO_AJMS_FIELD: sub-skill keywords are not mapped as separate competencies

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
- **JSON-LD:** ok, 316 RDF statements

## 6. Human-readable output (en)

### Candidate profile: Intensive care nurse

- **Profile ID:** `urn:uuid:0354d7b2-8e52-5f23-8488-b26a606ca143`
- **View:** FULL_PRIVATE
- **Updated:** 2026-10-27T11:10:00+01:00
- **Schema version:** 0.1.0
- **Search status:** unknown
- **Source:** json-resume-1, urn:sha256:25e8efa2154c6dc368f360e80e87e5dd59f11b74c4aace37cc36e8d200d336fa, retrieved 2026-10-27T11:10:00+01:00

#### Identity

- **Name:** Sam Example
- **Contact:** EMAIL: sam.example@example.org
- **Contact:** URL: https://example.org/sam

#### Summary

Synthetic example resume. Eight years in intensive care with ventilation experience.

#### Capabilities

- **Current career level:** unknown
- **Job archetypes:** unknown
- **Total experience:** unknown
- **Leadership experience:** unknown
- **Work authorization:** unknown

##### Competencies

| Competencies | Proficiency | years | basis |
|---|---|---|---|
| Ventilation care | ADVANCED | unknown | – |
| Patient monitoring | EXPERT | unknown | – |

##### Languages

| Languages | CEFR | basis |
|---|---|---|
| de | NATIVE | – |
| en | B1 | – |

##### Qualifications

| Qualifications | Type | EQF | basis |
|---|---|---|---|
| Vocational training, Nursing | VOCATIONAL_QUALIFICATION | unknown | – |
| Specialist training in intensive care and anaesthesia nursing | CERTIFICATION | unknown | DOCUMENT_EVIDENCED (ev-cert-1) |

#### Experience history

- **Intensive care nurse** — Example Hospital, 2018-04 – today (–)
  - Care of ventilated patients in a surgical ICU
  - Practical instructor for new colleagues
- **Nurse** — Example Clinic, 2015-10 – 2018-03 (–)

#### Evidence

| ID | Kind | Evidence | Verification |
|---|---|---|---|
| ev-cert-1 | CERTIFICATION | Specialist training in intensive care and anaesthesia nursing | UNVERIFIED |

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
