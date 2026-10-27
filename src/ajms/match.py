"""Deterministic demonstration matcher.

Hiring-Fit: does the candidate meet the job's requirements?
Career-Fit: does the job meet the candidate's hard conditions and wishes?

The two perspectives are computed and reported separately. Absent information is
UNKNOWN and is never scored as 0. Weights come from a separate MatchPolicy and are
illustrative only (UNCALIBRATED). This is a demonstration, not a validated selection
procedure: it must not be used for automated decisions about people.
"""

from __future__ import annotations

import json
import math
from typing import Any, Iterable

from . import SPEC_VERSION, __version__

MET, PARTIAL, NOT_MET, UNKNOWN, NA = "MET", "PARTIALLY_MET", "NOT_MET", "UNKNOWN", "NOT_APPLICABLE"
OUTCOMES = (MET, PARTIAL, NOT_MET, UNKNOWN, NA)
SCORE = {MET: 1.0, PARTIAL: 0.5, NOT_MET: 0.0}
# When sub-checks disagree, the overall outcome is the first one present in this order.
PRIORITY = (NOT_MET, UNKNOWN, PARTIAL, MET)

PROFICIENCY = ["BASIC", "INTERMEDIATE", "ADVANCED", "EXPERT"]
CEFR = ["A1", "A2", "B1", "B2", "C1", "C2", "NATIVE"]
CAREER = ["ENTRY", "JUNIOR", "PROFESSIONAL", "SENIOR", "LEAD", "HEAD", "DIRECTOR", "EXECUTIVE"]

DISCLAIMER = (
    "Demonstration output. Weights are UNCALIBRATED and illustrative. UNKNOWN means information is missing "
    "or not comparable; it is not a negative result. Not suitable for automated decisions about people."
)


def combine(outcomes: Iterable[str]) -> str:
    present = [o for o in outcomes if o != NA]
    if not present:
        return NA
    for outcome in PRIORITY:
        if outcome in present:
            return outcome
    return UNKNOWN


def _text(value: Any) -> str:
    if isinstance(value, dict) and "text" in value:
        return value["text"]
    return str(value)


def _fmt(number: float) -> str:
    return f"{number:,.0f}" if abs(number) >= 100 else f"{number:g}"


class _Collector:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, key: str, group: str, strength: str, outcome: str, explanation: str) -> None:
        self.items.append(
            {"criterionKey": key, "group": group, "strength": strength, "outcome": outcome, "explanation": explanation}
        )


# ----------------------------------------------------------------- shared helpers


def _code_matches(wanted: dict, offered: dict) -> bool:
    """Same scheme and the offered code equals or is a sub-code of the wanted code.

    "C10" covers "C10.1"; a one-letter section such as "Q" covers "Q86.1".
    """
    if wanted.get("scheme") != offered.get("scheme"):
        return False
    w, o = str(wanted.get("code", "")), str(offered.get("code", ""))
    return o == w or o.startswith(w + ".") or (len(w) == 1 and w.isalpha() and o.startswith(w))


def _archetype_matches(a: dict, b: dict) -> bool:
    if a.get("archetypeId") == b.get("archetypeId"):
        return True
    return any(_code_matches(x, y) for x in a.get("occupationCodes", []) for y in b.get("occupationCodes", []))


def _same_item(a: dict, b: dict, id_key: str) -> bool:
    if a.get(id_key) and a.get(id_key) == b.get(id_key):
        return True
    if a.get("code") and b.get("code") and _code_matches(a["code"], b["code"]):
        return True
    return _text(a.get("label", "")).casefold() == _text(b.get("label", "")).casefold() != ""


def _set_check(constraint: dict, job_values: list, matches) -> tuple[str, str]:
    """Evaluate an include/exclude constraint against the job's value(s)."""
    if not job_values:
        return UNKNOWN, "the job does not state this"
    excluded = [v for v in job_values for x in constraint.get("exclude", []) if matches(x, v)]
    if excluded:
        return NOT_MET, "the job has an excluded value"
    include = constraint.get("include")
    if include is None:
        return MET, "no excluded value present"
    if any(matches(x, v) for x in include for v in job_values):
        return MET, "the job has an included value"
    return NOT_MET, "none of the job's values is included"


