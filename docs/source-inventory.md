# Source inventory: candidate and job formats

Inventory of the input material reviewed on 2026-10-27. The material itself is **not** part of this repository. Several items contain personal data. This document records only fields, formats and observations, no personal content.

**Coverage is incomplete.** Only the listed sources were reviewed. Large job boards and agencies that are not listed (for example Indeed, Monster, Hays, Randstad, Manpower, company ATS portals) were not examined. Where a form was only partly visible, this is marked.

## 1. Inventory

| # | Source | Kind of material | Side | Observed fields | Mandatory fields | Formats and units | Accessibility / caveats |
|---|---|---|---|---|---|---|---|
| 1 | Staffing agency (Adecco) profile completion dialog | 2 screenshots | candidate | country of residence, federal state, sector, sub-sector, current employer (free text, max. 255 characters), reCAPTCHA | not marked in the dialog | dropdowns (state depends on country, sub-sector on sector) | only a completion dialog is visible; the full registration form was **not accessible** |
| 2 | Employer job description template (internal template of an industrial employer, one procurement role) | PDF | job | version/owner/approver; business job title, job code, job family and family group; division; scope (global / regional / country); reporting line (direct, functional); direct/indirect reports; location; job purpose (free text); scope figures (spend per country and category); key responsibilities (max. 6 areas with core activities); education (level + field); working experience (range in years + domain); management experience (range in years); licence/certification; languages with proficiency; technical skills (free text) | template, no mandatory marking | checkboxes, free text, year ranges (e.g. "3–8 years") | internal document, therefore only described structurally here; **no salary, working time, remote or contract fields**; only the first pages were reviewed in detail |
| 3 | Recruitment consultancy registration form (SKILLs HR Business Experts, Zoho Recruit) | screenshot + note | candidate | last name, salutation + first name, e-mail, mobile (country code), **current salary (€)**, **expected salary (€)**, additional information (free text), attachments: CV, cover letter, other, photo; captcha | last name, CV, captcha | currency symbol only: **no period, no gross/net, no component, no hours basis** | the note "Idee Anschreiben und Sonstiges" suggests using cover letter / "other" as carrier for target direction and preferences, i.e. a machine-readable counterpart to the cover letter → realised as `jobPreferences` |
| 4 | Platforms for job-seeker ads | empty folder | — | — | — | — | **no material** |
| 5 | LinkedIn profiles | 4 PDF exports of profiles of individuals (image-based) + 3 screenshots | candidate | headline, location, "open to work" (job titles, location, on-site/hybrid/remote; visible to recruiters only), about, experience (title, company, employment type, period, duration, location, work mode), education, skills with endorsements, activity, analytics | not visible | free text, date ranges as month/year | PDF exports are images (no text layer); the content of the "open to work" preferences was **not fully visible**; no salary field visible |
| 6 | XING profile | PDF export (image-based) | candidate | completeness checklist (work location, photo, languages, field of study, min. 5 skills); "job wishes" (visible to recruiters, 6 of 9 filled, job search status); documents with visibility control (CV "not visible to recruiters"); skills and knowledge (tags); career history | not visible | tags, free text | the **nine job-wish fields themselves were not visible** in the export → unverified; suggested jobs show annual salary ranges with "Vollzeit" |
| 7 | Research paper "Benchmark Research: Recruiter-Search- und Ranking-Logik bei LinkedIn und XING" (JobMatchMe, v0.1 working draft, 2026-10-20) | PDF, 28 pages | both | reference pipeline: hard filter → query understanding → retrieval → ranking → personalisation | — | — | internal working draft; its claims were **not re-verified** here; relevant finding for AJMS: hard filters decide before any ranking, so hard conditions must be explicit |
| 8 | Bundesagentur für Arbeit candidate profile ("Bewerberprofil") | PDF export (font encoding broken, read visually) | candidate | reference number; profile title (occupation); alternative occupations; ad text; **desired work locations, each with a radius in km**; start ("sofort" or date); school leaving certificate; experience yes/no; profile type (job); working time (full-time); experience entries (period, occupation, description); education (period, degree, focus); skills grouped by BA domains with three levels (basic / advanced / expert); languages by level; personal strengths; further training and certificates with validity dates; driving licences; vehicle; contact via the employment agency; other details (sex, age) | not visible in the export | BA occupation taxonomy (note in INPUT: "die BA hat eine eigene Berufstaxonomie", i.e. KldB 2010); radius in km per location | the export is labelled as anonymised (contact via the agency), yet it still lists sex, age, exact periods and employer-specific descriptions; **removing the name does not make a profile anonymous** |
| 9 | stellenmarkt.de job-seeker ad | screenshot | candidate | free text sections "Ich suche" / "Ich biete", contact button | — | free text only | no structured fields observed |
| 10 | Stepstone profile and dashboard | 4 screenshots | both | profile: name, current job title, e-mail, location, phone, status flags "open to offers" and "actively seeking"; tabs "Das suche ich", "Das kann ich", "Meine Unterlagen"; CV upload; salary planner (industry average gross per year with min/max for a job title + location); visibility analytics (search appearances, recruiter keywords and locations); job cards: title, company, location, "Homeoffice möglich", full/part-time, "Feste Anstellung", expiry date, match label | not visible | CV formats pdf, doc, docx, odt, jpg, jpeg, png, xls, xlsx, ods, txt, rtf; 8 KB–6 MB; salary as €/year gross | **content of "Das suche ich" / "Das kann ich" not captured** → unverified; "Homeoffice möglich" carries no extent |
| 11 | Concept drafts "11_Google schema org" | 8 Markdown + 3 Word files | both | see [prior-work-and-deviations.md](prior-work-and-deviations.md) | — | — | AI-generated working material and copies of third-party web pages; **not** an official Google specification |

