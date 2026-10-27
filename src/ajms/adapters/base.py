"""Shared machinery for import adapters.

An adapter converts *provided* source data (a file, an export, pasted text) into an AJMS
profile. It never fetches anything from a platform. Every converted field gets a
FieldStatement (EXPLICIT, NORMALIZED or DERIVED; lossy when meaning is lost); source
content that has no place in AJMS is listed in source.unmapped by field name only. Text
inputs pass an extraction-quality gate before a profile is produced.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field

from .. import CONTEXT_URL, SPEC_VERSION

TOOL = "ajms-adapters"
WORD = re.compile(r"^[(\"'„]?[A-Za-zÄÖÜäöüß0-9][A-Za-zÄÖÜäöüß0-9./&+@-]*[)\"'“,.:;!?]*$")

# Coarse city centroids (precision 10 km) used for DERIVED coordinates.
GAZETTEER = {
    "Hamburg": ("DE", 53.55, 9.99), "Bremen": ("DE", 53.08, 8.80), "Berlin": ("DE", 52.52, 13.40),
    "München": ("DE", 48.14, 11.58), "Leipzig": ("DE", 51.34, 12.37), "Köln": ("DE", 50.94, 6.96),
    "Frankfurt am Main": ("DE", 50.11, 8.68), "Stuttgart": ("DE", 48.78, 9.18),
}
COUNTRY_NAMES = {"deutschland": "DE", "germany": "DE", "österreich": "AT", "austria": "AT", "schweiz": "CH",
                 "switzerland": "CH", "niederlande": "NL", "netherlands": "NL", "frankreich": "FR", "france": "FR"}


class ConversionRejected(Exception):
    """The input did not pass the adapter's checks; no profile is produced."""

    def __init__(self, source_format: str, checks: list[str]):
        super().__init__(f"{source_format}: input rejected: " + "; ".join(checks))
        self.source_format = source_format
        self.checks = checks


@dataclass
class Conversion:
    profile: dict
    original: dict[str, str]                       # file or part name -> original content
    uninterpreted: list[str] = field(default_factory=list)


class Recorder:
    """Collects field statements and unmapped source content during a conversion."""

    def __init__(self) -> None:
        self.statements: list[dict] = []
        self.unmapped: list[dict] = []
        self.checks: list[str] = []

    def say(self, path: str, kind: str, excerpt: str | None = None, method: str | None = None,
            note: str | None = None, lossy: bool = False) -> None:
        item: dict = {"path": path, "statementKind": kind}
        if excerpt is not None:
            item["sourceExcerpt"] = excerpt
        if method is not None:
            item["method"] = method
        if lossy:
            item["lossy"] = True
        if note is not None:
            item["note"] = note
        self.statements.append(item)

    def skip(self, source_field: str, reason: str, note: str | None = None) -> None:
        item = {"sourceField": source_field, "reason": reason}
        if note:
            item["note"] = note
        self.unmapped.append(item)


def slug(text: str) -> str:
    text = text.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:60] or "item"


def text_value(value: str, language: str) -> dict:
    return {"text": value, "language": language}


def digest_parts(parts: dict[str, str]) -> str:
    """SHA-256 of one text, or of several files as 'name\\n' + content, in name order."""
    if len(parts) == 1:
        return hashlib.sha256(next(iter(parts.values())).encode("utf-8")).hexdigest()
    hasher = hashlib.sha256()
    for name in sorted(parts):
        hasher.update(name.encode("utf-8") + b"\n" + parts[name].encode("utf-8"))
    return hasher.hexdigest()


def readable_share(text: str) -> float:
    tokens = [t for t in text.split() if len(t) >= 2]
    if not tokens:
        return 0.0
    return sum(1 for t in tokens if WORD.match(t)) / len(tokens)


def text_quality(source_format: str, text: str, anchors: list[str], recognized: int, total: int,
                 uninterpreted: list[str], excerpts: list[str]) -> dict:
    """Extraction-quality gate for text input. Raises ConversionRejected or returns a quality record."""
    share = readable_share(text)
    tokens = len(text.split())
    checks = [f"{tokens} tokens (minimum 30)", f"readable word share {share:.0%} (minimum 60%)"]
    problems = []
    if tokens < 30:
        problems.append(f"almost no text ({tokens} tokens); the document probably has no text layer (scan or image)")
    elif share < 0.6:
        problems.append(f"text layer is not readable ({share:.0%} word-like tokens); use OCR or enter the data manually")
    missing = [a for a in anchors if a not in text]
    checks.append("layout anchors present" if not missing else f"layout anchors missing: {missing}")
    if missing:
        problems.append(f"layout anchors missing: {missing}")
    not_found = [e for e in excerpts if e not in text]
    checks.append("every source excerpt found verbatim in the input" if not not_found
                  else f"{len(not_found)} excerpts not found verbatim")
    if not_found:
        problems.append("source excerpts not found verbatim (adapter defect)")
    if problems:
        raise ConversionRejected(source_format, problems)
    checks.append(f"{recognized} of {total} non-empty lines recognized, {len(uninterpreted)} not interpreted")
    return {
        "status": "PASSED" if not uninterpreted else "REVIEW",
        "recognizedShare": round(recognized / total, 3) if total else 0.0,
        "uninterpretedLines": len(uninterpreted),
        "checks": checks,
    }


def new_profile(profile_type: str, parts: dict[str, str], source_url: str | None, language: str) -> dict:
    digest = digest_parts(parts)
    url = source_url or f"urn:sha256:{digest}"
    return {
        "@context": CONTEXT_URL,
        "@type": profile_type,
        "profileId": "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"{url}#{digest}")),
        "schemaVersion": SPEC_VERSION,
        "updatedAt": None,  # set by finish()
        "profileView": "FULL_PRIVATE",
        "defaultLanguage": language,
    }


def finish(profile: dict, rec: Recorder, parts: dict[str, str], *, source_url: str | None, retrieved_at: str,
           source_kind: str, source_format: str, input_kind: str, rules_version: str, quality: dict,
           file_name: str | None = None, record_id: str | None = None) -> dict:
    digest = digest_parts(parts)
    profile["updatedAt"] = retrieved_at
    source: dict = {"sourceUrl": source_url or f"urn:sha256:{digest}"}
    if file_name:
        source["sourceFileName"] = file_name
    if record_id:
        source["sourceRecordId"] = record_id
    source.update({
        "retrievedAt": retrieved_at,
        "sourceKind": source_kind,
        "sourceFormat": source_format,
        "inputKind": input_kind,
        "textDigest": {"algorithm": "SHA-256", "value": digest},
        "importedBy": {"tool": TOOL, "toolVersion": rules_version},
        "extractionQuality": quality,
    })
    if rec.unmapped:
        source["unmapped"] = rec.unmapped
    profile["source"] = source
    profile["fieldStatements"] = sorted(rec.statements, key=lambda s: s["path"])
    return profile


def place_from_city(city: str, rec: Recorder, base: str, excerpt: str, country: str | None = None) -> dict:
    """Place with country and DERIVED coarse coordinates when the city is in the gazetteer."""
    place: dict = {}
    if country:
        place["countryCode"] = country
    if city in GAZETTEER:
        g_country, lat, lon = GAZETTEER[city]
        if "countryCode" not in place:
            place["countryCode"] = g_country
            rec.say(f"{base}/countryCode", "DERIVED", city, "gazetteer-city-country")
        place["geo"] = {"latitude": lat, "longitude": lon, "precisionKm": 10}
        rec.say(f"{base}/geo", "DERIVED", excerpt, "gazetteer-city-centroid", "city centroid, precision 10 km")
    return place