def _domain_compare(condition: dict, fact: dict | None) -> tuple[str, str]:
    if fact is None:
        return UNKNOWN, "no value stated on the other side"
    if condition.get("unitCode") != fact.get("unitCode"):
        return UNKNOWN, f"units differ ({condition.get('unitCode')} vs {fact.get('unitCode')}); not converted"
    want, have, comparator = condition["value"], fact["value"], condition["comparator"]
    if comparator == "EQUALS":
        ok = have == want
    elif comparator == "AT_LEAST":
        ok = isinstance(have, (int, float)) and have >= want
    elif comparator == "AT_MOST":
        ok = isinstance(have, (int, float)) and have <= want
    elif comparator == "ANY_OF":
        wanted = set(want if isinstance(want, list) else [want])
        offered = set(have if isinstance(have, list) else [have])
        ok = bool(wanted & offered)
    elif comparator == "ALL_OF":
        wanted = set(want if isinstance(want, list) else [want])
        offered = set(have if isinstance(have, list) else [have])
        if wanted <= offered:
            return MET, f"all of {json.dumps(sorted(wanted))} present"
        if wanted & offered:
            return PARTIAL, f"missing {json.dumps(sorted(wanted - offered))}"
        return NOT_MET, f"none of {json.dumps(sorted(wanted))} present"
    else:
        return UNKNOWN, f"unsupported comparator {comparator}"
    return (MET if ok else NOT_MET), f"stated {json.dumps(have)}, condition {comparator} {json.dumps(want)}"


def _haversine_km(a: dict, b: dict) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a["latitude"], a["longitude"], b["latitude"], b["longitude"]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


# ----------------------------------------------------------------- Hiring-Fit


