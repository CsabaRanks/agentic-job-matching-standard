"""Adapter: German job ad text -> JobProfile.

Input format `job-ad-text-de` (layout job-ad-de-1): title on the first line, "<organisation> ·
Standort: <city>" on the second, then bullet lists ("- ") under the headings "Ihre Aufgaben",
"Ihr Profil" and "Wir bieten" (or the listed synonyms). Text input: a small deterministic rule
set extracts values and the extraction-quality gate checks the result. It is not a
production parser and fetches nothing; retrieving ads is a separate function.
"""

from __future__ import annotations

import re

from .base import Conversion, Recorder, finish, new_profile, place_from_city, slug, text_quality, text_value

FORMAT = "job-ad-text-de"
RULES_VERSION = "job-ad-de-1"

ARCHETYPES = [
    ("demand planner", "demand-planner", "Demand Planner"),
    ("supply planner", "supply-planner", "Supply Planner"),
    ("supply chain analyst", "supply-chain-analyst", "Supply Chain Analyst"),
]
CAREER_LEVELS = [("teamleit", "LEAD"), ("head of", "HEAD"), ("senior", "SENIOR"), ("junior", "JUNIOR"), ("lead", "LEAD")]
COMPETENCY_IDS = {"sql": "sql", "python": "python", "sap ibp": "sap-ibp", "excel": "excel"}
DOMAIN_IDS = {"supply-chain-planung": "supply-chain-planning", "absatzplanung": "demand-planning"}
PROFICIENCY = {"grundlegende": "BASIC", "gute": "INTERMEDIATE", "sehr gute": "ADVANCED", "exzellente": "EXPERT"}
LANGUAGES = {"deutsch": "de", "englisch": "en", "französisch": "fr", "spanisch": "es"}
PREFERRED_MARKERS = ("von vorteil", "wünschenswert", "idealerweise", "wäre schön")
SECTION_TASKS = ("ihre aufgaben", "aufgaben", "das erwartet sie")
SECTION_PROFILE = ("ihr profil", "was sie mitbringen", "anforderungen")
SECTION_OFFER = ("wir bieten", "das bieten wir", "unser angebot")


