# Conversion report: job-ad-text-de → JobProfile

Adapter `ajms-adapters`, rules `job-ad-de-1`. Deterministic, no network, no language model. Synthetic input.

## 1. Source data

- **Format:** `job-ad-text-de` (free text, values extracted)
- **Source reference:** https://jobs.example.com/ads/senior-demand-planner-4711 (file `senior-demand-planner.ad.de.txt`)
- **Retrieved / provided:** 2026-10-27T10:15:00+01:00
- **SHA-256:** `b5e18264f6c681f58387396e2d90c7bc116a153a33a9c2a01a646b4017481a4d`

`senior-demand-planner.ad.de.txt`:

```text
Senior Demand Planner (m/w/d)
Nordlicht Getränke GmbH (synthetisches Beispiel) · Standort: Hamburg

Ihre Aufgaben
- Erstellung statistischer Absatzprognosen für das Kernsortiment
- Moderation des monatlichen Consensus-Meetings mit Vertrieb und Produktion
- Weiterentwicklung unserer Planungsprozesse

Ihr Profil
- Mindestens 3 Jahre Erfahrung in der Supply-Chain-Planung
- Sehr gute SQL-Kenntnisse
- Gute Python-Kenntnisse sind von Vorteil
- Deutsch (C1) und Englisch (B2)
- Hands-on-Mentalität und Freude an Zahlen

Wir bieten
- Unbefristete Festanstellung in Vollzeit (38 Stunden/Woche)
- Hybrides Arbeiten
- Jahresgehalt 64.000–72.000 € brutto
- Jobticket und betriebliche Altersvorsorge
```

## 2. Extraction quality

- **Status:** REVIEW
- **Recognized lines:** 94.1%
- 88 tokens (minimum 30)
- readable word share 99% (minimum 60%)
- layout anchors present
- every source excerpt found verbatim in the input
- 16 of 17 non-empty lines recognized, 1 not interpreted

## 3. Field mapping

| Target field (JSON Pointer) | Value | Statement | Source excerpt | Method | Note |
|---|---|---|---|---|---|
| `/archetype` | demand-planner | DERIVED | Demand Planner | title-keyword-archetype |  |
| `/careerLevel` | SENIOR | DERIVED | Senior | title-keyword-career-level |  |
| `/hiringOrganization/name` | Nordlicht Getränke GmbH (synthetisches Beispiel) | EXPLICIT | Nordlicht Getränke GmbH (synthetisches Beispiel) | – |  |
| `/offer/benefits/0` | Jobticket und betriebliche Altersvorsorge | EXPLICIT | Jobticket und betriebliche Altersvorsorge | – | offer bullet not matched by any rule; kept verbatim as a benefit |
| `/offer/compensation/0/component` | BASE_SALARY | DERIVED | Jahresgehalt | salary-word-is-base-salary | 'Jahresgehalt' is read as fixed base salary; it may include variable pay |
| `/offer/compensation/0/currency` | EUR | NORMALIZED | € | currency-symbol-to-iso4217 |  |
| `/offer/compensation/0/grossOrNet` | GROSS | NORMALIZED | brutto | gross-net-words-de |  |
| `/offer/compensation/0/hoursPerWeekBasis` | 38 | DERIVED | 38 Stunden/Woche | salary-hours-from-working-time | assumes the salary refers to the stated contractual weekly hours |
| `/offer/compensation/0/max` | 72000 | NORMALIZED | 72.000 | german-number-format |  |
| `/offer/compensation/0/min` | 64000 | NORMALIZED | 64.000 | german-number-format |  |
| `/offer/compensation/0/period` | YEAR | NORMALIZED | Jahresgehalt | period-words-de |  |
| `/offer/contract/contractType` | PERMANENT_EMPLOYMENT | NORMALIZED | Unbefristete | contract-words-de |  |
| `/offer/locations/0/countryCode` | DE | DERIVED | Hamburg | gazetteer-city-country |  |
| `/offer/locations/0/geo` | latitude=53.55, longitude=9.99, precisionKm=10 | DERIVED | Hamburg | gazetteer-city-centroid | city centroid, precision 10 km |
| `/offer/locations/0/locality` | Hamburg | EXPLICIT | Hamburg | – |  |
| `/offer/workModel/arrangement` | HYBRID | NORMALIZED | Hybrides | work-model-words-de |  |
| `/offer/workingTime/schedule` | FULL_TIME | NORMALIZED | Vollzeit | schedule-words-de |  |
| `/offer/workingTime/weeklyHours` | min=38, max=38 | NORMALIZED | 38 Stunden/Woche | hours-per-week |  |
| `/requirements/competencies/0/competencyId` | sql | DERIVED | SQL | competency-keyword-table |  |
| `/requirements/competencies/0/label` | SQL | EXPLICIT | SQL | – |  |
| `/requirements/competencies/0/minimumProficiency` | ADVANCED | NORMALIZED · lossy | Sehr gute | proficiency-words-de | German grading words mapped onto four AJMS levels |
| `/requirements/competencies/0/requirementLevel` | REQUIRED | DERIVED | – | profile-section-default-required | listed under the profile section without a 'preferred' marker |
| `/requirements/competencies/1/competencyId` | python | DERIVED | Python | competency-keyword-table |  |
| `/requirements/competencies/1/label` | Python | EXPLICIT | Python | – |  |
| `/requirements/competencies/1/minimumProficiency` | INTERMEDIATE | NORMALIZED · lossy | Gute | proficiency-words-de | German grading words mapped onto four AJMS levels |
| `/requirements/competencies/1/requirementLevel` | PREFERRED | NORMALIZED | von Vorteil | preferred-marker-de |  |
| `/requirements/domainExperience/0/domainId` | supply-chain-planning | DERIVED | Supply-Chain-Planung | domain-keyword-table |  |
| `/requirements/domainExperience/0/label` | Supply-Chain-Planung | EXPLICIT | Supply-Chain-Planung | – |  |
| `/requirements/domainExperience/0/minimumMonths` | 36 | NORMALIZED | Mindestens 3 Jahre | years-to-months |  |
| `/requirements/domainExperience/0/requirementLevel` | REQUIRED | DERIVED | – | profile-section-default-required | listed under the profile section without a 'preferred' marker |
| `/requirements/languages/0/languageCode` | de | NORMALIZED | Deutsch | language-name-de-to-bcp47 |  |
| `/requirements/languages/0/minimumCefrLevel` | C1 | EXPLICIT | C1 | – |  |
| `/requirements/languages/0/requirementLevel` | REQUIRED | DERIVED | – | profile-section-default-required | listed under the profile section without a 'preferred' marker |
| `/requirements/languages/1/languageCode` | en | NORMALIZED | Englisch | language-name-de-to-bcp47 |  |
| `/requirements/languages/1/minimumCefrLevel` | B2 | EXPLICIT | B2 | – |  |
| `/requirements/languages/1/requirementLevel` | REQUIRED | DERIVED | – | profile-section-default-required | listed under the profile section without a 'preferred' marker |
| `/tasks/0/label` | Erstellung statistischer Absatzprognosen für das Kernsortiment | EXPLICIT | Erstellung statistischer Absatzprognosen für das Kernsortiment | – |  |
| `/tasks/1/label` | Moderation des monatlichen Consensus-Meetings mit Vertrieb und Produktion | EXPLICIT | Moderation des monatlichen Consensus-Meetings mit Vertrieb und Produktion | – |  |
| `/tasks/2/label` | Weiterentwicklung unserer Planungsprozesse | EXPLICIT | Weiterentwicklung unserer Planungsprozesse | – |  |
| `/title` | Senior Demand Planner (m/w/d) | EXPLICIT | Senior Demand Planner (m/w/d) | – |  |

