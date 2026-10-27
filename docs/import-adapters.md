# Import adapters

AJMS converts third-party candidate and job formats into its shared format. A search agent can then use CandidateProfile and JobProfile as its **internal standard format**, whatever the source.

- An **import adapter** processes source data that has been **provided** to it: a file, an export, pasted text.
- **Retrieving** data from platforms (crawling, logging in, APIs) is a separate function. It is not part of AJMS and not part of these adapters.

## Supported input formats (v0.1)

This is the complete list. Anything else is not supported.

| `--format` | Concrete input | Input kind | Result | Check before conversion | Reference case |
|---|---|---|---|---|---|
| `ba-bewerberprofil-text` | Bundesagentur für Arbeit candidate profile ("Ihr Bewerberprofil") as text: the profile table copied as text, one row per line, label and value separated by a tab or ≥ 2 spaces, continuation rows indented (layout `ba-text-1`). A PDF is accepted if `pdftotext` (poppler) is installed and the PDF has a usable text layer. | TEXT | CandidateProfile | extraction-quality gate | BA export from the project input |
| `linkedin-data-export-csv` | Directory with the CSV files of a LinkedIn data export: `Profile.csv`, `Positions.csv`, `Education.csv`, `Skills.csv`, `Languages.csv`, `Certifications.csv` (each optional). Expected columns: see [`linkedin_csv.py`](../src/ajms/adapters/linkedin_csv.py). | STRUCTURED | CandidateProfile | header check | LinkedIn profiles from the project input (see below) |
| `json-resume-1` | JSON Resume document (schema v1.x) | STRUCTURED | CandidateProfile | shape check (JSON object, section types) | open candidate format |
| `job-ad-text-de` | German job ad as plain text: title, "<organisation> · Standort: <city>", bullet lists under "Ihre Aufgaben" / "Ihr Profil" / "Wir bieten" (layout `job-ad-de-1`) | TEXT | JobProfile | extraction-quality gate | synthetic job ad |

**Not supported in v0.1:**
- LinkedIn profile PDFs ("Save to PDF" or printed pages), and LinkedIn's job-preference data ("Open to work").
- XING profiles.
- Stepstone profiles.
- Forms of staffing agencies and recruitment consultancies.
- HR Open Standards (HR-JSON / HR-XML).
- Job ads in other layouts or languages, HTML pages, schema.org `JobPosting` markup as input.
- Scanned PDFs (they need OCR).

## Pipeline

Every adapter follows the same path. The conversion report (`ajms convert … --report`) shows each stage:

1. **Source data.** The original content is kept unchanged in the report. The profile keeps the source reference:
   - `source.sourceUrl`, or `urn:sha256:<digest>` when the data was a file without a URL;
   - `sourceFileName`, `sourceRecordId` (e.g. the BA reference number);
   - `retrievedAt`, `sourceFormat`, `inputKind`;
   - `textDigest`: SHA-256 of the original text, or over several files as `name\n` + content in name order.
2. **Input check.**
   - STRUCTURED inputs: a header or shape check. Structured fields are mapped directly.
   - TEXT inputs: an extraction-quality gate (below). Values extracted from text are only as good as the extraction, so they are checked before use.
3. **Field mapping.** Every target field gets a `fieldStatements` entry with:
   - its JSON Pointer;
   - `EXPLICIT` (stated verbatim), `NORMALIZED` (stated, converted into AJMS units, codes or enumerations) or `DERIVED` (not stated, inferred by a named rule);
   - the `sourceExcerpt` and the `method`;
   - `lossy: true` plus a note when meaning is lost.
4. **Conversion.**
   - Missing information stays absent, which means UNKNOWN. The report lists the unknown core fields.
   - Content without a place in AJMS goes to `source.unmapped`, with field name and reason only, **never the value**.
   - Reasons: `NO_AJMS_FIELD`, `PROTECTED_CHARACTERISTIC_NOT_MAPPED` (sex, age, birth date, photo), `DATA_MINIMISATION`, `INTERMEDIARY_CONTACT`, `AMBIGUOUS`, `REDUNDANT`, `MISSING_REQUIRED_DETAIL`, `NOT_INTERPRETED`.
5. **AJMS validation.** JSON Schema, semantic rules (every `fieldStatements` pointer must resolve) and the JSON-LD check.
6. **Human-readable output.** The deterministic Markdown rendering of the result.

Imported profiles are `FULL_PRIVATE` working copies with `provenance.basis = DERIVED` (jobs). A shared view derived from them drops `source` and `fieldStatements`. An imported job profile is never exported as schema.org `JobPosting`: republishing someone else's vacancy as markup is the publisher's decision, not the agent's.

## Extraction-quality gate (text inputs)

