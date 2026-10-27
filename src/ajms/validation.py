"""Structural (JSON Schema) and semantic validation of AJMS documents.

Structural validation resolves every $ref from the local schemas directory; nothing is
fetched over the network. Semantic checks cover rules JSON Schema cannot express
(min <= max, date order, references between items).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from . import SCHEMA_DIR, SCHEMA_ID_BASE

SCHEMA_FILES = {
    "CandidateProfile": "candidate-profile.schema.json",
    "JobProfile": "job-profile.schema.json",
    "ProfileReference": "profile-reference.schema.json",
    "MatchPolicy": "match-policy.schema.json",
    "MatchResult": "match-result.schema.json",
}


@dataclass(frozen=True)
class Issue:
    level: str  # "error" or "warning"
    kind: str  # "schema" or "semantic"
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper()} [{self.kind}] {self.path or '/'}: {self.message}"


@lru_cache(maxsize=1)
def _registry() -> Registry:
    resources = []
    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        if contents.get("$id") != SCHEMA_ID_BASE + path.name:
            raise RuntimeError(f"$id of {path.name} does not match its file name")
        resources.append((contents["$id"], Resource.from_contents(contents, default_specification=DRAFT202012)))
    return Registry().with_resources(resources)


@lru_cache(maxsize=None)
def validator_for(doc_type: str) -> Draft202012Validator:
    if doc_type not in SCHEMA_FILES:
        raise KeyError(f"unknown document type {doc_type!r}")
    schema = _registry().contents(SCHEMA_ID_BASE + SCHEMA_FILES[doc_type])
    return Draft202012Validator(schema, registry=_registry())


def detect_type(doc: Any) -> str | None:
    if isinstance(doc, dict) and isinstance(doc.get("@type"), str) and doc["@type"] in SCHEMA_FILES:
        return doc["@type"]
    return None


def _pointer(parts) -> str:
    return "/" + "/".join(str(p) for p in parts) if parts else ""


def schema_issues(doc: Any, doc_type: str | None = None) -> list[Issue]:
    doc_type = doc_type or detect_type(doc)
    if doc_type is None:
        return [Issue("error", "schema", "/@type", "missing or unknown @type; expected one of " + ", ".join(SCHEMA_FILES))]
    errors = sorted(validator_for(doc_type).iter_errors(doc), key=lambda e: (list(e.absolute_path), e.message))
    return [Issue("error", "schema", _pointer(e.absolute_path), _message(e)) for e in errors]


def _short(error: ValidationError) -> str:
    """Error text without echoing large instance values (which may contain personal data)."""
    if error.validator in ("oneOf", "anyOf"):
        return "does not match any allowed form"
    if error.validator is None:
        keys = sorted(error.instance) if isinstance(error.instance, dict) else []
        return "False schema does not allow this value" + (f" (keys: {', '.join(keys)})" if keys else "")
    message = error.message
    return message if len(message) <= 160 else message[:157] + "..."


def _leaf_errors(errors) -> Iterator[ValidationError]:
    for error in errors:
        if error.context:
            yield from _leaf_errors(error.context)
        else:
            yield error


def _message(error: ValidationError) -> str:
    """For oneOf/anyOf, name the most specific failing sub-check (deepest instance path)."""
    message = _short(error)
    if error.context:
        leaves = list(_leaf_errors(error.context))
        informative = [e for e in leaves if not (e.validator == "required" and "'state'" in e.message)] or leaves
        cause = max(informative, key=lambda e: (len(e.absolute_path), -len(e.message)))
        message += f"; closest cause at {_pointer(cause.absolute_path) or '/'}: {_short(cause)}"
    return message


# ---------------------------------------------------------------- semantic checks


def _walk(node: Any, path: tuple = ()) -> Iterator[tuple[tuple, Any]]:
    yield path, node
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _walk(value, path + (key,))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk(value, path + (index,))


def _semantic_issues(doc: dict, doc_type: str) -> list[Issue]:
    issues: list[Issue] = []

    def err(path, msg):
        issues.append(Issue("error", "semantic", _pointer(path), msg))

    def warn(path, msg):
        issues.append(Issue("warning", "semantic", _pointer(path), msg))

    for path, node in _walk(doc):
        if not isinstance(node, dict):
            continue
        lo, hi = node.get("min"), node.get("max")
        if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and not isinstance(lo, bool) and lo > hi:
            err(path, f"min ({lo}) is greater than max ({hi})")
        early, late = node.get("earliestStartDate"), node.get("latestStartDate")
        if isinstance(early, str) and isinstance(late, str) and early > late:
            err(path, "earliestStartDate is after latestStartDate")
        start, end = node.get("startMonth"), node.get("endMonth")
        if isinstance(start, str) and isinstance(end, str) and start > end:
            err(path, "startMonth is after endMonth")
        if node.get("ongoing") is True and "endMonth" in node:
            err(path, "an ongoing entry must not have endMonth")
        if "component" in node and "currency" in node and "hoursPerWeekBasis" not in node and node.get("period") != "HOUR":
            warn(path, "compensation has no hoursPerWeekBasis; its hours basis is unknown")

    if isinstance(doc.get("datePosted"), str) and isinstance(doc.get("validThrough"), str):
        if doc["datePosted"] > doc["validThrough"]:
            err(("validThrough",), "validThrough is before datePosted")

    # Identifiers must be unique within their list.
    id_keys = ("competencyId", "qualificationId", "taskId", "domainId", "experienceId", "evidenceId", "requirementId")
    for path, node in _walk(doc):
        if isinstance(node, list):
            for key in id_keys:
                seen: set[str] = set()
                for index, item in enumerate(node):
                    if isinstance(item, dict) and key in item:
                        if item[key] in seen:
                            err(path + (index, key), f"duplicate {key} {item[key]!r}")
                        seen.add(item[key])

    # Evidence references.
    evidence_ids = {e.get("evidenceId") for e in doc.get("evidence", []) if isinstance(e, dict)}
    for path, node in _walk(doc):
        if isinstance(node, dict) and isinstance(node.get("evidenceRefs"), list):
            for ref in node["evidenceRefs"]:
                if "evidence" in doc and ref not in evidence_ids:
                    err(path + ("evidenceRefs",), f"evidence {ref!r} is not listed in /evidence")
                elif "evidence" not in doc:
                    warn(path + ("evidenceRefs",), f"evidence {ref!r} is referenced but not included in this view")

    # Field statements of imported profiles must point at existing, distinct fields.
    seen_paths: set[str] = set()
    for index, statement in enumerate(doc.get("fieldStatements", [])):
        where = ("fieldStatements", index, "path")
        if statement["path"] in seen_paths:
            err(where, f"duplicate statement for {statement['path']}")
        seen_paths.add(statement["path"])
        if not _resolves(doc, statement["path"]):
            err(where, f"{statement['path']} does not resolve in this document")

    if doc_type == "CandidateProfile" and doc.get("profileView") == "PUBLIC_MINIMAL":
        for path, node in _walk(doc):
            if isinstance(node, dict) and "latitude" in node and node.get("precisionKm", 0) < 10:
                err(path, "PUBLIC_MINIMAL requires geo precisionKm >= 10")
            if isinstance(node, dict) and "postalCode" in node:
                err(path + ("postalCode",), "PUBLIC_MINIMAL must not contain postal codes")

    return issues


def _resolves(doc: Any, pointer: str) -> bool:
    node = doc
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and token in node:
            node = node[token]
        elif isinstance(node, list) and token.isdigit() and int(token) < len(node):
            node = node[int(token)]
        else:
            return False
    return True


def validate_document(doc: Any, doc_type: str | None = None) -> list[Issue]:
    """Return all issues. Semantic checks run only when the structure is valid."""
    issues = schema_issues(doc, doc_type)
    if issues:
        return issues
    return _semantic_issues(doc, doc_type or detect_type(doc))


def has_errors(issues: list[Issue]) -> bool:
    return any(i.level == "error" for i in issues)


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
