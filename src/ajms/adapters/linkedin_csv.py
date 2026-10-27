"""Adapter: LinkedIn data export (CSV files) -> CandidateProfile.

Input format `linkedin-data-export-csv`: the CSV files of a LinkedIn "copy of your data"
export, provided as a directory. Structured input: columns are mapped directly; no text
extraction. LinkedIn does not publish a stable schema for these files. The expected columns
below reflect exports as commonly observed and were **not verified against a current export**;
a file whose header lacks an expected column is rejected, extra columns are reported.
The export contains no job-search preferences in these files, so `jobPreferences` stays
UNKNOWN.
"""

from __future__ import annotations

import calendar
import csv
import io
import re
from pathlib import Path

from .base import COUNTRY_NAMES, ConversionRejected, Conversion, Recorder, finish, new_profile, place_from_city, slug, \
    text_value

FORMAT = "linkedin-data-export-csv"
RULES_VERSION = "linkedin-csv-1"

EXPECTED = {
    "Profile.csv": ["First Name", "Last Name", "Headline", "Summary", "Geo Location"],
    "Positions.csv": ["Company Name", "Title", "Description", "Location", "Started On", "Finished On"],
    "Education.csv": ["School Name", "Start Date", "End Date", "Notes", "Degree Name", "Activities"],
    "Skills.csv": ["Name"],
    "Languages.csv": ["Name", "Proficiency"],
    "Certifications.csv": ["Name", "Url", "Authority", "Started On", "Finished On", "License Number"],
}
NOT_IMPORTED = {
    "Connections.csv": ("DATA_MINIMISATION", "personal data of third parties; never imported"),
    "Messages.csv": ("DATA_MINIMISATION", "private communication; never imported"),
}
PROFILE_UNMAPPED = {
    "Maiden Name": ("DATA_MINIMISATION", None),
    "Address": ("DATA_MINIMISATION", "a full address is not needed for matching"),
    "Birth Date": ("PROTECTED_CHARACTERISTIC_NOT_MAPPED", "age is not represented in AJMS; value not stored"),
    "Industry": ("NO_AJMS_FIELD", "current industry without duration; experience by industry needs months"),
    "Zip Code": ("DATA_MINIMISATION", "postal code of the residence is not needed for matching"),
    "Twitter Handles": ("NO_AJMS_FIELD", None),
    "Websites": ("NO_AJMS_FIELD", None),
    "Instant Messengers": ("DATA_MINIMISATION", None),
}
LANGUAGES = {"german": "de", "english": "en", "french": "fr", "spanish": "es", "italian": "it", "dutch": "nl",
             "polish": "pl", "turkish": "tr", "hungarian": "hu", "russian": "ru"}
PROFICIENCY_TO_CEFR = {
    "Native or bilingual proficiency": ("NATIVE", False),
    "Full professional proficiency": ("C1", True),
    "Professional working proficiency": ("B2", True),
    "Limited working proficiency": ("B1", True),
    "Elementary proficiency": ("A2", True),
}
DEGREE_EQF = [("master", 7), ("bachelor", 6), ("doctor", 8), ("phd", 8)]
MONTHS = {name: f"{i:02d}" for i, name in enumerate(calendar.month_abbr) if name}


def _month(value: str) -> str | None:
    m = re.fullmatch(r"([A-Z][a-z]{2}) (\d{4})", value.strip())
    return f"{m.group(2)}-{MONTHS[m.group(1)]}" if m and m.group(1) in MONTHS else None


def read_export(directory: str | Path) -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8-sig") for p in sorted(Path(directory).glob("*.csv"))}


