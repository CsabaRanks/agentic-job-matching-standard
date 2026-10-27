import json
import re

from ajms.validation import validate_document

from conftest import ROOT


def test_readme_json_example_is_valid():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```json\n(.*?)```", readme, flags=re.S)
    assert blocks
    for block in blocks:
        assert validate_document(json.loads(block)) == []


def test_relative_links_in_docs_resolve():
    broken = []
    for doc in [ROOT / "README.md", ROOT / "CONTRIBUTING.md", *sorted((ROOT / "docs").glob("*.md"))]:
        text = re.sub(r"`[^`\n]*`", "", doc.read_text(encoding="utf-8"))
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (doc.parent / target).exists():
                broken.append(f"{doc.relative_to(ROOT)} -> {target}")
    assert broken == []