Explicit, normalized, derived: EXPLICIT 12, NORMALIZED 15, DERIVED 13; with loss of meaning: 2.

## 4. Conversion result

Profile: [`senior-demand-planner.jobprofile.json`](senior-demand-planner.jobprofile.json) (`JobProfile`, `profileView` FULL_PRIVATE).

**Not carried into the profile** (field names only, values are not stored):

- `line 14` — NOT_INTERPRETED: no rule of job-ad-de-1 applies

**Unknown** (absent from the source, therefore absent from the profile):

- organization type (employer or agency) (`/hiringOrganization/organizationType`)
- industry (`/hiringOrganization/industries`)
- company size (`/hiringOrganization/sizeClass`)
- leadership responsibility (`/leadership`)
- qualification requirements (`/requirements/qualifications`)
- work authorization (`/requirements/workAuthorization`)
- start date (`/requirements/startTiming`)
- remote share (`/offer/workModel/remoteShare`)
- on-site days (`/offer/workModel/onsiteDays`)
- travel share (`/offer/workModel/travelShare`)
- shift work (`/offer/workingTime/shiftWork`)
- development perspectives (`/offer/development`)
- posting date (`/datePosted`)
- application deadline (`/validThrough`)

## 5. AJMS validation

- **JSON Schema + semantic rules:** valid
- **JSON-LD:** ok, 298 RDF statements

## 6. Matching (demonstration)

Candidate `urn:uuid:dcde3cca-c19a-55b6-8354-1d988ad1eb21`; weights `demo-hiring-fit-v0.1` / `demo-career-fit-v0.1` (UNCALIBRATED).

- **Hiring-Fit:** hard conditions ALL_MET, indicative score 1.00, known weight coverage 100%
- **Career-Fit:** hard conditions UNRESOLVED, indicative score 0.80, known weight coverage 38%

