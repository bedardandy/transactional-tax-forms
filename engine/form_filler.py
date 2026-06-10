"""Form filler — shim over the shared ``maine-forms-engine``, configured with
this repo's policy:

- ``fill_form`` / ``fill_form_from_json`` return the diagnostics dict
  ``{output_path, filled_count, missing_fields, overflowed}`` (the package's
  ``return_report=True``), because ``missing_fields`` is the stale-mapping
  signal callers here must surface.
- only ``addendum_policy="none"`` is supported: this repo does not ship the
  addendum renderer (it lives in the maine-court-forms sibling), so any other
  policy raises ValueError up front instead of silently dropping overflow.
"""
from pathlib import Path

from maine_forms_engine.fill.form_filler import (  # noqa: F401
    _multi_widget_mode,
    _split_address_at_commas,
    _widget_capacity_chars,
    _wrap_across_widgets,
    fill_form as _pkg_fill_form,
    generate_template,
    list_form_fields,
)

SUPPORTED_POLICIES = frozenset({"none"})


def fill_form(pdf_path, field_data, output_path=None, *,
              tree=None, addendum_policy="none", form_id=None) -> dict:
    """Fill an AcroForm PDF; returns the result dict (see package docs)."""
    return _pkg_fill_form(pdf_path, field_data, output_path,
                         tree=tree, addendum_policy=addendum_policy,
                         form_id=form_id,
                         supported_policies=SUPPORTED_POLICIES,
                         return_report=True)


def fill_form_from_json(pdf_path, json_path, output_path=None) -> dict:
    """Fill a form from a JSON file; returns the fill_form result dict."""
    import json
    data = json.loads(Path(json_path).read_text())
    return fill_form(pdf_path, data, output_path)