## 2. Criterion coverage across sources

Legend: **S** structured field · **T** free text only · **–** not observed · **?** not accessible / not visible

| Criterion | BA | XING | LinkedIn | Stepstone | SKILLs form | Adecco | Employer JD template | schema.org JobPosting | JSON Resume | **AJMS** |
|---|---|---|---|---|---|---|---|---|---|---|
| Compensation | – | ? (shown on jobs) | – | S (salary planner, €/year gross) | S (€, no period/gross) | – | – | S (`baseSalary`, `unitText`) | – | S (component, currency, period, gross/net, hours basis) |
| Industry / company | – | ? | S (company) | S (company) | – | S (sector, sub-sector) | S (division) | S (`industry`, `hiringOrganization`) | S (work.name) | S |
| Job archetype / occupation | S (BA taxonomy) | T | T | T | – | – | S (job family) | S (`occupationalCategory`) | T (position) | S (archetype + codes) |
| Career level | – | ? | – | – | – | – | T | – | – | S (ordered scale + leadership) |
| Tasks | T | T | T | – | – | – | S (responsibility areas) | T (`responsibilities`) | T (highlights) | S (tasks with share of time) |
| Skills / experience / qualifications | S (3 levels) | S (tags) | S (skills) | ? | – | – | S (ranges) | T/S (`skills`, `experienceRequirements`, `educationRequirements`) | S | S (proficiency, months, EQF, CEFR, provenance) |
| Location and commute | S (radius km per location) | S (work location) | S (location) | S (location) | – | S (country, state) | S (location) | S (`jobLocation`) | S (location) | S (distance **and** time, measured how) |
| Remote share | – | ? | S (on-site/hybrid/remote) | T ("Homeoffice möglich") | – | – | – | S (`TELECOMMUTE` only) | – | S (percent + reference period, on-site days) |
| Working time | S (full-time) | ? | S (employment type) | S (full/part-time) | – | – | – | S (`employmentType`, `workHours` text) | – | S (schedule, hours/week) |
| Contract / fixed term | – | ? | S (employment type) | S ("Feste Anstellung") | – | – | – | S (`employmentType`) | – | S (contract type, months) |
| Development | – | ? | – | – | – | – | – | – | – | S (paths, training days) |
| Start / availability | S (sofort / date) | ? | – | – | – | – | – | S (`jobStartDate`) | – | S (earliest/latest, notice period) |
| Domain-specific | S (licences, vehicle) | – | – | – | – | – | – | – | – | S (typed extensions) |
| Evidence / verification | S (certificate validity) | – | S (endorsements) | – | S (attachments) | – | – | – | – | S (evidence + provenance) |
| Hard condition vs. wish | – | ? | – | – | – | – | – | – | – | S |

## 3. Observations that shaped the model

1. **Salary fields are ambiguous in practice.** One form asks for a euro amount without period, gross/net or component. A portal's salary planner shows gross per year, while job cards in another portal show annual ranges. AJMS therefore requires currency, period, component and gross/net for every compensation figure, and records the hours basis.
2. **"Home office possible" and "hybrid" carry no extent.** AJMS keeps the arrangement and the share apart, and an unstated share remains UNKNOWN.
3. **Commute is given as distance (radius in km) by the employment agency.** Travel time is a different quantity. AJMS models both and never derives one from the other.
4. **Preferences are the least structured part everywhere.** They are mostly free text ("Ich suche"), or hidden or not exported. This is the main gap AJMS addresses.
5. **Removing the name is not anonymisation** (see item 8).
6. **Hard filters come first** in recruiter search (item 7). AJMS makes hard conditions explicit on both sides instead of hiding them in free text.
