"""Deterministic Markdown rendering of CandidateProfile, JobProfile and MatchResult.

Same input, same output: no timestamps, no randomness, no language model. Every core
criterion is listed; an absent value is shown as "unknown", an explicit StatedAbsence as
"not applicable" or "not disclosed".
"""

from __future__ import annotations

from typing import Any

LABELS = {
    "en": {
        "candidate": "Candidate profile", "job": "Job profile", "match": "Match result",
        "overview": "Overview", "profile_id": "Profile ID", "updated": "Updated", "view": "View",
        "schema": "Schema version", "status": "Search status", "summary": "Summary",
        "capabilities": "Capabilities", "career_level": "Current career level", "archetypes": "Job archetypes",
        "competencies": "Competencies", "languages": "Languages", "qualifications": "Qualifications",
        "domain_experience": "Domain experience", "total_experience": "Total experience",
        "leadership": "Leadership experience", "work_auth": "Work authorization", "domain": "Domain-specific criteria",
        "history": "Experience history", "evidence": "Evidence", "preferences": "Job preferences",
        "criterion": "Criterion", "hard": "Hard condition", "wish": "Wish", "availability": "Availability",
        "identity": "Identity", "name": "Name", "contact": "Contact",
        "organization": "Organization", "intermediary": "Intermediary", "archetype": "Archetype", "level": "Career level",
        "tasks": "Tasks", "requirements": "Requirements", "offer": "Offer", "posted": "Posted", "valid": "Valid through",
        "provenance": "Data provenance", "requirement": "Requirement", "required_level": "Level",
        "compensation": "Compensation", "location": "Location", "work_model": "Work model", "working_time": "Working time",
        "contract": "Contract", "development": "Development", "benefits": "Benefits", "start": "Start",
        "industry": "Industry", "tasks_pref": "Tasks", "unknown": "unknown", "NOT_APPLICABLE": "not applicable",
        "NOT_DISCLOSED": "not disclosed", "months": "months", "basis": "basis", "years": "years",
        "hiring_fit": "Hiring-Fit (does the candidate meet the job's requirements?)",
        "career_fit": "Career-Fit (does the job meet the candidate's conditions and wishes?)",
        "hard_status": "Hard conditions", "score": "Indicative score (soft criteria, known only)",
        "coverage": "Known weight coverage", "calibration": "Weights", "outcome": "Outcome", "strength": "Type",
        "explanation": "Explanation", "candidate_ref": "Candidate profile", "job_ref": "Job profile",
        "generated_note": "Generated deterministically by the AJMS reference implementation. Synthetic data.",
    },
    "de": {
        "candidate": "Kandidatenprofil", "job": "Stellenprofil", "match": "Matching-Ergebnis",
        "overview": "Überblick", "profile_id": "Profil-ID", "updated": "Aktualisiert", "view": "Ansicht",
        "schema": "Schemaversion", "status": "Suchstatus", "summary": "Zusammenfassung",
        "capabilities": "Qualifikationsprofil", "career_level": "Aktuelles Karrierelevel", "archetypes": "Jobarchetypen",
        "competencies": "Kompetenzen", "languages": "Sprachen", "qualifications": "Qualifikationen",
        "domain_experience": "Fachliche Erfahrung", "total_experience": "Berufserfahrung gesamt",
        "leadership": "Führungserfahrung", "work_auth": "Arbeitserlaubnis", "domain": "Domänenspezifische Kriterien",
        "history": "Berufliche Stationen", "evidence": "Nachweise", "preferences": "Wünsche und Bedingungen",
        "criterion": "Kriterium", "hard": "Harte Bedingung", "wish": "Wunsch", "availability": "Verfügbarkeit",
        "identity": "Identität", "name": "Name", "contact": "Kontakt",
        "organization": "Unternehmen", "intermediary": "Personaldienstleister", "archetype": "Jobarchetyp", "level": "Karrierelevel",
        "tasks": "Aufgaben", "requirements": "Anforderungen", "offer": "Angebot", "posted": "Veröffentlicht", "valid": "Gültig bis",
        "provenance": "Datenherkunft", "requirement": "Anforderung", "required_level": "Stufe",
        "compensation": "Vergütung", "location": "Arbeitsort", "work_model": "Arbeitsmodell", "working_time": "Arbeitszeit",
        "contract": "Vertrag", "development": "Entwicklung", "benefits": "Zusatzleistungen", "start": "Start",
        "industry": "Branche", "tasks_pref": "Aufgabeninhalte", "unknown": "unbekannt", "NOT_APPLICABLE": "nicht anwendbar",
        "NOT_DISCLOSED": "nicht offengelegt", "months": "Monate", "basis": "Grundlage", "years": "Jahre",
        "hiring_fit": "Hiring-Fit (erfüllt der Kandidat die Anforderungen der Stelle?)",
        "career_fit": "Career-Fit (erfüllt die Stelle die Bedingungen und Wünsche des Kandidaten?)",
        "hard_status": "Harte Bedingungen", "score": "Indikativer Wert (weiche Kriterien, nur bekannte)",
        "coverage": "Abdeckung bekannter Gewichte", "calibration": "Gewichte", "outcome": "Ergebnis", "strength": "Art",
        "explanation": "Begründung", "candidate_ref": "Kandidatenprofil", "job_ref": "Stellenprofil",
        "generated_note": "Deterministisch erzeugt mit der AJMS-Referenzimplementierung. Synthetische Daten.",
    },
}
PERIOD = {"en": {"HOUR": "hour", "DAY": "day", "WEEK": "week", "MONTH": "month", "YEAR": "year"},
          "de": {"HOUR": "Stunde", "DAY": "Tag", "WEEK": "Woche", "MONTH": "Monat", "YEAR": "Jahr"}}


