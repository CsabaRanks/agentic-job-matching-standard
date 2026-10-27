# Sources

Retrieval date for all online sources: **2026-10-27**. "Checked" means the page was retrieved and the cited content was read on that date. "Not inspected" means the source is named but its content was not verified.

## Official specifications and documentation

| Source | URL | Status | Used for |
|---|---|---|---|
| schema.org `JobPosting` (release V30.1, 2026-09-16) | https://schema.org/JobPosting | checked | property list and expected types; no property marked pending |
| schema.org `Person` | https://schema.org/Person | checked | `seeks`, `knowsAbout`, `knowsLanguage`, `hasCredential`, `hasOccupation`, `skills`, `homeLocation` |
| schema.org `Demand` | https://schema.org/Demand | checked | definition ("announcement … to seek … goods or services"); reason for not using `Person.seeks` for job search criteria |
| schema.org `Occupation` | https://schema.org/Occupation | checked | `occupationalCategory` (O*NET-SOC, ISCO-08), `estimatedSalary`, `experienceRequirements` |
| schema.org `OccupationalExperienceRequirements` | https://schema.org/OccupationalExperienceRequirements | checked | `monthsOfExperience` |
| schema.org `QuantitativeValue` | https://schema.org/QuantitativeValue | checked | `unitCode` = UN/CEFACT Common Code (3 characters) or URL; `minValue`, `maxValue` |
| Google Search Central: Job posting structured data | https://developers.google.com/search/docs/appearance/structured-data/job-posting | checked | required/recommended properties; `employmentType` values; `unitText` values; `TELECOMMUTE`; "Publishers may solicit resume collections for open positions only"; no `JobPosting` markup on pages without a job |
| JSON Schema Draft 2020-12 meta-schema | https://json-schema.org/draft/2020-12/schema | checked | `$schema` and `$id` are both `https://json-schema.org/draft/2020-12/schema` |
| JSON Resume schema (v1.7.0) | https://jsonresume.org/schema | checked | sections and fields; Draft-07; MIT licence |
| HR Open Standards: home page | https://www.hropenstandards.org/ | checked | lists HR-JSON / HR-XML, Trusted Career Profile, JEDx, Skills Proficiency Data API |
| HR Open Standards: downloads | https://www.hropenstandards.org/standards-downloads | checked | HR-JSON and HR-XML free to download subject to the HR Open IP agreement; work-in-progress repositories are members only |
| HR Open Recruiting workgroup slide deck (2019) | https://assets.noviams.com/novi-file-uploads/hropen/pdfs-and-documents/04_Recruiting_SM-dd7d0929.pdf | found via search, **not inspected** | names `Candidate` and `PositionOpening` as main recruiting schemas |
| HR-JSON Candidate / PositionOpening schema files | — | **not inspected** | no field-level comparison claimed |
| UN/CEFACT Recommendation 20 (unit codes `KMT`, `SMI`, `MIN`, `HUR`, `WEE`, `MON`) | https://unece.org/trade/uncefact/cl-recommendations | **not inspected in this session** | codes used as commonly published; to be verified |
| ISO 4217, ISO 3166-1, BCP 47, CEFR, EQF, ISCO-08, ESCO, NACE Rev. 2, KldB 2010 | — | referenced by name, **not inspected** | identifiers for codes and levels |
| W3C Verifiable Credentials, DIDs, DIDComm | — | referenced by name, **not inspected** | named as optional future extensions only |

## Project-internal material (not published)

These were read as input. They are **not** part of the repository. See [source-inventory.md](source-inventory.md) and [prior-work-and-deviations.md](prior-work-and-deviations.md).

| Material | Nature |
|---|---|
| `INPUT/11_Google schema org …` (8 Markdown files, 3 Word files) | AI-generated concept drafts and copies of third-party web pages; treated as working material, **not** as an official Google specification or reviewed documentation |
| `INPUT/1_…` to `INPUT/10_…` | screenshots and PDF exports of candidate and job forms (some contain personal data) |
| MyCareerAgent project 22_B3_L4 (schemas v0.2.1) | prior CandidateProfile, JobProfile, MatchPolicy definitions |
| MyCareerAgent project 28_C (Erfolgsfaktoren SF-v1.0, job evaluation factors prof-v0.3) | success-factor models |
