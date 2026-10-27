# Conversion report: ba-bewerberprofil-text → CandidateProfile

Adapter `ajms-adapters`, rules `ba-text-1`. Deterministic, no network, no language model. Synthetic input.

## 1. Source data

- **Format:** `ba-bewerberprofil-text` (free text, values extracted)
- **Source reference:** urn:sha256:910624853b490d848c0750b1299a5bb513a294510477765e2a0af89af20114a4 (file `synthetic-demand-planner.ba.txt`)
- **Record ID in the source:** `10000-0000000000-S`
- **Retrieved / provided:** 2026-10-27T11:00:00+01:00
- **SHA-256:** `910624853b490d848c0750b1299a5bb513a294510477765e2a0af89af20114a4`

`synthetic-demand-planner.ba.txt`:

```text
Bundesagentur für Arbeit
Ihr Bewerberprofil - Demand Planner/in

Überblick über das Bewerberprofil
Referenznummer	10000-0000000000-S
Titel des Bewerberprofils	Demand Planner/in
Alternativberufe	Supply-Chain-Analyst/in
Anzeigentext	Erfahrene Fachkraft für Absatzplanung sucht neue Aufgabe
Gewünschte Arbeitsorte	20095 Hamburg, Hamburg, Deutschland - Umkreis 40 km
	Bremen, Bremen, Deutschland - Umkreis 10 km
Beginn der Tätigkeit	01.01.2027
Schulabschluss	Allgemeine Hochschulreife - Gymnasium
Berufserfahrung	Mit Berufserfahrung

Anforderungen an die Stelle
Bewerberprofilart	Arbeitsplatz
Arbeitszeit	Vollzeit

Berufserfahrung
01.10.2020 - 31.12.2026	Supply-Chain-Analyst/in
	Beschreibung: Statistische Absatzprognosen und S&OP-Reporting
	Aufbau automatisierter Planungsberichte
01.09.2019 - 30.09.2020	Sonstiges
	Beschreibung: Traineeprogramm Logistik

Schul- und Berufsbildung
Schulabschluss	Allgemeine Hochschulreife - Gymnasium
01.10.2014 - 30.09.2019	Logistik (Master of Science)
	Beschreibung/ Schwerpunkte: Supply Chain Planning, Operations Research
	Master / Diplom / Magister
01.08.2006 - 30.06.2014	Allgemeine Hochschulreife

Persönliche Fähigkeiten und Kompetenzen
Wirtschaft, Verwaltung
	Expertenkenntnisse
	Absatzplanung, Bedarfsprognose
	Erweiterte Kenntnisse
	S&OP-Prozess
IT, DV, Computer
	Erweiterte Kenntnisse
	SQL, Python, SAP ERP
Sprachkenntnisse	Muttersprache
	Deutsch
	Verhandlungssicher
	Englisch
	Grundkenntnisse
	Französisch
Persönliche Stärken	Analysefähigkeit, Teamfähigkeit
Weiterbildungen und Zertifikate	Zertifikat Datenanalyse
	Datenanalyse mit Python (Zertifikatskurs)
	Gültig von 12.05.2023 bis 11.05.2028
	Zertifikat Datenanalyse
	Datenanalyse mit Python (Zertifikatskurs)
	Gültig von 12.05.2023 bis 11.05.2028
Führerscheine	Fahrerlaubnis B PKW/Kleinbusse (alt: FS 3)
Fahrzeug	Fahrzeug vorhanden
Mobilität	Reisebereitschaft vorhanden

Kontaktdaten und sonstige Angaben zur Bewerberin/ zum Bewerber
Name	Bewerber anonymisiert
Anschrift	Kontakt über:
	Agentur für Arbeit Beispielstadt
Telekommunikation	Telefon über die Agentur für Arbeit
Sonstige Angaben zum Bewerber	weiblich, Alter: 30 Jahre
```

## 2. Extraction quality

- **Status:** REVIEW
- **Recognized lines:** 98.3%
- 221 tokens (minimum 30)
- readable word share 100% (minimum 60%)
- layout anchors present
- every source excerpt found verbatim in the input
- 57 of 58 non-empty lines recognized, 1 not interpreted

## 3. Field mapping

