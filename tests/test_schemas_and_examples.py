import json
import re

import pytest
from jsonschema import Draft202012Validator

from ajms import CONTEXT_URL, SCHEMA_ID_BASE
from ajms.cli import cmd_check, generated_files
from ajms.jsonld_check import check_jsonld, context_terms
from ajms.validation import has_errors, validate_document

from conftest import EXAMPLES, ROOT, load

SCHEMAS = sorted((ROOT / "schemas" / "v0.1").glob("*.schema.json"))
JSONLD_SCHEMAS = ("common", "candidate-profile", "job-profile", "profile-reference")


@pytest.mark.parametrize("path", SCHEMAS, ids=lambda p: p.name)
def test_schema_is_valid_draft_2020_12_with_versioned_id(path):
    schema = json.loads(path.read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_ID_BASE + path.name
    assert re.fullmatch(r"https://csabaranks\.github\.io/agentic-job-matching-standard/schemas/v\d+\.\d+/[a-z-]+\.schema\.json", schema["$id"])
    Draft202012Validator.check_schema(schema)


def _property_names(node, found):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "properties" and isinstance(value, dict):
                found.update(value)
            _property_names(value, found)
    elif isinstance(node, list):
        for value in node:
            _property_names(value, found)
    return found


def test_every_profile_property_is_a_context_term():
    names = set()
    for stem in JSONLD_SCHEMAS:
        _property_names(json.loads((ROOT / "schemas" / "v0.1" / f"{stem}.schema.json").read_text()), names)
    missing = sorted(n for n in names if not n.startswith("@") and n not in context_terms())
    assert missing == []


def test_context_terms_use_only_known_namespaces():
    terms = context_terms()
    assert terms["schema"] == "https://schema.org/"
    for term, definition in terms.items():
        iri = definition["@id"] if isinstance(definition, dict) else definition
        if term in ("@version", "schema", "ajms", "xsd") or iri.startswith("@"):
            continue
        assert iri.split(":", 1)[0] in ("schema", "ajms"), term


@pytest.mark.parametrize("path", sorted((EXAMPLES / "valid").glob("*.json")), ids=lambda p: p.name)
def test_valid_examples_pass_schema_semantics_and_jsonld(path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert not has_errors(validate_document(doc))
    assert doc["@context"] == CONTEXT_URL
    report = check_jsonld(doc)
    assert report.ok, (report.undefined_terms, report.error)


EXPECTATIONS = load("examples/invalid/expectations.json")


@pytest.mark.parametrize("name", sorted(EXPECTATIONS))
def test_invalid_examples_fail_for_the_documented_reason(name):
    expected = EXPECTATIONS[name]
    errors = [i for i in validate_document(load(f"examples/{name}")) if i.level == "error"]
    assert any(i.kind == expected["kind"] and i.path == expected["path"] and expected["contains"] in i.message for i in errors), errors


def test_every_invalid_file_has_an_expectation():
    files = {f"{p.parent.name}/{p.name}" for folder in ("invalid", "invalid-semantic") for p in (EXAMPLES / folder).glob("*.json")}
    files.discard("invalid/expectations.json")
    assert files == set(EXPECTATIONS)


def test_jsonld_check_works_without_the_json_schema(job):
    # A JSON-LD processor would silently drop a key the context does not define.
    assert check_jsonld(job).ok
    assert check_jsonld(dict(job, unmappedKey="x")).undefined_terms == ["/unmappedKey"]


def test_generated_outputs_are_up_to_date():
    stale = [str(p.relative_to(ROOT)) for p, content in generated_files().items()
             if not p.exists() or p.read_text(encoding="utf-8") != content]
    assert stale == [], "run: python -m ajms build-examples"


def test_check_command_passes(capsys):
    assert cmd_check(None) == 0
