#!/usr/bin/env python3
"""Fill a form directly from its ``mapping.json`` + a canonical fact object.

Shim over the shared ``maine-forms-engine``
(``maine_forms_engine.fill.fill_via_mapping``), configured with this repo's
policy; the CLI and the ``resolve_mapping`` / ``fill_via_mapping`` APIs are
unchanged:

- only the allowlisted ``FILLABLE_STATUSES`` (reviewed tiers) fill; anything
  else — "recipe" (pointer-only map), "remap-pending" (upstream blank
  drifted), "unmapped" — is refused with a machine-readable reason instead of
  a silent partial fill. The unreviewed "vision-mapped" DRAFT tier is refused
  by default and only fills under an explicit opt-in (``allow_draft=True`` /
  ``TTF_ALLOW_DRAFT`` / ``--allow-draft``), which warns loudly.
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
import os
import pathlib
import sys
import warnings

from maine_forms_engine.fill.fill_via_mapping import (  # noqa: F401
    _resolve_key,
    _split_name,
    _width_fit,
    fill_via_mapping as _pkg_fill_via_mapping,
    resolve_mapping as _pkg_resolve_mapping,
)

OSS_ROOT = pathlib.Path(__file__).resolve().parent.parent
_MANIFEST = OSS_ROOT / "catalog" / "pdf_manifest.json"

# mapping.json statuses the engine will fill from BY DEFAULT — reviewed tiers
# only. "vision-mapped" is a DRAFT tier: every shipped vision-mapped map is an
# unreviewed vision-LLM draft carrying a "review before production" note, and
# these back real IRS/MRS PDFs. It is therefore NOT fillable by default; it is
# opt-in via allow_draft=True (or the TTF_ALLOW_DRAFT env var / --allow-draft
# CLI flag), which restores it with a loud warning.
FILLABLE_STATUSES = frozenset({"verified", "opus-adjudicated", "mapped"})

# The draft tier that allow_draft restores.
DRAFT_STATUSES = frozenset({"vision-mapped"})

# allow_draft also accepted via env (TTF_* is this repo's prefix; MCF_* honored
# as a fallback for setups carried over from the court-forms sibling repos).
_ALLOW_DRAFT_ENV = ("TTF_ALLOW_DRAFT", "MCF_ALLOW_DRAFT")


def _env_allow_draft() -> bool:
    for name in _ALLOW_DRAFT_ENV:
        val = os.environ.get(name)
        if val is not None:
            return val.strip().lower() not in ("", "0", "false", "no", "off")
    return False


def _fillable_statuses(allow_draft: bool) -> frozenset:
    """Resolve the effective fillable-status set. When drafts are allowed
    (explicit arg OR env), fold in DRAFT_STATUSES and warn loudly."""
    if not allow_draft:
        return FILLABLE_STATUSES
    warnings.warn(
        "allow_draft is enabled: UNREVIEWED 'vision-mapped' drafts will be "
        "filled onto real IRS/MRS PDFs. Every shipped vision-mapped map is a "
        "vision-LLM draft marked 'review before production' — do NOT use the "
        "output for a real filing without human review.",
        stacklevel=3)
    print(
        "WARNING: allow_draft — filling UNREVIEWED vision-mapped drafts "
        "onto real IRS/MRS PDFs. Review the output before any real filing.",
        file=sys.stderr)
    return FILLABLE_STATUSES | DRAFT_STATUSES

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
                    forms_root: pathlib.Path = OSS_ROOT / "forms",
                    *, allow_draft: bool | None = None) -> dict:
    """Resolve a form's mapping.json against a canonical fact object.

    Pure (no PDF needed): returns coverage stats + the field_id->value map.

    ``allow_draft``: opt in to filling unreviewed "vision-mapped" drafts.
    ``None`` (default) falls back to the TTF_ALLOW_DRAFT env var (default off).
    """
    if allow_draft is None:
        allow_draft = _env_allow_draft()
    return _pkg_resolve_mapping(form_id, facts, forms_root,
                                fillable_statuses=_fillable_statuses(
                                    allow_draft),
                                skip_reasons=_SKIP_REASONS,
                                require_built_against=True,
                                manifest_path=_MANIFEST)


def fill_via_mapping(form_id: str, facts: dict, out_dir: pathlib.Path,
                     forms_root: pathlib.Path = OSS_ROOT / "forms",
                     *, allow_draft: bool | None = None) -> dict:
    """Resolve mapping.json and write a filled PDF.

    ``allow_draft``: opt in to filling unreviewed "vision-mapped" drafts.
    ``None`` (default) falls back to the TTF_ALLOW_DRAFT env var (default off).
    """
    if allow_draft is None:
        allow_draft = _env_allow_draft()
    return _pkg_fill_via_mapping(form_id, facts, out_dir, forms_root,
                                 fillable_statuses=_fillable_statuses(
                                     allow_draft),
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
    ap.add_argument("--allow-draft", action="store_true",
                    help="ALSO fill unreviewed 'vision-mapped' drafts "
                         "(default: refused). Emits a loud warning; the "
                         "output must be human-reviewed before any real "
                         "filing. Also settable via TTF_ALLOW_DRAFT=1.")
    args = ap.parse_args()
    fdir = OSS_ROOT / "forms" / args.form
    case_path = args.case or (fdir / "examples" / "sample_case.json")
    facts = json.loads(case_path.read_text())
    # CLI flag OR env; None lets the function fall back to the env var.
    allow_draft = True if args.allow_draft else None
    res = fill_via_mapping(args.form, facts, args.out, allow_draft=allow_draft)
    print(json.dumps(res, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