| Target field (JSON Pointer) | Value | Statement | Source excerpt | Method | Note |
|---|---|---|---|---|---|
| `/availability/earliestStartDate` | 2027-01-01 | NORMALIZED | 01.01.2027 | german-date |  |
| `/capabilities/competencies/0/competencyId` | absatzplanung | DERIVED | Absatzplanung | slug-of-label |  |
| `/capabilities/competencies/0/label` | Absatzplanung | EXPLICIT | Absatzplanung | – |  |
| `/capabilities/competencies/0/proficiency` | EXPERT | NORMALIZED · lossy | Expertenkenntnisse | ba-skill-level | BA uses three levels; mapped onto the four AJMS levels; BA skill domain 'Wirtschaft, Verwaltung' not carried |
| `/capabilities/competencies/1/competencyId` | bedarfsprognose | DERIVED | Bedarfsprognose | slug-of-label |  |
| `/capabilities/competencies/1/label` | Bedarfsprognose | EXPLICIT | Bedarfsprognose | – |  |
| `/capabilities/competencies/1/proficiency` | EXPERT | NORMALIZED · lossy | Expertenkenntnisse | ba-skill-level | BA uses three levels; mapped onto the four AJMS levels; BA skill domain 'Wirtschaft, Verwaltung' not carried |
| `/capabilities/competencies/2/competencyId` | s-op-prozess | DERIVED | S&OP-Prozess | slug-of-label |  |
| `/capabilities/competencies/2/label` | S&OP-Prozess | EXPLICIT | S&OP-Prozess | – |  |
| `/capabilities/competencies/2/proficiency` | ADVANCED | NORMALIZED · lossy | Erweiterte Kenntnisse | ba-skill-level | BA uses three levels; mapped onto the four AJMS levels; BA skill domain 'Wirtschaft, Verwaltung' not carried |
| `/capabilities/competencies/3/competencyId` | sql | DERIVED | SQL | slug-of-label |  |
| `/capabilities/competencies/3/label` | SQL | EXPLICIT | SQL | – |  |
| `/capabilities/competencies/3/proficiency` | ADVANCED | NORMALIZED · lossy | Erweiterte Kenntnisse | ba-skill-level | BA uses three levels; mapped onto the four AJMS levels; BA skill domain 'IT, DV, Computer' not carried |
| `/capabilities/competencies/4/competencyId` | python | DERIVED | Python | slug-of-label |  |
| `/capabilities/competencies/4/label` | Python | EXPLICIT | Python | – |  |
| `/capabilities/competencies/4/proficiency` | ADVANCED | NORMALIZED · lossy | Erweiterte Kenntnisse | ba-skill-level | BA uses three levels; mapped onto the four AJMS levels; BA skill domain 'IT, DV, Computer' not carried |
| `/capabilities/competencies/5/competencyId` | sap-erp | DERIVED | SAP ERP | slug-of-label |  |
| `/capabilities/competencies/5/label` | SAP ERP | EXPLICIT | SAP ERP | – |  |
| `/capabilities/competencies/5/proficiency` | ADVANCED | NORMALIZED · lossy | Erweiterte Kenntnisse | ba-skill-level | BA uses three levels; mapped onto the four AJMS levels; BA skill domain 'IT, DV, Computer' not carried |
| `/capabilities/domainCriteria/0/value` | B | NORMALIZED · lossy | Fahrerlaubnis B | ba-driving-licence | description of the class and old class designation not carried |
| `/capabilities/domainCriteria/1/value` | True | NORMALIZED | Fahrzeug vorhanden | ba-vehicle |  |
| `/capabilities/languages/0/cefrLevel` | NATIVE | NORMALIZED | Muttersprache | ba-language-level-to-cefr |  |
| `/capabilities/languages/0/languageCode` | de | NORMALIZED | Deutsch | language-name-de-to-bcp47 |  |
| `/capabilities/languages/1/cefrLevel` | C1 | DERIVED · lossy | Verhandlungssicher | ba-language-level-to-cefr | no official equivalence between the BA level 'Verhandlungssicher' and CEFR C1 |
| `/capabilities/languages/1/languageCode` | en | NORMALIZED | Englisch | language-name-de-to-bcp47 |  |
| `/capabilities/languages/2/cefrLevel` | A2 | DERIVED · lossy | Grundkenntnisse | ba-language-level-to-cefr | no official equivalence between the BA level 'Grundkenntnisse' and CEFR A2 |
| `/capabilities/languages/2/languageCode` | fr | NORMALIZED | Französisch | language-name-de-to-bcp47 |  |
| `/capabilities/qualifications/0/eqfLevel` | 4 | DERIVED | Allgemeine Hochschulreife | dqr-eqf-table | German qualifications framework assigns the Abitur to level 4 |
| `/capabilities/qualifications/0/label` | Allgemeine Hochschulreife - Gymnasium | EXPLICIT | Allgemeine Hochschulreife - Gymnasium | – |  |
| `/capabilities/qualifications/0/qualificationType` | OTHER | DERIVED | Allgemeine Hochschulreife - Gymnasium | ba-school-certificate-type |  |
| `/capabilities/qualifications/1/completedOn` | 2019-09 | NORMALIZED · lossy | 30.09.2019 | german-date-to-month | day of month dropped |
| `/capabilities/qualifications/1/eqfLevel` | 7 | NORMALIZED | Master / Diplom / Magister | ba-degree-category-to-eqf |  |
| `/capabilities/qualifications/1/label` | Logistik (Master of Science) | EXPLICIT | Logistik (Master of Science) | – |  |
| `/capabilities/qualifications/1/qualificationType` | DEGREE | NORMALIZED | Master / Diplom / Magister | ba-degree-category-to-eqf |  |
| `/capabilities/qualifications/2/completedOn` | 2023-05 | NORMALIZED · lossy | 12.05.2023 | german-date-to-month | 'valid from' read as completion month; day dropped |
| `/capabilities/qualifications/2/label` | Datenanalyse mit Python (Zertifikatskurs) | EXPLICIT | Datenanalyse mit Python (Zertifikatskurs) | – |  |
| `/capabilities/qualifications/2/qualificationType` | CERTIFICATION | DERIVED | Weiterbildungen und Zertifikate | ba-further-training-is-certification |  |
| `/capabilities/qualifications/2/validUntil` | 2028-05-11 | NORMALIZED | 11.05.2028 | german-date |  |
| `/experienceHistory/0/endMonth` | 2026-12 | NORMALIZED · lossy | 31.12.2026 | german-date-to-month | day of month dropped |
| `/experienceHistory/0/roleTitle` | Supply-Chain-Analyst/in | EXPLICIT | Supply-Chain-Analyst/in | – |  |
| `/experienceHistory/0/startMonth` | 2020-10 | NORMALIZED · lossy | 01.10.2020 | german-date-to-month | day of month dropped |
| `/experienceHistory/0/tasks/0/label` | Statistische Absatzprognosen und S&OP-Reporting | EXPLICIT | Statistische Absatzprognosen und S&OP-Reporting | – |  |
| `/experienceHistory/0/tasks/1/label` | Aufbau automatisierter Planungsberichte | EXPLICIT | Aufbau automatisierter Planungsberichte | – | further description line |
| `/experienceHistory/1/endMonth` | 2020-09 | NORMALIZED · lossy | 30.09.2020 | german-date-to-month | day of month dropped |
| `/experienceHistory/1/roleTitle` | Sonstiges | EXPLICIT | Sonstiges | – |  |
| `/experienceHistory/1/startMonth` | 2019-09 | NORMALIZED · lossy | 01.09.2019 | german-date-to-month | day of month dropped |
| `/experienceHistory/1/tasks/0/label` | Traineeprogramm Logistik | EXPLICIT | Traineeprogramm Logistik | – |  |
| `/headline` | Erfahrene Fachkraft für Absatzplanung sucht neue Aufgabe | EXPLICIT | Erfahrene Fachkraft für Absatzplanung sucht neue Aufgabe | – |  |
| `/jobPreferences/archetypes/wish/include/0/archetypeId` | demand-planner | DERIVED · lossy | Demand Planner/in | slug-of-label-without-gender-suffix | the BA occupation code (KldB) is not contained in the text |
| `/jobPreferences/archetypes/wish/include/0/label` | Demand Planner/in | EXPLICIT | Demand Planner/in | – | BA profile title = target occupation |
| `/jobPreferences/archetypes/wish/include/1/archetypeId` | supply-chain-analyst | DERIVED | Supply-Chain-Analyst/in | slug-of-label-without-gender-suffix |  |
| `/jobPreferences/archetypes/wish/include/1/label` | Supply-Chain-Analyst/in | EXPLICIT | Supply-Chain-Analyst/in | – | BA alternative occupation |
| `/jobPreferences/location/wish/commute/maxOneWayDistance` | value=40, unitCode=KMT, measurement=STRAIGHT_LINE | NORMALIZED · lossy | Umkreis 40 km | ba-radius-km | BA 'Umkreis' read as straight-line one-way distance; BA does not state how it is measured |
| `/jobPreferences/location/wish/commute/origin/countryCode` | DE | NORMALIZED | Deutschland | country-name-to-iso3166 |  |
| `/jobPreferences/location/wish/commute/origin/geo` | latitude=53.55, longitude=9.99, precisionKm=10 | DERIVED | Hamburg | gazetteer-city-centroid | city centroid, precision 10 km |
| `/jobPreferences/location/wish/commute/origin/locality` | Hamburg | EXPLICIT | Hamburg | – |  |
| `/jobPreferences/location/wish/commute/origin/postalCode` | 20095 | EXPLICIT | 20095 | – |  |
| `/jobPreferences/location/wish/commute/origin/region` | Hamburg | EXPLICIT | Hamburg | – |  |
| `/jobPreferences/location/wish/places/0/countryCode` | DE | NORMALIZED | Deutschland | country-name-to-iso3166 |  |
| `/jobPreferences/location/wish/places/0/locality` | Bremen | EXPLICIT · lossy | Bremen | – | radius 'Umkreis 10 km' dropped: an AJMS condition has one commute origin |
| `/jobPreferences/location/wish/places/0/region` | Bremen | EXPLICIT | Bremen | – |  |
| `/jobPreferences/workingTime/wish/schedules/include` | FULL_TIME | NORMALIZED | Vollzeit | ba-working-time | BA search criterion read as a wish, not a hard condition |

