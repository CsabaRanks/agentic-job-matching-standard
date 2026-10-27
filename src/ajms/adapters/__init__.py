"""Import adapters: provided source data -> AJMS profile (no platform access).

| format                     | input                                   | kind       | profile          |
|----------------------------|-----------------------------------------|------------|------------------|
| ba-bewerberprofil-text     | BA candidate profile as text / PDF text | TEXT       | CandidateProfile |
| linkedin-data-export-csv   | directory with LinkedIn export CSVs     | STRUCTURED | CandidateProfile |
| json-resume-1              | JSON Resume document                    | STRUCTURED | CandidateProfile |
| job-ad-text-de             | German job ad as plain text             | TEXT       | JobProfile       |
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from . import ba_text, job_ad_text, json_resume, linkedin_csv
from .base import Conversion, ConversionRejected

FORMATS = {
    ba_text.FORMAT: "BA candidate profile (text; PDF via pdftotext)",
    linkedin_csv.FORMAT: "LinkedIn data export (directory of CSV files)",
    json_resume.FORMAT: "JSON Resume document",
    job_ad_text.FORMAT: "German job ad (plain text)",
}

__all__ = ["FORMATS", "Conversion", "ConversionRejected", "convert_path", "pdf_text"]


def pdf_text(path: Path) -> str:
    """Text layer of a PDF via poppler's pdftotext (optional external tool)."""
    if shutil.which("pdftotext") is None:
        raise ConversionRejected("pdf", ["pdftotext (poppler-utils) is not installed; provide the text instead"])
    return subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True).stdout


def convert_path(source_format: str, path: str | Path, *, retrieved_at: str, source_url: str | None = None) -> Conversion:
    path = Path(path)
    if source_format == linkedin_csv.FORMAT:
        if not path.is_dir():
            raise ConversionRejected(source_format, ["expects a directory with the export's CSV files"])
        return linkedin_csv.convert(linkedin_csv.read_export(path), retrieved_at=retrieved_at, source_url=source_url,
                                    file_name=path.name)
    if source_format not in FORMATS:
        raise ConversionRejected(source_format, ["unknown format; supported: " + ", ".join(FORMATS)])
    if path.suffix.lower() == ".pdf":
        if source_format != ba_text.FORMAT:
            raise ConversionRejected(source_format, ["PDF input is only supported for " + ba_text.FORMAT])
        text = pdf_text(path)
    else:
        text = path.read_text(encoding="utf-8")
    module = {ba_text.FORMAT: ba_text, json_resume.FORMAT: json_resume, job_ad_text.FORMAT: job_ad_text}[source_format]
    return module.convert(text, retrieved_at=retrieved_at, source_url=source_url, file_name=path.name)
