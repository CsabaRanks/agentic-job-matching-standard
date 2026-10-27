"""Conversion report: source data -> field mapping -> conversion -> validation -> readable output."""

from __future__ import annotations

from ..jsonld_check import check_jsonld
from ..match import match
from ..render import render
from ..validation import _resolves, validate_document
from .base import Conversion

CORE = {
    "JobProfile": [
        ("/hiringOrganization/organizationType", "organization type (employer or agency)"),
        ("/hiringOrganization/industries", "industry"), ("/hiringOrganization/sizeClass", "company size"),
        ("/archetype", "job archetype"), ("/careerLevel", "career level"), ("/leadership", "leadership responsibility"),
        ("/tasks", "tasks"), ("/requirements/competencies", "competency requirements"),
        ("/requirements/languages", "language requirements"), ("/requirements/qualifications", "qualification requirements"),
        ("/requirements/domainExperience", "experience requirements"), ("/requirements/workAuthorization", "work authorization"),
        ("/requirements/startTiming", "start date"), ("/offer/compensation", "compensation"), ("/offer/locations", "work location"),
        ("/offer/workModel", "work model"), ("/offer/workModel/remoteShare", "remote share"),
        ("/offer/workModel/onsiteDays", "on-site days"), ("/offer/workModel/travelShare", "travel share"),
        ("/offer/workingTime/schedule", "full-time / part-time"), ("/offer/workingTime/weeklyHours", "weekly hours"),
        ("/offer/workingTime/shiftWork", "shift work"), ("/offer/contract", "contract type"),
        ("/offer/development", "development perspectives"), ("/datePosted", "posting date"),
        ("/validThrough", "application deadline"),
    ],
    "CandidateProfile": [
        ("/capabilities/currentCareerLevel", "current career level"), ("/capabilities/archetypes", "practised job archetypes"),
        ("/capabilities/competencies", "competencies"), ("/capabilities/languages", "languages"),
        ("/capabilities/qualifications", "qualifications"), ("/capabilities/domainExperience", "experience by domain (months)"),
        ("/capabilities/totalExperienceMonths", "total experience (months)"),
        ("/capabilities/workAuthorizations", "work authorization"), ("/experienceHistory", "experience history"),
        ("/jobPreferences/archetypes", "wished job archetypes"), ("/jobPreferences/careerLevel", "wished career level"),
        ("/jobPreferences/industries", "industry preferences"), ("/jobPreferences/compensation", "compensation expectation"),
        ("/jobPreferences/location", "location / commute"), ("/jobPreferences/workModel", "work model / remote share"),
        ("/jobPreferences/workingTime", "working time"), ("/jobPreferences/contract", "contract preferences"),
        ("/jobPreferences/development", "development wishes"), ("/availability", "availability / start date"),
        ("/searchStatus", "search status"),
    ],
}


def unknown_core_fields(profile: dict) -> list[tuple[str, str]]:
    unknown = []
    arrangement = profile.get("offer", {}).get("workModel", {}).get("arrangement")
    for path, label in CORE[profile["@type"]]:
        if path in ("/offer/workModel/remoteShare", "/offer/workModel/onsiteDays") and arrangement in ("REMOTE", "ONSITE"):
            continue  # follows from the arrangement
        if not _resolves(profile, path):
            unknown.append((path, label))
    return unknown