def _hiring_fit(candidate: dict, job: dict) -> list[dict]:
    out = _Collector()
    caps = candidate.get("capabilities", {})
    req = job.get("requirements", {})

    def strength(item):
        return "HARD" if item.get("requirementLevel") == "REQUIRED" else "SOFT"

    for r in req.get("competencies", []):
        found = next((c for c in caps.get("competencies", []) if _same_item(r, c, "competencyId")), None)
        label = _text(r["label"])
        if found is None:
            out.add(f"competencies/{r['competencyId']}", "competencies", strength(r), UNKNOWN, f"{label}: not stated in the candidate profile")
            continue
        parts, notes = [], []
        if "minimumProficiency" in r:
            if "proficiency" not in found:
                parts.append(UNKNOWN)
                notes.append("proficiency not stated")
            else:
                gap = PROFICIENCY.index(r["minimumProficiency"]) - PROFICIENCY.index(found["proficiency"])
                parts.append(MET if gap <= 0 else PARTIAL if gap == 1 else NOT_MET)
                notes.append(f"proficiency {found['proficiency']} vs required {r['minimumProficiency']}")
        if "minimumYearsOfPractice" in r:
            if "yearsOfPractice" not in found:
                parts.append(UNKNOWN)
                notes.append("years of practice not stated")
            else:
                years = found["yearsOfPractice"]
                parts.append(MET if years >= r["minimumYearsOfPractice"] else NOT_MET)
                notes.append(f"{_fmt(years)} years vs required {_fmt(r['minimumYearsOfPractice'])}")
        outcome = combine(parts) if parts else MET
        basis = found.get("provenance", {}).get("basis", "basis not stated")
        out.add(f"competencies/{r['competencyId']}", "competencies", strength(r), outcome,
                f"{label}: " + ("; ".join(notes) if notes else "stated") + f" ({basis})")

    for r in req.get("languages", []):
        wanted = r["languageCode"].split("-")[0]
        found = next((l for l in caps.get("languages", []) if l["languageCode"].split("-")[0] == wanted), None)
        key = f"languages/{r['languageCode']}"
        if found is None:
            out.add(key, "languages", strength(r), UNKNOWN, f"{r['languageCode']}: not stated in the candidate profile")
            continue
        gap = CEFR.index(r["minimumCefrLevel"]) - CEFR.index(found["cefrLevel"])
        outcome = MET if gap <= 0 else PARTIAL if gap == 1 else NOT_MET
        out.add(key, "languages", strength(r), outcome, f"{r['languageCode']}: {found['cefrLevel']} vs required {r['minimumCefrLevel']}")

    for r in req.get("qualifications", []):
        key = f"qualifications/{r['requirementId']}"
        same_type = [q for q in caps.get("qualifications", []) if q["qualificationType"] == r["qualificationType"]]
        if not same_type:
            out.add(key, "qualifications", strength(r), UNKNOWN, f"{_text(r['label'])}: no {r['qualificationType']} stated")
            continue
        if "minimumEqfLevel" not in r:
            out.add(key, "qualifications", strength(r), MET, f"{_text(r['label'])}: {r['qualificationType']} stated; field of study not compared automatically")
            continue
        levels = [q["eqfLevel"] for q in same_type if "eqfLevel" in q]
        if not levels:
            out.add(key, "qualifications", strength(r), UNKNOWN, f"{_text(r['label'])}: EQF level not stated")
        elif max(levels) >= r["minimumEqfLevel"]:
            out.add(key, "qualifications", strength(r), MET, f"{_text(r['label'])}: EQF {max(levels)} vs required {r['minimumEqfLevel']}; field of study not compared automatically")
        else:
            outcome = UNKNOWN if r.get("experienceInPlaceOfEducation") else NOT_MET
            out.add(key, "qualifications", strength(r), outcome, f"{_text(r['label'])}: EQF {max(levels)} vs required {r['minimumEqfLevel']}" + ("; experience may substitute - needs human judgement" if outcome == UNKNOWN else ""))

    for r in req.get("domainExperience", []):
        key = f"domainExperience/{r['domainId']}"
        found = next((d for d in caps.get("domainExperience", []) if _same_item(r, d, "domainId")), None)
        if found is None:
            out.add(key, "domainExperience", strength(r), UNKNOWN, f"{_text(r['label'])}: not stated")
            continue
        months, need = found["months"], r["minimumMonths"]
        outcome = MET if months >= need else PARTIAL if months >= 0.75 * need else NOT_MET
        out.add(key, "domainExperience", strength(r), outcome, f"{_text(r['label'])}: {months} months vs required {need}")

    if "totalExperienceMonths" in req:
        r = req["totalExperienceMonths"]
        if "totalExperienceMonths" not in caps:
            out.add("totalExperience", "totalExperience", strength(r), UNKNOWN, "total experience not stated")
        else:
            months, need = caps["totalExperienceMonths"], r["minimumMonths"]
            outcome = MET if months >= need else PARTIAL if months >= 0.75 * need else NOT_MET
            out.add("totalExperience", "totalExperience", strength(r), outcome, f"{months} months vs required {need}")

    if "leadershipExperience" in req:
        r = req["leadershipExperience"]
        have = caps.get("leadershipExperience", {}).get("leadershipType")
        if have is None:
            outcome, why = UNKNOWN, "leadership experience not stated"
        elif have == "DISCIPLINARY" or have == r["leadershipType"]:
            outcome, why = MET, f"{have} vs required {r['leadershipType']}"
        else:
            outcome, why = NOT_MET, f"{have} vs required {r['leadershipType']}"
        out.add("leadershipExperience", "leadershipExperience", strength(r), outcome, why)

    if "careerLevel" in job:
        have = caps.get("currentCareerLevel")
        if have is None:
            out.add("careerLevel", "careerLevel", "SOFT", UNKNOWN, "candidate's current career level not stated")
        else:
            step = CAREER.index(job["careerLevel"]) - CAREER.index(have)
            outcome = MET if -1 <= step <= 1 else PARTIAL if -2 <= step <= 2 else NOT_MET
            out.add("careerLevel", "careerLevel", "SOFT", outcome, f"job {job['careerLevel']}, candidate currently {have} (step {step:+d})")

    if "workAuthorization" in req:
        r = req["workAuthorization"]
        parts, notes = [], []
        for country in r["countryCodes"]:
            auth = next((a for a in caps.get("workAuthorizations", []) if a["countryCode"] == country), None)
            if auth is None:
                parts.append(UNKNOWN)
                notes.append(f"{country}: not stated")
            elif auth["status"] == "AUTHORIZED":
                parts.append(MET)
                notes.append(f"{country}: authorized")
            else:
                sponsor = r.get("sponsorshipAvailable")
                parts.append(MET if sponsor is True else NOT_MET if sponsor is False else UNKNOWN)
                notes.append(f"{country}: requires sponsorship, sponsorship " + {True: "available", False: "not available", None: "not stated"}[sponsor])
        out.add("workAuthorization", "workAuthorization", "HARD", combine(parts), "; ".join(notes))

    if "startTiming" in req:
        r, avail = req["startTiming"], candidate.get("availability")
        latest = r.get("latestStartDate")
        if avail is None:
            outcome, why = UNKNOWN, "candidate availability not stated"
        elif latest is None:
            outcome, why = MET, "the job states no latest start date"
        elif avail.get("immediate"):
            outcome, why = MET, "candidate available immediately"
        elif "earliestStartDate" in avail:
            ok = avail["earliestStartDate"] <= latest
            outcome, why = (MET if ok else NOT_MET), f"candidate from {avail['earliestStartDate']}, job latest {latest}"
        else:
            outcome, why = UNKNOWN, "only a notice period is stated; no reference date to compute a start"
        out.add("startTiming", "startTiming", "SOFT", outcome, why)

    for entry in req.get("domainCriteria", []):
        cond = entry["criterion"]
        fact = next((d for d in caps.get("domainCriteria", []) if d["criterionId"] == cond["criterionId"]), None)
        outcome, why = _domain_compare(cond, fact)
        out.add(f"domainCriteria/{cond['criterionId']}", "domainCriteria", strength(entry), outcome, f"{_text(cond['label'])}: {why}")

    return out.items


