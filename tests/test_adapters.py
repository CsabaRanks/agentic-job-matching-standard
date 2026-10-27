"""Import adapters: source data -> field mapping -> conversion -> validation -> readable output."""

import copy
import hashlib
import json

import pytest

from ajms.adapters import ConversionRejected, ba_text, convert_path, job_ad_text, json_resume, linkedin_csv
from ajms.adapters.base import readable_share
from ajms.adapters.report import render_conversion_report, unknown_core_fields
from ajms.jsonld_check import check_jsonld
from ajms.match import match
from ajms.schemaorg_export import to_job_posting
from ajms.validation import validate_document
from ajms.views import derive_view

from conftest import ROOT, load

A = ROOT / "examples" / "adapters"
T = "2026-10-27T12:00:00+01:00"
CASES = {
    "ba": ("ba-bewerberprofil-text", A / "ba-bewerberprofil-text" / "synthetic-demand-planner.ba.txt"),
    "linkedin": ("linkedin-data-export-csv", A / "linkedin-data-export-csv" / "export"),
    "resume": ("json-resume-1", A / "json-resume-1" / "synthetic-icu-nurse.resume.json"),
    "jobad": ("job-ad-text-de", A / "job-ad-text-de" / "senior-demand-planner.ad.de.txt"),
}


@pytest.fixture(params=sorted(CASES))
def case(request):
    fmt, path = CASES[request.param]
    return request.param, convert_path(fmt, path, retrieved_at=T, source_url="https://example.org/source")


def value_at(doc, pointer):
    node = doc
    for token in pointer.split("/")[1:]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def original_text(conv):
    return "\n".join(conv.original.values())


def test_converted_profiles_are_valid_and_linked_data(case):
    _, conv = case
    assert [i for i in validate_document(conv.profile) if i.level == "error"] == []
    assert check_jsonld(conv.profile).ok


def test_source_reference_and_digest_are_kept(case):
    _, conv = case
    src = conv.profile["source"]
    assert src["sourceUrl"] == "https://example.org/source"
    assert src["retrievedAt"] == T
    assert src["sourceFormat"] in CASES[case[0]][0]
    if len(conv.original) == 1:
        assert src["textDigest"]["value"] == hashlib.sha256(next(iter(conv.original.values())).encode()).hexdigest()


def test_statements_distinguish_explicit_normalized_derived(case):
    _, conv = case
    text = original_text(conv)
    for s in conv.profile["fieldStatements"]:
        if "sourceExcerpt" in s:
            assert s["sourceExcerpt"] in text, s
        if s["statementKind"] == "EXPLICIT":
            value = value_at(conv.profile, s["path"])
            assert (value["text"] if isinstance(value, dict) else value) == s["sourceExcerpt"], s
        else:
            assert s.get("method"), s
        if s.get("lossy"):
            assert s.get("note"), s


def test_input_kind_and_quality(case):
    name, conv = case
    src = conv.profile["source"]
    assert src["inputKind"] == ("TEXT" if name in ("ba", "jobad") else "STRUCTURED")
    if src["inputKind"] == "TEXT":
        assert "recognizedShare" in src["extractionQuality"]
        assert any("readable word share" in c for c in src["extractionQuality"]["checks"])


def test_unmapped_content_is_listed_without_values(case):
    _, conv = case
    unmapped = json.dumps(conv.profile["source"].get("unmapped", []), ensure_ascii=False)
    for secret in ("weiblich", "Alter: 30", "Musterstraße", "Jan 1, 1990", "ABC-123", "Beispielweg", "Synthetic reference text"):
        assert secret not in unmapped
        assert secret not in json.dumps(conv.profile, ensure_ascii=False)


def test_report_has_every_stage(case):
    _, conv = case
    report = render_conversion_report(conv, "profile.json")
    for heading in ("## 1. Source data", "## 3. Field mapping", "## 4. Conversion result", "## 5. AJMS validation",
                    "Human-readable output"):
        assert heading in report


