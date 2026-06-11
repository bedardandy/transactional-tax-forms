#!/usr/bin/env python3
"""Re-verify a mapping.json against the pinned blank, then stamp it.

``built_against_sha256`` is the staleness gate the engine enforces at fill
time (the MRS-1041ME incident class: the status flag said fillable while 37
mapped widgets no longer existed in a re-issued blank). A mapping must only
carry the stamp after an honest re-verification against the very revision the
manifest pins — never as a blind back-fill. Per form this tool checks:

1. **blank identity** — the on-disk ``forms/<ID>/<ID>.pdf`` matches the
   ``catalog/pdf_manifest.json`` SHA-256 byte-for-byte (so the field check
   below is made against the pinned revision, not a swapped file);
2. **field survival** — every ``mapping.map`` field_id resolves through
   ``schema.json`` to a widget name present in the blank's AcroForm tree.
   Names introduced by ``field_splits.json`` count as present (the fill path
   splits a working copy before writing). ``"manual"`` radio entries and
   documented ``dropped_keys`` never enter ``map`` and are exempt by
   construction.

Read-only by default. ``--stamp`` writes ``built_against_sha256`` (the
manifest hash) into ``mapping.json`` — only for forms that fully verify; a
form that fails stays unstamped and is reported (re-map it, the MRS-1041ME
treatment, before it may fill). Exit code is non-zero when any checked form
fails, so it gates a pipeline.

Usage:
    python3 tools/verify_mapping_fields.py                   # verify all
    python3 tools/verify_mapping_fields.py --forms IRS-706
    python3 tools/verify_mapping_fields.py --json            # machine report
    python3 tools/verify_mapping_fields.py --stamp           # verify + stamp
"""
import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"
MANIFEST = ROOT / "catalog" / "pdf_manifest.json"


def _acroform_names(pdf_path: pathlib.Path) -> set:
    import fitz
    doc = fitz.open(str(pdf_path))
    try:
        return {w.field_name for page in doc for w in page.widgets() or []}
    finally:
        doc.close()


def _split_names(fdir: pathlib.Path) -> set:
    """Widget names a fill-time field split introduces (field_splits.json)."""
    p = fdir / "field_splits.json"
    if not p.exists():
        return set()
    spec = json.loads(p.read_text())
    return {s["new_name"] for s in spec.get("splits", []) if s.get("new_name")}


def verify_form(fid: str, manifest: dict,
                forms_root: pathlib.Path = FORMS) -> dict:
    """Verify one form's mapping against the pinned blank.

    Returns ``{form_id, ok, ...}``; ``ok`` is True only when the blank
    matches the manifest hash AND every mapped field resolves to a live
    widget. Failure modes carry a ``reason`` plus the offending lists.
    """
    fdir = forms_root / fid
    out = {"form_id": fid, "ok": False}
    mapping = json.loads((fdir / "mapping.json").read_text())
    out["status"] = mapping.get("status")
    fmap = mapping.get("map") or {}
    if not fmap:
        out["reason"] = "empty map (recipe pointer) — nothing to verify"
        return out
    entry = (manifest.get("forms") or {}).get(fid) or {}
    pinned = (entry.get("sha256") or "").lower()
    if not pinned:
        out["reason"] = "no catalog/pdf_manifest.json sha256 entry"
        return out
    out["manifest_sha256"] = pinned
    pdf = fdir / f"{fid}.pdf"
    if not pdf.exists():
        out["reason"] = f"blank not fetched: {pdf.name} (tools/fetch_pdfs.py)"
        return out
    on_disk = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if on_disk != pinned:
        out["reason"] = (f"on-disk blank is {on_disk[:12]}… but the manifest "
                         f"pins {pinned[:12]}… — refusing to verify a mapping "
                         "against the wrong revision")
        return out
    labels = {f["field_id"]: f["label"]
              for f in json.loads((fdir / "schema.json").read_text())
              .get("fields", [])}
    names = _acroform_names(pdf) | _split_names(fdir)
    missing_in_schema = sorted(f for f in fmap if f not in labels)
    missing_in_pdf = sorted({labels[f] for f in fmap
                             if f in labels and labels[f] not in names})
    out["mapped_fields"] = len(fmap)
    out["missing_in_schema"] = missing_in_schema
    out["missing_in_pdf"] = missing_in_pdf
    if missing_in_schema or missing_in_pdf:
        out["reason"] = (f"{len(missing_in_schema)} field_id(s) absent from "
                         f"schema.json, {len(missing_in_pdf)} widget name(s) "
                         "absent from the blank — re-map before stamping")
        return out
    out["ok"] = True
    return out


def stamp(fid: str, sha: str, forms_root: pathlib.Path = FORMS) -> bool:
    """Write ``built_against_sha256`` into mapping.json (after ``model`` /
    ``status``, the shape MRS-1041ME and MRS-700SOV already carry). Returns
    True when the file changed."""
    p = forms_root / fid / "mapping.json"
    raw = p.read_text()
    mapping = json.loads(raw)
    if mapping.get("built_against_sha256") == sha:
        return False
    rebuilt = {}
    anchor = "model" if "model" in mapping else "status"
    for k, v in mapping.items():
        if k == "built_against_sha256":
            continue
        rebuilt[k] = v
        if k == anchor:
            rebuilt["built_against_sha256"] = sha
    indent = 4 if raw.startswith('{\n    "') else 2
    p.write_text(json.dumps(rebuilt, indent=indent)
                 + ("\n" if raw.endswith("\n") else ""))
    return True


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forms", help="comma list of form ids (default: all)")
    ap.add_argument("--stamp", action="store_true",
                    help="write built_against_sha256 for forms that verify")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="machine-readable report on stdout")
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    fids = ([f.strip() for f in args.forms.split(",") if f.strip()]
            if args.forms else
            sorted(d.name for d in FORMS.iterdir()
                   if (d / "mapping.json").exists()))
    results, failed = [], []
    for fid in fids:
        r = verify_form(fid, manifest)
        if r["ok"] and args.stamp:
            r["stamped"] = stamp(fid, r["manifest_sha256"])
        results.append(r)
        if not r["ok"]:
            failed.append(fid)
        if not args.as_json:
            mark = "OK " if r["ok"] else "FAIL"
            extra = (f" ({r['mapped_fields']} mapped fields live)"
                     if r["ok"] else f" — {r['reason']}")
            if r.get("stamped"):
                extra += " [stamped]"
            print(f"{mark} {fid}{extra}")
    if args.as_json:
        print(json.dumps({"results": results, "failed": failed}, indent=2))
    elif failed:
        print(f"\n{len(failed)} form(s) failed verification: "
              f"{', '.join(failed)} — fix or mark remap-pending; "
              "do NOT stamp them.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