class _Doc:
    def __init__(self, lang: str):
        self.lang = lang
        self.L = LABELS[lang]
        self.lines: list[str] = []

    def h(self, level: int, text: str) -> None:
        if self.lines:
            self.lines.append("")
        self.lines += ["#" * level + " " + text, ""]

    def p(self, text: str) -> None:
        self.lines.append(text)

    def bullet(self, label: str, value: str) -> None:
        self.lines.append(f"- **{label}:** {value}")

    def table(self, header: list[str], rows: list[list[str]]) -> None:
        self.lines.append("| " + " | ".join(header) + " |")
        self.lines.append("|" + "|".join(["---"] * len(header)) + "|")
        for row in rows:
            self.lines.append("| " + " | ".join(_cell(c) for c in row) + " |")

    def text(self) -> str:
        return "\n".join(self.lines).rstrip() + "\n"


def _cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _t(value: Any) -> str:
    if isinstance(value, dict) and "text" in value:
        return value["text"]
    return str(value)


def _num(n: float) -> str:
    return f"{n:,.0f}" if abs(n) >= 1000 else f"{n:g}"


def _range(r: dict, unit: str = "") -> str:
    lo, hi = r.get("min"), r.get("max")
    suffix = f" {unit}" if unit else ""
    if lo is not None and hi is not None:
        return (f"{_num(lo)}" if lo == hi else f"{_num(lo)}–{_num(hi)}") + suffix
    if lo is not None:
        return f"≥ {_num(lo)}{suffix}"
    return f"≤ {_num(hi)}{suffix}"


def _amount(a: dict, d: _Doc) -> str:
    if "value" in a:
        figure = _num(a["value"])
    else:
        figure = _range({k: a[k] for k in ("min", "max") if k in a})
    parts = [f"{a['component']} {figure} {a['currency']}/{PERIOD[d.lang][a['period']]} {a['grossOrNet'].lower()}"]
    parts.append(f"{_num(a['hoursPerWeekBasis'])} h/week" if "hoursPerWeekBasis" in a else f"h/week {d.L['unknown']}")
    if "paymentsPerYear" in a:
        parts.append(f"{a['paymentsPerYear']}×/year")
    if a["informationKind"] == "ESTIMATED":
        parts.append("ESTIMATED")
    return ", ".join(parts)


