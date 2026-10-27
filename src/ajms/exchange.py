"""Minimal exchange convention: content digest and ProfileReference."""

from __future__ import annotations

import hashlib
import json

from . import CONTEXT_URL, SPEC_VERSION


def canonical_bytes(doc: dict) -> bytes:
    """AJMS-JSON-SORTED-KEYS-V1: UTF-8 JSON, keys sorted, no insignificant whitespace.

    Sufficient for documents produced by the same kind of serializer. It is not RFC 8785
    (JCS); number formatting may differ across implementations (see open questions).
    """
    return json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def content_digest(doc: dict) -> str:
    return hashlib.sha256(canonical_bytes(doc)).hexdigest()


def make_reference(doc: dict, profile_url: str, access_method: str, access_request_url: str | None = None,
                   intended_recipient: str | None = None, expires_at: str | None = None) -> dict:
    reference = {
        "@context": CONTEXT_URL,
        "@type": "ProfileReference",
        "profileId": doc["profileId"],
        "profileType": doc["@type"],
        "schemaVersion": SPEC_VERSION,
        "updatedAt": doc["updatedAt"],
        "profileView": doc["profileView"],
        "profileUrl": profile_url,
        "accessMethod": access_method,
        "mediaType": "application/ld+json",
        "contentDigest": {
            "algorithm": "SHA-256",
            "canonicalization": "AJMS-JSON-SORTED-KEYS-V1",
            "value": content_digest(doc),
        },
    }
    if access_request_url:
        reference["accessRequestUrl"] = access_request_url
    if intended_recipient:
        reference["intendedRecipient"] = intended_recipient
    if expires_at:
        reference["expiresAt"] = expires_at
    return reference
