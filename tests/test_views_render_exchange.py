import copy
import json

import pytest

from ajms.exchange import content_digest, make_reference
from ajms.render import render
from ajms.schemaorg_export import to_job_posting
from ajms.validation import has_errors, validate_document
from ajms.views import derive_view


def _strings(node):
    return json.dumps(node, ensure_ascii=False)


def test_shared_view_removes_identity_and_coarsens(private_candidate):
    shared = derive_view(private_candidate, "SHARED_VIEW")
    assert "identity" not in shared
    assert shared["profileId"] != private_candidate["profileId"]
    text = _strings(shared)
    for secret in ("jordan.example@example.org", "Jordan Example", "Example Foods GmbH", "21073"):
        assert secret not in text
    assert not has_errors(validate_document(shared))


def test_public_minimal_view(private_candidate):
    public = derive_view(private_candidate, "PUBLIC_MINIMAL")
    for key in ("identity", "experienceHistory", "evidence", "summary"):
        assert key not in public
    assert not has_errors(validate_document(public))
    origin = public["jobPreferences"]["location"]["hardCondition"]["commute"]["origin"]["geo"]
    assert origin["precisionKm"] >= 10


def test_views_are_derived_only_from_private_profiles(shared_candidate):
    with pytest.raises(ValueError):
        derive_view(shared_candidate, "PUBLIC_MINIMAL")


def test_render_is_deterministic_and_shows_unknowns(agency_job):
    first, second = render(agency_job, "en"), render(copy.deepcopy(agency_job), "en")
    assert first == second
    assert "not disclosed" in first
    assert "remote share unknown" in first
    assert "| Entwicklung | unbekannt |" in render(agency_job, "de")


def test_candidate_render_lists_every_preference_criterion(shared_candidate):
    text = render(shared_candidate, "en")
    for label in ("Compensation", "Location", "Work model", "Working time", "Contract", "Development"):
        assert f"| {label} |" in text


def test_digest_is_stable_and_content_sensitive(job):
    digest = content_digest(job)
    assert digest == content_digest(json.loads(json.dumps(job)))
    changed = copy.deepcopy(job)
    changed["offer"]["compensation"][0]["min"] += 1
    assert content_digest(changed) != digest


def test_reference_is_valid_and_private_profiles_are_not_public(private_candidate, job):
    reference = make_reference(job, "https://example.com/job.json", "PUBLIC")
    assert validate_document(reference) == []
    private_ref = make_reference(private_candidate, "https://example.org/p.json", "PUBLIC")
    assert has_errors(validate_document(private_ref))


def test_schemaorg_export_only_for_public_jobs(job, private_candidate):
    posting = to_job_posting(job)
    assert posting["@type"] == "JobPosting"
    assert posting["baseSalary"]["value"]["unitText"] == "YEAR"
    for key in ("title", "description", "datePosted", "hiringOrganization", "jobLocation"):
        assert key in posting
    with pytest.raises(ValueError):
        to_job_posting(private_candidate)
    internal = dict(job, profileView="FULL_PRIVATE")
    with pytest.raises(ValueError):
        to_job_posting(internal)
