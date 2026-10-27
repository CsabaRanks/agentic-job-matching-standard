"""Generate docs/property-index.md from the JSON Schemas (one table per definition)."""

from __future__ import annotations

import json

from . import SCHEMA_DIR

ORDER = ["candidate-profile", "job-profile", "common", "profile-reference", "match-policy", "match-result"]


def _type_of(spec: dict, stem: str) -> str:
    if "$ref" in spec:
        file, _, frag = spec["$ref"].partition("#")
        name = frag.rsplit("/", 1)[-1]
        owner = file.replace(".schema.json", "") if file else stem
        return f"[{name}](#{owner}-{name.lower()})"
    if "const" in spec:
        return f"const `{spec['const']}`"
    if "enum" in spec:
        return "enum: " + ", ".join(f"`{v}`" for v in spec["enum"])
    if "oneOf" in spec or "anyOf" in spec:
        return " or ".join(_type_of(s, stem) for s in spec.get("oneOf", spec.get("anyOf")))
    if spec.get("type") == "array":
        return "array of " + _type_of(spec.get("items", {}), stem)
    if spec is False:
        return "not allowed"
    kind = spec.get("type", "any")
    if isinstance(kind, list):
        kind = " or ".join(kind)
    extras = []
    for key in ("minimum", "exclusiveMinimum", "maximum", "minLength"):
        if key in spec:
            extras.append(f"{key} {spec[key]}")
    if "pattern" in spec:
        extras.append("pattern `" + spec["pattern"].replace("|", "\\|") + "`")
    return kind + (f" ({'; '.join(extras)})" if extras else "")


def _table(title: str, anchor: str, spec: dict, lines: list[str], stem: str) -> None:
    lines += [f'<a id="{anchor}"></a>', f"### {title}", ""]
    if spec.get("description"):
        lines += [spec["description"], ""]
    props = spec.get("properties")
    if not props:
        lines += [f"Type: {_type_of(spec, stem)}", ""]
        return
    required = set(spec.get("required", []))
    lines += ["| Property | Required | Type | Description |", "|---|---|---|---|"]
    for name, prop in props.items():
        desc = (prop.get("description", "") if isinstance(prop, dict) else "").replace("|", "\\|")
        kind = _type_of(prop, stem) if isinstance(prop, dict) else "not allowed"
        lines.append(f"| `{name}` | {'yes' if name in required else ''} | {kind} | {desc} |")
    lines.append("")


def property_index() -> str:
    lines = [
        "# Property index (generated)",
        "",
        "Generated from `schemas/v0.1/*.schema.json` by `python -m ajms build-examples`. Do not edit by hand.",
        "The curated explanation of criteria, units and unknown-semantics is in [field-catalog.md](field-catalog.md).",
        "",
    ]
    for stem in ORDER:
        schema = json.loads((SCHEMA_DIR / f"{stem}.schema.json").read_text(encoding="utf-8"))
        lines += [f"## `{stem}.schema.json`", ""]
        if "properties" in schema:
            _table(schema["title"], stem + "-root", schema, lines, stem)
        for name, spec in schema.get("$defs", {}).items():
            _table(name, f"{stem}-{name.lower()}", spec, lines, stem)
    return "\n".join(lines).rstrip() + "\n"


def _descriptions() -> dict[str, str]:
    """First description found for each property name across all schemas."""
    found: dict[str, str] = {}

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.get("properties", {}).items() if isinstance(node.get("properties"), dict) else []:
                if isinstance(value, dict) and value.get("description") and key not in found:
                    found[key] = value["description"]
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for stem in ORDER:
        walk(json.loads((SCHEMA_DIR / f"{stem}.schema.json").read_text(encoding="utf-8")))
    return found


def vocabulary_html() -> str:
    """Human-readable target of the ajms: namespace (one anchor per term)."""
    from html import escape

    from . import CONTEXT_FILE, CONTEXT_URL, ID_BASE

    context = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))["@context"]
    namespace = context["ajms"]
    descriptions = _descriptions()
    own, reused = [], []
    for term, definition in context.items():
        if term.startswith("@") or term in ("schema", "ajms", "xsd"):
            continue
        iri = definition["@id"] if isinstance(definition, dict) else definition
        datatype = definition.get("@type") if isinstance(definition, dict) else None
        (own if iri.startswith("ajms:") else reused).append((term, iri, datatype))
    rows = []
    for term, iri, datatype in own:
        local = iri.split(":", 1)[1]
        desc = escape(descriptions.get(term, ""))
        dt = f" <code>{escape(datatype)}</code>" if datatype else ""
        rows.append(f'<tr id="{escape(local)}"><td><code>{escape(namespace + local)}</code></td>'
                    f"<td><code>{escape(term)}</code>{dt}</td><td>{desc}</td></tr>")
    reused_rows = [f"<tr><td><code>{escape(term)}</code></td><td><code>{escape(iri)}</code></td></tr>"
                   for term, iri, _ in reused]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AJMS vocabulary v0.1</title>
<style>body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;line-height:1.45}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #ccc;padding:.35rem;vertical-align:top;text-align:left}}
code{{font-size:.9em}}tr:target{{background:#fff3b0}}</style>
</head>
<body>
<h1>AJMS vocabulary v0.1</h1>
<p><strong>Community Draft v0.1</strong> &mdash; a proposal, not an adopted standard. Namespace IRI:
<code>{escape(namespace)}</code>. Generated from the JSON-LD context
<a href="{escape(CONTEXT_URL)}">{escape(CONTEXT_URL)}</a>.</p>
<p>Specification and source: <a href="https://github.com/CsabaRanks/agentic-job-matching-standard">github.com/CsabaRanks/agentic-job-matching-standard</a>.
Schemas: <a href="{escape(ID_BASE)}schemas/v0.1/">{escape(ID_BASE)}schemas/v0.1/</a>.</p>
<h2>Terms in the AJMS namespace ({len(own)})</h2>
<table><thead><tr><th>IRI</th><th>JSON key</th><th>Description (from the schemas, where available)</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table>
<h2>Keys mapped to existing vocabularies ({len(reused)})</h2>
<table><thead><tr><th>JSON key</th><th>IRI</th></tr></thead>
<tbody>
{chr(10).join(reused_rows)}
</tbody></table>
</body>
</html>
"""
