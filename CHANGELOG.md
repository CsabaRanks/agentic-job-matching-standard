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
- Synthetic examples (7 valid, 18 negative with expected errors), generated outputs, pytest suite, GitHub Actions workflow.
- Documentation: specification, field catalog, generated property index, success factors, schema.org mapping, privacy and exchange, architecture, source inventory, prior work and deviations, sources, limitations and roadmap.
