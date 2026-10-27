"""Adapter: JSON Resume (schema v1.x) -> CandidateProfile.

Input format `json-resume-1`: a JSON Resume document (https://jsonresume.org/schema).
Structured input: fields are mapped directly. The document is checked for its basic shape
(object with known sections of the right JSON types); it is **not** validated against the
official JSON Resume schema. JSON Resume has no job-search preferences, so `jobPreferences`
stays UNKNOWN.
"""

from __future__ import annotations

import json
import re

from .base import ConversionRejected, Conversion, Recorder, finish, new_profile, place_from_city, slug, \
    text_value

FORMAT = "json-resume-1"
RULES_VERSION = "json-resume-1"

SECTIONS = {"basics": dict, "work": list, "volunteer": list, "education": list, "awards": list, "certificates": list,
            "publications": list, "skills": list, "languages": list, "interests": list, "references": list,
            "projects": list, "meta": dict}
NOT_MAPPED_SECTIONS = {
    "volunteer": ("NO_AJMS_FIELD", None), "awards": ("NO_AJMS_FIELD", None), "publications": ("NO_AJMS_FIELD", None),
    "interests": ("NO_AJMS_FIELD", "private interests are not matching criteria"),
    "references": ("DATA_MINIMISATION", "statements by third parties; never imported"),
    "projects": ("NO_AJMS_FIELD", None), "meta": ("REDUNDANT", "metadata of the resume document"),
}
LEVELS = {"beginner": "BASIC", "basic": "BASIC", "intermediate": "INTERMEDIATE", "advanced": "ADVANCED",
          "expert": "EXPERT", "master": "EXPERT"}
LANGUAGES = {"german": "de", "english": "en", "french": "fr", "spanish": "es", "italian": "it", "dutch": "nl"}
FLUENCY = {"native speaker": ("NATIVE", False), "native": ("NATIVE", False), "fluent": ("C1", True),
           "professional working": ("B2", True), "conversational": ("B1", True), "basic": ("A2", True),
           "elementary": ("A2", True)}
EQF = [("master", 7), ("bachelor", 6), ("doctor", 8), ("phd", 8)]


def _month(value: str) -> tuple[str | None, bool]:
    """'YYYY-MM-DD' or 'YYYY-MM' -> ('YYYY-MM', day_dropped); 'YYYY' -> (None, False)."""
    m = re.fullmatch(r"(\d{4})-(\d{2})(-\d{2})?", value or "")
    return (f"{m.group(1)}-{m.group(2)}", bool(m.group(3))) if m else (None, False)