# ----------------------------------------------------------------- Career-Fit


def _to_comparable(entry: dict, target: dict) -> tuple[float | None, float | None, list[str]]:
    """Convert a job compensation entry into the candidate's period and hours basis."""
    notes: list[str] = []
    per_year = {"YEAR": 1.0, "WEEK": 52.0}

    def annual_factor(e: dict) -> float | None:
        if e["period"] in per_year:
            if e["period"] == "WEEK":
                notes.append("weeks converted at 52 per year")
            return per_year[e["period"]]
        if e["period"] == "MONTH":
            if "paymentsPerYear" in e:
                return float(e["paymentsPerYear"])
            notes.append("months converted at 12 payments per year (not stated)")
            return 12.0
        if e["period"] == "HOUR" and "hoursPerWeekBasis" in target:
            return 52.0 * target["hoursPerWeekBasis"]
        return None

    lo = entry.get("min", entry.get("value"))
    hi = entry.get("max", entry.get("value"))
    if entry["period"] != target["period"]:
        f_job, f_target = annual_factor(entry), annual_factor(target)
        if f_job is None or f_target is None:
            return None, None, ["periods cannot be converted (" + entry["period"] + " vs " + target["period"] + ")"]
        scale = f_job / f_target
        lo = lo * scale if lo is not None else None
        hi = hi * scale if hi is not None else None
    elif entry["period"] == "MONTH" and entry.get("paymentsPerYear") not in (None, target.get("paymentsPerYear")):
        notes.append(f"job pays {entry['paymentsPerYear']} times per year; compared per month")
    jh, th = entry.get("hoursPerWeekBasis"), target.get("hoursPerWeekBasis")
    if entry["period"] != "HOUR" and jh and th and jh != th:
        lo = lo * th / jh if lo is not None else None
        hi = hi * th / jh if hi is not None else None
        notes.append(f"scaled from {_fmt(jh)} h to {_fmt(th)} h per week")
    elif entry["period"] != "HOUR" and not (jh and th):
        notes.append("hours basis not stated on both sides; compared as stated")
    return lo, hi, notes


