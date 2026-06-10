#!/usr/bin/env python3
"""Harvest checkbox-paradox constraints into per-form ``constraints.json``.

Reproducible (re-run instead of hand-editing): scans every form's
``mapping.json`` + ``schema.json`` (and the local blank's printed text, when
fetched) and emits the optional ``forms/<ID>/constraints.json`` that the
shared engine's constraints layer (``maine_forms_engine.constraints``)
surfaces as **warnings-only** fill diagnostics. A paradoxical selection never
blocks a fill — it gets a yellow light in the report.

Deliberately conservative — a constraint is emitted only where the paradox is
logically certain from the form's own text/structure:

  A. Yes/No pairs: two mapped checkboxes whose canonical keys differ only by
     a ``_yes`` / ``_no`` suffix (one question, two answer boxes).
  B. Resident/Nonresident pairs: ``facts.resident_X`` + ``facts.nonresident_X``
     (a return is filed under exactly one residency status).
  C. Entity-type sets (``facts.entity_type_*``), emitted ONLY when the local
     blank's printed text literally says "check one box" next to "type of
     entity" — the note quotes the form. No blank, no constraint.
  D. Refund account type: ``facts.account_type_checking`` /
     ``facts.account_type_savings`` (one refund account, one type).

"Check the boxes that apply" clusters (initial/final/amended return, name/
address changes, ...) are NOT mutually exclusive and are never emitted.

    python3 tools/harvest_constraints.py            # write/refresh
    python3 tools/harvest_constraints.py --check    # verify, write nothing
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"

GENERATED_BY = "tools/harvest_constraints.py"

_ENTITY_TYPE_LITERAL = re.compile(r"type\s+of\s+entity\s*\(check\s+one\s+box\)",
                                  re.I)


def _mapped_checkbox_keys(fdir: pathlib.Path) -> list[str]:
    """Canonical keys of this form's mapped checkbox widgets (map order)."""
    mp = fdir / "mapping.json"
    sp = fdir / "schema.json"
    if not (mp.exists() and sp.exists()):
        return []
    mapping = json.loads(mp.read_text())
    schema = json.loads(sp.read_text())
    cb_fids = {f["field_id"] for f in schema.get("fields", [])
               if f.get("type") == "checkbox"}
    return [key for fid, key in (mapping.get("map") or {}).items()
            if fid in cb_fids]


def _page_text(fdir: pathlib.Path) -> str:
    """Whitespace-collapsed printed text of the local blank ('' if unfetched)."""
    pdf = fdir / f"{fdir.name}.pdf"
    if not pdf.exists():
        return ""
    import fitz
    doc = fitz.open(str(pdf))
    txt = " ".join(p.get_text() for p in doc)
    doc.close()
    return re.sub(r"\s+", " ", txt)


def harvest_form(fdir: pathlib.Path) -> dict | None:
    keys = _mapped_checkbox_keys(fdir)
    if not keys:
        return None
    keyset = set(keys)
    groups: list[dict] = []

    # A — Yes/No pairs (facts.<stem>_yes / facts.<stem>_no)
    for k in keys:
        if k.endswith("_yes") and (mate := k[:-4] + "_no") in keyset:
            groups.append({
                "keys": [k, mate],
                "note": "Yes/No answer pair for one printed question — "
                        "at most one box can be checked."})

    # B — Resident/Nonresident pairs (facts.resident_X / facts.nonresident_X)
    for k in keys:
        m = re.match(r"^(.*?\.)resident_(.+)$", k)
        if m and (mate := f"{m.group(1)}nonresident_{m.group(2)}") in keyset:
            groups.append({
                "keys": [k, mate],
                "note": "Resident / Nonresident — a return is filed under "
                        "exactly one residency status."})

    # C — entity-type set, only on the printed "check one box" literal
    entity = [k for k in keys if ".entity_type_" in k]
    if len(entity) >= 2:
        text = _page_text(fdir)
        m = _ENTITY_TYPE_LITERAL.search(text)
        if m:
            groups.append({
                "keys": entity,
                "note": f"The form says \"{m.group(0)}\" — exactly one "
                        "entity-type box."})
        elif text:
            print(f"  {fdir.name}: entity_type_* cluster found but the blank "
                  "does not say 'check one box' — skipped (not certain)")
        else:
            print(f"  {fdir.name}: entity_type_* cluster found but no local "
                  "blank to confirm the 'check one box' literal — skipped "
                  "(fetch the blank and re-run)")

    # D — refund account type (Checking / Savings)
    for k in keys:
        if k.endswith("account_type_checking") and \
                (mate := k.replace("_checking", "_savings")) in keyset:
            groups.append({
                "keys": [k, mate],
                "note": "Refund account type: Checking / Savings — one "
                        "account, one type."})

    if not groups:
        return None
    return {
        "form_id": fdir.name,
        "generated_by": GENERATED_BY,
        "note": ("Warnings-only paradox constraints (see the shared engine's "
                 "constraints layer); a firing constraint never blocks or "
                 "alters a fill."),
        "mutually_exclusive": groups,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="verify shipped constraints.json files match a fresh "
                         "harvest; write nothing")
    args = ap.parse_args()
    stale = []
    n_written = n_groups = 0
    for fdir in sorted(p for p in FORMS.iterdir() if p.is_dir()):
        want = harvest_form(fdir)
        out = fdir / "constraints.json"
        have = json.loads(out.read_text()) if out.exists() else None
        if want is None:
            if have is not None and have.get("generated_by") == GENERATED_BY:
                stale.append(f"{fdir.name}: harvester no longer emits this file")
            continue
        n_groups += len(want["mutually_exclusive"])
        if have == want:
            continue
        if args.check:
            stale.append(f"{fdir.name}: constraints.json out of date "
                         "(run tools/harvest_constraints.py)")
            continue
        out.write_text(json.dumps(want, indent=2) + "\n")
        n_written += 1
        print(f"  {fdir.name}: wrote {out.relative_to(ROOT)} "
              f"({len(want['mutually_exclusive'])} groups)")
    if stale:
        print("\n".join(stale))
        return 1
    print(f"done — {n_groups} certain groups across the tree"
          + (f", {n_written} files (re)written" if not args.check else ", all current"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
