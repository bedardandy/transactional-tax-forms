#!/usr/bin/env python3
"""Detect when an agency has re-issued a blank form out from under its mapping.

Shim over the shared ``maine-forms-engine``
(``maine_forms_engine.drift.check_upstream``); the CLI is unchanged, with this
repo's ``catalog/pdf_manifest.json`` as the default manifest. Maine Revenue
Services and the IRS re-issue forms (often yearly); when the bytes change, the
widget layout can move and a fill built on the old mapping can land values in
the wrong place. Read-only by default; exit code is non-zero if any form is
CHANGED or GONE, so it gates a pipeline.

Usage:
    python3 tools/check_upstream.py                      # check every form
    python3 tools/check_upstream.py --forms IRS-SS-4,MRS-706ME
    python3 tools/check_upstream.py --json               # machine-readable report
    python3 tools/check_upstream.py --update-manifest    # after re-mapping: adopt new hashes
"""
import pathlib
import sys

from maine_forms_engine.drift import check_upstream as _cu

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tools.fetch_pdfs import _download  # noqa: E402,F401 — kept patchable for tests

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "catalog" / "pdf_manifest.json"


def check_one(fid: str, entry: dict, timeout: int, retries: int) -> dict:
    """Probe one form's official URL and classify it against the manifest."""
    return _cu.check_one(fid, entry, timeout, retries,
                         downloader=lambda u, t, r: _download(u, t, r))


def _update_hint(changed: list) -> str:
    ids_changed = ",".join(r["form_id"] for r in changed)
    return ("The per-form widget inventories are NOT refreshed by this "
            "tool — run\n"
            f"  python3 tools/build_manifest.py --forms {ids_changed}\n"
            "to rewrite widgets.json, then re-map + audit each form "
            "before publishing.")


def main() -> int:
    return _cu.main(default_manifest=MANIFEST, update_hint=_update_hint,
                    downloader=lambda u, t, r: _download(u, t, r))


if __name__ == "__main__":
    sys.exit(main())
