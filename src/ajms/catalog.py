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
