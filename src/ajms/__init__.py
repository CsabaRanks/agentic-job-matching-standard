"""Reference implementation of the Agentic Job Matching Standard (AJMS), Community Draft v0.1."""

from pathlib import Path

__version__ = "0.1.0"
SPEC_VERSION = "0.1.0"

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "schemas" / "v0.1"
CONTEXT_FILE = REPO_ROOT / "context" / "v0.1" / "ajms.context.jsonld"

ID_BASE = "https://raw.githubusercontent.com/CsabaRanks/agentic-job-matching-standard/v0.1.0/"
SCHEMA_ID_BASE = ID_BASE + "schemas/v0.1/"
CONTEXT_URL = ID_BASE + "context/v0.1/ajms.context.jsonld"