| Perspective | Criterion | Type | Outcome | Explanation |
|---|---|---|---|---|
| Hiring | `competencies/sql` | HARD | MET | SQL: proficiency ADVANCED vs required ADVANCED (SELF_REPORTED) |
| Hiring | `competencies/python` | SOFT | MET | Python: proficiency INTERMEDIATE vs required INTERMEDIATE (DOCUMENT_EVIDENCED) |
| Hiring | `languages/de` | HARD | MET | de: NATIVE vs required C1 |
| Hiring | `languages/en` | HARD | MET | en: C1 vs required B2 |
| Hiring | `domainExperience/supply-chain-planning` | HARD | MET | Supply-Chain-Planung: 72 months vs required 36 |
| Hiring | `careerLevel` | SOFT | MET | job SENIOR, candidate currently PROFESSIONAL (step +1) |
| Career | `archetypes/hard` | HARD | MET | job archetype demand-planner: the job has an included value |
| Career | `archetypes/wish` | SOFT | MET | job archetype demand-planner: the job has an included value |
| Career | `careerLevel/hard` | HARD | MET | job level SENIOR |
| Career | `careerLevel/wish` | SOFT | MET | job level SENIOR |
| Career | `industries/hard` | HARD | **UNKNOWN** | the job does not state this |
| Career | `industries/wish` | SOFT | **UNKNOWN** | the job does not state this |
| Career | `organization/wish` | SOFT | **UNKNOWN** | size not stated |
| Career | `tasks/wish` | SOFT | **UNKNOWN** | none of 2 desired tasks matched literally (tasks may be worded differently) |
| Career | `compensation/hard` | HARD | MET | job 67,368-75,789 EUR/year vs at least 62,000; scaled from 38 h to 40 h per week |
| Career | `compensation/wish` | SOFT | PARTIALLY_MET | job 67,368-75,789 EUR/year vs at least 70,000; scaled from 38 h to 40 h per week |
| Career | `location/hard` | HARD | MET | Hamburg: 10.0 km straight line (+/-15.0 km) vs max 40.0 km |
| Career | `location/wish` | SOFT | **UNKNOWN** | Hamburg: travel time limit 45 MIN needs routing or timetable data; not derived from distance |
| Career | `workModel/hard` | HARD | **UNKNOWN** | arrangement HYBRID; travel share not stated |
| Career | `workModel/wish` | SOFT | **UNKNOWN** | remote share not stated (HYBRID without extent) |
| Career | `workingTime/hard` | HARD | **UNKNOWN** | schedule FULL_TIME; 38-38 h/week vs acceptable 35-40; shiftWork not stated |
| Career | `contract/hard` | HARD | MET | PERMANENT_EMPLOYMENT |
| Career | `contract/wish` | SOFT | MET | PERMANENT_EMPLOYMENT |
| Career | `development/wish` | SOFT | **UNKNOWN** | job paths: not stated |
| Career | `domainCriteria/org.example.supplychain.planning_tool_budget` | SOFT | **UNKNOWN** | Budget for planning tool licences available: no value stated on the other side |

> Demonstration output. Weights are UNCALIBRATED and illustrative. UNKNOWN means information is missing or not comparable; it is not a negative result. Not suitable for automated decisions about people.

## 7. Human-readable output (de)

### Stellenprofil: Senior Demand Planner (m/w/d)

- **Unternehmen:** Nordlicht Getränke GmbH (synthetisches Beispiel)
- **Jobarchetyp:** Demand Planner (`demand-planner`)
- **Karrierelevel:** SENIOR
- **Führungserfahrung:** unbekannt
- **Profil-ID:** `urn:uuid:5d2671cc-7e2b-5f18-8444-4ff63d11b269`
- **Ansicht:** FULL_PRIVATE
- **Aktualisiert:** 2026-10-27T10:15:00+01:00
- **Veröffentlicht:** unbekannt
- **Gültig bis:** unbekannt
- **Datenherkunft:** DERIVED
- **Source:** https://jobs.example.com/ads/senior-demand-planner-4711 (JOB_AD_WEB_PAGE), retrieved 2026-10-27T10:15:00+01:00
- **Field statements:** EXPLICIT 12, NORMALIZED 15, DERIVED 13

#### Aufgaben

- Erstellung statistischer Absatzprognosen für das Kernsortiment
- Moderation des monatlichen Consensus-Meetings mit Vertrieb und Produktion
- Weiterentwicklung unserer Planungsprozesse

#### Anforderungen

| Kriterium | Anforderung | Stufe |
|---|---|---|
| Kompetenzen | SQL (ADVANCED) | REQUIRED |
| Kompetenzen | Python (INTERMEDIATE) | PREFERRED |
| Sprachen | de ≥ C1 | REQUIRED |
| Sprachen | en ≥ B2 | REQUIRED |
| Fachliche Erfahrung | Supply-Chain-Planung ≥ 36 Monate | REQUIRED |

#### Angebot

| Kriterium | Angebot |
|---|---|
| Vergütung | BASE_SALARY 64,000–72,000 EUR/Jahr gross, 38 h/week |
| Arbeitsort | Hamburg, DE |
| Arbeitsmodell | HYBRID; remote share unbekannt |
| Arbeitszeit | FULL_TIME; 38 h/week |
| Vertrag | PERMANENT_EMPLOYMENT |
| Entwicklung | unbekannt |
| Zusatzleistungen | Jobticket und betriebliche Altersvorsorge |

_Deterministisch erzeugt mit der AJMS-Referenzimplementierung. Synthetische Daten._