def convert(text: str, *, retrieved_at: str, source_url: str | None = None, file_name: str | None = None) -> Conversion:
    try:
        doc = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConversionRejected(FORMAT, [f"not valid JSON: {exc}"]) from exc
    if not isinstance(doc, dict):
        raise ConversionRejected(FORMAT, ["top level is not a JSON object"])
    wrong = [k for k, t in SECTIONS.items() if k in doc and not isinstance(doc[k], t)]
    if wrong:
        raise ConversionRejected(FORMAT, [f"sections with wrong JSON type: {wrong}"])
    rec = Recorder()
    checks = ["valid JSON object; known sections have the expected JSON types",
              "not validated against the official JSON Resume schema"]
    for key in doc:
        if key not in SECTIONS:
            rec.skip(key, "NOT_INTERPRETED", "section unknown to " + RULES_VERSION)
        elif key in NOT_MAPPED_SECTIONS and doc[key]:
            reason, note = NOT_MAPPED_SECTIONS[key]
            rec.skip(key, reason, note)

    profile = new_profile("CandidateProfile", {"resume": text}, source_url, "en")
    caps: dict = {}
    basics = doc.get("basics", {})
    if basics.get("name"):
        identity: dict = {"displayName": basics["name"]}
        rec.say("/identity/displayName", "EXPLICIT", basics["name"])
        contacts = []
        for key, kind in (("email", "EMAIL"), ("phone", "PHONE"), ("url", "URL")):
            if basics.get(key):
                rec.say(f"/identity/contactPoints/{len(contacts)}/contactValue", "EXPLICIT", basics[key])
                contacts.append({"contactType": kind, "contactValue": basics[key]})
        if contacts:
            identity["contactPoints"] = contacts
        loc = basics.get("location", {})
        if loc.get("city"):
            country = loc.get("countryCode") or None
            residence = place_from_city(loc["city"], rec, "/identity/residence", loc["city"], country)
            if residence.get("countryCode"):
                residence["locality"] = loc["city"]
                rec.say("/identity/residence/locality", "EXPLICIT", loc["city"])
                if country:
                    rec.say("/identity/residence/countryCode", "EXPLICIT", country)
                for src, dst in (("region", "region"), ("postalCode", "postalCode")):
                    if loc.get(src):
                        residence[dst] = loc[src]
                        rec.say(f"/identity/residence/{dst}", "EXPLICIT", loc[src])
                identity["residence"] = residence
        if loc.get("address"):
            rec.skip("basics.location.address", "DATA_MINIMISATION", "a street address is not needed for matching")
        if basics.get("profiles"):
            rec.skip("basics.profiles", "NO_AJMS_FIELD", "social network profile links")
        if basics.get("image"):
            rec.skip("basics.image", "PROTECTED_CHARACTERISTIC_NOT_MAPPED", "photos are not represented in AJMS")
        profile["identity"] = identity
    else:
        checks.append("basics.name missing: no identity mapped")
    if basics.get("label"):
        profile["headline"] = text_value(basics["label"], "en")
        rec.say("/headline", "EXPLICIT", basics["label"])
    if basics.get("summary"):
        profile["summary"] = text_value(basics["summary"], "en")
        rec.say("/summary", "EXPLICIT", basics["summary"])

    history = []
    for r, work in enumerate(doc.get("work", [])):
        start, dropped = _month(work.get("startDate", ""))
        if not work.get("position") or not start:
            rec.skip(f"work[{r}]", "MISSING_REQUIRED_DETAIL", "position or start month missing")
            continue
        base = f"/experienceHistory/{len(history)}"
        entry: dict = {"experienceId": f"exp-{r + 1}", "roleTitle": text_value(work["position"], "en"), "startMonth": start}
        rec.say(f"{base}/roleTitle", "EXPLICIT", work["position"])
        rec.say(f"{base}/startMonth", "NORMALIZED", work["startDate"], "iso-date-to-month",
                "day of month dropped" if dropped else None, lossy=dropped)
        if work.get("name"):
            entry["organization"] = {"name": work["name"]}
            rec.say(f"{base}/organization/name", "EXPLICIT", work["name"])
        end, dropped = _month(work.get("endDate", ""))
        if end:
            entry["endMonth"] = end
            rec.say(f"{base}/endMonth", "NORMALIZED", work["endDate"], "iso-date-to-month",
                    "day of month dropped" if dropped else None, lossy=dropped)
        elif not work.get("endDate"):
            entry["ongoing"] = True
            rec.say(f"{base}/ongoing", "DERIVED", None, "missing-end-date-means-current")
        tasks = [t for t in [work.get("summary")] + list(work.get("highlights", [])) if t]
        if tasks:
            entry["tasks"] = []
            for k, task in enumerate(tasks):
                entry["tasks"].append({"taskId": f"task-{k + 1}", "label": text_value(task, "en")})
                rec.say(f"{base}/tasks/{k}/label", "EXPLICIT", task)
        for key in ("location", "url"):
            if work.get(key):
                rec.skip(f"work[{r}].{key}", "NO_AJMS_FIELD", None)
        history.append(entry)
    if history:
        profile["experienceHistory"] = history

    quals: list = []
    evidence: list = []
    for r, edu in enumerate(doc.get("education", [])):
        label = ", ".join(x for x in (edu.get("studyType"), edu.get("area")) if x)
        if not label:
            rec.skip(f"education[{r}]", "MISSING_REQUIRED_DETAIL", "neither studyType nor area")
            continue
        base = f"/capabilities/qualifications/{len(quals)}"
        qual: dict = {"qualificationId": f"edu-{r + 1}", "label": text_value(label, "en")}
        rec.say(f"{base}/label", "NORMALIZED", edu.get("studyType") or edu.get("area"), "join-study-type-and-area")
        study = (edu.get("studyType") or "").lower()
        level = next((lvl for kw, lvl in EQF if kw in study), None)
        qual["qualificationType"] = "DEGREE" if level else "VOCATIONAL_QUALIFICATION" if "vocational" in study else "OTHER"
        rec.say(f"{base}/qualificationType", "DERIVED", edu.get("studyType"), "study-type-keyword")
        if level:
            qual["eqfLevel"] = level
            rec.say(f"{base}/eqfLevel", "DERIVED", edu["studyType"], "degree-keyword-to-eqf")
        if edu.get("area"):
            qual["fieldOfStudy"] = text_value(edu["area"], "en")
            rec.say(f"{base}/fieldOfStudy", "EXPLICIT", edu["area"])
        if edu.get("institution"):
            qual["issuerName"] = edu["institution"]
            rec.say(f"{base}/issuerName", "EXPLICIT", edu["institution"])
        end, dropped = _month(edu.get("endDate", ""))
        if end:
            qual["completedOn"] = end
            rec.say(f"{base}/completedOn", "NORMALIZED", edu["endDate"], "iso-date-to-month",
                    "day of month dropped" if dropped else None, lossy=dropped)
        for key in ("score", "courses"):
            if edu.get(key):
                rec.skip(f"education[{r}].{key}", "NO_AJMS_FIELD", None)
        quals.append(qual)
    for r, cert in enumerate(doc.get("certificates", [])):
        if not cert.get("name"):
            continue
        base = f"/capabilities/qualifications/{len(quals)}"
        qual = {"qualificationId": f"cert-{r + 1}", "qualificationType": "CERTIFICATION", "label": text_value(cert["name"], "en")}
        rec.say(f"{base}/label", "EXPLICIT", cert["name"])
        rec.say(f"{base}/qualificationType", "DERIVED", None, "certificates-section")
        if cert.get("issuer"):
            qual["issuerName"] = cert["issuer"]
            rec.say(f"{base}/issuerName", "EXPLICIT", cert["issuer"])
        month, dropped = _month(cert.get("date", ""))
        if month:
            qual["completedOn"] = month
            rec.say(f"{base}/completedOn", "NORMALIZED", cert["date"], "iso-date-to-month",
                    "day of month dropped" if dropped else None, lossy=dropped)
        if cert.get("url"):
            ev_id = f"ev-cert-{r + 1}"
            evidence.append({"evidenceId": ev_id, "evidenceKind": "CERTIFICATION", "label": text_value(cert["name"], "en"),
                             "documentUrl": cert["url"], "verificationStatus": "UNVERIFIED"})
            rec.say(f"/evidence/{len(evidence) - 1}/documentUrl", "EXPLICIT", cert["url"])
            rec.say(f"/evidence/{len(evidence) - 1}/verificationStatus", "DERIVED", None, "nothing-verified-on-import")
            qual["provenance"] = {"basis": "DOCUMENT_EVIDENCED", "evidenceRefs": [ev_id]}
            rec.say(f"{base}/provenance", "DERIVED", None, "certificate-url-is-evidence-reference")
        quals.append(qual)
    if quals:
        caps["qualifications"] = quals
    if evidence:
        profile["evidence"] = evidence

    comps = []
    for r, skill in enumerate(doc.get("skills", [])):
        if not skill.get("name"):
            continue
        base = f"/capabilities/competencies/{len(comps)}"
        comp: dict = {"competencyId": slug(skill["name"]), "label": text_value(skill["name"], "en")}
        rec.say(f"{base}/label", "EXPLICIT", skill["name"])
        rec.say(f"{base}/competencyId", "DERIVED", skill["name"], "slug-of-label")
        level = (skill.get("level") or "").strip()
        if level.lower() in LEVELS:
            comp["proficiency"] = LEVELS[level.lower()]
            rec.say(f"{base}/proficiency", "NORMALIZED", level, "json-resume-level-words")
        elif level:
            rec.skip(f"skills[{r}].level", "AMBIGUOUS", "free-text level not recognized")
        if skill.get("keywords"):
            rec.skip(f"skills[{r}].keywords", "NO_AJMS_FIELD", "sub-skill keywords are not mapped as separate competencies")
        comps.append(comp)
    if comps:
        caps["competencies"] = comps

    langs = []
    for r, lang in enumerate(doc.get("languages", [])):
        code = LANGUAGES.get((lang.get("language") or "").lower())
        fluency = (lang.get("fluency") or "").strip()
        if code is None:
            rec.skip(f"languages[{r}]", "AMBIGUOUS", "language name not recognized")
            continue
        if fluency.lower() not in FLUENCY:
            rec.skip(f"languages[{r}].fluency", "MISSING_REQUIRED_DETAIL", "fluency missing or not recognized; language not mapped")
            continue
        cefr, lossy = FLUENCY[fluency.lower()]
        base = f"/capabilities/languages/{len(langs)}"
        langs.append({"languageCode": code, "cefrLevel": cefr})
        rec.say(f"{base}/languageCode", "NORMALIZED", lang["language"], "language-name-en-to-bcp47")
        rec.say(f"{base}/cefrLevel", "DERIVED", fluency, "json-resume-fluency-to-cefr",
                f"free-text fluency '{fluency}' has no official CEFR equivalence" if lossy else None, lossy=lossy)
    if langs:
        caps["languages"] = langs
    if caps:
        profile["capabilities"] = caps

    quality = {"status": "PASSED" if not any(u["reason"] == "NOT_INTERPRETED" for u in rec.unmapped) else "REVIEW",
               "checks": checks}
    finish(profile, rec, {"resume": text}, source_url=source_url, retrieved_at=retrieved_at, source_kind="DOCUMENT",
           source_format=FORMAT, input_kind="STRUCTURED", rules_version=RULES_VERSION, quality=quality, file_name=file_name)
    return Conversion(profile=profile, original={file_name or "resume.json": text})