Explicit, normalized, derived: EXPLICIT 22, NORMALIZED 26, DERIVED 14; with loss of meaning: 18.

## 4. Conversion result

Profile: [`synthetic-demand-planner.candidateprofile.json`](synthetic-demand-planner.candidateprofile.json) (`CandidateProfile`, `profileView` FULL_PRIVATE).

**Not carried into the profile** (field names only, values are not stored):

- `Überblick: Berufserfahrung` — REDUNDANT: yes/no flag; the experience entries are mapped individually
- `Anforderungen: Bewerberprofilart` — NO_AJMS_FIELD: type of position sought (job, apprenticeship, ...)
- `Schul- und Berufsbildung: Schulabschluss` — REDUNDANT: same certificate listed twice in the BA export
- `Schul- und Berufsbildung: Logistik (Master of Science): Schwerpunkte` — NO_AJMS_FIELD: focus areas of a degree have no AJMS field
- `Schul- und Berufsbildung: Allgemeine Hochschulreife (01.08.2006 - 30.06.2014)` — REDUNDANT: dated school period of the school-leaving certificate already mapped
- `Persönliche Stärken` — NO_AJMS_FIELD: self-described personal strengths are not mapped to competencies
- `Weiterbildungen und Zertifikate: short title of 'Datenanalyse mit Python (Zertifikatskurs)'` — REDUNDANT: short title next to the full certificate name
- `Weiterbildungen und Zertifikate: 'Datenanalyse mit Python (Zertifikatskurs)' (repeated)` — REDUNDANT: identical certificate listed more than once in the BA export
- `line 57` — NOT_INTERPRETED: row label 'Mobilität' is unknown to ba-text-1
- `Kontaktdaten: Name` — INTERMEDIARY_CONTACT: the BA profile is anonymised; contact runs via the employment agency
- `Kontaktdaten: Anschrift` — INTERMEDIARY_CONTACT: the BA profile is anonymised; contact runs via the employment agency
- `Kontaktdaten: Telekommunikation` — INTERMEDIARY_CONTACT: the BA profile is anonymised; contact runs via the employment agency
- `Sonstige Angaben zum Bewerber` — PROTECTED_CHARACTERISTIC_NOT_MAPPED: sex and age are not represented in AJMS; values are not stored