def _share(s: dict) -> str:
    return f"{_range(s['percent'], '%')} / {s['referencePeriod']}"


def _set(c: dict, fmt=str) -> str:
    parts = []
    if c.get("include"):
        parts.append("include: " + ", ".join(fmt(x) for x in c["include"]))
    if c.get("exclude"):
        parts.append("exclude: " + ", ".join(fmt(x) for x in c["exclude"]))
    return "; ".join(parts)


def _code(c: dict) -> str:
    return f"{c['scheme']} {c['code']}"


def _arch(a: dict) -> str:
    return f"{_t(a['label'])} (`{a['archetypeId']}`)"


def _commute(c: dict) -> str:
    parts = []
    if "maxOneWayDistance" in c:
        dist = c["maxOneWayDistance"]
        parts.append(f"≤ {_num(dist['value'])} {dist['unitCode']} one way ({dist['measurement']})")
    if "maxOneWayDuration" in c:
        dur = c["maxOneWayDuration"]
        parts.append(f"≤ {_num(dur['value'])} {dur['unitCode']} one way (travel time)")
    if c.get("transportModes"):
        parts.append("modes: " + ", ".join(c["transportModes"]))
    if "relocationPossible" in c:
        parts.append("relocation: " + ("yes" if c["relocationPossible"] else "no"))
    origin = c["origin"]
    parts.append("from " + ", ".join(x for x in (origin.get("locality"), origin.get("region"), origin["countryCode"]) if x))
    return "; ".join(parts)


def _constraint(group: str, c: dict, d: _Doc) -> str:
    if group == "archetypes":
        return _set(c, _arch)
    if group == "industries":
        return _set(c, _code)
    if group == "tasks":
        return _set(c, lambda t: _t(t["label"]))
    if group == "careerLevel":
        return _set(c)
    if group == "compensation":
        return "≥ " + _amount(c["atLeast"], d)
    parts = []
    if group == "organization":
        for key in ("organizationTypes", "sizeClasses"):
            if key in c:
                parts.append(f"{key}: {_set(c[key])}")
    elif group == "location":
        if "commute" in c:
            parts.append(_commute(c["commute"]))
        if c.get("places"):
            parts.append("places: " + ", ".join(p.get("locality", p.get("region", p["countryCode"])) for p in c["places"]))
    elif group == "workModel":
        if "arrangements" in c:
            parts.append(_set(c["arrangements"]))
        if "remoteShareAtLeast" in c:
            s = c["remoteShareAtLeast"]
            parts.append(f"remote ≥ {_num(s['percent'])} % / {s['referencePeriod']}")
        if "travelShareAtMost" in c:
            s = c["travelShareAtMost"]
            parts.append(f"travel ≤ {_num(s['percent'])} % / {s['referencePeriod']}")
    elif group == "workingTime":
        if "schedules" in c:
            parts.append(_set(c["schedules"]))
        if "weeklyHours" in c:
            parts.append(_range(c["weeklyHours"], "h/week"))
        for key in ("shiftWorkAcceptable", "onCallDutyAcceptable"):
            if key in c:
                parts.append(f"{key}: {'yes' if c[key] else 'no'}")
    elif group == "contract":
        if "contractTypes" in c:
            parts.append(_set(c["contractTypes"]))
        if "fixedTermMonthsAtLeast" in c:
            parts.append(f"fixed term ≥ {_num(c['fixedTermMonthsAtLeast'])} {d.L['months']}")
    elif group == "development":
        parts.append(_set(c["paths"]))
    return "; ".join(parts)


