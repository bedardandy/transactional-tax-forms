#!/usr/bin/env python3
"""Re-verify a mapping.json against the pinned blank, then stamp it.

Shim over the shared ``maine-forms-engine``
(``maine_forms_engine.verify_mapping``, extracted from this tool); the CLI is
unchanged, anchored to this repo's ``forms/`` tree and
``catalog/pdf_manifest.json``. ``built_against_sha256`` is the staleness gate
the engine enforces at fill time (the MRS-1041ME incident class: the status
flag said fillable while 37 mapped widgets no longer existed in a re-issued
blank). A mapping must only carry the stamp after an honest re-verification
against the very revision the manifest pins — never as a blind back-fill.
Per form this tool checks blank identity (on-disk PDF matches the manifest
SHA-256 byte-for-byte) and field survival (every ``mapping.map`` field_id
resolves through ``schema.json`` to a live AcroForm widget;
``field_splits.json`` names count as present).

Read-only by default. ``--stamp`` writes ``built_against_sha256`` only for
forms that fully verify; exit code is non-zero when any checked form fails,
so it gates a pipeline.

Usage:
    python3 tools/verify_mapping_fields.py                   # verify all
    python3 tools/verify_mapping_fields.py --forms IRS-706
    python3 tools/verify_mapping_fields.py --json            # machine report
    python3 tools/verify_mapping_fields.py --stamp           # verify + stamp
"""
import pathlib
import sys

from maine_forms_engine import verify_mapping as _vm

ROOT = pathlib.Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"
MANIFEST = ROOT / "catalog" / "pdf_manifest.json"


def verify_form(fid: str, manifest: dict,
                forms_root: pathlib.Path = FORMS) -> dict:
    """Verify one form's mapping against the pinned blank.

    Returns ``{form_id, ok, ...}``; ``ok`` is True only when the blank
    matches the manifest hash AND every mapped field resolves to a live
    widget. Failure modes carry a ``reason`` plus the offending lists.
    """
    return _vm.verify_form(fid, manifest, forms_root)


def stamp(fid: str, sha: str, forms_root: pathlib.Path = FORMS) -> bool:
    """Write ``built_against_sha256`` into mapping.json (after ``model`` /
    ``status``, the shape MRS-1041ME and MRS-700SOV already carry). Returns
    True when the file changed."""
    return _vm.stamp(fid, sha, forms_root)


def main(argv=None) -> int:
    return _vm.main(argv, default_forms_root=FORMS, default_manifest=MANIFEST)


if __name__ == "__main__":
    sys.exit(main())