def _compensation_check(constraint: dict, offer: Any) -> tuple[str, str]:
    target = constraint["atLeast"]
    if isinstance(offer, dict):
        return (NA if offer["state"] == "NOT_APPLICABLE" else UNKNOWN), f"job compensation {offer['state'].lower().replace('_', ' ')}"
    if not offer:
        return UNKNOWN, "job compensation not stated"
    threshold = target.get("value", target.get("min"))
    if threshold is None:
        return UNKNOWN, "candidate threshold has no lower bound"
    candidates = [e for e in offer if e["component"] == target["component"]]
    if not candidates:
        stated = sorted({e["component"] for e in offer})
        return UNKNOWN, f"job states {', '.join(stated)} but not {target['component']}"
    entry = sorted(candidates, key=lambda e: e["informationKind"] != "STATED")[0]
    if entry["currency"] != target["currency"] or entry["grossOrNet"] != target["grossOrNet"]:
        return UNKNOWN, f"{entry['currency']} {entry['grossOrNet']} vs {target['currency']} {target['grossOrNet']}; not converted"
    lo, hi, notes = _to_comparable(entry, target)
    if lo is None and hi is None:
        return UNKNOWN, "; ".join(notes)
    if lo is not None and lo >= threshold:
        outcome = MET
    elif hi is not None and hi < threshold:
        outcome = NOT_MET
    else:
        outcome = PARTIAL
    if entry["informationKind"] == "ESTIMATED" and outcome == MET:
        outcome = PARTIAL
        notes.append("job figure is an estimate")
    shown = f"{_fmt(lo)}" if lo is not None else "?"
    shown += f"-{_fmt(hi)}" if hi is not None and hi != lo else ""
    why = f"job {shown} {entry['currency']}/{target['period'].lower()} vs at least {_fmt(threshold)}"
    return outcome, why + ("; " + "; ".join(notes) if notes else "")


def _location_check(constraint: dict, job: dict) -> tuple[str, str]:
    work_model = job.get("offer", {}).get("workModel")
    if isinstance(work_model, dict) and work_model.get("arrangement") == "REMOTE":
        return NA, "fully remote job; commute does not apply"
    locations = job.get("offer", {}).get("locations")
    if not isinstance(locations, list):
        return UNKNOWN, "job location not stated"
    results: list[tuple[str, str]] = []
    commute = constraint.get("commute")
    if commute:
        origin = commute["origin"].get("geo")
        for loc in locations:
            parts, notes = [], []
            limit = commute.get("maxOneWayDistance")
            if limit:
                if limit["measurement"] != "STRAIGHT_LINE":
                    parts.append(UNKNOWN)
                    notes.append("route distance needs a routing service (not part of the demo)")
                elif origin is None or "geo" not in loc:
                    parts.append(UNKNOWN)
                    notes.append("coordinates missing")
                else:
                    km = _haversine_km(origin, loc["geo"])
                    max_km = limit["value"] * (1.609344 if limit["unitCode"] == "SMI" else 1.0)
                    slack = origin["precisionKm"] + loc["geo"]["precisionKm"]
                    outcome = MET if km + slack <= max_km else NOT_MET if km - slack > max_km else PARTIAL
                    if outcome == NOT_MET and commute.get("relocationPossible"):
                        outcome = PARTIAL
                        notes.append("relocation possible")
                    parts.append(outcome)
                    notes.append(f"{km:.1f} km straight line (+/-{slack:.1f} km) vs max {max_km:.1f} km")
            if "maxOneWayDuration" in commute:
                parts.append(UNKNOWN)
                d = commute["maxOneWayDuration"]
                notes.append(f"travel time limit {_fmt(d['value'])} {d['unitCode']} needs routing or timetable data; not derived from distance")
            if not parts and commute.get("relocationPossible"):
                parts.append(MET)
                notes.append("relocation possible")
            results.append((combine(parts), f"{loc.get('locality', loc['countryCode'])}: " + "; ".join(notes)))
    for place in constraint.get("places", []):
        for loc in locations:
            same = loc["countryCode"] == place["countryCode"] and all(
                loc.get(k) == place[k] for k in ("region", "locality") if k in place
            )
            results.append((MET if same else NOT_MET, f"{loc.get('locality', loc['countryCode'])} vs acceptable place {place.get('locality', place.get('region', place['countryCode']))}"))
    if not results:
        return UNKNOWN, "no comparable location condition"
    for outcome in (MET, PARTIAL, UNKNOWN, NOT_MET):
        best = [why for o, why in results if o == outcome]
        if best:
            return outcome, best[0]
    return UNKNOWN, results[0][1]


