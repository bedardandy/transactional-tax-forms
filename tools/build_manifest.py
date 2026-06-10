#!/usr/bin/env python3
"""Fetch every source blank, pin it by SHA-256, and dump its widget inventory.

For each form in ``catalog/source_urls.json`` this downloads the blank from its
official URL (Maine Revenue Services or the IRS), records sha256 + bytes +
page/widget counts in ``catalog/pdf_manifest.json`` (keyed by form id), and
writes the raw AcroForm widget inventory to ``forms/<ID>/widgets.json`` — the
input the mapping step turns into mapping.json / schema.json.

Source PDFs are never committed; only their hashes and field inventories are.

    python3 tools/build_manifest.py                 # all forms
    python3 tools/build_manifest.py --forms IRS-SS-4,ME-RETTD
    python3 tools/build_manifest.py --check          # report only; do not write
"""
import argparse
import hashlib
import json
import pathlib
import sys

import fitz

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.fetch_pdfs import _download  # shared retrying downloader  # noqa: E402

SOURCE_URLS = ROOT / "catalog" / "source_urls.json"
MANIFEST = ROOT / "catalog" / "pdf_manifest.json"
FORMS = ROOT / "forms"


def widget_inventory(data: bytes) -> dict:
    doc = fitz.open(stream=data, filetype="pdf")
    widgets = []
    for pno in range(doc.page_count):
        for w in (doc[pno].widgets() or []):
            r = w.rect
            entry = {
                "name": w.field_name,
                "type": w.field_type_string,
                "page": pno,
                "rect": [round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1)],
            }
            states = None
            try:
                states = w.button_states()
            except Exception:  # noqa: BLE001
                states = None
            if states:
                entry["button_states"] = states
            if getattr(w, "choice_values", None):
                entry["choices"] = w.choice_values
            widgets.append(entry)
    n_pages = doc.page_count
    doc.close()
    return {"num_pages": n_pages, "n_widgets": len(widgets), "widgets": widgets}


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch blanks, pin hashes, dump widget inventory")
    ap.add_argument("--forms", help="comma list (default: all in source_urls.json)")
    ap.add_argument("--timeout", type=int, default=40)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--check", action="store_true", help="report only; do not write")
    args = ap.parse_args()

    src = json.loads(SOURCE_URLS.read_text())["forms"]
    ids = ([f.strip() for f in args.forms.split(",")] if args.forms else sorted(src))
    unknown = [f for f in ids if f not in src]
    if unknown:
        print(f"unknown form ids: {', '.join(unknown)}")
        return 2

    forms, flat, fails = {}, [], []
    for i, fid in enumerate(ids, 1):
        try:
            data = _download(src[fid], args.timeout, args.retries)
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(ids)}] FAIL  {fid}: {e}")
            fails.append(fid)
            continue
        if data[:5] != b"%PDF-":
            print(f"  [{i}/{len(ids)}] FAIL  {fid}: not a PDF (error/HTML page)")
            fails.append(fid)
            continue
        inv = widget_inventory(data)
        has_acro = inv["n_widgets"] > 0
        forms[fid] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "num_pages": inv["num_pages"],
            "has_acroform": has_acro,
            "url": src[fid],
        }
        if not has_acro:
            flat.append(fid)
        if not args.check:
            (FORMS / fid).mkdir(parents=True, exist_ok=True)
            (FORMS / fid / "widgets.json").write_text(json.dumps(inv, indent=2) + "\n")
        tag = "" if has_acro else "  (FLAT — no AcroForm, needs geometry mapping)"
        print(f"  [{i}/{len(ids)}] ok    {fid}: {forms[fid]['bytes']}B "
              f"{inv['num_pages']}pg {inv['n_widgets']} widgets {forms[fid]['sha256'][:12]}…{tag}")

    print(f"\nhashed {len(forms)}/{len(ids)} | flat (no AcroForm): {len(flat)} {flat} | failed: {len(fails)} {fails}")

    if args.check:
        print("--check: not writing")
        return 1 if fails else 0

    manifest = {"forms": {}}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text())
        manifest.setdefault("forms", {})
    manifest["forms"].update(forms)
    manifest["forms"] = {k: manifest["forms"][k] for k in sorted(manifest["forms"])}
    manifest["count"] = len(manifest["forms"])
    manifest["note"] = ("SHA-256 of each official blank (Maine Revenue Services / IRS). "
                        "Verified at fill time and by tools/check_upstream.py.")
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST.relative_to(ROOT)} ({manifest['count']} forms)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
