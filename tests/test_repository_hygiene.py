"""Guards against publishing personal data, credentials or source material by accident."""

import re
import subprocess

from conftest import ROOT

TEXT_SUFFIXES = {".md", ".json", ".jsonld", ".py", ".toml", ".yml", ".yaml", ".txt", ".cff", ".html", ""}
BINARY_SOURCE_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".doc", ".xlsx", ".pptx", ".zip"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
ALLOWED_EMAIL_DOMAINS = ("example.org", "example.com", "example.net", "users.noreply.github.com")
PHONE = re.compile(r"\+\d{2}[\s-]?\(?\d{2,5}\)?[\s-]?\d{3,}[\s-]?\d{2,}")
SECRETS = re.compile(r"(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


def repo_files():
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, text=True, check=True).stdout.split("\n")
        return [ROOT / f for f in out if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and ".venv" not in p.parts]


def test_no_input_or_source_documents_in_repository():
    files = repo_files()
    assert not [f for f in files if "INPUT" in f.relative_to(ROOT).parts]
    assert not [f for f in files if f.suffix.lower() in BINARY_SOURCE_SUFFIXES]


def test_no_real_email_addresses_phone_numbers_or_secrets():
    findings = []
    for path in repo_files():
        if path.suffix not in TEXT_SUFFIXES or not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in EMAIL.finditer(text):
            if not match.group(0).lower().endswith(ALLOWED_EMAIL_DOMAINS):
                findings.append(f"{path.relative_to(ROOT)}: e-mail {match.group(0)}")
        for match in PHONE.finditer(text):
            findings.append(f"{path.relative_to(ROOT)}: phone-like {match.group(0)}")
        if SECRETS.search(text):
            findings.append(f"{path.relative_to(ROOT)}: secret-like token")
    assert findings == []
