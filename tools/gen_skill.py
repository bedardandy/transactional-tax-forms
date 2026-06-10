#!/usr/bin/env python3
"""Generate SKILL.md + examples/sample_case.json for mapped tax forms.

Deterministic — everything is derived from the form folder (form.yaml,
mapping.json, schema.json); no LLM. Intended for the tax-native-keyed forms
(status vision-mapped / opus-adjudicated), whose mappings use the ``entity`` /
``decedent`` / ``transferor`` / ``facts.*`` roles.

The generated sample case gives every mapped canonical key a plausible but
obviously fictional value ("Example LLC", "00-0000000" EINs, 555 phone
numbers, "123 Main St, Portland, ME 04101") and is validated against the
engine's resolve path: generation fails for a form if fewer than 90% of its
mapped keys resolve from the sample.

    python3 tools/gen_skill.py --forms IRS-SS-4,ME-RETTD
    python3 tools/gen_skill.py --forms IRS-706 --force   # overwrite existing
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.fill_via_mapping import resolve_mapping  # noqa: E402

MIN_COVERAGE = 0.90

# ---------------------------------------------------------------- sample data
# Fixed fictional identities, one per canonical role. SSNs use the 000-00-xxxx
# range, EINs 00-0000000, phones the reserved 555-01xx block.
_ROLE_NAME = {
    "entity": "Example LLC",
    "responsible_party": "Riley J. Example",
    "decedent": "Morgan T. Example",
    "executor": "Pat Q. Example",
    "fiduciary": "Pat Q. Example",
    "estate": "Estate of Morgan T. Example",
    "trust": "Example Family Trust",
    "transferor": "Sam R. Example",
    "transferee": "Casey L. Example",
    "owner": "Riley J. Example",
    "officer": "Riley J. Example",
    "shareholder": "Riley J. Example",
    "beneficiary": "Jordan K. Example",
    "preparer": "Alex P. Example",
}

_ATTR_VALUE = {
    "ein": "00-0000000",
    "ssn": "000-00-0000",
    "ssn_or_ein": "000-00-0000",
    "ssn_itin_ein": "000-00-0000",
    "address": "123 Main St, Portland, ME 04101",
    "street_address": "123 Main St",
    "mailing_address": "123 Main St",
    "city": "Portland",
    "mailing_city": "Portland",
    "town": "Portland",
    "state": "ME",
    "mailing_state": "ME",
    "domicile_state": "ME",
    "zip": "04101",
    "mailing_zip": "04101",
    "county": "Cumberland",
    "domicile_county": "Cumberland",
    "phone": "(207) 555-0100",
    "title": "Managing Member",
    "trade_name": "Example Trading Co",
    "state_of_formation": "Maine",
    "entity_type": "Limited Liability Company",
    "naics": "541110",
    "purchase_price": "250000",
    "map_block_lot": "Map 1, Block 2, Lot 3",
    "book_page": "Book 1234, Page 56",
    "type": "Single-family residence",
    "email": "name@example.com",
}

_MONEY_RE = re.compile(
    r"(amount|tax|income|price|value|payment|deduction|credit|wages|gain|"
    r"loss|total|balance|exemption|interest|penalty|distribut|proceeds|"
    r"contribution|fee)")


def _facts_value(attr: str) -> str:
    """Heuristic fictional value for a facts.<snake_case> key, by its name."""
    a = attr.lower()
    if "ssn" in a:
        return "000-00-0000"
    if "ein" in a or a.endswith("_tin") or "_tin_" in a or a.startswith("tin_"):
        return "00-0000000"
    if "date" in a:
        return "2025-01-15"
    if "phone" in a or "fax" in a:
        return "(207) 555-0100"
    if "email" in a:
        return "name@example.com"
    if "zip" in a:
        return "04101"
    if "address" in a or "street" in a:
        return "123 Main St, Portland, ME 04101"
    if "city" in a or "town" in a:
        return "Portland"
    if "county" in a:
        return "Cumberland"
    if a == "state" or a.endswith("_state") or a.startswith("state_"):
        return "ME"
    if "country" in a:
        return "United States"
    if "year" in a:
        return "2025"
    if a.startswith("number_of") or "count" in a:
        return "1"
    if "percent" in a or "factor" in a or "ratio" in a:
        return "1.000000"
    if _MONEY_RE.search(a):
        return "1000"
    if "name" in a:
        return "Example LLC"
    if "signature" in a or a.startswith("signed"):
        return "Riley J. Example"
    # generic labeled value: echo the label so the sample is self-describing
    return attr.replace("_", " ").capitalize() + " (example)"


def _value_for(key: str, checkbox_only: bool) -> str | None:
    """Fictional value for one canonical key. None = engine computes it."""
    if key == "today()":
        return None
    if checkbox_only:
        return "yes"
    if key == "signature":
        return "Riley J. Example"
    role, _, attr = key.partition(".")
    if role == "facts":
        return _facts_value(attr)
    if attr in ("name", "legal_name"):
        return _ROLE_NAME.get(role, "Riley J. Example")
    if attr in _ATTR_VALUE:
        return _ATTR_VALUE[attr]
    if "date" in attr:
        return "2025-01-15"
    return attr.replace("_", " ").capitalize() + " (example)"


def build_sample_case(mapping: dict, schema: dict) -> tuple[dict, list[str]]:
    """Nested fact object covering every mapped key; returns (case, conflicts)."""
    fid_types: dict[str, set[str]] = {}
    for f in schema.get("fields", []):
        fid_types.setdefault(f["field_id"], set()).add(f.get("type", "text"))
    key_types: dict[str, set[str]] = {}
    for fid, key in mapping["map"].items():
        key_types.setdefault(key, set()).update(fid_types.get(fid, set()))

    case: dict = {}
    conflicts: list[str] = []
    for key in sorted(key_types):
        types = key_types[key]
        cb_only = bool(types) and types <= {"checkbox", "radio"}
        v = _value_for(key, cb_only)
        if v is None:
            continue
        parts = key.split(".")
        node = case
        ok = True
        for p in parts[:-1]:
            nxt = node.setdefault(p, {})
            if not isinstance(nxt, dict):
                conflicts.append(key)
                ok = False
                break
            node = nxt
        if ok:
            if isinstance(node.get(parts[-1]), dict):
                conflicts.append(key)
            else:
                node[parts[-1]] = v
    return case, conflicts


# ------------------------------------------------------------------- SKILL.md
_WIDGETISH_RE = re.compile(r"^[A-Za-z0-9_\[\]().-]+$")  # no spaces = field name


def _humanize(key: str) -> str:
    role, _, attr = key.partition(".")
    if not attr:
        return key
    return f"{role.replace('_', ' ')} — {attr.replace('_', ' ')}"


def _key_table(mapping: dict, schema: dict) -> list[tuple[str, str]]:
    """[(canonical key, where it lands)] — captions from schema.json.

    The captions are heuristic (nearest printed text); when a field has none,
    or only a widget-name-ish fragment, fall back to the canonical key itself
    so the table never shows raw internal names.
    """
    caption = {}
    for f in schema.get("fields", []):
        caption[f["field_id"]] = (f.get("caption") or "").strip()
    by_key: dict[str, list[str]] = {}
    for fid, key in mapping["map"].items():
        by_key.setdefault(key, []).append(caption.get(fid, ""))
    rows = []
    for key in sorted(by_key):
        caps = by_key[key]
        usable = [c for c in caps
                  if len(c) >= 5 and not _WIDGETISH_RE.match(c)]
        desc = usable[0][:90] if usable else _humanize(key)
        if len(caps) > 1:
            desc += f" (+{len(caps) - 1} more field{'s' if len(caps) > 2 else ''})"
        rows.append((key, desc.replace("|", "/")))
    return rows


def render_skill(fid: str, meta: dict, mapping: dict, schema: dict) -> str:
    title = meta.get("title", fid)
    status = mapping.get("status", meta.get("status", ""))
    n_widgets = meta.get("n_widgets", len(schema.get("fields", [])))
    n_keys = len(mapping["map"])
    n_distinct = len(set(mapping["map"].values()))
    rows = _key_table(mapping, schema)
    lines = [
        f"# {fid} — {title}",
        "",
        f"**Agency:** {meta.get('agency', '')}  |  **Domain:** "
        f"{meta.get('domain', '')}  |  **Status:** `{status}`",
        f"**Pages:** {meta.get('num_pages', '?')}  |  **Fillable widgets:** "
        f"{n_widgets}  |  **Mapped:** {n_keys} fields / {n_distinct} keys",
        "",
        "> Not tax or legal advice. The fill output is a draft; verify every "
        "value against the current official form before filing.",
        "",
        "## What an agent needs",
        "",
        "Build a canonical fact object (JSON) using the keys in the table "
        "below — tax-native roles (`entity`, `decedent`, `executor`, "
        "`transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` "
        "for the form's labeled line items. `examples/sample_case.json` "
        "exercises every mapped key with fictional placeholder values.",
    ]
    if status == "opus-adjudicated":
        lines += [
            "",
            "Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed "
            "field-by-field against each printed caption by Opus "
            "(corrections under `mapping.json.adjudication`). Fillable, but "
            "verify placement on the rendered output before relying on it.",
        ]
    lines += [
        "",
        "## Fill",
        "",
        "```bash",
        f"python3 tools/fetch_pdfs.py --forms {fid}   # verified official blank",
        f"python3 -m engine.fill_via_mapping --form {fid} \\",
        f"    --case forms/{fid}/examples/sample_case.json --out /tmp/out",
        "```",
        "",
        "## Canonical keys",
        "",
        "| key | filled into (printed caption) |",
        "|---|---|",
    ]
    lines += [f"| `{k}` | {d} |" for k, d in rows]
    lines.append("")
    return "\n".join(lines)


# ----------------------------------------------------------------------- main
def generate(fid: str, force: bool) -> bool:
    fdir = ROOT / "forms" / fid
    meta = {}
    try:
        import yaml
        meta = yaml.safe_load((fdir / "form.yaml").read_text()) or {}
    except ImportError:
        for line in (fdir / "form.yaml").read_text().splitlines():
            m = re.match(r"^([a-z_]+):\s*(.*)$", line)
            if m:
                meta[m.group(1)] = m.group(2).split("#")[0].strip().strip('"')
    mapping = json.loads((fdir / "mapping.json").read_text())
    schema = json.loads((fdir / "schema.json").read_text())
    if not mapping.get("map"):
        print(f"  {fid}: empty map — nothing to generate")
        return False

    case, conflicts = build_sample_case(mapping, schema)
    res = resolve_mapping(fid, case)
    coverage = res["resolved"] / max(res["mapped_keys"], 1)
    if conflicts:
        print(f"  {fid}: key conflicts skipped: {conflicts}")
    if coverage < MIN_COVERAGE:
        print(f"  {fid}: FAIL — sample resolves only {res['resolved']}/"
              f"{res['mapped_keys']} mapped fields ({coverage:.0%}); "
              f"unresolved: {[k for _, k in res['unresolved']][:10]}")
        return False

    skill = fdir / "SKILL.md"
    sample = fdir / "examples" / "sample_case.json"
    for p in (skill, sample):
        if p.exists() and not force:
            print(f"  {fid}: {p.relative_to(ROOT)} exists (use --force)")
            return False
    case["_note"] = ("All values are fictional placeholders for testing fills "
                     "(Example names, 000/555 numbers). Replace every value "
                     "with real case data before any actual use.")
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_text(json.dumps(case, indent=2) + "\n")
    skill.write_text(render_skill(fid, meta, mapping, schema))
    print(f"  {fid}: SKILL.md + examples/sample_case.json written — sample "
          f"resolves {res['resolved']}/{res['mapped_keys']} mapped fields "
          f"({coverage:.0%})")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", required=True, help="comma list of form ids")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing SKILL.md / sample_case.json")
    args = ap.parse_args()
    ok = True
    for fid in [f.strip() for f in args.forms.split(",") if f.strip()]:
        ok = generate(fid, args.force) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