def _domain(dc: dict) -> str:
    value = dc["value"]
    shown = ", ".join(value) if isinstance(value, list) else ("yes" if value is True else "no" if value is False else _num(value) if isinstance(value, (int, float)) else str(value))
    unit = f" {dc['unitCode']}" if "unitCode" in dc else ""
    comparator = f"{dc['comparator']} " if "comparator" in dc else ""
    return f"{_t(dc['label'])} (`{dc['criterionId']}`): {comparator}{shown}{unit}"


def _prov(item: dict) -> str:
    p = item.get("provenance")
    if not p:
        return "–"
    refs = f" ({', '.join(p['evidenceRefs'])})" if p.get("evidenceRefs") else ""
    return p["basis"] + refs


PREFERENCE_GROUPS = [
    ("archetypes", "archetypes"), ("careerLevel", "level"), ("industries", "industry"), ("organization", "organization"),
    ("tasks", "tasks_pref"), ("compensation", "compensation"), ("location", "location"), ("workModel", "work_model"),
    ("workingTime", "working_time"), ("contract", "contract"), ("development", "development"),
]


def render_candidate(p: dict, lang: str = "en") -> str:
    d = _Doc(lang)
    L = d.L
    d.h(1, f"{L['candidate']}: {_t(p['headline']) if 'headline' in p else p['profileId']}")
    d.bullet(L["profile_id"], f"`{p['profileId']}`")
    d.bullet(L["view"], p["profileView"])
    d.bullet(L["updated"], p["updatedAt"])
    d.bullet(L["schema"], p["schemaVersion"])
    d.bullet(L["status"], p.get("searchStatus", L["unknown"]))
    if "identity" in p:
        d.h(2, L["identity"])
        d.bullet(L["name"], p["identity"]["displayName"])
        for cp in p["identity"].get("contactPoints", []):
            d.bullet(L["contact"], f"{cp['contactType']}: {cp['contactValue']}")
    if "summary" in p:
        d.h(2, L["summary"])
        d.p(_t(p["summary"]))

    caps = p.get("capabilities", {})
    d.h(2, L["capabilities"])
    d.bullet(L["career_level"], caps.get("currentCareerLevel", L["unknown"]))
    d.bullet(L["archetypes"], ", ".join(_arch(a) for a in caps.get("archetypes", [])) or L["unknown"])
    d.bullet(L["total_experience"], f"{caps['totalExperienceMonths']} {L['months']}" if "totalExperienceMonths" in caps else L["unknown"])
    lead = caps.get("leadershipExperience")
    d.bullet(L["leadership"], (lead["leadershipType"] + (f", {_range(lead['directReports'])}" if "directReports" in lead else "")) if lead else L["unknown"])
    d.bullet(L["work_auth"], ", ".join(f"{a['countryCode']} {a['status']}" for a in caps.get("workAuthorizations", [])) or L["unknown"])
    if caps.get("competencies"):
        d.h(3, L["competencies"])
        d.table([L["competencies"], "Proficiency", L["years"], L["basis"]], [
            [_t(c["label"]), c.get("proficiency", L["unknown"]), _num(c["yearsOfPractice"]) if "yearsOfPractice" in c else L["unknown"], _prov(c)]
            for c in caps["competencies"]
        ])
    if caps.get("languages"):
        d.h(3, L["languages"])
        d.table([L["languages"], "CEFR", L["basis"]], [[l["languageCode"], l["cefrLevel"], _prov(l)] for l in caps["languages"]])
    if caps.get("qualifications"):
        d.h(3, L["qualifications"])
        d.table([L["qualifications"], "Type", "EQF", L["basis"]], [
            [_t(q["label"]), q["qualificationType"], str(q.get("eqfLevel", L["unknown"])), _prov(q)] for q in caps["qualifications"]
        ])
    if caps.get("domainExperience"):
        d.h(3, L["domain_experience"])
        d.table([L["domain_experience"], L["months"], L["basis"]], [[_t(x["label"]), str(x["months"]), _prov(x)] for x in caps["domainExperience"]])
    if caps.get("domainCriteria"):
        d.h(3, L["domain"])
        for dc in caps["domainCriteria"]:
            d.p(f"- {_domain(dc)} — {_prov(dc)}")

    if p.get("experienceHistory"):
        d.h(2, L["history"])
        for e in p["experienceHistory"]:
            end = "today" if e.get("ongoing") else e.get("endMonth", L["unknown"])
            org = e.get("organization", {})
            org_text = org.get("name") or ", ".join(_code(i) for i in org.get("industries", [])) or L["unknown"]
            d.p(f"- **{_t(e['roleTitle'])}** — {org_text}, {e['startMonth']} – {end} ({_prov(e)})")
            for task in e.get("tasks", []):
                d.p(f"  - {_t(task['label'])}")
    if p.get("evidence"):
        d.h(2, L["evidence"])
        d.table(["ID", "Kind", L["evidence"], "Verification"], [
            [e["evidenceId"], e["evidenceKind"], _t(e["label"]), e["verificationStatus"]] for e in p["evidence"]
        ])

    prefs = p.get("jobPreferences", {})
    d.h(2, L["preferences"])
    rows = []
    for group, label in PREFERENCE_GROUPS:
        block = prefs.get(group)
        if block is None:
            rows.append([L[label], L["unknown"], L["unknown"]])
        elif "state" in block:
            rows.append([L[label], L[block["state"]], L[block["state"]]])
        else:
            rows.append([L[label],
                         _constraint(group, block["hardCondition"], d) if "hardCondition" in block else "–",
                         _constraint(group, block["wish"], d) if "wish" in block else "–"])
    d.table([L["criterion"], L["hard"], L["wish"]], rows)
    domain = prefs.get("domainCriteria", {})
    for side in ("hardCondition", "wish"):
        for dc in domain.get(side, []):
            d.p(f"- {L['hard'] if side == 'hardCondition' else L['wish']}: {_domain(dc)}")

    avail = p.get("availability")
    d.h(2, L["availability"])
    if avail is None:
        d.p(L["unknown"])
    else:
        if avail.get("immediate"):
            d.bullet(L["start"], "immediate")
        if "earliestStartDate" in avail:
            d.bullet(L["start"], "≥ " + avail["earliestStartDate"])
        if "noticePeriod" in avail:
            d.bullet("Notice period", f"{_num(avail['noticePeriod']['value'])} {avail['noticePeriod']['unitCode']}")
    d.p("")
    d.p(f"_{L['generated_note']}_")
    return d.text()


