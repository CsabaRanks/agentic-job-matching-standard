"""Derive a SHARED_VIEW or PUBLIC_MINIMAL candidate profile from a FULL_PRIVATE one.

Derivation removes and coarsens data deterministically. It reduces what is disclosed;
it does not make a profile anonymous. Combinations of the remaining attributes can still
identify a person, and anything shared can be kept by its recipient.
"""

from __future__ import annotations

import copy
import uuid

SHARED_DROP = ("identity",)
PUBLIC_KEEP_TOP = (
    "@context", "@type", "profileId", "schemaVersion", "updatedAt", "profileView", "defaultLanguage",
    "headline", "capabilities", "jobPreferences", "availability", "searchStatus",
)
PUBLIC_KEEP_CAPABILITIES = ("currentCareerLevel", "archetypes", "competencies", "languages", "qualifications", "totalExperienceMonths")
PUBLIC_KEEP_PREFERENCES = ("archetypes", "careerLevel", "industries", "workModel", "workingTime", "contract", "location")


def _derived_id(profile_id: str, view: str) -> str:
    """A new, stable id per view so that the views cannot be joined by id alone."""
    return "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"{profile_id}#{view}"))


def _coarsen_geo(node, precision_km: float) -> None:
    if isinstance(node, dict):
        if "latitude" in node and "longitude" in node:
            if node.get("precisionKm", 0) < precision_km:
                node["latitude"] = round(node["latitude"], 1)
                node["longitude"] = round(node["longitude"], 1)
                node["precisionKm"] = precision_km
        for value in node.values():
            _coarsen_geo(value, precision_km)
    elif isinstance(node, list):
        for value in node:
            _coarsen_geo(value, precision_km)


def _drop_keys(node, keys: tuple[str, ...]) -> None:
    if isinstance(node, dict):
        for key in keys:
            node.pop(key, None)
        for value in node.values():
            _drop_keys(value, keys)
    elif isinstance(node, list):
        for value in node:
            _drop_keys(value, keys)


def derive_view(profile: dict, view: str) -> dict:
    if profile.get("@type") != "CandidateProfile" or profile.get("profileView") != "FULL_PRIVATE":
        raise ValueError("derive_view expects a FULL_PRIVATE CandidateProfile")
    if view not in ("SHARED_VIEW", "PUBLIC_MINIMAL"):
        raise ValueError("view must be SHARED_VIEW or PUBLIC_MINIMAL")
    out = copy.deepcopy(profile)
    out["profileId"] = _derived_id(profile["profileId"], view)
    out["profileView"] = view
    for key in SHARED_DROP:
        out.pop(key, None)
    # Employer names and document links are the most direct identifiers after the name itself.
    for entry in out.get("experienceHistory", []):
        entry.get("organization", {}).pop("name", None)
        entry.get("organization", {}).pop("url", None)
        if entry.get("organization") == {}:
            entry.pop("organization")
    for evidence in out.get("evidence", []):
        evidence.pop("documentUrl", None)
        evidence.pop("issuerName", None)
    _drop_keys(out, ("postalCode", "locality"))
    _coarsen_geo(out, 5.0)
    if view == "SHARED_VIEW":
        return out

    public = {k: out[k] for k in PUBLIC_KEEP_TOP if k in out}
    caps = public.get("capabilities", {})
    public["capabilities"] = {k: caps[k] for k in PUBLIC_KEEP_CAPABILITIES if k in caps}
    prefs = public.get("jobPreferences", {})
    public["jobPreferences"] = {k: prefs[k] for k in PUBLIC_KEEP_PREFERENCES if k in prefs}
    # Evidence documents are not part of a public view. The opaque evidenceRefs stay so that
    # an evidenced statement remains marked as such; the documents can be shared on request.
    _drop_keys(public, ("issuerName", "completedOn", "lastUsedYear"))
    _coarsen_geo(public, 10.0)
    if "availability" in public:
        public["availability"] = {k: v for k, v in public["availability"].items() if k in ("immediate", "earliestStartDate")}
    return public
