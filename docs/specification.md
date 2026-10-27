# AJMS Specification — Community Draft v0.1

**Status:** Community Draft v0.1.0. This is a proposal, not an adopted standard. It has not been reviewed or endorsed by any standards body, by schema.org, by any search engine or by any ATS vendor.

The key words MUST, MUST NOT, SHOULD and MAY are used as in RFC 2119.

## 1. Purpose and scope

AJMS defines two independent, platform-neutral profile documents:

- **CandidateProfile**: what a candidate brings (`capabilities`, `experienceHistory`, `evidence`) and what they look for (`jobPreferences`, `availability`).
- **JobProfile**: what a job requires (`requirements`) and what it offers (`offer`).

Both use the same shared definitions ([common.schema.json](../schemas/v0.1/common.schema.json)). This makes a comparison possible in **two directions**:

| Perspective | Question | Inputs |
|---|---|---|
| **Hiring-Fit** | How well does the candidate meet the job's requirements? | `JobProfile.requirements` ↔ `CandidateProfile.capabilities`, `availability` |
| **Career-Fit** | How well does the job meet the candidate's conditions and wishes? | `CandidateProfile.jobPreferences` ↔ `JobProfile.offer`, `archetype`, `careerLevel`, `tasks`, `hiringOrganization` |

"Bidirectional" refers to these two perspectives. A human-readable rendering of a profile is a separate function (section 8).

**Out of scope:** storage, transport, authentication, authorization, a matching algorithm, a ranking, and any decision about people. AJMS is independent of platform, storage location, agent framework and matching algorithm.

## 2. Documents and identifiers

| Document | Schema `$id` |
|---|---|
| CandidateProfile | `https://raw.githubusercontent.com/CsabaRanks/agentic-job-matching-standard/v0.1.0/schemas/v0.1/candidate-profile.schema.json` |
| JobProfile | `…/schemas/v0.1/job-profile.schema.json` |
| ProfileReference | `…/schemas/v0.1/profile-reference.schema.json` |
| MatchPolicy | `…/schemas/v0.1/match-policy.schema.json` |
| MatchResult | `…/schemas/v0.1/match-result.schema.json` |
| shared definitions | `…/schemas/v0.1/common.schema.json` |

All schemas use JSON Schema Draft 2020-12 (`"$schema": "https://json-schema.org/draft/2020-12/schema"`). The `$id` values include the release tag (`v0.1.0`) and the schema line (`v0.1`). They become resolvable once the tag `v0.1.0` is published. Validators SHOULD resolve them from a local copy and MUST NOT depend on network access.

JSON-LD context: `https://raw.githubusercontent.com/CsabaRanks/agentic-job-matching-standard/v0.1.0/context/v0.1/ajms.context.jsonld`.
Vocabulary namespace for AJMS-specific terms: `https://csabaranks.github.io/agentic-job-matching-standard/ns/v0.1#` (prefix `ajms:`). In v0.1 this namespace IRI is an identifier only and is **not yet dereferenceable** (see [roadmap](limitations-and-roadmap.md)).

## 3. Conformance

A document **conforms** to AJMS v0.1 if:

1. it is valid against the schema for its `@type` (structural validation), **and**
2. it raises no semantic error (section 6), **and**
3. for CandidateProfile, JobProfile and ProfileReference, every key is a term of the AJMS context (JSON-LD check, section 7).

Warnings (for example an unknown hours basis) do not affect conformance. The reference implementation checks all three: `ajms validate --jsonld <file>`.

A **consumer** (agent, tool, matcher) conforms if it:

- treats an absent field as UNKNOWN and MUST NOT treat it as zero, "no" or a failed requirement;
- keeps NOT_APPLICABLE and NOT_DISCLOSED distinct from UNKNOWN in what it reports;
- MUST NOT merge Hiring-Fit and Career-Fit into one number without also reporting both separately;
- MUST NOT apply weights to hard conditions (`hardCondition`, `REQUIRED`);
- MUST NOT convert currencies, distance into travel time, or units without stating the assumption in its output.

## 4. Information model rules