def convert(text: str, *, retrieved_at: str, source_url: str | None = None, file_name: str | None = None,
            language: str = "de") -> Conversion:
    rec = Recorder()
    excerpts: list[str] = []

    def say(path, kind, excerpt=None, method=None, note=None, lossy=False):
        if excerpt is not None:
            excerpts.append(excerpt)
        rec.say(path, kind, excerpt, method, note, lossy)

    lines = text.splitlines()
    numbered = [(n + 1, line.rstrip()) for n, line in enumerate(lines) if line.strip()]
    job = new_profile("JobProfile", {"text": text}, source_url, language)
    uninterpreted: list[tuple[int, str]] = []
    recognized = 0

    title_no, title = numbered[0]
    recognized += 1
    job["title"] = text_value(title, language)
    say("/title", "EXPLICIT", title)
    lowered = title.lower()
    for keyword, archetype_id, label in ARCHETYPES:
        if keyword in lowered:
            job["archetype"] = {"archetypeId": archetype_id, "label": text_value(label, "en")}
            say("/archetype", "DERIVED", title[lowered.index(keyword):lowered.index(keyword) + len(keyword)], "title-keyword-archetype")
            break
    for keyword, level in CAREER_LEVELS:
        if keyword in lowered:
            job["careerLevel"] = level
            say("/careerLevel", "DERIVED", title[lowered.index(keyword):lowered.index(keyword) + len(keyword)], "title-keyword-career-level")
            break

    offer: dict = {}
    rest = numbered[1:]
    if rest and "·" in rest[0][1]:
        no, line = rest[0]
        rest = rest[1:]
        org_part, _, location_part = (part.strip() for part in line.partition("·"))
        job["hiringOrganization"] = {"name": org_part}
        say("/hiringOrganization/name", "EXPLICIT", org_part)
        city = re.sub(r"^(Standort|Arbeitsort):\s*", "", location_part)
        place = place_from_city(city, rec, "/offer/locations/0", city)
        if place.get("countryCode"):
            place["locality"] = city
            offer["locations"] = [place]
            say("/offer/locations/0/locality", "EXPLICIT", city)
            recognized += 1
        else:
            uninterpreted.append((no, line))

    sections: dict[str, list[tuple[int, str]]] = {"tasks": [], "profile": [], "offer": []}
    current = None
    for no, line in rest:
        key = line.strip().lower()
        if key in SECTION_TASKS + SECTION_PROFILE + SECTION_OFFER:
            current = "tasks" if key in SECTION_TASKS else "profile" if key in SECTION_PROFILE else "offer"
            recognized += 1
        elif line.startswith("- ") and current:
            sections[current].append((no, line[2:].strip()))
        else:
            uninterpreted.append((no, line))

    if sections["tasks"]:
        job["tasks"] = []
        for index, (_, bullet) in enumerate(sections["tasks"]):
            job["tasks"].append({"taskId": f"task-{index + 1}", "label": text_value(bullet, language)})
            say(f"/tasks/{index}/label", "EXPLICIT", bullet)
            recognized += 1

    req: dict = {}
    for no, bullet in sections["profile"]:
        low = bullet.lower()
        marker = next((m for m in PREFERRED_MARKERS if m in low), None)

        def level_statement(path: str) -> str:
            if marker:
                say(path, "NORMALIZED", bullet[low.index(marker):low.index(marker) + len(marker)], "preferred-marker-de")
                return "PREFERRED"
            say(path, "DERIVED", None, "profile-section-default-required",
                "listed under the profile section without a 'preferred' marker")
            return "REQUIRED"

        matched = False
        m = re.match(r"((?:Mindestens|Mind\.)\s+(\d+)\s+Jahren?)\s+Erfahrung\s+(?:in|im)\s+(?:der|dem|den)?\s*(.+)$", bullet, re.I)
        if m:
            matched = True
            items = req.setdefault("domainExperience", [])
            base = f"/requirements/domainExperience/{len(items)}"
            domain = m.group(3).strip()
            entry = {"domainId": DOMAIN_IDS.get(domain.lower(), slug(domain)), "label": text_value(domain, language),
                     "minimumMonths": int(m.group(2)) * 12}
            items.append(entry)
            say(f"{base}/label", "EXPLICIT", domain)
            say(f"{base}/domainId", "DERIVED", domain, "domain-keyword-table" if domain.lower() in DOMAIN_IDS else "slug-of-label")
            say(f"{base}/minimumMonths", "NORMALIZED", m.group(1), "years-to-months")
            entry["requirementLevel"] = level_statement(f"{base}/requirementLevel")
        m = re.match(r"(Sehr gute|Gute|Grundlegende|Exzellente)\s+([\w+#. ]+?)-Kenntnisse", bullet)
        if m:
            matched = True
            items = req.setdefault("competencies", [])
            base = f"/requirements/competencies/{len(items)}"
            skill = m.group(2).strip()
            entry = {"competencyId": COMPETENCY_IDS.get(skill.lower(), slug(skill)), "label": text_value(skill, language),
                     "minimumProficiency": PROFICIENCY[m.group(1).lower()]}
            items.append(entry)
            say(f"{base}/label", "EXPLICIT", skill)
            say(f"{base}/competencyId", "DERIVED", skill, "competency-keyword-table" if skill.lower() in COMPETENCY_IDS else "slug-of-label")
            say(f"{base}/minimumProficiency", "NORMALIZED", m.group(1), "proficiency-words-de",
                "German grading words mapped onto four AJMS levels", lossy=True)
            entry["requirementLevel"] = level_statement(f"{base}/requirementLevel")
        for lm in re.finditer(r"(Deutsch|Englisch|Französisch|Spanisch)\s*\((A1|A2|B1|B2|C1|C2)\)", bullet):
            matched = True
            items = req.setdefault("languages", [])
            base = f"/requirements/languages/{len(items)}"
            entry = {"languageCode": LANGUAGES[lm.group(1).lower()], "minimumCefrLevel": lm.group(2)}
            items.append(entry)
            say(f"{base}/languageCode", "NORMALIZED", lm.group(1), "language-name-de-to-bcp47")
            say(f"{base}/minimumCefrLevel", "EXPLICIT", lm.group(2))
            entry["requirementLevel"] = level_statement(f"{base}/requirementLevel")
        if matched:
            recognized += 1
        else:
            uninterpreted.append((no, "- " + bullet))
    if req:
        job["requirements"] = req

    hours = hours_excerpt = None
    for no, bullet in sections["offer"]:
        matched = False
        found = re.search(r"\bunbefristet\w*", bullet, re.I)
        if found:
            matched = True
            offer["contract"] = {"contractType": "PERMANENT_EMPLOYMENT"}
            say("/offer/contract/contractType", "NORMALIZED", found.group(0), "contract-words-de")
        fixed = re.search(r"befristet auf (\d+) Monate", bullet, re.I)
        if fixed:
            matched = True
            offer["contract"] = {"contractType": "FIXED_TERM_EMPLOYMENT", "fixedTermMonths": int(fixed.group(1))}
            say("/offer/contract/contractType", "NORMALIZED", fixed.group(0), "contract-words-de")
            say("/offer/contract/fixedTermMonths", "NORMALIZED", fixed.group(0), "contract-words-de")
        for word, schedule in (("Vollzeit", "FULL_TIME"), ("Teilzeit", "PART_TIME")):
            if word in bullet:
                matched = True
                offer.setdefault("workingTime", {})["schedule"] = schedule
                say("/offer/workingTime/schedule", "NORMALIZED", word, "schedule-words-de")
        hm = re.search(r"(\d+(?:,\d+)?)\s*Stunden/Woche", bullet)
        if hm:
            matched = True
            value = float(hm.group(1).replace(",", "."))
            hours = int(value) if value.is_integer() else value
            hours_excerpt = hm.group(0)
            offer.setdefault("workingTime", {})["weeklyHours"] = {"min": hours, "max": hours}
            say("/offer/workingTime/weeklyHours", "NORMALIZED", hours_excerpt, "hours-per-week")
        wm = re.search(r"\b(hybrid\w*|remote|vor ort)\b", bullet, re.I)
        if wm:
            matched = True
            word = wm.group(1).lower()
            offer["workModel"] = {"arrangement": "HYBRID" if word.startswith("hybrid") else "REMOTE" if word == "remote" else "ONSITE"}
            say("/offer/workModel/arrangement", "NORMALIZED", wm.group(0), "work-model-words-de")
        sm = re.search(r"(\d{1,3}(?:\.\d{3})+)\s*[–-]\s*(\d{1,3}(?:\.\d{3})+)\s*€\s*(brutto|netto)", bullet)
        pm = re.search(r"Jahresgehalt|p\.\s?a\.|pro Jahr|Monatsgehalt|pro Monat", bullet)
        if sm and pm:
            matched = True
            offer["compensation"] = [{
                "component": "BASE_SALARY", "currency": "EUR", "period": "MONTH" if "monat" in pm.group(0).lower() else "YEAR",
                "grossOrNet": "GROSS" if sm.group(3) == "brutto" else "NET",
                "min": int(sm.group(1).replace(".", "")), "max": int(sm.group(2).replace(".", "")), "informationKind": "STATED"}]
            base = "/offer/compensation/0"
            say(f"{base}/min", "NORMALIZED", sm.group(1), "german-number-format")
            say(f"{base}/max", "NORMALIZED", sm.group(2), "german-number-format")
            say(f"{base}/currency", "NORMALIZED", "€", "currency-symbol-to-iso4217")
            say(f"{base}/grossOrNet", "NORMALIZED", sm.group(3), "gross-net-words-de")
            say(f"{base}/period", "NORMALIZED", pm.group(0), "period-words-de")
            say(f"{base}/component", "DERIVED", pm.group(0), "salary-word-is-base-salary",
                "'Jahresgehalt' is read as fixed base salary; it may include variable pay")
        if not matched:
            offer.setdefault("benefits", []).append(text_value(bullet, language))
            say(f"/offer/benefits/{len(offer['benefits']) - 1}", "EXPLICIT", bullet, None,
                "offer bullet not matched by any rule; kept verbatim as a benefit")
        recognized += 1
    if hours is not None and offer.get("compensation"):
        offer["compensation"][0]["hoursPerWeekBasis"] = hours
        say("/offer/compensation/0/hoursPerWeekBasis", "DERIVED", hours_excerpt, "salary-hours-from-working-time",
            "assumes the salary refers to the stated contractual weekly hours")
    if offer:
        job["offer"] = offer
    job["provenance"] = {"basis": "DERIVED", "note": "Imported from a published job ad by a search agent; not confirmed by the employer."}
    if source_url:
        job["provenance"]["sourceUrl"] = source_url

    for no, _ in uninterpreted:
        rec.skip(f"line {no}", "NOT_INTERPRETED", f"no rule of {RULES_VERSION} applies")
    quality = text_quality(FORMAT, text, [], recognized, len(numbered), [u for _, u in uninterpreted], excerpts)
    if not (job.get("tasks") or job.get("requirements") or offer):
        quality["status"] = "REVIEW"
        quality["checks"].append("no section heading recognized")
    finish(job, rec, {"text": text}, source_url=source_url, retrieved_at=retrieved_at, source_kind="JOB_AD_WEB_PAGE",
           source_format=FORMAT, input_kind="TEXT", rules_version=RULES_VERSION, quality=quality, file_name=file_name)
    return Conversion(profile=job, original={file_name or "ad.txt": text}, uninterpreted=[u for _, u in uninterpreted])
