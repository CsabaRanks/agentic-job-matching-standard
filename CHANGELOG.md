# Changelog

All notable changes are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-27

First Community Draft. Not an adopted standard.

### Added

- JSON Schemas (Draft 2020-12) with versioned IDs: `common`, `candidate-profile`, `job-profile`, `profile-reference`, `match-policy`, `match-result`.
- JSON-LD context (`context/v0.1/ajms.context.jsonld`) reusing schema.org terms where the value types match, everything else in the `ajms:` namespace.
- Shared definitions for compensation (component, currency, period, gross/net, hours basis), company and industry, job archetype, career level, tasks, competencies, experience, qualifications, location and commute (distance and travel time kept apart), work model and remote share (with reference period), working time, contract, development, start timing, and typed domain-specific criteria.
- Separation of facts / self-reports / evidence, requirements / offers, hard conditions / wishes, and profile data / weights.
- Explicit `NOT_APPLICABLE` and `NOT_DISCLOSED`; absence means UNKNOWN.
- Candidate views `FULL_PRIVATE`, `SHARED_VIEW`, `PUBLIC_MINIMAL` and the `ProfileReference` exchange convention.
- Reference implementation (`src/ajms`): validation (schema + semantic), JSON-LD check, deterministic Markdown rendering (EN/DE), view derivation, ProfileReference with SHA-256 digest, schema.org JobPosting export, demo matcher with separate Hiring-Fit and Career-Fit and uncalibrated weights.
- Import adapters for provided data (no platform retrieval): Bundesagentur für Arbeit candidate profile as text (`ba-bewerberprofil-text`, PDF via `pdftotext`), LinkedIn data export CSV (`linkedin-data-export-csv`), JSON Resume (`json-resume-1`), German job ad text (`job-ad-text-de`); `ajms convert` with conversion report (source data → field mapping → conversion → validation → readable output, optional matching).
- Field-level provenance for imported profiles: `source` (reference, retrieval date, format, input kind, digest, extraction quality, unmapped fields without values) and `fieldStatements` (EXPLICIT / NORMALIZED / DERIVED, `lossy`).
- Extraction-quality gate for text inputs (token count, readable word share, layout anchors, verbatim excerpts); verified against the project's original reference files (BA, LinkedIn, XING PDF exports rejected; transcribed BA profile converted completely).
- Schema IDs, JSON-LD context and vocabulary namespace hosted on GitHub Pages; generated vocabulary page; `tools/check_published_urls.py`.
- Synthetic examples (7 valid, 20 negative with expected errors), generated outputs, pytest suite, GitHub Actions workflow.
- Documentation: specification, field catalog, generated property index, success factors, schema.org mapping, privacy and exchange, architecture, source inventory, prior work and deviations, sources, limitations and roadmap.
