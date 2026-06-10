#!/usr/bin/env python3
"""Associate each AcroForm widget with the caption printed next to it.

IRS/XFA forms carry opaque field names (``f1_1[0]``) and no ``/TU`` alt-text, so
the only on-form signal of what a widget means is the visible caption. For each
widget this finds the nearest printed text — to the LEFT on the same row for a
text box, to the RIGHT for a checkbox, falling back to the line ABOVE — and
writes a reviewable inventory to ``forms/<ID>/fields.csv``.

The CSV schema (``field_id,label,caption,type,page,rect``) is shared with
``tools/vision_map.py`` so ``tools/opus_adjudicate.py`` can read either tool's
output. ``field_id`` is the slugged widget name, ``label`` the raw widget name,
``caption`` the inferred printed text.

The captions are heuristic (dense multi-column forms misattribute some); they
are the first-pass input a mapping/vision step refines, not ground truth.

    python3 tools/infer_labels.py                 # all forms with a local blank
    python3 tools/infer_labels.py --forms IRS-SS-4
"""
import argparse
import csv
import pathlib
import re
import sys

import fitz

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.vision_map import _slug  # shared field_id slugger  # noqa: E402

FORMS = ROOT / "forms"


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s[:120]


def caption_for(rect, words, is_checkbox: bool) -> str:
    """words: list of (x0,y0,x1,y1,text,...) from page.get_text('words')."""
    x0, y0, x1, y1 = rect
    ymid = (y0 + y1) / 2
    row = [w for w in words if w[1] <= ymid <= w[3] or (y0 <= w[3] and w[1] <= y1)]
    if is_checkbox:
        # caption to the right, same row, nearest
        right = sorted([w for w in row if w[0] >= x1 - 2 and w[0] < x1 + 260],
                       key=lambda w: w[0])
        if right:
            return _clean(" ".join(w[4] for w in right[:8]))
    # text field: caption to the left, same row
    left = sorted([w for w in row if w[2] <= x0 + 2 and w[2] > x0 - 320],
                  key=lambda w: w[0])
    if left:
        return _clean(" ".join(w[4] for w in left[-10:]))
    # fall back to the nearest line above (x-overlapping)
    above = [w for w in words if w[3] <= y0 + 1 and not (w[2] < x0 - 40 or w[0] > x1 + 40)]
    if above:
        ny = max(w[3] for w in above)
        line = sorted([w for w in above if abs(w[3] - ny) < 6], key=lambda w: w[0])
        return _clean(" ".join(w[4] for w in line[:10]))
    return ""


def inventory(fid: str) -> int:
    pdf = FORMS / fid / f"{fid}.pdf"
    if not pdf.exists():
        return -1
    doc = fitz.open(pdf)
    rows, used = [], set()
    for pno in range(doc.page_count):
        page = doc[pno]
        words = page.get_text("words")
        for w in (page.widgets() or []):
            r = w.rect
            t = w.field_type_string
            is_cb = "CheckBox" in t or "RadioButton" in t
            rows.append({
                "field_id": _slug(w.field_name, used),
                "label": w.field_name,
                "caption": caption_for((r.x0, r.y0, r.x1, r.y1), words, is_cb),
                "type": ("checkbox" if "CheckBox" in t
                         else "radio" if "RadioButton" in t
                         else t.lower() if t != "Text" else "text"),
                "page": pno,
                "rect": f"{r.x0:.1f},{r.y0:.1f},{r.x1:.1f},{r.y1:.1f}",
            })
    doc.close()
    out = FORMS / fid / "fields.csv"
    with open(out, "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["field_id", "label", "caption",
                                            "type", "page", "rect"])
        wr.writeheader()
        wr.writerows(rows)
    labeled = sum(1 for r in rows if r["caption"])
    print(f"  {fid}: {len(rows)} widgets, {labeled} captioned ({100*labeled//max(len(rows),1)}%) -> {out.relative_to(ROOT)}")
    return labeled


def main():
    ap = argparse.ArgumentParser(description="Infer widget captions into fields.csv")
    ap.add_argument("--forms", help="comma list (default: all forms with a local blank)")
    args = ap.parse_args()
    ids = ([f.strip() for f in args.forms.split(",")] if args.forms
           else sorted(d.name for d in FORMS.iterdir() if d.is_dir()))
    for fid in ids:
        if inventory(fid) < 0:
            print(f"  {fid}: no local blank (run tools/fetch_pdfs.py --forms {fid})")


if __name__ == "__main__":
    main()
