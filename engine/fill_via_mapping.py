#!/usr/bin/env python3
"""Fill a form directly from its ``mapping.json`` + a canonical fact object.

Shim over the shared ``maine-forms-engine``
(``maine_forms_engine.fill.fill_via_mapping``), configured with this repo's
policy; the CLI and the ``resolve_mapping`` / ``fill_via_mapping`` APIs are
unchanged:

- only the allowlisted ``FILLABLE_STATUSES`` fill; anything else — "recipe"
  (pointer-only map), "remap-pending" (upstream blank drifted), "unmapped" —
  is refused with a machine-readable reason instead of a silent partial fill.
- a mapping recording ``built_against_sha256`` is refused when the manifest
  no longer pins that revision (the MRS-1041ME incident class).
- the fill-time blank guard reads ``TTF_VERIFY_BLANK`` (with
  ``MCF_VERIFY_BLANK`` honored as a fallback for setups carried over from the
  court-forms sibling repos).
- results carry the fill diagnostics (``fields_written`` = widgets actually
  written, ``missing_widgets``, ``overflowed``, ``blank_verified``).
"""
from __future__ import annotations

import argparse
import json
import pathlib

from maine_forms_engine.fill.fill_via_mapping import (  # noqa: F401
    _resolve_key,
    _split_name,
    _width_fit,
    fill_via_mapping as _pkg_fill_via_mapping,
    resolve_mapping as _pkg_resolve_mapping,
)

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
_MANIFEST = OSS_ROOT / "catalog" / "pdf_manifest.json"

# mapping.json statuses the engine will fill from. "vision-mapped" is a draft
# tier: filling it is how a draft is reviewed, so it stays fillable; its
# status travels in the result for the caller to see.
FILLABLE_STATUSES = frozenset({"verified", "opus-adjudicated", "mapped",
                               "vision-mapped"})

_SKIP_REASONS = {
    "recipe": ("mapping.json is a pointer with an empty map — no direct "
               "mapping exists in this repo; build one (tools/build_manifest.py "
               "+ a mapping pass) before filling"),
    "remap-pending": ("the upstream blank drifted from the revision this "
                      "mapping was built against; re-map "
                      "(tools/build_manifest.py + a mapping pass) before "
                      "filling"),
}


def resolve_mapping(form_id: str, facts: dict,
                    forms_root: pathlib.Path = OSS_ROOT / "forms") -> dict:
    """Resolve a form's mapping.json against a canonical fact object.

    Pure (no PDF needed): returns coverage stats + the field_id->value map.
    """
    return _pkg_resolve_mapping(form_id, facts, forms_root,
                                fillable_statuses=FILLABLE_STATUSES,
                                skip_reasons=_SKIP_REASONS,
                                require_built_against=True,
                                manifest_path=_MANIFEST)


def fill_via_mapping(form_id: str, facts: dict, out_dir: pathlib.Path,
                     forms_root: pathlib.Path = OSS_ROOT / "forms") -> dict:
    """Resolve mapping.json and write a filled PDF."""
    return _pkg_fill_via_mapping(form_id, facts, out_dir, forms_root,
                                 fillable_statuses=FILLABLE_STATUSES,
                                 skip_reasons=_SKIP_REASONS,
                                 require_built_against=True,
                                 manifest_path=_MANIFEST,
                                 blank_verify_env=("TTF_VERIFY_BLANK",
                                                   "MCF_VERIFY_BLANK"),
                                 result_style="tax")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--form", required=True)
    ap.add_argument("--case", type=pathlib.Path,
                    help="canonical fact object JSON "
                         "(default: the form's examples/sample_case.json)")
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("/tmp/mapping_fill"))
    args = ap.parse_args()
    fdir = OSS_ROOT / "forms" / args.form
    case_path = args.case or (fdir / "examples" / "sample_case.json")
    facts = json.loads(case_path.read_text())
    res = fill_via_mapping(args.form, facts, args.out)
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