def convert(files: dict[str, str], *, retrieved_at: str, source_url: str | None = None,
            file_name: str | None = None) -> Conversion:
    rec = Recorder()
    rows: dict[str, list[dict]] = {}
    checks: list[str] = []
    problems: list[str] = []
    for name, content in sorted(files.items()):
        reader = csv.DictReader(io.StringIO(content))
        header = reader.fieldnames or []
        if name in EXPECTED:
            missing = [c for c in EXPECTED[name] if c not in header]
            if missing:
                problems.append(f"{name}: expected columns missing {missing}")
                continue
            rows[name] = list(reader)
            known = set(EXPECTED[name]) | (set(PROFILE_UNMAPPED) if name == "Profile.csv" else set())
            extra = [c for c in header if c not in known]
            for column in extra:
                rec.skip(f"{name}:{column}", "NOT_INTERPRETED", "column unknown to " + RULES_VERSION)
            checks.append(f"{name}: header has all expected columns, {len(rows[name])} rows"
                          + (f", {len(extra)} unknown columns" if extra else ""))
        elif name in NOT_IMPORTED:
            reason, note = NOT_IMPORTED[name]
            rec.skip(name, reason, note)
            checks.append(f"{name}: not imported ({reason})")
        else:
            rec.skip(name, "NOT_INTERPRETED", "file unknown to " + RULES_VERSION)
            checks.append(f"{name}: unknown file, not interpreted")
    if problems:
        raise ConversionRejected(FORMAT, problems)
    if not rows:
        raise ConversionRejected(FORMAT, ["none of the expected CSV files is present"])
    for name in EXPECTED:
        if name not in files:
            checks.append(f"{name}: not provided (its information stays unknown)")

    profile = new_profile("CandidateProfile", files, source_url, "en")
    caps: dict = {}

    def x(file: str, row: int, column: str) -> str:
        return rows[file][row][column].strip()

    if rows.get("Profile.csv"):
        prof = rows["Profile.csv"][0]
        first, last = prof["First Name"].strip(), prof["Last Name"].strip()
        identity: dict = {"displayName": f"{first} {last}".strip()}
        rec.say("/identity/displayName", "NORMALIZED", first, "join-first-and-last-name", "First Name and Last Name joined")
        geo = prof["Geo Location"].strip()
        if geo:
            parts = [p.strip() for p in geo.split(",")]
            city, country_name = parts[0], parts[-1]
            country = COUNTRY_NAMES.get(country_name.lower())
            residence = place_from_city(city, rec, "/identity/residence", city, country)
            if residence.get("countryCode"):
                residence["locality"] = city
                identity["residence"] = residence
                rec.say("/identity/residence/locality", "EXPLICIT", city)
                if country:
                    rec.say("/identity/residence/countryCode", "NORMALIZED", country_name, "country-name-to-iso3166")
            else:
                rec.skip("Profile.csv:Geo Location", "AMBIGUOUS", "country not recognized")
        profile["identity"] = identity
        if prof["Headline"].strip():
            profile["headline"] = text_value(prof["Headline"].strip(), "en")
            rec.say("/headline", "EXPLICIT", prof["Headline"].strip())
        if prof["Summary"].strip():
            profile["summary"] = text_value(prof["Summary"].strip(), "en")
            rec.say("/summary", "EXPLICIT", prof["Summary"].strip())
        for column, (reason, note) in PROFILE_UNMAPPED.items():
            if prof.get(column, "").strip():
                rec.skip(f"Profile.csv:{column}", reason, note)

    history = []
    for r, row in enumerate(rows.get("Positions.csv", [])):
        base = f"/experienceHistory/{len(history)}"
        entry: dict = {"experienceId": f"exp-{r + 1}", "roleTitle": text_value(x("Positions.csv", r, "Title"), "en")}
        rec.say(f"{base}/roleTitle", "EXPLICIT", entry["roleTitle"]["text"])
        if row["Company Name"].strip():
            entry["organization"] = {"name": row["Company Name"].strip()}
            rec.say(f"{base}/organization/name", "EXPLICIT", row["Company Name"].strip())
        start = _month(row["Started On"])
        if start is None:
            rec.skip(f"Positions.csv row {r + 1}", "MISSING_REQUIRED_DETAIL", "start month missing or not in 'Mon YYYY' form; entry skipped")
            history_skip = True
        else:
            history_skip = False
            entry["startMonth"] = start
            rec.say(f"{base}/startMonth", "NORMALIZED", row["Started On"].strip(), "linkedin-month-year")
        if row["Finished On"].strip():
            end = _month(row["Finished On"])
            if end:
                entry["endMonth"] = end
                rec.say(f"{base}/endMonth", "NORMALIZED", row["Finished On"].strip(), "linkedin-month-year")
        else:
            entry["ongoing"] = True
            rec.say(f"{base}/ongoing", "DERIVED", None, "empty-finished-on-means-current")
        if row["Description"].strip():
            entry["tasks"] = [{"taskId": "task-1", "label": text_value(row["Description"].strip(), "en")}]
            rec.say(f"{base}/tasks/0/label", "EXPLICIT", row["Description"].strip(),
                    note="the whole description becomes one task", lossy=True)
        if row["Location"].strip():
            rec.skip(f"Positions.csv row {r + 1}:Location", "NO_AJMS_FIELD", "experience entries have no location in AJMS v0.1")
        if history_skip:
            rec.statements = [s for s in rec.statements if not s["path"].startswith(base + "/")]
        else:
            history.append(entry)
    if history:
        profile["experienceHistory"] = history

    quals: list = []
    evidence: list = []
    for r, row in enumerate(rows.get("Education.csv", [])):
        degree = row["Degree Name"].strip()
        if not degree:
            rec.skip(f"Education.csv row {r + 1}", "MISSING_REQUIRED_DETAIL", "no degree name")
            continue
        base = f"/capabilities/qualifications/{len(quals)}"
        qual: dict = {"qualificationId": f"edu-{r + 1}", "qualificationType": "DEGREE", "label": text_value(degree, "en")}
        rec.say(f"{base}/label", "EXPLICIT", degree)
        rec.say(f"{base}/qualificationType", "DERIVED", None, "education-row-is-degree")
        if row["School Name"].strip():
            qual["issuerName"] = row["School Name"].strip()
            rec.say(f"{base}/issuerName", "EXPLICIT", qual["issuerName"])
        for keyword, level in DEGREE_EQF:
            if keyword in degree.lower():
                qual["eqfLevel"] = level
                rec.say(f"{base}/eqfLevel", "DERIVED", degree, "degree-keyword-to-eqf")
                break
        end = row["End Date"].strip()
        if end:
            month = _month(end)
            if month:
                qual["completedOn"] = month
                rec.say(f"{base}/completedOn", "NORMALIZED", end, "linkedin-month-year")
            else:
                rec.skip(f"Education.csv row {r + 1}:End Date", "MISSING_REQUIRED_DETAIL",
                         "year without month; completion month stays unknown")
        for column in ("Notes", "Activities"):
            if row[column].strip():
                rec.skip(f"Education.csv row {r + 1}:{column}", "NO_AJMS_FIELD", None)
        quals.append(qual)

    for r, row in enumerate(rows.get("Certifications.csv", [])):
        base = f"/capabilities/qualifications/{len(quals)}"
        qual = {"qualificationId": f"cert-{r + 1}", "qualificationType": "CERTIFICATION", "label": text_value(row["Name"].strip(), "en")}
        rec.say(f"{base}/label", "EXPLICIT", row["Name"].strip())
        rec.say(f"{base}/qualificationType", "DERIVED", None, "certification-row")
        if row["Authority"].strip():
            qual["issuerName"] = row["Authority"].strip()
            rec.say(f"{base}/issuerName", "EXPLICIT", qual["issuerName"])
        started = _month(row["Started On"])
        if started:
            qual["completedOn"] = started
            rec.say(f"{base}/completedOn", "NORMALIZED", row["Started On"].strip(), "linkedin-month-year",
                    "'Started On' read as issue month")
        finished = _month(row["Finished On"])
        if finished:
            year, month = map(int, finished.split("-"))
            qual["validUntil"] = f"{finished}-{calendar.monthrange(year, month)[1]:02d}"
            rec.say(f"{base}/validUntil", "DERIVED", row["Finished On"].strip(), "month-to-last-day",
                    "month-precision expiry mapped to the last day of that month", lossy=True)
        if row["Url"].strip():
            ev_id = f"ev-cert-{r + 1}"
            evidence.append({"evidenceId": ev_id, "evidenceKind": "CERTIFICATION", "label": text_value(row["Name"].strip(), "en"),
                             "documentUrl": row["Url"].strip(), "verificationStatus": "UNVERIFIED"})
            ebase = f"/evidence/{len(evidence) - 1}"
            rec.say(f"{ebase}/documentUrl", "EXPLICIT", row["Url"].strip())
            rec.say(f"{ebase}/verificationStatus", "DERIVED", None, "nothing-verified-on-import")
            qual["provenance"] = {"basis": "DOCUMENT_EVIDENCED", "evidenceRefs": [ev_id]}
            rec.say(f"{base}/provenance", "DERIVED", None, "certificate-url-is-evidence-reference")
        if row["License Number"].strip():
            rec.skip(f"Certifications.csv row {r + 1}:License Number", "DATA_MINIMISATION", None)
        quals.append(qual)
    if quals:
        caps["qualifications"] = quals
    if evidence:
        profile["evidence"] = evidence

    comps = []
    for r, row in enumerate(rows.get("Skills.csv", [])):
        name = row["Name"].strip()
        if not name:
            continue
        base = f"/capabilities/competencies/{len(comps)}"
        comps.append({"competencyId": slug(name), "label": text_value(name, "en")})
        rec.say(f"{base}/label", "EXPLICIT", name)
        rec.say(f"{base}/competencyId", "DERIVED", name, "slug-of-label")
    if comps:
        caps["competencies"] = comps

    langs = []
    for r, row in enumerate(rows.get("Languages.csv", [])):
        name, level = row["Name"].strip(), row["Proficiency"].strip()
        code = LANGUAGES.get(name.lower())
        if code is None:
            rec.skip(f"Languages.csv row {r + 1}", "AMBIGUOUS", "language name not recognized")
            continue
        if level not in PROFICIENCY_TO_CEFR:
            rec.skip(f"Languages.csv row {r + 1}:Proficiency", "MISSING_REQUIRED_DETAIL",
                     "no proficiency stated; AJMS requires a level, so the language is not mapped")
            continue
        cefr, lossy = PROFICIENCY_TO_CEFR[level]
        base = f"/capabilities/languages/{len(langs)}"
        langs.append({"languageCode": code, "cefrLevel": cefr})
        rec.say(f"{base}/languageCode", "NORMALIZED", name, "language-name-en-to-bcp47")
        rec.say(f"{base}/cefrLevel", "DERIVED", level, "linkedin-proficiency-to-cefr",
                f"no official equivalence between LinkedIn '{level}' and CEFR {cefr}" if lossy else None, lossy=lossy)
    if langs:
        caps["languages"] = langs
    if caps:
        profile["capabilities"] = caps

    quality = {"status": "PASSED" if not any(u["reason"] == "NOT_INTERPRETED" for u in rec.unmapped) else "REVIEW",
               "checks": checks}
    finish(profile, rec, files, source_url=source_url, retrieved_at=retrieved_at, source_kind="PLATFORM_EXPORT",
           source_format=FORMAT, input_kind="STRUCTURED", rules_version=RULES_VERSION, quality=quality, file_name=file_name)
    return Conversion(profile=profile, original=files)