**Unknown** (absent from the source, therefore absent from the profile):

- current career level (`/capabilities/currentCareerLevel`)
- practised job archetypes (`/capabilities/archetypes`)
- experience by domain (months) (`/capabilities/domainExperience`)
- total experience (months) (`/capabilities/totalExperienceMonths`)
- work authorization (`/capabilities/workAuthorizations`)
- wished career level (`/jobPreferences/careerLevel`)
- industry preferences (`/jobPreferences/industries`)
- compensation expectation (`/jobPreferences/compensation`)
- work model / remote share (`/jobPreferences/workModel`)
- contract preferences (`/jobPreferences/contract`)
- development wishes (`/jobPreferences/development`)
- search status (`/searchStatus`)

## 5. AJMS validation

- **JSON Schema + semantic rules:** valid
- **JSON-LD:** ok, 526 RDF statements

## 6. Human-readable output (de)

### Kandidatenprofil: Erfahrene Fachkraft für Absatzplanung sucht neue Aufgabe

- **Profil-ID:** `urn:uuid:8f73559a-b25b-56dd-a91d-cf81a2926480`
- **Ansicht:** FULL_PRIVATE
- **Aktualisiert:** 2026-10-27T11:00:00+01:00
- **Schemaversion:** 0.1.0
- **Suchstatus:** unbekannt
- **Source:** ba-bewerberprofil-text, urn:sha256:910624853b490d848c0750b1299a5bb513a294510477765e2a0af89af20114a4, retrieved 2026-10-27T11:00:00+01:00