def test_ba_specifics():
    conv = ba_text.convert(CASES["ba"][1].read_text(encoding="utf-8"), retrieved_at=T)
    p, reasons = conv.profile, {u["reason"] for u in conv.profile["source"]["unmapped"]}
    assert {"PROTECTED_CHARACTERISTIC_NOT_MAPPED", "INTERMEDIARY_CONTACT", "REDUNDANT", "NOT_INTERPRETED"} <= reasons
    assert p["source"]["extractionQuality"]["status"] == "REVIEW"  # the fixture has one unknown row
    assert p["source"]["sourceRecordId"] == "10000-0000000000-S"
    assert p["jobPreferences"]["archetypes"]["wish"]["include"][0]["archetypeId"] == "demand-planner"
    assert p["jobPreferences"]["location"]["wish"]["commute"]["maxOneWayDistance"]["value"] == 40
    assert len([q for q in p["capabilities"]["qualifications"] if q["qualificationType"] == "CERTIFICATION"]) == 1
    assert len(p["experienceHistory"][0]["tasks"]) == 2
    lossy = {s["path"] for s in p["fieldStatements"] if s.get("lossy")}
    assert "/capabilities/languages/1/cefrLevel" in lossy  # "Verhandlungssicher" -> C1 has no official equivalence
    assert "compensation" not in p.get("jobPreferences", {})  # not in the source -> unknown
    assert ("/jobPreferences/compensation", "compensation expectation") in unknown_core_fields(p)


@pytest.mark.parametrize("text, reason", [
    ("$%&'()*&'%+,-)(./01%,+)( 20&'34*5-(6)(%%, " * 20, "not readable"),
    ("Ihr Bewerberprofil", "almost no text"),
    ("Ein beliebiger Text ohne die erwartete Struktur eines Bewerberprofils " * 5, "layout anchors missing"),
])
def test_ba_quality_gate_rejects_unusable_text(text, reason):
    with pytest.raises(ConversionRejected) as exc:
        ba_text.convert(text, retrieved_at=T)
    assert any(reason in c for c in exc.value.checks)


def test_readable_share_separates_text_from_broken_encoding():
    assert readable_share("Überblick über das Bewerberprofil Referenznummer 10000") == 1.0
    assert readable_share("$%&'()*&'%+,-)(./01%,+)( 20&'34*5-(6)(%%,") < 0.3


def test_linkedin_header_check_rejects_unexpected_layout():
    files = linkedin_csv.read_export(CASES["linkedin"][1])
    files["Positions.csv"] = "Firma,Titel\nX,Y\n"
    with pytest.raises(ConversionRejected) as exc:
        linkedin_csv.convert(files, retrieved_at=T)
    assert "Positions.csv" in exc.value.checks[0]


def test_linkedin_specifics():
    conv = convert_path(*CASES["linkedin"], retrieved_at=T)
    p = conv.profile
    assert p["experienceHistory"][0]["ongoing"] is True
    assert {l["languageCode"] for l in p["capabilities"]["languages"]} == {"de", "en"}  # Spanish has no level
    assert "jobPreferences" not in p  # the export has no preferences -> unknown
    assert p["evidence"][0]["verificationStatus"] == "UNVERIFIED"
    assert any(u["sourceField"] == "Connections.csv" for u in p["source"]["unmapped"])


def test_json_resume_rejects_wrong_shape():
    with pytest.raises(ConversionRejected):
        json_resume.convert('{"work": {}}', retrieved_at=T)
    with pytest.raises(ConversionRejected):
        json_resume.convert("[1, 2]", retrieved_at=T)


def test_job_ad_to_matching_keeps_unknowns(shared_candidate, policies):
    job = convert_path(*CASES["jobad"], retrieved_at=T).profile
    result = match(shared_candidate, job, *policies)
    career = {c["criterionKey"]: c for c in result["careerFit"]["criteria"]}
    assert career["workModel/wish"]["outcome"] == "UNKNOWN"
    assert career["compensation/hard"]["outcome"] == "MET"
    with pytest.raises(ValueError):
        to_job_posting(dict(job, profileView="PUBLIC"))


def test_imported_candidate_can_be_matched_and_shared(policies):
    ba = convert_path(*CASES["ba"], retrieved_at=T).profile
    job = convert_path(*CASES["jobad"], retrieved_at=T).profile
    result = match(ba, job, *policies)
    assert validate_document(result) == []
    assert {c["criterionKey"]: c for c in result["careerFit"]["criteria"]}["archetypes/wish"]["outcome"] == "MET"
    shared = derive_view(copy.deepcopy(ba), "SHARED_VIEW")
    assert "source" not in shared and "fieldStatements" not in shared
    assert [i for i in validate_document(shared) if i.level == "error"] == []


def test_conversion_is_deterministic():
    a = convert_path(*CASES["ba"], retrieved_at=T).profile
    b = convert_path(*CASES["ba"], retrieved_at=T).profile
    assert a == b



def test_committed_job_profile_matches_adapter():
    committed = load("examples/adapters/job-ad-text-de/senior-demand-planner.jobprofile.json")
    fresh = job_ad_text.convert(CASES["jobad"][1].read_text(encoding="utf-8"), retrieved_at=committed["source"]["retrievedAt"],
                                source_url=committed["source"]["sourceUrl"], file_name="senior-demand-planner.ad.de.txt").profile
    assert fresh == committed
