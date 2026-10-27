"""Command line interface: python -m ajms <command> ..."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import REPO_ROOT, __version__
from .catalog import property_index, vocabulary_html
from .exchange import make_reference
from .adapters import FORMATS, ConversionRejected, convert_path
from .adapters.report import render_conversion_report
from .jsonld_check import check_jsonld
from .match import match
from .render import render
from .schemaorg_export import to_job_posting
from .validation import has_errors, load_json, validate_document
from .views import derive_view

EXAMPLES = REPO_ROOT / "examples"

# (candidate, job) pairs for the demonstration.
MATCH_PAIRS = [
    ("candidate-supply-chain-analyst.shared-view", "job-demand-planner.public"),
    ("candidate-supply-chain-analyst.shared-view", "job-supply-planner-agency.public"),
    ("candidate-icu-nurse.shared-view", "job-icu-nurse.public"),
]
DERIVED_SOURCE = "candidate-supply-chain-analyst.full-private"
ADAPTER_EXAMPLES = [
    {"format": "ba-bewerberprofil-text", "input": "synthetic-demand-planner.ba.txt", "stem": "synthetic-demand-planner",
     "retrieved_at": "2026-10-27T11:00:00+01:00", "source_url": None, "lang": "de"},
    {"format": "linkedin-data-export-csv", "input": "export", "stem": "synthetic-supply-chain-analyst",
     "retrieved_at": "2026-10-27T11:05:00+01:00", "source_url": None, "lang": "en"},
    {"format": "json-resume-1", "input": "synthetic-icu-nurse.resume.json", "stem": "synthetic-icu-nurse",
     "retrieved_at": "2026-10-27T11:10:00+01:00", "source_url": None, "lang": "en"},
    {"format": "job-ad-text-de", "input": "senior-demand-planner.ad.de.txt", "stem": "senior-demand-planner",
     "retrieved_at": "2026-10-27T10:15:00+01:00", "source_url": "https://jobs.example.com/ads/senior-demand-planner-4711",
     "lang": "de", "match": True},
]


def dump(doc: dict) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def generated_files() -> dict[Path, str]:
    """Every generated artefact, computed from the hand-written examples."""
    valid = EXAMPLES / "valid"
    files: dict[Path, str] = {}
    private = load_json(valid / f"{DERIVED_SOURCE}.json")
    for view, suffix in (("SHARED_VIEW", "shared-view"), ("PUBLIC_MINIMAL", "public-minimal")):
        files[valid / f"candidate-supply-chain-analyst.{suffix}.json"] = dump(derive_view(private, view))

    def doc(name: str) -> dict:
        path = valid / f"{name}.json"
        return json.loads(files[path]) if path in files else load_json(path)

    shared = doc("candidate-supply-chain-analyst.shared-view")
    files[EXAMPLES / "exchange" / "candidate-supply-chain-analyst.shared-view.reference.json"] = dump(make_reference(
        shared, "https://profiles.example.org/p/7c1e0b52.json", "ACCESS_CONTROLLED",
        intended_recipient="Example Staffing Partner GmbH (synthetic)", expires_at="2027-01-31T23:59:59+01:00"))
    public = doc("candidate-supply-chain-analyst.public-minimal")
    files[EXAMPLES / "exchange" / "candidate-supply-chain-analyst.public-minimal.reference.json"] = dump(make_reference(
        public, "https://profiles.example.org/public/9d4a.json", "PUBLIC"))
    job = doc("job-demand-planner.public")
    files[EXAMPLES / "exchange" / "job-demand-planner.public.reference.json"] = dump(make_reference(
        job, "https://example.com/harbour-beverages/jobs/demand-planner.ajms.json", "PUBLIC"))

    hiring = load_json(EXAMPLES / "policies" / "demo-hiring-fit.policy.json")
    career = load_json(EXAMPLES / "policies" / "demo-career-fit.policy.json")
    out = EXAMPLES / "output"
    for cand, job_name in MATCH_PAIRS:
        result = match(doc(cand), doc(job_name), hiring, career)
        stem = f"{cand.split('.')[0]}__{job_name.split('.')[0]}"
        files[out / "match" / f"{stem}.match.json"] = dump(result)
        files[out / "match" / f"{stem}.match.en.md"] = render(result, "en")

    # Hand-written examples plus the derived views (which may not exist on disk yet).
    names = sorted({p.stem for p in valid.glob("*.json")} | {p.stem for p in files if p.parent == valid})
    for name in names:
        document = doc(name)
        files[out / "render" / f"{name}.en.md"] = render(document, "en")
        files[out / "render" / f"{name}.de.md"] = render(document, "de")
        if document["@type"] == "JobProfile" and document["profileView"] == "PUBLIC" \
                and document.get("provenance", {}).get("basis") != "DERIVED":
            files[out / "schemaorg" / f"{name}.jobposting.jsonld"] = dump(to_job_posting(document))
    files[REPO_ROOT / "docs" / "property-index.md"] = property_index()
    files[REPO_ROOT / "ns" / "v0.1" / "index.html"] = vocabulary_html()

    # Import adapters: source data -> mapping -> conversion -> validation -> readable output.
    converted = {}
    for ex in ADAPTER_EXAMPLES:
        folder = EXAMPLES / "adapters" / ex["format"]
        conv = convert_path(ex["format"], folder / ex["input"], retrieved_at=ex["retrieved_at"], source_url=ex["source_url"])
        converted[ex["format"]] = conv.profile
        name = f"{ex['stem']}.{conv.profile['@type'].lower()}.json"
        files[folder / name] = dump(conv.profile)
        files[folder / f"{ex['stem']}.conversion-report.md"] = render_conversion_report(
            conv, name, lang=ex["lang"], candidate=shared if ex.get("match") else None,
            hiring_policy=hiring, career_policy=career)
    combined = match(converted["ba-bewerberprofil-text"], converted["job-ad-text-de"], hiring, career)
    files[out / "match" / "ba-candidate__imported-job-ad.match.json"] = dump(combined)
    files[out / "match" / "ba-candidate__imported-job-ad.match.en.md"] = render(combined, "en")
    return files


def cmd_validate(args) -> int:
    failed = 0
    for name in args.files:
        doc = load_json(name)
        issues = validate_document(doc)
        status = "INVALID" if has_errors(issues) else "valid"
        print(f"{status}: {name}")
        for issue in issues:
            print(f"  {issue}")
        if args.jsonld and not has_errors(issues) and doc.get("@type") in ("CandidateProfile", "JobProfile", "ProfileReference"):
            report = check_jsonld(doc)
            print(f"  JSON-LD: {'ok' if report.ok else 'FAILED'}, {report.statements} RDF statements"
                  + (f", undefined terms: {report.undefined_terms}" if report.undefined_terms else "")
                  + (f", error: {report.error}" if report.error else ""))
            failed += 0 if report.ok else 1
        failed += 1 if has_errors(issues) else 0
    return 1 if failed else 0


def cmd_render(args) -> int:
    sys.stdout.write(render(load_json(args.file), args.lang))
    return 0


def cmd_match(args) -> int:
    hiring = load_json(args.hiring_policy)
    career = load_json(args.career_policy)
    result = match(load_json(args.candidate), load_json(args.job), hiring, career)
    sys.stdout.write(render(result, args.lang) if args.format == "md" else dump(result))
    return 0


def cmd_derive_view(args) -> int:
    sys.stdout.write(dump(derive_view(load_json(args.file), args.view)))
    return 0


def cmd_export(args) -> int:
    sys.stdout.write(dump(to_job_posting(load_json(args.file))))
    return 0


def cmd_reference(args) -> int:
    sys.stdout.write(dump(make_reference(load_json(args.file), args.url, args.access)))
    return 0


def cmd_convert(args) -> int:
    try:
        conv = convert_path(args.format, args.input, retrieved_at=args.retrieved_at, source_url=args.source_url)
    except ConversionRejected as exc:
        print(f"REJECTED ({exc.source_format}): no profile produced", file=sys.stderr)
        for check in exc.checks:
            print(f"  - {check}", file=sys.stderr)
        return 2
    if args.report:
        candidate = load_json(args.candidate) if args.candidate else None
        hiring = load_json(EXAMPLES / "policies" / "demo-hiring-fit.policy.json")
        career = load_json(EXAMPLES / "policies" / "demo-career-fit.policy.json")
        sys.stdout.write(render_conversion_report(conv, "(stdout)", lang=args.lang, candidate=candidate,
                                                  hiring_policy=hiring, career_policy=career))
    else:
        sys.stdout.write(dump(conv.profile))
    return 0


def cmd_build_examples(args) -> int:
    for path, content in sorted(generated_files().items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(REPO_ROOT)}")
    return 0


def cmd_check(args) -> int:
    """Validate every example and verify that generated files are up to date."""
    problems: list[str] = []
    for path in sorted((EXAMPLES / "valid").glob("*.json")) + sorted((EXAMPLES / "exchange").glob("*.json")) \
            + sorted((EXAMPLES / "policies").glob("*.json")) + sorted((EXAMPLES / "output" / "match").glob("*.json")) \
            + sorted((EXAMPLES / "adapters").glob("*/*.*profile.json")):
        doc = load_json(path)
        issues = validate_document(doc)
        if has_errors(issues):
            problems.append(f"{path.relative_to(REPO_ROOT)} should be valid: {issues[0]}")
        if doc.get("@type") in ("CandidateProfile", "JobProfile", "ProfileReference"):
            report = check_jsonld(doc)
            if not report.ok:
                problems.append(f"{path.relative_to(REPO_ROOT)} JSON-LD: {report.undefined_terms or report.error}")
    expectations = load_json(EXAMPLES / "invalid" / "expectations.json")
    for folder in ("invalid", "invalid-semantic"):
        for path in sorted((EXAMPLES / folder).glob("*.json")):
            if path.name == "expectations.json":
                continue
            expected = expectations.get(f"{folder}/{path.name}")
            if expected is None:
                problems.append(f"{folder}/{path.name} has no entry in invalid/expectations.json")
                continue
            errors = [i for i in validate_document(load_json(path)) if i.level == "error"]
            if not any(i.kind == expected["kind"] and i.path == expected["path"] and expected["contains"] in i.message for i in errors):
                problems.append(f"{folder}/{path.name} did not fail as expected {expected}; got {[str(i) for i in errors][:3]}")
    for path, content in sorted(generated_files().items()):
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            problems.append(f"{path.relative_to(REPO_ROOT)} is missing or out of date; run: python -m ajms build-examples")
    for problem in problems:
        print("FAIL", problem)
    print(f"ajms check: {'FAILED' if problems else 'OK'} ({len(problems)} problems)")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ajms", description="AJMS Community Draft v0.1 reference tools (offline, no LLM).")
    parser.add_argument("--version", action="version", version=f"ajms {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="validate documents (JSON Schema + semantic checks)")
    p.add_argument("files", nargs="+")
    p.add_argument("--jsonld", action="store_true", help="also run the JSON-LD semantic check")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("render", help="render a profile or match result as Markdown")
    p.add_argument("file")
    p.add_argument("--lang", choices=("en", "de"), default="en")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("match", help="demonstration matching: Hiring-Fit and Career-Fit")
    p.add_argument("candidate")
    p.add_argument("job")
    p.add_argument("--hiring-policy", default=str(EXAMPLES / "policies" / "demo-hiring-fit.policy.json"))
    p.add_argument("--career-policy", default=str(EXAMPLES / "policies" / "demo-career-fit.policy.json"))
    p.add_argument("--format", choices=("md", "json"), default="md")
    p.add_argument("--lang", choices=("en", "de"), default="en")
    p.set_defaults(func=cmd_match)

    p = sub.add_parser("derive-view", help="derive SHARED_VIEW or PUBLIC_MINIMAL from a FULL_PRIVATE candidate profile")
    p.add_argument("file")
    p.add_argument("--view", choices=("SHARED_VIEW", "PUBLIC_MINIMAL"), required=True)
    p.set_defaults(func=cmd_derive_view)

    p = sub.add_parser("export-schemaorg", help="export a PUBLIC JobProfile as schema.org JobPosting JSON-LD")
    p.add_argument("file")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("reference", help="create a ProfileReference (exchange convention) for a profile")
    p.add_argument("file")
    p.add_argument("--url", required=True)
    p.add_argument("--access", choices=("PUBLIC", "ACCESS_CONTROLLED", "ON_REQUEST"), required=True)
    p.set_defaults(func=cmd_reference)

    p = sub.add_parser("convert", help="import adapter: provided source data -> AJMS profile with field-level provenance")
    p.add_argument("input", help="file, or directory for linkedin-data-export-csv")
    p.add_argument("--format", required=True, choices=sorted(FORMATS))
    p.add_argument("--retrieved-at", required=True, help="when the data was retrieved or provided (RFC 3339 with offset)")
    p.add_argument("--source-url", help="where the data came from; default urn:sha256:<digest>")
    p.add_argument("--report", action="store_true", help="print the conversion report (Markdown) instead of the profile")
    p.add_argument("--lang", choices=("en", "de"), default="en")
    p.add_argument("--candidate", help="for job profiles: candidate profile to match against in the report")
    p.set_defaults(func=cmd_convert)

    p = sub.add_parser("build-examples", help="regenerate derived examples and outputs")
    p.set_defaults(func=cmd_build_examples)

    p = sub.add_parser("check", help="validate all examples and verify generated outputs are current")
    p.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)