| Check | Rejects when | Why |
|---|---|---|
| token count | fewer than 30 tokens | the document has no text layer (scan, image-based PDF) |
| readable word share | fewer than 60 % of tokens look like words | broken font encoding in the PDF text layer |
| layout anchors | expected headings missing (BA: "Ihr Bewerberprofil", "Überblick über das Bewerberprofil") | not the expected format |
| excerpts verbatim | a `sourceExcerpt` does not occur in the input | adapter defect |

A rejected input produces **no profile**; the CLI exits with code 2 and lists the reasons. An accepted input gets `extractionQuality.status`:
- `PASSED`: every non-empty line was interpreted.
- `REVIEW`: some lines were not interpreted. They are listed as `NOT_INTERPRETED`, with their line number, and are not guessed.

`recognizedShare` gives the share of interpreted lines.

## Results on the project's reference cases (2026-10-27)

The original input files contain personal data. They were processed **locally only** and are not part of this repository; only the results are recorded here.

| Reference case | Result |
|---|---|
| BA candidate profile, original PDF export | **rejected**: the PDF text layer has a broken font encoding (9 % readable tokens). The visible content can only be used after OCR or manual transcription. |
| Same BA profile, transcribed into the `ba-text-1` layout | **PASSED**: 100 % of lines interpreted, valid profile. Mapped: 15 competencies, 5 languages, 3 qualifications, 2 experience entries; 101 field statements, 33 of them lossy. Sex and age are not mapped. This case revealed three gaps that are now covered and included in the synthetic fixture: multi-line descriptions, a dated school-certificate row, a certificate listed twice. |
| 4 LinkedIn profile PDFs (printed profile pages) | **rejected**: no text layer (6–17 tokens) |
| XING profile PDF | **rejected**: broken text layer (11 % readable tokens); XING is not supported |

The committed examples are **synthetic** and reproduce the structure of these reference cases:
- [`ba-bewerberprofil-text/`](../examples/adapters/ba-bewerberprofil-text/) contains, on purpose, one row the adapter does not know, so the REVIEW path is tested.
- [`linkedin-data-export-csv/`](../examples/adapters/linkedin-data-export-csv/)
- [`json-resume-1/`](../examples/adapters/json-resume-1/)
- [`job-ad-text-de/`](../examples/adapters/job-ad-text-de/)

Each folder has the input, the converted profile and the conversion report.

## Known losses of meaning (documented per field as `lossy`)

| Source | Loss |
|---|---|
| BA skill levels (3) → AJMS proficiency (4) | coarser source scale; the BA skill domain is not carried |
| BA language levels ("Verhandlungssicher", "Grundkenntnisse") → CEFR | no official equivalence |
| BA "Umkreis n km" → straight-line distance | BA does not state how the radius is measured; further desired locations lose their radius |
| BA, LinkedIn dates → months | day of month dropped |
| LinkedIn proficiency → CEFR | no official equivalence |
| LinkedIn position description → one task | structure of the description lost |
| LinkedIn certificate expiry (month) → date | mapped to the last day of the month |
| German proficiency words in job ads ("sehr gute") → AJMS levels | wording is not a defined scale |

## Assumptions to verify

- **LinkedIn columns.** The expected LinkedIn CSV columns reflect exports as commonly observed. LinkedIn publishes no stable schema, and the columns were **not checked against a current export**. The header check rejects deviating files instead of guessing.
- **JSON Resume.** Documents are not validated against the official JSON Resume schema.
- **BA layout `ba-text-1`.** Derived from the PDF export of the BA portal; other BA export variants were not available.

## Usage

```bash
ajms convert --format ba-bewerberprofil-text examples/adapters/ba-bewerberprofil-text/synthetic-demand-planner.ba.txt \
             --retrieved-at 2026-10-27T11:00:00+01:00 --report --lang de
ajms convert --format linkedin-data-export-csv examples/adapters/linkedin-data-export-csv/export \
             --retrieved-at 2026-10-27T11:05:00+01:00 > candidate.json
ajms convert --format job-ad-text-de examples/adapters/job-ad-text-de/senior-demand-planner.ad.de.txt \
             --retrieved-at 2026-10-27T10:15:00+01:00 --source-url https://jobs.example.com/ads/senior-demand-planner-4711 \
             --report --candidate examples/valid/candidate-supply-chain-analyst.shared-view.json
```

## Writing a new adapter

Use [`adapters/base.py`](../src/ajms/adapters/base.py):
- `Recorder.say()` for every target field, and `Recorder.skip()` for content without a target;
- `text_quality()` for text inputs;
- `finish()` to attach `source` and `fieldStatements`.

Add a synthetic fixture, the generated profile and report (`ADAPTER_EXAMPLES` in `cli.py`), and tests. A new adapter must never store the values of unmapped fields and must never turn a missing value into a default.