def _share_range(work_model: dict, key: str) -> tuple[float | None, float | None, str | None, list[str]]:
    notes: list[str] = []
    if key == "remoteShare":
        if work_model["arrangement"] == "REMOTE" and "remoteShare" not in work_model:
            return 100.0, 100.0, None, ["fully remote"]
        if work_model["arrangement"] == "ONSITE" and "remoteShare" not in work_model:
            return 0.0, 0.0, None, ["on-site"]
        if "remoteShare" not in work_model and work_model.get("onsiteDays", {}).get("referencePeriod") == "WEEK":
            days = work_model["onsiteDays"]["days"]
            notes.append("derived from on-site days assuming a 5-day week")
            lo = (5 - days["max"]) / 5 * 100 if "max" in days else None
            hi = (5 - days["min"]) / 5 * 100 if "min" in days else None
            return lo, hi, "WEEK", notes
    share = work_model.get(key)
    if share is None:
        return None, None, None, notes
    return share["percent"].get("min"), share["percent"].get("max"), share["referencePeriod"], notes


def _work_model_check(constraint: dict, offer: Any) -> tuple[str, str]:
    if isinstance(offer, dict) and "state" in offer:
        return (NA if offer["state"] == "NOT_APPLICABLE" else UNKNOWN), f"job work model {offer['state'].lower().replace('_', ' ')}"
    if offer is None:
        return UNKNOWN, "job work model not stated"
    parts, notes = [], []
    if "arrangements" in constraint:
        outcome, _ = _set_check(constraint["arrangements"], [offer["arrangement"]], lambda a, b: a == b)
        parts.append(outcome)
        notes.append(f"arrangement {offer['arrangement']}")
    if "remoteShareAtLeast" in constraint:
        want = constraint["remoteShareAtLeast"]
        lo, hi, period, extra = _share_range(offer, "remoteShare")
        notes += extra
        if lo is None and hi is None:
            parts.append(UNKNOWN)
            notes.append("remote share not stated (HYBRID without extent)")
        else:
            if period and period != want["referencePeriod"]:
                notes.append(f"reference periods differ ({period} vs {want['referencePeriod']}); compared as average share")
            parts.append(MET if lo is not None and lo >= want["percent"] else NOT_MET if hi is not None and hi < want["percent"] else PARTIAL)
            notes.append(f"remote share {_fmt(lo) if lo is not None else '?'}-{_fmt(hi) if hi is not None else '?'} % vs at least {_fmt(want['percent'])} %")
    if "travelShareAtMost" in constraint:
        want = constraint["travelShareAtMost"]
        lo, hi, period, _ = _share_range(offer, "travelShare")
        if lo is None and hi is None:
            parts.append(UNKNOWN)
            notes.append("travel share not stated")
        else:
            parts.append(MET if hi is not None and hi <= want["percent"] else NOT_MET if lo is not None and lo > want["percent"] else PARTIAL)
            notes.append(f"travel share up to {_fmt(hi) if hi is not None else '?'} % vs at most {_fmt(want['percent'])} %")
    return combine(parts), "; ".join(notes)


def _working_time_check(constraint: dict, offer: Any) -> tuple[str, str]:
    if isinstance(offer, dict) and "state" in offer:
        return (NA if offer["state"] == "NOT_APPLICABLE" else UNKNOWN), f"job working time {offer['state'].lower().replace('_', ' ')}"
    if offer is None:
        return UNKNOWN, "job working time not stated"
    parts, notes = [], []
    if "schedules" in constraint:
        outcome, _ = _set_check(constraint["schedules"], [offer["schedule"]] if "schedule" in offer else [], lambda a, b: a == b)
        parts.append(outcome)
        notes.append(f"schedule {offer.get('schedule', 'not stated')}")
    if "weeklyHours" in constraint:
        want, have = constraint["weeklyHours"], offer.get("weeklyHours")
        if have is None:
            parts.append(UNKNOWN)
            notes.append("weekly hours not stated")
        else:
            w_lo, w_hi = want.get("min", 0), want.get("max", math.inf)
            h_lo, h_hi = have.get("min", have.get("max")), have.get("max", have.get("min"))
            inside = w_lo <= h_lo and h_hi <= w_hi
            disjoint = h_hi < w_lo or h_lo > w_hi
            parts.append(MET if inside else NOT_MET if disjoint else PARTIAL)
            notes.append(f"{_fmt(h_lo)}-{_fmt(h_hi)} h/week vs acceptable {_fmt(w_lo)}-{_fmt(w_hi) if w_hi != math.inf else 'open'}")
    for flag, job_key in (("shiftWorkAcceptable", "shiftWork"), ("onCallDutyAcceptable", "onCallDuty")):
        if flag in constraint:
            if job_key not in offer:
                parts.append(UNKNOWN)
                notes.append(f"{job_key} not stated")
            else:
                parts.append(NOT_MET if offer[job_key] and not constraint[flag] else MET)
                notes.append(f"{job_key} {'yes' if offer[job_key] else 'no'}")
    return combine(parts), "; ".join(notes)


