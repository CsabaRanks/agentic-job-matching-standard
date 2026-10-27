"""Adapter: Bundesagentur für Arbeit candidate profile ("Bewerberprofil") as text -> CandidateProfile.

Input format `ba-bewerberprofil-text` (layout ba-text-1): the profile table as text, one table
row per line, label and value separated by a tab or by two or more spaces, continuation rows
indented. This is what copying the profile table yields, and what `pdftotext -layout` yields
for a PDF export with an intact text layer. PDF exports with a broken text layer are rejected
by the extraction-quality gate.
"""

from __future__ import annotations

import re

from .base import (COUNTRY_NAMES, Conversion, Recorder, finish, new_profile, place_from_city, slug, text_quality,
                   text_value)

FORMAT = "ba-bewerberprofil-text"
RULES_VERSION = "ba-text-1"
ANCHORS = ["Ihr Bewerberprofil", "Überblick über das Bewerberprofil"]

SECTIONS = {
    "Überblick über das Bewerberprofil": "overview",
    "Anforderungen an die Stelle": "requirements",
    "Berufserfahrung": "experience",
    "Schul- und Berufsbildung": "education",
    "Persönliche Fähigkeiten und Kompetenzen": "skills",
    "Kontaktdaten und sonstige Angaben zur Bewerberin/ zum Bewerber": "contact",
}
SKILL_LEVELS = {"Grundkenntnisse": "BASIC", "Erweiterte Kenntnisse": "ADVANCED", "Expertenkenntnisse": "EXPERT"}
LANGUAGE_LEVELS = {"Muttersprache": ("NATIVE", False), "Verhandlungssicher": ("C1", True),
                   "Erweiterte Kenntnisse": ("B1", True), "Grundkenntnisse": ("A2", True)}
LANGUAGE_CODES = {"deutsch": "de", "englisch": "en", "französisch": "fr", "spanisch": "es", "italienisch": "it",
                  "niederländisch/flämisch": "nl", "niederländisch": "nl", "polnisch": "pl", "türkisch": "tr",
                  "ungarisch": "hu", "russisch": "ru"}
DEGREE_EQF = {"Master / Diplom / Magister": 7, "Bachelor": 6, "Promotion": 8}
WORKING_TIME = {"Vollzeit": "FULL_TIME", "Teilzeit": "PART_TIME"}
INTERMEDIARY_LABELS = ("Name", "Anschrift", "Telekommunikation")
SCHOOL_CERTIFICATE = re.compile(r"Hochschulreife|Fachhochschulreife|Realschulabschluss|Mittlere Reife|Hauptschulabschluss|Abitur")
DATE_RANGE = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})\s*-\s*(\d{2})\.(\d{2})\.(\d{4})$")
LOCATION = re.compile(r"^(?:(\d{5})\s+)?([^,]+),\s*([^,]+),\s*(.+?)\s+-\s+(Umkreis\s+(\d+)\s*km)$")


def _occupation_id(title: str) -> str:
    """Identifier of a BA occupation title without the gender suffix ('Planer/in' -> 'planer')."""
    return slug(re.sub(r"\s*\((?:m/w/d|w/m/d|m/f/d)\)|/(?:in|innen|frau|mann)\b", "", title))


