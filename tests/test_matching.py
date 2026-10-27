import copy

from ajms.match import match
from ajms.validation import validate_document

from conftest import load


def by_key(perspective):
    return {c["criterionKey"]: c for c in perspective["criteria"]}


def test_result_is_valid_and_reports_both_perspectives_separately(shared_candidate, job, policies):
    result = match(shared_candidate, job, *policies)
    assert validate_document(result) == []
    assert result["hiringFit"]["perspective"] == "HIRING_FIT"
    assert result["careerFit"]["perspective"] == "CAREER_FIT"
    assert "score" not in result  # no merged overall number


def test_matching_is_deterministic(shared_candidate, job, policies):
    assert match(shared_candidate, job, *policies) == match(copy.deepcopy(shared_candidate), copy.deepcopy(job), *policies)


def test_undisclosed_salary_is_unknown_not_zero(shared_candidate, agency_job, policies):
    career = match(shared_candidate, agency_job, *policies)["careerFit"]
    comp = by_key(career)["compensation/hard"]
    assert comp["outcome"] == "UNKNOWN"
    assert "not disclosed" in comp["explanation"]
    assert career["knownWeightCoverage"] < 1


def test_unknown_criteria_are_excluded_from_the_score(shared_candidate, job, policies):
    hiring, career = policies
    base = match(shared_candidate, job, hiring, career)["careerFit"]
    # Remove the job's tasks: the task wish becomes UNKNOWN; the score must not drop because of it.
    no_tasks = copy.deepcopy(job)
    no_tasks.pop("tasks")
    changed = match(shared_candidate, no_tasks, hiring, career)["careerFit"]
    assert by_key(changed)["tasks/wish"]["outcome"] == "UNKNOWN"
    assert changed["knownWeightCoverage"] < base["knownWeightCoverage"]
    assert changed["indicativeScore"] <= base["indicativeScore"] + 1e-9
    assert changed["indicativeScore"] > 0


def test_missing_candidate_skill_is_unknown_not_failed(shared_candidate, job, policies):
    hiring = match(shared_candidate, job, *policies)["hiringFit"]
    assert by_key(hiring)["competencies/stakeholder-facilitation"]["outcome"] == "UNKNOWN"


def test_stated_shortfall_is_not_met(shared_candidate, job, policies):
    weak = copy.deepcopy(shared_candidate)
    weak["capabilities"]["languages"] = [{"languageCode": "de", "cefrLevel": "A2"}]
    hiring = match(weak, job, *policies)["hiringFit"]
    assert by_key(hiring)["languages/de"]["outcome"] == "NOT_MET"
    assert hiring["hardConditionStatus"] == "NOT_MET"


def test_travel_time_is_never_derived_from_distance(shared_candidate, job, policies):
    career = by_key(match(shared_candidate, job, *policies)["careerFit"])
    assert career["location/hard"]["outcome"] == "MET"  # straight-line distance limit
    assert career["location/wish"]["outcome"] == "UNKNOWN"  # travel-time limit
    assert "not derived from distance" in career["location/wish"]["explanation"]


def test_hard_conditions_are_not_weighted(shared_candidate, agency_job, policies):
    hiring, career = policies
    heavy = copy.deepcopy(career)
    heavy["weights"] = {k: 0 for k in heavy["weights"]}
    a = match(shared_candidate, agency_job, hiring, career)["careerFit"]
    b = match(shared_candidate, agency_job, hiring, heavy)["careerFit"]
    assert a["hardConditionStatus"] == b["hardConditionStatus"] == "NOT_MET"
    assert b["indicativeScore"] is None


def test_salary_comparison_respects_hours_basis(shared_candidate, job, policies):
    explanation = by_key(match(shared_candidate, job, *policies)["careerFit"])["compensation/hard"]["explanation"]
    assert "scaled from 38 h to 40 h per week" in explanation


def test_domain_criterion_hard_condition(policies):
    nurse = load("examples/valid/candidate-icu-nurse.shared-view.json")
    nurse_job = load("examples/valid/job-icu-nurse.public.json")
    result = match(nurse, nurse_job, *policies)
    career = by_key(result["careerFit"])
    assert career["domainCriteria/org.example.healthcare.night_shifts_per_month"]["outcome"] == "NOT_MET"
    assert career["workModel"]["outcome"] == "NOT_APPLICABLE"
    assert result["hiringFit"]["hardConditionStatus"] == "ALL_MET"


def test_policies_are_marked_uncalibrated(policies):
    for policy in policies:
        assert policy["calibrationStatus"] == "UNCALIBRATED"
        assert validate_document(policy) == []