def _contract_check(constraint: dict, offer: Any) -> tuple[str, str]:
    if isinstance(offer, dict) and "state" in offer:
        return (NA if offer["state"] == "NOT_APPLICABLE" else UNKNOWN), f"job contract {offer['state'].lower().replace('_', ' ')}"
    if offer is None:
        return UNKNOWN, "job contract not stated"
    parts, notes = [], [offer["contractType"]]
    if "contractTypes" in constraint:
        parts.append(_set_check(constraint["contractTypes"], [offer["contractType"]], lambda a, b: a == b)[0])
    if "fixedTermMonthsAtLeast" in constraint and offer["contractType"] in ("FIXED_TERM_EMPLOYMENT", "TEMPORARY_AGENCY_WORK"):
        if "fixedTermMonths" not in offer:
            parts.append(UNKNOWN)
            notes.append("term length not stated")
        else:
            parts.append(MET if offer["fixedTermMonths"] >= constraint["fixedTermMonthsAtLeast"] else NOT_MET)
            notes.append(f"{_fmt(offer['fixedTermMonths'])} months vs at least {_fmt(constraint['fixedTermMonthsAtLeast'])}")
    return combine(parts), "; ".join(notes)


def _tasks_check(constraint: dict, tasks: list) -> tuple[str, str]:
    if not tasks:
        return UNKNOWN, "job tasks not stated"
    hits = lambda wanted: [t for t in wanted if any(_same_item(t, j, "taskId") for j in tasks)]
    excluded = hits(constraint.get("exclude", []))
    if excluded:
        return NOT_MET, "job includes excluded task: " + _text(excluded[0]["label"])
    include = constraint.get("include", [])
    if not include:
        return MET, "no excluded task present"
    found = hits(include)
    outcome = MET if len(found) == len(include) else PARTIAL if found else NOT_MET
    return outcome, f"{len(found)} of {len(include)} desired tasks present"


def _career_fit(candidate: dict, job: dict) -> list[dict]:
    out = _Collector()
    prefs = candidate.get("jobPreferences", {})
    offer = job.get("offer", {})
    org = job.get("hiringOrganization", {})

    def evaluate(group: str, check) -> None:
        block = prefs.get(group)
        if block is None:
            return
        if "state" in block:
            out.add(group, group, "SOFT", NA, f"candidate marked this as {block['state'].lower().replace('_', ' ')}")
            return
        for side, strength in (("hardCondition", "HARD"), ("wish", "SOFT")):
            if side in block:
                outcome, why = check(block[side])
                out.add(f"{group}/{'hard' if side == 'hardCondition' else 'wish'}", group, strength, outcome, why)

    def archetypes(c):
        outcome, why = _set_check(c, [job["archetype"]] if "archetype" in job else [], _archetype_matches)
        return outcome, f"job archetype {job['archetype']['archetypeId']}: {why}" if "archetype" in job else why

    def industries(c):
        outcome, why = _set_check(c, org.get("industries", []), _code_matches)
        codes = ", ".join(f"{i['scheme']} {i['code']}" for i in org.get("industries", []))
        return outcome, f"job industry {codes}: {why}" if codes else why

    evaluate("archetypes", archetypes)
    evaluate("careerLevel", lambda c: (lambda r: (r[0], f"job level {job.get('careerLevel', 'not stated')}"))(
        _set_check(c, [job["careerLevel"]] if "careerLevel" in job else [], lambda a, b: a == b)))
    evaluate("industries", industries)

    def organization(c):
        parts, notes = [], []
        if "organizationTypes" in c:
            parts.append(_set_check(c["organizationTypes"], [org["organizationType"]] if "organizationType" in org else [], lambda a, b: a == b)[0])
            notes.append(f"type {org.get('organizationType', 'not stated')}")
        if "sizeClasses" in c:
            parts.append(_set_check(c["sizeClasses"], [org["sizeClass"]] if "sizeClass" in org else [], lambda a, b: a == b)[0])
            notes.append(f"size {org.get('sizeClass', 'not stated')}")
        return combine(parts), "; ".join(notes)

    evaluate("organization", organization)
    evaluate("tasks", lambda c: _tasks_check(c, job.get("tasks", [])))
    evaluate("compensation", lambda c: _compensation_check(c, offer.get("compensation")))
    evaluate("location", lambda c: _location_check(c, job))
    evaluate("workModel", lambda c: _work_model_check(c, offer.get("workModel")))
    evaluate("workingTime", lambda c: _working_time_check(c, offer.get("workingTime")))
    evaluate("contract", lambda c: _contract_check(c, offer.get("contract")))

    def development(c):
        dev = offer.get("development")
        if isinstance(dev, dict) and "state" in dev:
            return (NA if dev["state"] == "NOT_APPLICABLE" else UNKNOWN), f"job development {dev['state'].lower().replace('_', ' ')}"
        paths = (dev or {}).get("paths", [])
        outcome, _ = _set_check(c["paths"], paths, lambda a, b: a == b)
        return outcome, "job paths: " + (", ".join(paths) if paths else "not stated")

    evaluate("development", development)

    domain = prefs.get("domainCriteria", {})
    for side, strength in (("hardCondition", "HARD"), ("wish", "SOFT")):
        for cond in domain.get(side, []):
            fact = next((d for d in offer.get("domainCriteria", []) if d["criterionId"] == cond["criterionId"]), None)
            outcome, why = _domain_compare(cond, fact)
            out.add(f"domainCriteria/{cond['criterionId']}", "domainCriteria", strength, outcome, f"{_text(cond['label'])}: {why}")

    return out.items


