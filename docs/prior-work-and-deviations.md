# Prior work, adopted elements and deviations

AJMS v0.1 builds on three bodies of earlier work. None of them is published with this repository.

## 1. MyCareerAgent / L4 Open Reciprocal Matching (schema package v0.2.1)

The earlier package defines `CandidateProfile`, `JobProfile`, `MatchPolicy`, `CriterionAssessment` and `MatchAssessment` (JSON Schema 2020-12, snake_case).

| Element in v0.2.1 | AJMS v0.1 | Reason for the deviation |
|---|---|---|
| `CandidateProfile` contains only facts (skills, experience, education, languages, certifications); minimum salary, exclusions and weights sit in a private `MatchPolicy` | **Adopted in part:** weights stay in `MatchPolicy`. **Changed:** hard conditions and wishes (`jobPreferences`) are part of the CandidateProfile | AJMS is meant to be shared selectively with agencies and employers, and a recipient needs to know the candidate's conditions. Weights remain private and separate. |
| `CompensationEntry`: one figure per basis; estimates must be intervals; `OBSERVED`/`ESTIMATED`; `full_time_equivalent` | **Adopted:** one figure per component, intervals for estimates, `informationKind`. **Changed:** `hoursPerWeekBasis` (explicit hours) instead of an FTE fraction; `paymentsPerYear` added; source kind moved to `provenance` | An FTE fraction needs a reference full-time value, which differs by employer. Hours are unambiguous. |
| `FieldAvailability`: `AVAILABLE`, `MISSING`, `UNPARSABLE`, `CONFLICTING` per field | **Changed:** absence = UNKNOWN; explicit `NOT_APPLICABLE` / `NOT_DISCLOSED` | `UNPARSABLE` and `CONFLICTING` describe an extraction pipeline, not a profile a person maintains. How to carry them is an open question. |
| `CriterionStatus`: `PASS`, `FAIL`, `UNKNOWN` | **Extended:** `MET`, `PARTIALLY_MET`, `NOT_MET`, `UNKNOWN`, `NOT_APPLICABLE` | Ranges that straddle a threshold, and criteria that do not apply, needed their own states. |
| `CriterionEffect` (`EXCLUSION`, `RANKING`, `INFORMATION_ONLY`) and `MissingInformationPolicy` | **Changed:** `hardCondition`/`wish` and `REQUIRED`/`PREFERRED` in the profiles; the missing-information rule is fixed (UNKNOWN never fails) | Simpler for profile authors. A configurable missing-information policy is on the roadmap. |
| `SeniorityLevel` (7 levels, `MID`) | **Changed:** 8 levels (`PROFESSIONAL` instead of `MID`, `HEAD` added) plus a separate `Leadership` object | Expert and leadership careers diverge; "head of" was missing. |
| `EmploymentType` mixes schedule and contract (`FULL_TIME`, `CONTRACT`, `TEMPORARY`, …) | **Split** into `Schedule` and `ContractType` | Full-time and fixed-term are independent dimensions. |
| `WorkArrangement` `ONSITE`/`HYBRID`/`REMOTE` | **Adopted**, plus remote share with reference period | |
| `TextValue` with language and derived-translation flag | **Adopted in simplified form** (`text` + `language`) | Translation handling is left to renderers. |
| snake_case keys | **Changed** to camelCase | Alignment with schema.org/JSON-LD terms. |
| Principle "silence is not evidence" (a missing value never becomes zero) | **Adopted** as a conformance rule | |

## 2. MyCareerAgent success-factor work (28_C)

- The **job evaluation factors** (profile prof-v0.3: F1 industry fit … F9 remote share, F10 unused) are the basis of the shared success factors. See [success-factors.md](success-factors.md).
- Adopted decisions: "hybrid" without extent is UNKNOWN; no blanket distance exclusion; remote share is a separate factor; weekly commuting load depends on distance **and** on-site days; a skill missing from the profile is not evidence that the candidate lacks it.
- **Deviation:** in 28_C, "Careerfit" (F4) means the career direction only and explicitly excludes location, distance, presence and salary (rule K-8). In AJMS, **Career-Fit** is the whole candidate perspective: all conditions and wishes, including compensation and location. 28_C's F4 corresponds to the AJMS groups `archetypes`, `careerLevel`, `tasks` and `development`.
- The **system success factors SF-v1.0** (F00–F15) compare career-agent *systems*, not jobs. They are not a job criteria model. Some of them are carried over as design principles: F00 (reliable, evidenced data base, statement classes) → `provenance`, `evidence`; F05 (separate partial judgements, unknown shown as unknown) → separate Hiring-Fit / Career-Fit, visible UNKNOWN; F12/F13 (control over disclosure, data sovereignty) → views and exchange convention.

