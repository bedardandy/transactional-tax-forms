"""Offline engine unit tests — no fetched blanks needed, so they run in CI.

Covers the pieces test_fill_smoke.py only exercises when a local blank PDF is
present: text fitting, canonical key resolution, multi-widget wrapping, and a
real fill round-trip against a synthetic AcroForm built with PyMuPDF.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import text_fit  # noqa: E402
from engine.fill_via_mapping import _resolve_key, resolve_mapping  # noqa: E402
from engine.form_filler import _wrap_across_widgets, fill_form  # noqa: E402


class TextFit(unittest.TestCase):
    def test_fit_name_collapses_middle_then_first(self):
        name = "Robert James Sterling"
        self.assertEqual(text_fit.fit_name(name, 18), "Robert J. Sterling")
        self.assertEqual(text_fit.fit_name(name, 14), "R. J. Sterling")

    def test_fit_name_never_truncates(self):
        # Two-part name: nothing safe to collapse -> returned unchanged.
        self.assertEqual(text_fit.fit_name("Jane Doe", 4), "Jane Doe")

    def test_fit_name_keeps_suffix(self):
        out = text_fit.fit_name("Robert James Sterling Jr.", 22)
        self.assertEqual(out, "Robert J. Sterling Jr.")

    def test_abbreviate_address(self):
        self.assertEqual(text_fit.abbreviate_address("100 Main Street, Suite 4"),
                         "100 Main St, Ste 4")

    def test_fit_generic_truncates_at_word_boundary(self):
        self.assertEqual(text_fit.fit("alpha beta gamma", 12), "alpha beta")

    def test_widget_char_budget(self):
        self.assertEqual(text_fit.widget_char_budget([0, 0, 100, 20]), 20)
        self.assertEqual(text_fit.widget_char_budget([0, 0, 0, 20]), 999)


class ResolveKey(unittest.TestCase):
    FACTS = {
        "matter": {"docket_number": "RE-2025-1"},
        "parties": {"plaintiff": {"full_name": "Jane Q. Doe"}},
        "entity": {"ein": "00-0000000"},
        "facts": {"date_of_death": "2025-01-15", "amount": 1000},
    }

    def test_dotted_walk(self):
        self.assertEqual(_resolve_key("matter.docket_number", self.FACTS),
                         "RE-2025-1")
        self.assertEqual(_resolve_key("entity.ein", self.FACTS), "00-0000000")

    def test_missing_key_is_none(self):
        self.assertIsNone(_resolve_key("entity.phone", self.FACTS))
        self.assertIsNone(_resolve_key("nobody.name", self.FACTS))

    def test_name_parts_derived_from_full_name(self):
        self.assertEqual(
            _resolve_key("parties.plaintiff.first_name", self.FACTS), "Jane")
        self.assertEqual(
            _resolve_key("parties.plaintiff.middle_name", self.FACTS), "Q.")
        self.assertEqual(
            _resolve_key("parties.plaintiff.last_name", self.FACTS), "Doe")

    def test_iso_dates_render_us_style(self):
        self.assertEqual(_resolve_key("facts.date_of_death", self.FACTS),
                         "01/15/2025")

    def test_numbers_stringified(self):
        self.assertEqual(_resolve_key("facts.amount", self.FACTS), "1000")

    def test_today_is_computed(self):
        import datetime
        self.assertEqual(_resolve_key("today()", {}),
                         datetime.date.today().strftime("%m/%d/%Y"))


class WrapAcrossWidgets(unittest.TestCase):
    def test_value_wraps_in_capacity_order(self):
        lines, rem = _wrap_across_widgets("one two three four", [8, 20])
        self.assertEqual(lines, ["one two", "three four"])
        self.assertEqual(rem, "")

    def test_overflow_past_last_widget_is_returned(self):
        lines, rem = _wrap_across_widgets("aa bb cc dd", [5, 5])
        self.assertEqual(lines, ["aa bb", "cc dd"][:len(lines)])
        # whatever didn't fit must come back as the remainder, not vanish
        self.assertEqual((" ".join(lines) + " " + rem).split(),
                         "aa bb cc dd".split())

    def test_word_wider_than_widget_skips_ahead(self):
        lines, rem = _wrap_across_widgets("longword ok", [4, 10])
        self.assertEqual(lines[0], "")
        self.assertEqual(lines[1], "longword")
        self.assertEqual(rem, "ok")


def _synthetic_form(path: Path) -> None:
    """Two-page AcroForm: text fields, a checkbox, and a 2-widget group."""
    doc = fitz.open()
    page = doc.new_page()
    for i, name in enumerate(("name_field", "addr_field")):
        w = fitz.Widget()
        w.field_name = name
        w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        w.rect = fitz.Rect(72, 100 + 40 * i, 400, 120 + 40 * i)
        page.add_widget(w)
    cb = fitz.Widget()
    cb.field_name = "consent_box"
    cb.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
    cb.rect = fitz.Rect(72, 200, 86, 214)
    page.add_widget(cb)
    # multi-widget group: same field name on two stacked lines
    for i in range(2):
        w = fitz.Widget()
        w.field_name = "narrative"
        w.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        w.rect = fitz.Rect(72, 250 + 22 * i, 300, 266 + 22 * i)
        page.add_widget(w)
    doc.save(str(path))
    doc.close()


class FillSyntheticPdf(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.blank = Path(self.td.name) / "blank.pdf"
        _synthetic_form(self.blank)

    def tearDown(self):
        self.td.cleanup()

    def test_fill_roundtrip_and_diagnostics(self):
        out = Path(self.td.name) / "filled.pdf"
        data = {
            "name_field": "Example LLC",
            "addr_field": "123 Main St, Portland, ME 04101",
            "consent_box": "yes",
            "ghost_field": "value with no widget",
        }
        res = fill_form(self.blank, data, out)
        self.assertEqual(res["missing_fields"], ["ghost_field"])
        self.assertEqual(res["filled_count"], 3)
        self.assertEqual(res["output_path"], str(out))

        doc = fitz.open(str(out))
        values = {w.field_name: w.field_value
                  for p in doc for w in p.widgets()}
        doc.close()
        self.assertEqual(values["name_field"], "Example LLC")
        self.assertEqual(values["addr_field"], "123 Main St, Portland, ME 04101")
        self.assertEqual(values["consent_box"], "Yes")

    def test_checkbox_ignores_non_affirmative_value(self):
        out = Path(self.td.name) / "filled.pdf"
        fill_form(self.blank, {"consent_box": "Jane Q. Doe"}, out)
        doc = fitz.open(str(out))
        values = {w.field_name: w.field_value
                  for p in doc for w in p.widgets()}
        doc.close()
        self.assertEqual(values["consent_box"], "Off")

    def test_multi_widget_group_wraps_as_overlay(self):
        out = Path(self.td.name) / "filled.pdf"
        long_text = "alpha beta gamma delta epsilon zeta eta theta " * 2
        res = fill_form(self.blank, {"narrative": long_text.strip()}, out)
        self.assertGreaterEqual(res["filled_count"], 1)
        # group widgets are deleted and replaced with stamped text
        doc = fitz.open(str(out))
        names = {w.field_name for p in doc for w in p.widgets()}
        page_text = doc[0].get_text()
        doc.close()
        self.assertNotIn("narrative", names)
        self.assertIn("alpha beta", page_text)

    def test_unsupported_addendum_policy_raises(self):
        with self.assertRaises(ValueError):
            fill_form(self.blank, {}, Path(self.td.name) / "x.pdf",
                      addendum_policy="auto")

    def test_fill_form_from_json(self):
        from engine.form_filler import fill_form_from_json
        case = Path(self.td.name) / "data.json"
        case.write_text(json.dumps({"name_field": "From JSON"}))
        out = Path(self.td.name) / "filled.pdf"
        res = fill_form_from_json(self.blank, case, out)
        self.assertEqual(res["filled_count"], 1)


class BuiltAgainstSha(unittest.TestCase):
    """resolve_mapping refuses a mapping pinned to a drifted blank revision."""

    FID = "MRS-1041ME"  # any form with a real catalog/pdf_manifest.json entry

    def _root_with_mapping(self, td: Path, sha: str) -> Path:
        fdir = td / self.FID
        fdir.mkdir(parents=True)
        (fdir / "mapping.json").write_text(json.dumps({
            "form_id": self.FID, "status": "mapped",
            "built_against_sha256": sha,
            "map": {"some_field": "facts.amount"}}))
        (fdir / "schema.json").write_text(json.dumps({
            "form_id": self.FID,
            "fields": [{"field_id": "some_field", "label": "Some Field",
                        "type": "text", "page": 0, "rect": [0, 0, 100, 12]}]}))
        return td

    def test_drifted_revision_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._root_with_mapping(Path(td), "0" * 64)
            res = resolve_mapping(self.FID, {"facts": {"amount": 1}},
                                  forms_root=root)
        self.assertTrue(res.get("skipped"))
        self.assertIn("drifted", res["reason"])

    def test_matching_revision_resolves(self):
        manifest = json.loads(
            (ROOT / "catalog" / "pdf_manifest.json").read_text())
        pinned = manifest["forms"][self.FID]["sha256"]
        with tempfile.TemporaryDirectory() as td:
            root = self._root_with_mapping(Path(td), pinned)
            res = resolve_mapping(self.FID, {"facts": {"amount": 1}},
                                  forms_root=root)
        self.assertFalse(res.get("skipped"))
        self.assertEqual(res["resolved"], 1)


if __name__ == "__main__":
    unittest.main()