1. **Unknown is absence.** Optional fields that are not known are omitted. `null` is not used.
2. **Explicit absence.** A criterion block in `jobPreferences` or `offer` MAY be replaced by `{"state": "NOT_APPLICABLE"}` or `{"state": "NOT_DISCLOSED"}`.
3. **Provenance.** Capabilities, qualifications, experience entries and domain facts SHOULD carry `provenance.basis`. `DOCUMENT_EVIDENCED` and `THIRD_PARTY_CONFIRMED` MUST reference at least one `evidence` item.
4. **Hard vs. wish.** Each candidate preference block states `hardCondition` and/or `wish`. A job outside a `hardCondition` is not acceptable to the candidate; a `wish` is desirable only.
5. **No weights in profiles.** Weights belong to a `MatchPolicy` per perspective and MUST state `calibrationStatus`.
6. **Units.** Every quantity carries its unit or a unit-bearing property name (`weeklyHours`, `months`, `percent`). Compensation carries currency, period, component and gross/net; shares carry a reference period; distance and travel time are separate quantities with UN/CEFACT unit codes.
7. **Text and language.** Free text is `{"text": …, "language": <BCP 47>}`. A translation never replaces the original.
8. **Candidate wishes are not vacancies.** A CandidateProfile MUST NOT be published as, or converted into, a schema.org `JobPosting`.

## 5. Views of a candidate profile

| `profileView` | Purpose | Constraints (schema and semantic checks) |
|---|---|---|
| `FULL_PRIVATE` | the owner's complete profile | none beyond the schema; MUST NOT be announced as publicly retrievable |
| `SHARED_VIEW` | a selection for a named recipient | MAY contain `identity` if the candidate decides to disclose it |
| `PUBLIC_MINIMAL` | optional coarse public representation | MUST NOT contain `identity`, `experienceHistory`, `evidence`, postal codes; coordinates MUST have `precisionKm ≥ 10` |

Derived views SHOULD use a different `profileId` from the private profile. The reference implementation derives views deterministically (`ajms derive-view`). See [privacy-and-exchange.md](privacy-and-exchange.md) for why this reduces disclosure but does not achieve anonymity.

## 6. Semantic rules (beyond JSON Schema)

| Rule | Severity |
|---|---|
| `min` ≤ `max` in every range | error |
| `earliestStartDate` ≤ `latestStartDate`; `startMonth` ≤ `endMonth`; `datePosted` ≤ `validThrough` | error |
| an `ongoing` experience entry has no `endMonth` | error |
| identifiers (`competencyId`, `taskId`, `evidenceId`, …) unique within their list | error |
| `evidenceRefs` resolve to `evidence[].evidenceId` when `evidence` is present | error |
| `evidenceRefs` while the view carries no `evidence` | warning |
| compensation without `hoursPerWeekBasis` (period other than `HOUR`) | warning |
| PUBLIC_MINIMAL: no postal code, geo precision ≥ 10 km | error |

## 7. JSON-LD semantics

The JSON-LD context maps every AJMS key to an IRI. The mapping is in [schema-org-mapping.md](schema-org-mapping.md):

- schema.org terms are used where the AJMS value has the type schema.org expects (e.g. `title` → `schema:title`, `updatedAt` → `schema:dateModified`, `currency` → `schema:currency`);
- `text`/`language` are aliases of `@value`/`@language`, so a Text object becomes a language-tagged literal;
- all other terms are in the `ajms:` namespace.

JSON Schema validation and JSON-LD processing are **separate checks**. Schema validity does not imply that a JSON-LD processor keeps every key (it silently drops undefined terms). The reference implementation checks that every key is a defined term and that the document converts to RDF without errors.

## 8. Human-readable rendering

A conforming renderer SHOULD be deterministic (same input, same output), show every core criterion, and show absent values as "unknown". The reference renderer produces Markdown in English and German without any language model. A renderer MAY add generated prose, but such prose MUST be marked as generated and MUST NOT add facts that are not in the profile.

## 9. Exchange convention

The minimal exchange object is a **ProfileReference**: `profileId`, `profileType`, `schemaVersion`, `updatedAt`, `profileView`, `profileUrl`, `accessMethod`, optional `contentDigest`, `expiresAt`, `accessRequestUrl`. Details are in [privacy-and-exchange.md](privacy-and-exchange.md).

## 10. Versioning

- `schemaVersion` follows semantic versioning. v0.x releases MAY contain breaking changes between minor versions.
- Published schema files are immutable: a change produces a new schema line (`schemas/v0.2/`) and a new tag.
- Enumerations MAY grow in minor versions. Consumers SHOULD treat unknown enumeration values as UNKNOWN, not as errors, when processing documents of a newer minor version.
- Domain criterion identifiers are owned by their definers and never change meaning.