## 3. Concept drafts "11_Google schema org" (AI-generated)

The folder contains AI-generated answers (Markdown) and copies of three third-party web pages (Word: Google Search Central JobPosting documentation, a job-board blog article, an SEO lexicon entry). They were treated as working material. Every technical claim was either checked against an official source or not used.

| Draft proposal | Decision | Reason |
|---|---|---|
| Problem framing: no schema.org counterpart to `JobPosting` for candidates; privacy is the main obstacle | **Adopted** as motivation | consistent with schema.org (no candidate/resume type) and Google's guidelines (resume collection only for open positions) |
| "Data to code" / edge matching: job profiles travel to the candidate's agent, the private profile stays local | **Adopted as a deployment option**, not mandated | AJMS makes it possible (public JobProfiles, private CandidateProfiles); it does not prescribe where matching runs |
| Double opt-in before identity disclosure | **Adopted as a recommended process** ([privacy-and-exchange.md](privacy-and-exchange.md)), without cryptography | |
| Profile wrapped in a W3C `VerifiableCredential` with a DID issuer | **Not adopted for the core.** Listed as an optional future extension | a mandatory credential envelope adds key management without solving the matching problem; most issuers do not yet issue such credentials |
| `"@context": ["https://schema.org", "https://github.io"]` | **Replaced** | `https://github.io` is a placeholder, not a context |
| `"$schema": "https://json-schema.org"`, `"$id": "https://githubusercontent.com"` | **Replaced** | not a valid Draft 2020-12 meta-schema reference and not a real schema ID; AJMS uses `https://json-schema.org/draft/2020-12/schema` and versioned IDs |
| Candidate preferences typed as `"@type": "JobPosting"` | **Rejected** | a wish is not an advertised job; Google disallows `JobPosting` markup on pages without a job |
| `zeroKnowledgeProofs` with strings like `zk-proof:sha256:0x…` | **Rejected** | placeholders, not proofs; a hash prefix is not a zero-knowledge proof |
| `encryptedPrivateData` with "AES-GCM-256" cipher text and `requiredKeyType: Ed25519VerificationKey2020` | **Rejected** | presents a placeholder as working security; Ed25519 is a signature key type and does not decrypt AES data; access control belongs to hosting/transport |
| `schema.org` extension proposal (`agentRequirements`, `zkRequirements`, `endpointPublicKey`) | **Not adopted** in v0.1 | AJMS defines its own namespace instead of proposing schema.org changes before there is any practical use |
| `matchingCapabilities` as `ItemList` of `PropertyValue` with free `propertyID`s | **Replaced** by typed fields | free keys cannot be validated or compared reliably |
| `maximumCommuteDistance` as schema.org `Distance` with `unitCode: KMT` | **Changed** | schema.org `Distance` is a text-valued quantity; AJMS uses value + UN/CEFACT `unitCode` + measurement method and adds travel time as a separate limit |
| `jobLocationType: HYBRID` | **Changed** | schema.org/Google know `TELECOMMUTE` only; AJMS uses its own `arrangement` plus a remote share with reference period |
| `contractType`: `UNLIMITED`, `LIMITED`, `FREELANCE`, `INTERNSHIP` | **Extended** | AJMS `ContractType` incl. temporary agency work, apprenticeship, working student |
| `customDomainVariables` with `minItems: 2`, `maxItems: 4` | **Changed** | AJMS allows 0..n domain criteria; a minimum forces invented criteria. Each criterion has a stable reverse-DNS identifier, data type, optional unit and comparator |
| `matchingRule: FUZZY_SEMANTIC` | **Not adopted** | non-deterministic and not reproducible; AJMS comparators are deterministic |
| Local semantic matching with `sentence-transformers` and `scikit-learn`, threshold 0.75, "50 % role + 50 % skills" | **Not adopted** | the demo needs no model, network or API key; embeddings are a possible future extension, and fixed weights would need calibration |
| LLM-generated human-readable exposé | **Replaced** by a deterministic renderer | an LLM may add prose but must not add facts; the reference renderer uses no model |
| "DSGVO-konform by design", "Recht auf Löschung obsolet", "100 % Datenhoheit", "resistent gegen Scraping … entfällt komplett" | **Rejected** | unverifiable absolute claims; a recipient can keep copies; AJMS makes no compliance promises |
| Statements on the EU AI Act timeline and on an AI vendor's usage policy | **Not used** | not verified in this work; AJMS does not rely on them |
| Reference to an "Agent Resume Standard" initiative | **Not used** | could not be verified |
