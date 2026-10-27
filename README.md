# Agentic Job Matching Standard (AJMS)

**Maintain your candidate profile once. Share it selectively.
Enable agents to compare opportunities in both directions.**

[![CI](https://github.com/CsabaRanks/agentic-job-matching-standard/actions/workflows/ci.yml/badge.svg)](https://github.com/CsabaRanks/agentic-job-matching-standard/actions/workflows/ci.yml)

> **Status: Community Draft v0.1.** This is a proposal, not an adopted standard. It is not endorsed by schema.org, Google, any ATS vendor or any standards body.

AJMS defines two independent, machine-readable profiles: a **CandidateProfile** and a **JobProfile**. They are built from the same definitions for compensation, location and commute, remote share, working time, contract, career level, tasks, competencies, development and start date. As a result, an agent can answer two separate questions:

| | Question | Compares |
|---|---|---|
| **Hiring-Fit** | Does the candidate meet the job's requirements? | job `requirements` ↔ candidate `capabilities` |
| **Career-Fit** | Does the job meet the candidate's conditions and wishes? | candidate `jobPreferences` ↔ job `offer` |

Both profiles are independent of platform, storage location, agent framework and matching algorithm. Rendering a profile for humans is an additional function and not what "bidirectional" means here.

## Why

- **Candidates** re-enter the same data into every portal and agency form, and their conditions ("hybrid, at most 2 office days, at least €62k base for 40 h") end up in free text or not at all. With AJMS they maintain one private profile and hand out a reduced view per recipient.
- **Agencies and employers** receive conditions in a structured form before the first call. Mismatches on salary, location, remote share or contract type show up early, and unknowns are labelled as unknown.
- **Agent developers** get a validated, documented format with explicit units, a clear "unknown" semantics and a reference implementation that runs offline without any model or API key.

## What makes it different

- **Hard conditions and wishes are separate** (`hardCondition` / `wish`; `REQUIRED` / `PREFERRED`). Weights live outside the profiles, in a `MatchPolicy`.
- **Missing means unknown.** Absent data is never read as 0 or "no". `NOT_APPLICABLE` and `NOT_DISCLOSED` can be stated explicitly.
- **Units are explicit.** Every compensation figure has a currency, period, component, gross/net and hours basis. Remote share has a reference period. Commute **distance** and commute **time** are different quantities.
- **Provenance.** Each statement can be marked as self-reported, document-evidenced or confirmed by a third party, with references to the evidence.
- **Domain extensions.** Typed criteria with stable reverse-DNS identifiers, for example `org.example.healthcare.night_shifts_per_month`. A profile can have any number of them, including none.
- **Privacy views.** `FULL_PRIVATE`, `SHARED_VIEW`, `PUBLIC_MINIMAL`, plus a minimal `ProfileReference` for exchange. Access control stays with the host.
- **Linked Data without lock-in.** A JSON-LD context reuses schema.org terms where they fit; everything else is in its own namespace. Public JobProfiles can be exported as schema.org `JobPosting`. Candidate wishes never are.

## Quickstart

Requires Python ≥ 3.10. No network access is needed after installation.

```bash
git clone https://github.com/CsabaRanks/agentic-job-matching-standard.git
cd agentic-job-matching-standard
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -e ".[test]"

# 1. Validate: JSON Schema + semantic rules + JSON-LD check
ajms validate --jsonld examples/valid/job-demand-planner.public.json

# 2. Human-readable rendering (deterministic, English or German)
ajms render examples/valid/candidate-supply-chain-analyst.shared-view.json --lang de

# 3. Bidirectional demo match (weights are uncalibrated)
ajms match examples/valid/candidate-supply-chain-analyst.shared-view.json \
           examples/valid/job-supply-planner-agency.public.json

# 4. Derive a reduced view from a private profile, create an exchange reference
ajms derive-view examples/valid/candidate-supply-chain-analyst.full-private.json --view PUBLIC_MINIMAL
ajms reference examples/valid/job-demand-planner.public.json --url https://example.com/job.json --access PUBLIC

# 5. Export a public JobProfile as schema.org JobPosting
ajms export-schemaorg examples/valid/job-demand-planner.public.json

# 6. Convert a provided job ad (text) into a JobProfile, with a conversion report
ajms convert --format job-ad-text-de examples/adapters/job-ad-text-de/senior-demand-planner.ad.de.txt \
             --retrieved-at 2026-10-27T10:15:00+01:00 --report

# 7. Run every check and the test suite
ajms check
pytest
```

`python -m ajms …` works the same as `ajms …`.

Excerpt from step 3. The agency job is not a hard "no" because of unknown data; it fails three stated conditions, while the undisclosed salary stays visibly unknown:

```text
## Career-Fit (does the job meet the candidate's conditions and wishes?)
- Hard conditions: NOT_MET
- Indicative score (soft criteria, known only): 0.20
- Known weight coverage: 38%
| `location/hard`     | HARD | NOT_MET | Bremen: 89.1 km straight line (+/-10.0 km) vs max 40.0 km |
| `location/wish`     | SOFT | UNKNOWN | Bremen: travel time limit 45 MIN needs routing or timetable data; not derived from distance |
| `compensation/hard` | HARD | UNKNOWN | job compensation not disclosed |
| `workModel/wish`    | SOFT | UNKNOWN | remote share not stated (HYBRID without extent) |
| `contract/hard`     | HARD | NOT_MET | TEMPORARY_AGENCY_WORK; 12 months vs at least 24 |
```

Generated outputs for all examples are in [`examples/output/`](examples/output/).

## Converting existing formats

A search agent can use AJMS as its internal format by converting what it is given. Adapters process **provided** data; retrieving data from platforms is a separate function.

| `--format` | Input | Kind |
|---|---|---|
| `ba-bewerberprofil-text` | Bundesagentur für Arbeit candidate profile as text (PDF via `pdftotext` if the text layer is usable) | text, quality-gated |
| `linkedin-data-export-csv` | LinkedIn data export CSV files | structured |
| `json-resume-1` | JSON Resume document | structured |
| `job-ad-text-de` | German job ad as plain text | text, quality-gated |

```bash
ajms convert --format job-ad-text-de examples/adapters/job-ad-text-de/senior-demand-planner.ad.de.txt \
  --retrieved-at 2026-10-27T10:15:00+01:00 --source-url https://jobs.example.com/ads/senior-demand-planner-4711 \
  --report --candidate examples/valid/candidate-supply-chain-analyst.shared-view.json
```

The report runs original text → field mapping → conversion → validation → matching → human-readable output. Every field is marked:
- **explicit** (stated verbatim),
- **normalized** (converted into AJMS units or codes), or
- **derived** (inferred by a named rule; for example, the salary's hours basis comes from the stated 38-hour week).

The report also shows:
- what stays **unknown**: the ad states no remote share and no start date;
- what was **not mapped**;
- which mappings **lose meaning**.

Example: [conversion report](examples/adapters/job-ad-text-de/senior-demand-planner.conversion-report.md). All formats and limits are in [docs/import-adapters.md](docs/import-adapters.md).

## A minimal job profile

```json
{
  "@context": "https://csabaranks.github.io/agentic-job-matching-standard/context/v0.1/ajms.context.jsonld",
  "@type": "JobProfile",
  "profileId": "urn:uuid:9b2e4d71-0c3a-4f5e-8d6b-1a2b3c4d5e6f",
  "schemaVersion": "0.1.0",
  "updatedAt": "2026-10-18T14:30:00+02:00",
  "profileView": "PUBLIC",
  "title": { "text": "Demand Planner (m/f/d)", "language": "en" },
  "offer": {
    "compensation": [
      { "component": "BASE_SALARY", "currency": "EUR", "period": "YEAR", "grossOrNet": "GROSS",
        "min": 64000, "max": 74000, "hoursPerWeekBasis": 38, "informationKind": "STATED" }
    ],
    "workModel": { "arrangement": "HYBRID",
                   "remoteShare": { "percent": { "min": 40, "max": 60 }, "referencePeriod": "WEEK" } }
  }
}
```

Everything not stated (location, contract, requirements …) is UNKNOWN.

## Implemented vs. proposed

| Implemented and tested | Proposed / out of scope |
|---|---|
| JSON Schemas (Draft 2020-12) for CandidateProfile, JobProfile, ProfileReference, MatchPolicy, MatchResult | hosting, authentication, authorization, transport |
| JSON-LD context and a check that is separate from schema validation; schema IDs, context and namespace published via GitHub Pages | |
| import adapters for BA candidate profiles (text), LinkedIn data exports (CSV), JSON Resume and German job ad text, with field-level provenance | automatic retrieval from platforms; other formats (see [import adapters](docs/import-adapters.md)) |
| semantic validation, 7 valid and 20 negative examples with expected errors | DIDs, Verifiable Credentials, DIDComm, zero-knowledge proofs (possible future extensions, nothing specified) |
| deterministic Markdown rendering (EN/DE) | LLM-generated prose (optional for implementers, must not add facts) |
| view derivation, ProfileReference with SHA-256 digest | signatures; anonymity guarantees (not achievable by a format) |
| schema.org JobPosting export for public jobs | any claim of search-engine or ATS support |
| demo matcher with separate Hiring-Fit / Career-Fit, visible UNKNOWN, **uncalibrated** weights | a validated matching or ranking procedure |

Details: [limitations and roadmap](docs/limitations-and-roadmap.md).

## Documentation

| Document | Content |
|---|---|
| [Specification](docs/specification.md) | conformance, documents, rules, views, versioning |
| [Import adapters](docs/import-adapters.md) | supported input formats, pipeline, extraction quality, losses of meaning |
| [Field catalog](docs/field-catalog.md) | shared criteria, units, unknown-semantics, domain extensions |
| [Property index](docs/property-index.md) | every property and type (generated from the schemas) |
| [Success factors](docs/success-factors.md) | the shared criteria and what they mean to candidate and employer |
| [schema.org mapping](docs/schema-org-mapping.md) | adopted / transformed / extended / not mappable |
| [Privacy and exchange](docs/privacy-and-exchange.md) | views, ProfileReference, retrieval flow, limits |
| [Architecture](docs/architecture.md) | layers, data flow, design decisions |
| [Source inventory](docs/source-inventory.md) | reviewed candidate and job formats |
| [Prior work and deviations](docs/prior-work-and-deviations.md) | what was adopted from earlier work and concept drafts, and why some proposals were rejected |
| [Sources](docs/sources.md) | references with retrieval dates |

## Privacy notice

All examples are synthetic. AJMS does not provide anonymity: removing a name does not make a profile anonymous, and a recipient can keep a copy of anything shared. AJMS makes no claim of GDPR or EU AI Act compliance. The demo matcher must not be used for automated decisions about people.

## Contributing and licence

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md). Licensed under the [MIT License](LICENSE).

---

## Kurzfassung (Deutsch)

**AJMS** ist ein offener Entwurf (Community Draft v0.1, kein verabschiedeter Standard) für zwei maschinenlesbare Profile: **CandidateProfile** und **JobProfile**. Beide nutzen gemeinsame Definitionen für Vergütung, Arbeitsort und Pendeln, Remote-Anteil, Arbeitszeit, Vertrag, Karrierelevel, Aufgaben, Kompetenzen, Entwicklung und Starttermin. Ein Kandidat pflegt sein Profil einmal und gibt Personaldienstleistern oder Arbeitgebern gezielt eine reduzierte Ansicht. Agenten können dann zwei getrennte Fragen beantworten:

- **Hiring-Fit:** Erfüllt der Kandidat die Anforderungen der Stelle?
- **Career-Fit:** Erfüllt die Stelle die Bedingungen und Wünsche des Kandidaten?

Harte Bedingungen und Wünsche sind getrennt. Gewichte stehen nicht im Profil, sondern in einer separaten MatchPolicy. Fehlende Angaben gelten als **unbekannt**, nicht als „nein“. Einheiten sind eindeutig: Gehalt mit Währung, Zeitraum, Bestandteil, brutto/netto und Stundenbasis; Remote-Anteil mit Bezugszeitraum; Pendelentfernung und Pendelzeit getrennt. Domänenspezifische Zusatzkriterien haben stabile Bezeichner.

Importadapter konvertieren bereitgestellte Daten aus Bundesagentur-Bewerberprofilen (Text), LinkedIn-Datenexporten (CSV), JSON Resume und deutschen Stellenanzeigen (Text) in AJMS. Explizite, normalisierte und abgeleitete Angaben werden je Feld gekennzeichnet, nicht abbildbare Inhalte und Bedeutungsverluste ausgewiesen. Texteingaben durchlaufen eine Prüfung der Extraktionsqualität. Der automatische Abruf von Plattformen ist nicht Teil von AJMS.

Die Referenzimplementierung validiert Profile (JSON Schema, semantische Regeln, JSON-LD), erzeugt deterministische Markdown-Darstellungen auf Deutsch und Englisch, leitet reduzierte Ansichten ab und zeigt ein Demo-Matching mit unkalibrierten Gewichten. Sie läuft lokal, ohne LLM, Cloud-API oder API-Schlüssel. Zugriffskontrolle ist Aufgabe der Hosting- bzw. Transportlösung. Entfernte Namen allein machen ein Profil nicht anonym. AJMS gibt keine DSGVO- oder AI-Act-Konformitätsversprechen ab.
