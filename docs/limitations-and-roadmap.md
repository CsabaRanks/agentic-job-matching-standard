# Limitations, open questions and roadmap

## What is implemented and what is proposed

| Area | Status in v0.1 |
|---|---|
| JSON Schemas (Draft 2020-12) for CandidateProfile, JobProfile, ProfileReference, MatchPolicy, MatchResult | **implemented**, tested |
| JSON-LD context, term-coverage and RDF conversion check | **implemented**, tested |
| Semantic validation (ranges, dates, references, public-view rules) | **implemented**, tested |
| Deterministic Markdown rendering (EN/DE) | **implemented**, tested |
| Derivation of shared and public views | **implemented**, tested |
| ProfileReference with SHA-256 content digest | **implemented**, tested |
| Export of public JobProfiles to schema.org `JobPosting` | **implemented**, tested structurally; not tested with any search engine tool |
| Matching demonstration (Hiring-Fit, Career-Fit) | **implemented as a demonstration**; weights uncalibrated |
| Hosting, access control, transport, retrieval protocol | **proposed** (illustrative flow only); outside AJMS |
| DIDs, Verifiable Credentials, DIDComm, zero-knowledge proofs | **named as possible future extensions**; nothing specified |
| Vocabulary namespace dereferencing (`ajms:` IRIs) | **not yet**: the IRIs are identifiers only |
| Schema `$id` resolution | IDs become resolvable once tag `v0.1.0` is pushed |

## Known limitations

1. **Not an adopted standard.** No standards body, vendor or platform has reviewed or adopted AJMS.
2. **Source review is incomplete.** Only the sources in [source-inventory.md](source-inventory.md) were reviewed. HR Open Standards schema files were not inspected; no field-level mapping to HR-JSON is claimed.
3. **The matcher is a demonstration.** It compares fields literally (identifiers, codes, case-insensitive labels). It does not understand synonyms, has no taxonomy mapping (e.g. ESCO ↔ KldB), no currency conversion, no routing (travel time stays UNKNOWN) and no learning. Its weights were not calibrated. **It must not be used for automated decisions about people.**
4. **Assumptions in comparisons** are stated in each explanation: 12 payments per year if not stated, 52 weeks per year, a 5-day week when remote share is derived from on-site days, straight-line distance with coordinate precision as tolerance.
5. **Self-reported data stays self-reported.** AJMS records provenance and evidence references; it verifies nothing.
6. **Anonymity is not provided.** Reduced views lower disclosure; they do not prevent re-identification, and recipients can keep copies.
7. **Content digest is not a signature** and its canonicalisation is not RFC 8785.
8. **Bias.** Structured criteria can encode discriminatory preferences or requirements (e.g. via domain criteria). AJMS has no fields for protected characteristics, but it cannot prevent misuse of free text or extensions. Deployers are responsible for fair use.
9. **Unit codes** (`KMT`, `SMI`, `MIN`, `HUR`, `WEE`, `MON`) follow UN/CEFACT Recommendation 20 as commonly published; the code list was not re-checked in this work.

## Open questions

| # | Question |
|---|---|
| Q1 | Should extraction states (`UNPARSABLE`, `CONFLICTING` from the earlier MyCareerAgent schema) be representable in a profile, or only in pipeline metadata? |
| Q2 | Should a candidate be able to set a missing-information policy per criterion (e.g. "unknown salary = review", "unknown remote share = acceptable")? |
| Q3 | Which taxonomy should be recommended for archetypes and skills (ESCO, ISCO-08, KldB 2010, O*NET), and how should cross-walks be referenced? |
| Q4 | How should a candidate express trade-offs (e.g. "more on-site days acceptable if salary ≥ X")? v0.1 has only independent criteria. |
| Q5 | Should weekly commuting load (distance × on-site days) become a first-class criterion? |
| Q6 | How should multiple locations of one job (alternative vs. rotating) be distinguished? |
| Q7 | Should the digest move to RFC 8785 (JCS) canonicalisation? |
| Q8 | Is a public minimal candidate representation desirable at all, given crawling risks? It is optional in v0.1. |
| Q9 | Should AJMS register a persistent namespace (e.g. w3id.org) instead of a GitHub Pages URL? |

## Roadmap (proposal)

| Version | Content |
|---|---|
| v0.1.x | publish tag `v0.1.0` so schema IDs and context resolve; enable GitHub Pages for the `ajms:` namespace and a human-readable vocabulary page; community feedback |
| v0.2 | decisions on Q1–Q6; JSON Resume importer (`basics`, `work`, `education`, `skills` → capabilities/history); taxonomy guidance; field-level comparison with HR-JSON after reviewing the specifications |
| v0.3 | optional evidence extension referencing W3C Verifiable Credentials (no mandatory envelope); interoperability tests with a second, independent implementation |
| later | consider a retrieval profile on top of an existing protocol; calibration methodology for match policies with published evaluation data |