def _split(line: str) -> tuple[str, str]:
    parts = re.split(r"\t+| {2,}", line.strip(), maxsplit=1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (parts[0].strip(), "")


def _ym(day: str, month: str, year: str) -> str:
    return f"{year}-{month}"


def convert(text: str, *, retrieved_at: str, source_url: str | None = None, file_name: str | None = None) -> Conversion:
    rec = Recorder()
    lines = text.splitlines()
    nonempty = [i for i, line in enumerate(lines) if line.strip()]
    recognized: set[int] = set()
    uninterpreted: list[str] = []
    excerpts: list[str] = []

    profile = new_profile("CandidateProfile", {"text": text}, source_url, "de")
    caps: dict = {}
    prefs: dict = {}
    history: list = []
    record_id = None

    def say(path, kind, excerpt=None, method=None, note=None, lossy=False):
        if excerpt is not None:
            excerpts.append(excerpt)
        rec.say(path, kind, excerpt, method, note, lossy)

    section = None
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        indented = raw[:1] in ("\t", " ")
        if not line:
            i += 1
            continue
        if line == "Bundesagentur für Arbeit" or line.startswith("Ihr Bewerberprofil"):
            recognized.add(i)
            i += 1
            continue
        if not indented and line in SECTIONS:
            section = SECTIONS[line]
            recognized.add(i)
            i += 1
            continue
        label, value = _split(raw)
        # Continuation rows that belong to the current label.
        block = [value] if value else []
        j = i + 1
        while j < len(lines) and lines[j][:1] in ("\t", " ") and lines[j].strip():
            block.append(lines[j].strip())
            j += 1

        def done(n=None):
            for k in range(i, j if n is None else n):
                recognized.add(k)

        if section == "overview" and label == "Referenznummer":
            record_id = value
            done()
        elif section == "overview" and label == "Titel des Bewerberprofils":
            wish = prefs.setdefault("archetypes", {}).setdefault("wish", {}).setdefault("include", [])
            base = f"/jobPreferences/archetypes/wish/include/{len(wish)}"
            wish.append({"archetypeId": _occupation_id(value), "label": text_value(value, "de")})
            say(f"{base}/label", "EXPLICIT", value, note="BA profile title = target occupation")
            say(f"{base}/archetypeId", "DERIVED", value, "slug-of-label-without-gender-suffix",
                "the BA occupation code (KldB) is not contained in the text", lossy=True)
            done()
        elif section == "overview" and label == "Alternativberufe":
            wish = prefs.setdefault("archetypes", {}).setdefault("wish", {}).setdefault("include", [])
            for item in block:
                for name in [x.strip() for x in item.split(",") if x.strip()]:
                    base = f"/jobPreferences/archetypes/wish/include/{len(wish)}"
                    wish.append({"archetypeId": _occupation_id(name), "label": text_value(name, "de")})
                    say(f"{base}/label", "EXPLICIT", name, note="BA alternative occupation")
                    say(f"{base}/archetypeId", "DERIVED", name, "slug-of-label-without-gender-suffix")
            done()
        elif section == "overview" and label == "Anzeigentext":
            profile["headline"] = text_value(value, "de")
            say("/headline", "EXPLICIT", value)
            done()
        elif section == "overview" and label == "Gewünschte Arbeitsorte":
            wish = prefs.setdefault("location", {}).setdefault("wish", {})
            for item in block:
                m = LOCATION.match(item)
                if not m:
                    uninterpreted.append(item)
                    continue
                postal, city, region, country_name, radius_text, radius = m.groups()
                country = COUNTRY_NAMES.get(country_name.lower())
                if "commute" not in wish:
                    base = "/jobPreferences/location/wish/commute/origin"
                    origin = place_from_city(city, rec, base, city, country)
                    origin.update({"countryCode": country or origin.get("countryCode"), "region": region, "locality": city})
                    if postal:
                        origin["postalCode"] = postal
                        say(f"{base}/postalCode", "EXPLICIT", postal)
                    say(f"{base}/countryCode", "NORMALIZED", country_name, "country-name-to-iso3166")
                    say(f"{base}/region", "EXPLICIT", region)
                    say(f"{base}/locality", "EXPLICIT", city)
                    wish["commute"] = {"origin": origin, "maxOneWayDistance": {"value": int(radius), "unitCode": "KMT", "measurement": "STRAIGHT_LINE"}}
                    say("/jobPreferences/location/wish/commute/maxOneWayDistance", "NORMALIZED", radius_text, "ba-radius-km",
                        "BA 'Umkreis' read as straight-line one-way distance; BA does not state how it is measured", lossy=True)
                else:
                    places = wish.setdefault("places", [])
                    base = f"/jobPreferences/location/wish/places/{len(places)}"
                    places.append({"countryCode": country, "region": region, "locality": city})
                    say(f"{base}/locality", "EXPLICIT", city,
                        note=f"radius '{radius_text}' dropped: an AJMS condition has one commute origin", lossy=True)
                    say(f"{base}/countryCode", "NORMALIZED", country_name, "country-name-to-iso3166")
                    say(f"{base}/region", "EXPLICIT", region)
            done()
        elif section == "overview" and label == "Beginn der Tätigkeit":
            if value == "Sofort":
                profile["availability"] = {"immediate": True}
                say("/availability/immediate", "NORMALIZED", value, "ba-start-sofort")
            else:
                d = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", value)
                if d:
                    profile["availability"] = {"earliestStartDate": f"{d.group(3)}-{d.group(2)}-{d.group(1)}"}
                    say("/availability/earliestStartDate", "NORMALIZED", value, "german-date")
                else:
                    uninterpreted.append(raw.strip())
            done()
        elif label == "Schulabschluss" and section in ("overview", "education"):
            quals = caps.setdefault("qualifications", [])
            if any(q["qualificationId"] == "school-leaving" for q in quals):
                heading = next(name for name, key in SECTIONS.items() if key == section)
                rec.skip(f"{heading}: Schulabschluss", "REDUNDANT", "same certificate listed twice in the BA export")
            else:
                base = f"/capabilities/qualifications/{len(quals)}"
                quals.append({"qualificationId": "school-leaving", "qualificationType": "OTHER", "label": text_value(value, "de")})
                say(f"{base}/label", "EXPLICIT", value)
                say(f"{base}/qualificationType", "DERIVED", value, "ba-school-certificate-type")
                if value.startswith("Allgemeine Hochschulreife"):
                    quals[-1]["eqfLevel"] = 4
                    say(f"{base}/eqfLevel", "DERIVED", "Allgemeine Hochschulreife", "dqr-eqf-table",
                        "German qualifications framework assigns the Abitur to level 4")
            done()
        elif section == "overview" and label == "Berufserfahrung":
            rec.skip("Überblick: Berufserfahrung", "REDUNDANT", "yes/no flag; the experience entries are mapped individually")
            done()
        elif section == "requirements" and label == "Bewerberprofilart":
            rec.skip("Anforderungen: Bewerberprofilart", "NO_AJMS_FIELD", "type of position sought (job, apprenticeship, ...)")
            done()
        elif section == "requirements" and label == "Arbeitszeit":
            schedules = []
            for name in [x.strip() for x in value.split(",") if x.strip()]:
                if name in WORKING_TIME:
                    schedules.append(WORKING_TIME[name])
            if schedules:
                prefs["workingTime"] = {"wish": {"schedules": {"include": schedules}}}
                say("/jobPreferences/workingTime/wish/schedules/include", "NORMALIZED", value, "ba-working-time",
                    "BA search criterion read as a wish, not a hard condition")
            else:
                uninterpreted.append(raw.strip())
            done()
        elif section in ("experience", "education") and DATE_RANGE.match(label):
            d = DATE_RANGE.match(label)
            start, end = _ym(*d.groups()[:3]), _ym(*d.groups()[3:])
            details = block[1:] if value else block
            if section == "experience":
                base = f"/experienceHistory/{len(history)}"
                entry = {"experienceId": f"exp-{len(history) + 1}", "roleTitle": text_value(value, "de"),
                         "startMonth": start, "endMonth": end}
                say(f"{base}/roleTitle", "EXPLICIT", value)
                say(f"{base}/startMonth", "NORMALIZED", label[:10], "german-date-to-month", "day of month dropped", lossy=True)
                say(f"{base}/endMonth", "NORMALIZED", label[-10:], "german-date-to-month", "day of month dropped", lossy=True)
                for detail in details:
                    desc = detail.split(":", 1)[1].strip() if detail.startswith("Beschreibung:") else detail
                    if not detail.startswith("Beschreibung:") and "tasks" not in entry:
                        uninterpreted.append(detail)
                        continue
                    tasks = entry.setdefault("tasks", [])
                    say(f"{base}/tasks/{len(tasks)}/label", "EXPLICIT", desc,
                        note="further description line" if tasks else None)
                    tasks.append({"taskId": f"task-{len(tasks) + 1}", "label": text_value(desc, "de")})
                history.append(entry)
            elif SCHOOL_CERTIFICATE.search(value):
                quals = caps.setdefault("qualifications", [])
                if any(q["qualificationId"] == "school-leaving" for q in quals):
                    rec.skip(f"Schul- und Berufsbildung: {value} ({label})", "REDUNDANT",
                             "dated school period of the school-leaving certificate already mapped")
                else:
                    uninterpreted.append(raw.strip())
            else:
                quals = caps.setdefault("qualifications", [])
                base = f"/capabilities/qualifications/{len(quals)}"
                qual = {"qualificationId": f"edu-{len(quals) + 1}", "qualificationType": "DEGREE",
                        "label": text_value(value, "de"), "completedOn": end}
                say(f"{base}/label", "EXPLICIT", value)
                say(f"{base}/completedOn", "NORMALIZED", label[-10:], "german-date-to-month", "day of month dropped", lossy=True)
                typed = False
                for detail in details:
                    if detail in DEGREE_EQF:
                        typed = True
                        qual["eqfLevel"] = DEGREE_EQF[detail]
                        say(f"{base}/eqfLevel", "NORMALIZED", detail, "ba-degree-category-to-eqf")
                        say(f"{base}/qualificationType", "NORMALIZED", detail, "ba-degree-category-to-eqf")
                    elif detail.startswith("Beschreibung/ Schwerpunkte:"):
                        rec.skip(f"Schul- und Berufsbildung: {value}: Schwerpunkte", "NO_AJMS_FIELD",
                                 "focus areas of a degree have no AJMS field")
                    else:
                        uninterpreted.append(detail)
                if not typed:
                    say(f"{base}/qualificationType", "DERIVED", value, "ba-education-entry-is-degree")
                quals.append(qual)
            done()
        elif section == "skills" and not indented and label not in ("Sprachkenntnisse", "Persönliche Stärken",
                                                                     "Weiterbildungen und Zertifikate", "Führerscheine",
                                                                     "Fahrzeug") and not value:
            # Skill domain heading followed by level lines and skill lists.
            domain = label
            comps = caps.setdefault("competencies", [])
            level = None
            for item in block:
                if item in SKILL_LEVELS:
                    level = item
                    continue
                for name in [x.strip() for x in item.split(",") if x.strip()]:
                    base = f"/capabilities/competencies/{len(comps)}"
                    entry = {"competencyId": slug(name), "label": text_value(name, "de")}
                    say(f"{base}/label", "EXPLICIT", name)
                    say(f"{base}/competencyId", "DERIVED", name, "slug-of-label")
                    if level:
                        entry["proficiency"] = SKILL_LEVELS[level]
                        say(f"{base}/proficiency", "NORMALIZED", level, "ba-skill-level",
                            f"BA uses three levels; mapped onto the four AJMS levels; BA skill domain '{domain}' not carried",
                            lossy=True)
                    comps.append(entry)
            done()
        elif section == "skills" and label == "Sprachkenntnisse":
            langs = caps.setdefault("languages", [])
            level = None
            for item in block:
                if item in LANGUAGE_LEVELS:
                    level = item
                    continue
                for name in [x.strip() for x in item.split(",") if x.strip()]:
                    code = LANGUAGE_CODES.get(name.lower())
                    if code is None or level is None:
                        uninterpreted.append(name)
                        continue
                    cefr, lossy = LANGUAGE_LEVELS[level]
                    base = f"/capabilities/languages/{len(langs)}"
                    langs.append({"languageCode": code, "cefrLevel": cefr})
                    say(f"{base}/languageCode", "NORMALIZED", name, "language-name-de-to-bcp47")
                    if lossy:
                        say(f"{base}/cefrLevel", "DERIVED", level, "ba-language-level-to-cefr",
                            f"no official equivalence between the BA level '{level}' and CEFR {cefr}", lossy=True)
                    else:
                        say(f"{base}/cefrLevel", "NORMALIZED", level, "ba-language-level-to-cefr")
            done()
        elif section == "skills" and label == "Persönliche Stärken":
            rec.skip("Persönliche Stärken", "NO_AJMS_FIELD", "self-described personal strengths are not mapped to competencies")
            done()
        elif section == "skills" and label == "Weiterbildungen und Zertifikate":
            quals = caps.setdefault("qualifications", [])
            pending: list[str] = []
            for item in block:
                validity = re.fullmatch(r"Gültig von (\d{2})\.(\d{2})\.(\d{4}) bis (\d{2})\.(\d{2})\.(\d{4})", item)
                if not validity:
                    pending.append(item)
                    continue
                if not pending:
                    uninterpreted.append(item)
                    continue
                name = pending[-1]
                d = validity.groups()
                if any(q["label"]["text"] == name and q.get("validUntil") == f"{d[5]}-{d[4]}-{d[3]}" for q in quals):
                    rec.skip(f"Weiterbildungen und Zertifikate: '{name}' (repeated)", "REDUNDANT",
                             "identical certificate listed more than once in the BA export")
                    pending = []
                    continue
                base = f"/capabilities/qualifications/{len(quals)}"
                quals.append({"qualificationId": f"cert-{len(quals) + 1}", "qualificationType": "CERTIFICATION",
                              "label": text_value(name, "de"), "completedOn": f"{d[2]}-{d[1]}",
                              "validUntil": f"{d[5]}-{d[4]}-{d[3]}"})
                say(f"{base}/label", "EXPLICIT", name)
                say(f"{base}/qualificationType", "DERIVED", label, "ba-further-training-is-certification")
                say(f"{base}/completedOn", "NORMALIZED", item[validity.start(1):validity.end(3)], "german-date-to-month",
                    "'valid from' read as completion month; day dropped", lossy=True)
                say(f"{base}/validUntil", "NORMALIZED", item[validity.start(4):validity.end(6)], "german-date")
                for short in pending[:-1]:
                    rec.skip(f"Weiterbildungen und Zertifikate: short title of '{name}'", "REDUNDANT",
                             "short title next to the full certificate name")
                pending = []
            uninterpreted.extend(pending)
            done()
        elif section == "skills" and label == "Führerscheine":
            classes = re.findall(r"Fahrerlaubnis ([A-Z0-9]{1,3})\b", value)
            if classes:
                crit = caps.setdefault("domainCriteria", [])
                base = f"/capabilities/domainCriteria/{len(crit)}"
                crit.append({"criterionId": "io.github.csabaranks.ajms.driving_licence_classes",
                             "label": text_value("Fahrerlaubnisklassen", "de"), "dataType": "CODE_LIST", "value": classes})
                say(f"{base}/value", "NORMALIZED", f"Fahrerlaubnis {classes[0]}", "ba-driving-licence",
                    "description of the class and old class designation not carried", lossy=True)
            else:
                uninterpreted.append(raw.strip())
            done()
        elif section == "skills" and label == "Fahrzeug":
            if value == "Fahrzeug vorhanden":
                crit = caps.setdefault("domainCriteria", [])
                base = f"/capabilities/domainCriteria/{len(crit)}"
                crit.append({"criterionId": "io.github.csabaranks.ajms.own_vehicle",
                             "label": text_value("Eigenes Fahrzeug", "de"), "dataType": "BOOLEAN", "value": True})
                say(f"{base}/value", "NORMALIZED", value, "ba-vehicle")
            else:
                uninterpreted.append(raw.strip())
            done()
        elif section == "contact" and label in INTERMEDIARY_LABELS:
            rec.skip(f"Kontaktdaten: {label}", "INTERMEDIARY_CONTACT",
                     "the BA profile is anonymised; contact runs via the employment agency")
            done()
        elif section == "contact" and label == "Sonstige Angaben zum Bewerber":
            rec.skip("Sonstige Angaben zum Bewerber", "PROTECTED_CHARACTERISTIC_NOT_MAPPED",
                     "sex and age are not represented in AJMS; values are not stored")
            done()
        else:
            uninterpreted.append(raw.strip())
            rec.skip(f"line {i + 1}", "NOT_INTERPRETED", f"row label '{label}' is unknown to {RULES_VERSION}")
            recognized.update(range(i + 1, j))  # continuation rows belong to the uninterpreted row
        i = j

    if caps:
        profile["capabilities"] = caps
    if history:
        profile["experienceHistory"] = history
    if prefs:
        profile["jobPreferences"] = prefs
    total = len(nonempty)
    count = max(0, total - len(uninterpreted))
    quality = text_quality(FORMAT, text, ANCHORS, count, total, uninterpreted, excerpts)
    finish(profile, rec, {"text": text}, source_url=source_url, retrieved_at=retrieved_at, source_kind="PORTAL_PROFILE",
           source_format=FORMAT, input_kind="TEXT", rules_version=RULES_VERSION, quality=quality,
           file_name=file_name, record_id=record_id)
    return Conversion(profile=profile, original={file_name or "input.txt": text}, uninterpreted=uninterpreted)
