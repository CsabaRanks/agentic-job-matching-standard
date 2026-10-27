"""JSON-LD semantic check, separate from JSON Schema validation.

A JSON-LD processor silently drops keys that the context does not map to an IRI, so a
document can be schema-valid and still lose meaning as Linked Data. This check
(1) reports every key that is not a term of the AJMS context (the context is flat, so this
is exact), and (2) expands the document and converts it to RDF with the local context
(no network access), reporting the number of RDF statements produced.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from pyld import jsonld

from . import CONTEXT_FILE, CONTEXT_URL


@lru_cache(maxsize=1)
def context_terms() -> dict:
    return json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))["@context"]


def _local_loader(url: str, options: dict | None = None) -> dict:
    if url != CONTEXT_URL:
        raise jsonld.JsonLdError(
            f"remote document {url} not available offline", "jsonld.LoadDocumentError", code="loading document failed"
        )
    return {
        "contextUrl": None,
        "documentUrl": url,
        "document": {"@context": context_terms()},
        "contentType": "application/ld+json",
    }


@dataclass
class JsonLdReport:
    statements: int
    undefined_terms: list[str]
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and not self.undefined_terms and self.statements > 0


def _undefined(node: Any, terms: dict, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "@context":
                continue
            here = f"{prefix}/{key}"
            if not key.startswith("@") and key not in terms:
                found.append(here)
            found += _undefined(value, terms, here)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found += _undefined(value, terms, f"{prefix}/{index}")
    return found


def check_jsonld(doc: dict) -> JsonLdReport:
    undefined = _undefined(doc, context_terms())
    try:
        nquads = jsonld.to_rdf(copy.deepcopy(doc), {"documentLoader": _local_loader, "format": "application/n-quads"})
    except jsonld.JsonLdError as exc:
        return JsonLdReport(statements=0, undefined_terms=undefined, error=str(exc).splitlines()[0])
    statements = len([line for line in nquads.splitlines() if line.strip()])
    return JsonLdReport(statements=statements, undefined_terms=undefined)


def to_nquads(doc: dict) -> str:
    return jsonld.to_rdf(copy.deepcopy(doc), {"documentLoader": _local_loader, "format": "application/n-quads"})