def _offer_value(value: Any, fmt, d: _Doc) -> str:
    if value is None:
        return d.L["unknown"]
    if isinstance(value, dict) and "state" in value:
        return d.L[value["state"]] + (f" ({value['note']})" if value.get("note") else "")
    return fmt(value)


def render_job(j: dict, lang: str = "en") -> str:
    d = _Doc(lang)
    L = d.L
    d.h(1, f"{L['job']}: {_t(j['title'])}")
    org = j.get("hiringOrganization", {})
    d.bullet(L["organization"], org.get("name", L["unknown"]) + (f" ({', '.join(_code(i) for i in org['industries'])})" if org.get("industries") else ""))
    if "intermediary" in j:
        d.bullet(L["intermediary"], j["intermediary"].get("name", L["unknown"]))
    d.bullet(L["archetype"], _arch(j["archetype"]) if "archetype" in j else L["unknown"])
    d.bullet(L["level"], j.get("careerLevel", L["unknown"]))
    d.bullet(L["leadership"], j["leadership"]["leadershipType"] if "leadership" in j else L["unknown"])
    d.bullet(L["profile_id"], f"`{j['profileId']}`")
    d.bullet(L["view"], j["profileView"])
    d.bullet(L["updated"], j["updatedAt"])
    d.bullet(L["posted"], j.get("datePosted", L["unknown"]))
    d.bullet(L["valid"], j.get("validThrough", L["unknown"]))
    d.bullet(L["provenance"], _prov(j) if "provenance" in j else L["unknown"])

    d.h(2, L["tasks"])
    if j.get("tasks"):
        for task in j["tasks"]:
            share = f" ({_num(task['shareOfTimePercent'])} %)" if "shareOfTimePercent" in task else ""
            d.p(f"- {_t(task['label'])}{share}")
    else:
        d.p(L["unknown"])

    req = j.get("requirements", {})
    d.h(2, L["requirements"])
    rows = []
    for c in req.get("competencies", []):
        detail = ", ".join(x for x in (c.get("minimumProficiency"), f"≥ {_num(c['minimumYearsOfPractice'])} {L['years']}" if "minimumYearsOfPractice" in c else None) if x)
        rows.append([L["competencies"], _t(c["label"]) + (f" ({detail})" if detail else ""), c["requirementLevel"]])
    for l in req.get("languages", []):
        rows.append([L["languages"], f"{l['languageCode']} ≥ {l['minimumCefrLevel']}", l["requirementLevel"]])
    for q in req.get("qualifications", []):
        detail = f" (EQF ≥ {q['minimumEqfLevel']})" if "minimumEqfLevel" in q else ""
        rows.append([L["qualifications"], _t(q["label"]) + detail, q["requirementLevel"]])
    for e in req.get("domainExperience", []):
        rows.append([L["domain_experience"], f"{_t(e['label'])} ≥ {e['minimumMonths']} {L['months']}", e["requirementLevel"]])
    if "totalExperienceMonths" in req:
        t = req["totalExperienceMonths"]
        rows.append([L["total_experience"], f"≥ {t['minimumMonths']} {L['months']}", t["requirementLevel"]])
    if "leadershipExperience" in req:
        rows.append([L["leadership"], req["leadershipExperience"]["leadershipType"], req["leadershipExperience"]["requirementLevel"]])
    if "workAuthorization" in req:
        w = req["workAuthorization"]
        sponsor = {True: "sponsorship available", False: "no sponsorship", None: "sponsorship unknown"}[w.get("sponsorshipAvailable")]
        rows.append([L["work_auth"], ", ".join(w["countryCodes"]) + f" ({sponsor})", "REQUIRED"])
    if "startTiming" in req:
        s = req["startTiming"]
        rows.append([L["start"], " – ".join(x for x in (s.get("earliestStartDate"), s.get("latestStartDate")) if x) or ("immediate" if s.get("immediate") else L["unknown"]), "–"])
    for entry in req.get("domainCriteria", []):
        rows.append([L["domain"], _domain(entry["criterion"]), entry["requirementLevel"]])
    if rows:
        d.table([L["criterion"], L["requirement"], L["required_level"]], rows)
    else:
        d.p(L["unknown"])

    offer = j.get("offer", {})
    d.h(2, L["offer"])

    def locations(v):
        return "; ".join(", ".join(x for x in (p.get("locality"), p.get("region"), p["countryCode"]) if x) for p in v)

    def work_model(v):
        parts = [v["arrangement"]]
        parts.append("remote " + _share(v["remoteShare"]) if "remoteShare" in v else f"remote share {L['unknown']}" if v["arrangement"] == "HYBRID" else None)
        if "onsiteDays" in v:
            parts.append(f"on-site {_range(v['onsiteDays']['days'], 'days')} / {v['onsiteDays']['referencePeriod']}")
        if "travelShare" in v:
            parts.append("travel " + _share(v["travelShare"]))
        return "; ".join(x for x in parts if x)

    def working_time(v):
        parts = [v.get("schedule", f"schedule {L['unknown']}")]
        parts.append(_range(v["weeklyHours"], "h/week") if "weeklyHours" in v else f"h/week {L['unknown']}")
        for key in ("shiftWork", "onCallDuty", "flexibleHours"):
            if key in v:
                parts.append(f"{key}: {'yes' if v[key] else 'no'}")
        return "; ".join(parts)

    def contract(v):
        parts = [v["contractType"]]
        if "fixedTermMonths" in v:
            parts.append(f"{_num(v['fixedTermMonths'])} {L['months']}")
        if "permanentConversionPossible" in v:
            parts.append("conversion to permanent possible" if v["permanentConversionPossible"] else "no conversion")
        if "probationMonths" in v:
            parts.append(f"probation {_num(v['probationMonths'])} {L['months']}")
        return "; ".join(parts)

    def development(v):
        parts = [", ".join(v.get("paths", []))] if v.get("paths") else []
        if "trainingDaysPerYear" in v:
            parts.append(f"training {_range(v['trainingDaysPerYear'], 'days/year')}")
        return "; ".join(parts) or "–"

    rows = [
        [L["compensation"], _offer_value(offer.get("compensation"), lambda v: "<br>".join(_amount(a, d) for a in v), d)],
        [L["location"], _offer_value(offer.get("locations"), locations, d)],
        [L["work_model"], _offer_value(offer.get("workModel"), work_model, d)],
        [L["working_time"], _offer_value(offer.get("workingTime"), working_time, d)],
        [L["contract"], _offer_value(offer.get("contract"), contract, d)],
        [L["development"], _offer_value(offer.get("development"), development, d)],
        [L["benefits"], ", ".join(_t(b) for b in offer["benefits"]) if offer.get("benefits") else L["unknown"]],
    ]
    for dc in offer.get("domainCriteria", []):
        rows.append([L["domain"], _domain(dc)])
    d.table([L["criterion"], L["offer"]], rows)
    d.p("")
    d.p(f"_{L['generated_note']}_")
    return d.text()