# ----------------------------------------------------------------- aggregation


def _summarize(perspective: str, criteria: list[dict], policy: dict) -> dict:
    hard = [c["outcome"] for c in criteria if c["strength"] == "HARD" and c["outcome"] != NA]
    if not hard:
        hard_status = "NONE_DEFINED"
    elif NOT_MET in hard:
        hard_status = "NOT_MET"
    elif UNKNOWN in hard or PARTIAL in hard:
        hard_status = "UNRESOLVED"
    else:
        hard_status = "ALL_MET"

    soft = [c for c in criteria if c["strength"] == "SOFT" and c["outcome"] != NA]
    per_group: dict[str, int] = {}
    for c in soft:
        per_group[c["group"]] = per_group.get(c["group"], 0) + 1
    weights = policy.get("weights", {})
    total = known = scored = 0.0
    for c in soft:
        w = weights.get(c["group"], 0.0) / per_group[c["group"]]
        total += w
        if c["outcome"] in SCORE:
            known += w
            scored += w * SCORE[c["outcome"]]
    counts = {o: sum(1 for c in criteria if c["outcome"] == o) for o in OUTCOMES}
    return {
        "perspective": perspective,
        "policyId": policy["policyId"],
        "calibrationStatus": policy["calibrationStatus"],
        "hardConditionStatus": hard_status,
        "indicativeScore": round(scored / known, 3) if known > 0 else None,
        "knownWeightCoverage": round(known / total, 3) if total > 0 else 0.0,
        "outcomeCounts": counts,
        "criteria": criteria,
    }


def match(candidate: dict, job: dict, hiring_policy: dict, career_policy: dict) -> dict:
    if hiring_policy.get("perspective") != "HIRING_FIT" or career_policy.get("perspective") != "CAREER_FIT":
        raise ValueError("policies must be a HIRING_FIT and a CAREER_FIT policy")
    result = {
        "@type": "MatchResult",
        "schemaVersion": SPEC_VERSION,
        "candidateProfileId": candidate["profileId"],
        "candidateUpdatedAt": candidate["updatedAt"],
        "jobProfileId": job["profileId"],
        "jobUpdatedAt": job["updatedAt"],
        "hiringFit": _summarize("HIRING_FIT", _hiring_fit(candidate, job), hiring_policy),
        "careerFit": _summarize("CAREER_FIT", _career_fit(candidate, job), career_policy),
        "generatedBy": {"tool": "ajms-reference", "toolVersion": __version__},
        "disclaimer": DISCLAIMER,
    }
    return result