def _value(profile: dict, path: str):
    node = profile
    for token in path.split("/")[1:]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    if isinstance(node, dict) and "text" in node:
        return node["text"]
    if isinstance(node, dict) and "archetypeId" in node:
        return node["archetypeId"]
    if isinstance(node, dict):
        return ", ".join(f"{k}={v}" for k, v in node.items() if not isinstance(v, (dict, list)))
    if isinstance(node, list):
        return ", ".join(str(v) for v in node)
    return node


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_conversion_report(conv: Conversion, profile_file: str, *, lang: str = "en", candidate: dict | None = None,
                             hiring_policy: dict | None = None, career_policy: dict | None = None) -> str:
    profile = conv.profile
    src = profile["source"]
    q = src["extractionQuality"]
    out = [
        f"# Conversion report: {src['sourceFormat']} → {profile['@type']}",
        "",
        f"Adapter `{src['importedBy']['tool']}`, rules `{src['importedBy']['toolVersion']}`. Deterministic, no network, "
        "no language model. Synthetic input.",
        "",
        "## 1. Source data",
        "",
        f"- **Format:** `{src['sourceFormat']}` ({'structured fields, mapped directly' if src['inputKind'] == 'STRUCTURED' else 'free text, values extracted'})",
        f"- **Source reference:** {src['sourceUrl']}" + (f" (file `{src['sourceFileName']}`)" if "sourceFileName" in src else ""),
    ]
    if "sourceRecordId" in src:
        out.append(f"- **Record ID in the source:** `{src['sourceRecordId']}`")
    out += [f"- **Retrieved / provided:** {src['retrievedAt']}", f"- **SHA-256:** `{src['textDigest']['value']}`", ""]
    for name, content in sorted(conv.original.items()):
        out += [f"`{name}`:", "", "```text", content.rstrip("\n"), "```", ""]

    title = "Extraction quality" if src["inputKind"] == "TEXT" else "Structural checks"
    out += [f"## 2. {title}", "", f"- **Status:** {q['status']}"]
    if "recognizedShare" in q:
        out.append(f"- **Recognized lines:** {q['recognizedShare']:.1%}")
    out += [f"- {check}" for check in q["checks"]]
    out.append("")

    out += ["## 3. Field mapping", "",
            "| Target field (JSON Pointer) | Value | Statement | Source excerpt | Method | Note |", "|---|---|---|---|---|---|"]
    for s in profile["fieldStatements"]:
        kind = s["statementKind"] + (" · lossy" if s.get("lossy") else "")
        out.append("| " + " | ".join(_cell(c) for c in (f"`{s['path']}`", _value(profile, s["path"]), kind,
                                                            s.get("sourceExcerpt", "–"), s.get("method", "–"),
                                                            s.get("note", ""))) + " |")
    counts = {k: sum(1 for s in profile["fieldStatements"] if s["statementKind"] == k) for k in ("EXPLICIT", "NORMALIZED", "DERIVED")}
    lossy = sum(1 for s in profile["fieldStatements"] if s.get("lossy"))
    out += ["", "Explicit, normalized, derived: " + ", ".join(f"{k} {v}" for k, v in counts.items())
            + f"; with loss of meaning: {lossy}.", ""]

    out += ["## 4. Conversion result", "", f"Profile: [`{profile_file}`]({profile_file}) "
            f"(`{profile['@type']}`, `profileView` {profile['profileView']}).", "",
            "**Not carried into the profile** (field names only, values are not stored):", ""]
    out += [f"- `{u['sourceField']}` — {u['reason']}" + (f": {u['note']}" if u.get("note") else "")
            for u in src.get("unmapped", [])] or ["- nothing"]
    out += ["", "**Unknown** (absent from the source, therefore absent from the profile):", ""]
    out += [f"- {label} (`{path}`)" for path, label in unknown_core_fields(profile)] or ["- nothing"]

    issues = validate_document(profile)
    report = check_jsonld(profile)
    out += ["", "## 5. AJMS validation", "",
            "- **JSON Schema + semantic rules:** " + ("valid" if not any(i.level == "error" for i in issues) else "INVALID")]
    out += [f"  - {issue}" for issue in issues]
    out.append(f"- **JSON-LD:** {'ok' if report.ok else 'FAILED'}, {report.statements} RDF statements")

    if candidate is not None and profile["@type"] == "JobProfile":
        result = match(candidate, profile, hiring_policy, career_policy)
        out += ["", "## 6. Matching (demonstration)", "",
                f"Candidate `{candidate['profileId']}`; weights `{hiring_policy['policyId']}` / `{career_policy['policyId']}` (UNCALIBRATED).", ""]
        for key, name in (("hiringFit", "Hiring-Fit"), ("careerFit", "Career-Fit")):
            part = result[key]
            score = "–" if part["indicativeScore"] is None else f"{part['indicativeScore']:.2f}"
            out.append(f"- **{name}:** hard conditions {part['hardConditionStatus']}, indicative score {score}, "
                       f"known weight coverage {part['knownWeightCoverage']:.0%}")
        out += ["", "| Perspective | Criterion | Type | Outcome | Explanation |", "|---|---|---|---|---|"]
        for key, name in (("hiringFit", "Hiring"), ("careerFit", "Career")):
            for c in result[key]["criteria"]:
                outcome = f"**{c['outcome']}**" if c["outcome"] in ("UNKNOWN", "NOT_MET") else c["outcome"]
                out.append(f"| {name} | `{c['criterionKey']}` | {c['strength']} | {outcome} | {_cell(c['explanation'])} |")
        out += ["", "> " + result["disclaimer"]]

    rendered = render(profile, lang)
    shifted = "\n".join(("##" + line) if line.startswith("#") else line for line in rendered.splitlines())
    out += ["", f"## {'7' if candidate is not None and profile['@type'] == 'JobProfile' else '6'}. Human-readable output ({lang})", "", shifted]
    return "\n".join(out).rstrip() + "\n"
