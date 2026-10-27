"""Check that the published identifiers resolve and match this repository.

Run after GitHub Pages has deployed (needs network access):

    python tools/check_published_urls.py

Checks: every schema $id and the JSON-LD context URL return HTTP 200 with a JSON content
type and exactly the bytes in this repository; the namespace IRI resolves to the vocabulary
page with one anchor per ajms: term; an example document expands online (context fetched
over HTTPS) to the same RDF as offline.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pyld import jsonld  # noqa: E402

from ajms import CONTEXT_FILE, CONTEXT_URL, SCHEMA_DIR  # noqa: E402
from ajms.jsonld_check import to_nquads  # noqa: E402

JSON_TYPES = ("application/json", "application/ld+json")


def fetch(url: str) -> tuple[int, str, bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "ajms-url-check"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read(), response.geturl()


def main() -> int:
    problems: list[str] = []

    def check_file(url: str, local: Path) -> None:
        try:
            status, ctype, body, _ = fetch(url)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{url}: {exc}")
            return
        ok = status == 200 and ctype.split(";")[0].strip() in JSON_TYPES and body == local.read_bytes()
        print(f"{'OK  ' if ok else 'FAIL'} {status} {ctype:<32} {url}")
        if not ok:
            problems.append(f"{url}: status {status}, type {ctype}, identical={body == local.read_bytes()}")

    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        check_file(json.loads(path.read_text(encoding="utf-8"))["$id"], path)
    check_file(CONTEXT_URL, CONTEXT_FILE)

    context = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))["@context"]
    namespace = context["ajms"]
    try:
        status, ctype, body, final = fetch(namespace.rstrip("#"))
        page = body.decode("utf-8")
        terms = set()
        for definition in context.values():
            iri = definition["@id"] if isinstance(definition, dict) else definition
            if isinstance(iri, str) and iri.startswith("ajms:"):
                terms.add(iri.split(":", 1)[1])
        missing = sorted(t for t in terms if f'id="{t}"' not in page)
        ok = status == 200 and ctype.startswith("text/html") and not missing
        print(f"{'OK  ' if ok else 'FAIL'} {status} {ctype:<32} {namespace} -> {final} ({len(terms) - len(missing)}/{len(terms)} term anchors)")
        if not ok:
            problems.append(f"namespace: status {status}, missing anchors {missing[:5]}")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"{namespace}: {exc}")

    def online_loader(url, options=None):
        status, ctype, body, final = fetch(url)
        if ctype.split(";")[0].strip() not in JSON_TYPES:
            raise jsonld.JsonLdError(f"unexpected content type {ctype}", "jsonld.LoadDocumentError", code="loading document failed")
        return {"contextUrl": None, "documentUrl": final, "document": json.loads(body), "contentType": ctype}

    example = json.loads((ROOT / "examples/valid/job-demand-planner.public.json").read_text(encoding="utf-8"))
    try:
        online = jsonld.to_rdf(json.loads(json.dumps(example)), {"documentLoader": online_loader, "format": "application/n-quads"})
        same = sorted(online.splitlines()) == sorted(to_nquads(example).splitlines())
        print(f"{'OK  ' if same else 'FAIL'} JSON-LD expansion with the online context ({len(online.splitlines())} statements, identical to offline: {same})")
        if not same:
            problems.append("online JSON-LD expansion differs from offline expansion")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"online JSON-LD expansion failed: {exc}")

    for problem in problems:
        print("PROBLEM", problem)
    print("published URL check:", "FAILED" if problems else "OK")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