def render_match(r: dict, lang: str = "en") -> str:
    d = _Doc(lang)
    L = d.L
    d.h(1, L["match"])
    d.bullet(L["candidate_ref"], f"`{r['candidateProfileId']}` ({r.get('candidateUpdatedAt', L['unknown'])})")
    d.bullet(L["job_ref"], f"`{r['jobProfileId']}` ({r.get('jobUpdatedAt', L['unknown'])})")
    d.p("")
    d.p("> " + r.get("disclaimer", ""))
    for key, title in (("hiringFit", L["hiring_fit"]), ("careerFit", L["career_fit"])):
        s = r[key]
        d.h(2, title)
        d.bullet(L["hard_status"], s["hardConditionStatus"])
        score = "–" if s["indicativeScore"] is None else f"{s['indicativeScore']:.2f}"
        d.bullet(L["score"], score)
        d.bullet(L["coverage"], f"{s['knownWeightCoverage']:.0%}")
        d.bullet(L["calibration"], f"{s['policyId']} ({s['calibrationStatus']})")
        d.bullet(L["outcome"], ", ".join(f"{k} {v}" for k, v in s["outcomeCounts"].items() if v))
        d.p("")
        d.table([L["criterion"], L["strength"], L["outcome"], L["explanation"]], [
            [f"`{c['criterionKey']}`", c["strength"], ("**" + c["outcome"] + "**") if c["outcome"] in ("NOT_MET", "UNKNOWN") else c["outcome"], c["explanation"]]
            for c in s["criteria"]
        ])
    d.p("")
    d.p(f"_{L['generated_note']}_")
    return d.text()


def render(doc: dict, lang: str = "en") -> str:
    kind = doc.get("@type")
    if kind == "CandidateProfile":
        return render_candidate(doc, lang)
    if kind == "JobProfile":
        return render_job(doc, lang)
    if kind == "MatchResult":
        return render_match(doc, lang)
    raise ValueError(f"cannot render @type {kind!r}")