#### Qualifikationsprofil

- **Aktuelles Karrierelevel:** unbekannt
- **Jobarchetypen:** unbekannt
- **Berufserfahrung gesamt:** unbekannt
- **Führungserfahrung:** unbekannt
- **Arbeitserlaubnis:** unbekannt

##### Kompetenzen

| Kompetenzen | Proficiency | Jahre | Grundlage |
|---|---|---|---|
| Absatzplanung | EXPERT | unbekannt | – |
| Bedarfsprognose | EXPERT | unbekannt | – |
| S&OP-Prozess | ADVANCED | unbekannt | – |
| SQL | ADVANCED | unbekannt | – |
| Python | ADVANCED | unbekannt | – |
| SAP ERP | ADVANCED | unbekannt | – |

##### Sprachen

| Sprachen | CEFR | Grundlage |
|---|---|---|
| de | NATIVE | – |
| en | C1 | – |
| fr | A2 | – |

##### Qualifikationen

| Qualifikationen | Type | EQF | Grundlage |
|---|---|---|---|
| Allgemeine Hochschulreife - Gymnasium | OTHER | 4 | – |
| Logistik (Master of Science) | DEGREE | 7 | – |
| Datenanalyse mit Python (Zertifikatskurs) | CERTIFICATION | unbekannt | – |

##### Domänenspezifische Kriterien

- Fahrerlaubnisklassen (`io.github.csabaranks.ajms.driving_licence_classes`): B — –
- Eigenes Fahrzeug (`io.github.csabaranks.ajms.own_vehicle`): yes — –

#### Berufliche Stationen

- **Supply-Chain-Analyst/in** — unbekannt, 2020-10 – 2026-12 (–)
  - Statistische Absatzprognosen und S&OP-Reporting
  - Aufbau automatisierter Planungsberichte
- **Sonstiges** — unbekannt, 2019-09 – 2020-09 (–)
  - Traineeprogramm Logistik

#### Wünsche und Bedingungen

| Kriterium | Harte Bedingung | Wunsch |
|---|---|---|
| Jobarchetypen | – | include: Demand Planner/in (`demand-planner`), Supply-Chain-Analyst/in (`supply-chain-analyst`) |
| Karrierelevel | unbekannt | unbekannt |
| Branche | unbekannt | unbekannt |
| Unternehmen | unbekannt | unbekannt |
| Aufgabeninhalte | unbekannt | unbekannt |
| Vergütung | unbekannt | unbekannt |
| Arbeitsort | – | ≤ 40 KMT one way (STRAIGHT_LINE); from Hamburg, Hamburg, DE; places: Bremen |
| Arbeitsmodell | unbekannt | unbekannt |
| Arbeitszeit | – | include: FULL_TIME |
| Vertrag | unbekannt | unbekannt |
| Entwicklung | unbekannt | unbekannt |

#### Verfügbarkeit

- **Start:** ≥ 2027-01-01

_Deterministisch erzeugt mit der AJMS-Referenzimplementierung. Synthetische Daten._
