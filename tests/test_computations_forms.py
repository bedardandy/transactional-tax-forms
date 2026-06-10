"""Per-form computations.json: anti-fabrication + end-to-end behavior.

Offline checks (always run): every computations.json loads through the shared
engine (op vocabulary, cycle detection), every target/input key is actually
mapped, and the declared arithmetic balances on the form's sample case.

PDF-dependent checks (skip when the blank isn't fetched, like the fill
smoke): every ``formula_text`` is the instruction printed VERBATIM on the
official blank, and the two fill behaviors hold end-to-end — an omitted total
is computed and lands in the PDF; a supplied contradiction is written as-is
with a COMPUTATION_MISMATCH warning in the CLI result and the MCP fill_form
response.
"""
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from maine_forms_engine.computations import (  # noqa: E402
    evaluate, load_computations)
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402

FORMS = ROOT / "forms"
COMP_FORMS = sorted(d.parent.name
                    for d in FORMS.glob("*/computations.json"))


def _norm(s: str) -> str:
    """Whitespace/leader-dot/dash normalization for verbatim matching."""
    s = s.replace("—", "-").replace("–", "-")
    s = re.sub(r"\.{2,}", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class ComputationsOffline(unittest.TestCase):
    def test_forms_with_computations_exist(self):
        self.assertEqual(COMP_FORMS, ["IRS-1041", "IRS-706", "MRS-1041ME",
                                      "MRS-1120ME", "MRS-706ME", "MRS-W4ME"])

    def test_loads_and_keys_are_mapped(self):
        for fid in COMP_FORMS:
            with self.subTest(form=fid):
                comp = load_computations(FORMS / fid)  # validates ops/cycles
                mapping = json.loads((FORMS / fid / "mapping.json").read_text())
                mapped = set(mapping.get("map", {}).values())
                for key, spec in comp["computed"].items():
                    self.assertIn(key, mapped, f"{fid}: target {key}")
                    for raw in spec["inputs"]:
                        self.assertIn(raw.lstrip("-"), mapped,
                                      f"{fid}: input {raw}")
                    # anti-fabrication: verbatim quote required
                    self.assertTrue(spec.get("formula_text", "").strip())

    def test_sample_cases_balance(self):
        """The shipped examples are arithmetic-consistent: no mismatch
        warnings, no skip notes, nothing left to compute."""
        for fid in COMP_FORMS:
            with self.subTest(form=fid):
                comp = load_computations(FORMS / fid)
                case = json.loads(
                    (FORMS / fid / "examples" / "sample_case.json").read_text())
                r = evaluate(comp, case)
                self.assertEqual(r["warnings"], [])
                self.assertEqual(r["notes"], [])
                self.assertEqual(r["computed"], [])


class ComputationsVerbatim(unittest.TestCase):
    """formula_text must appear verbatim in the fetched blank's text."""

    def test_formula_text_is_printed_on_the_blank(self):
        import fitz
        ran = 0
        for fid in COMP_FORMS:
            pdf = FORMS / fid / f"{fid}.pdf"
            if not pdf.exists():
                continue
            ran += 1
            doc = fitz.open(str(pdf))
            text = _norm(" ".join(p.get_text() for p in doc))
            doc.close()
            comp = load_computations(FORMS / fid)
            for key, spec in comp["computed"].items():
                with self.subTest(form=fid, key=key):
                    self.assertIn(_norm(spec["formula_text"]), text)
        if not ran:
            self.skipTest("no local blank PDFs (CI / unfetched)")


class ComputationsEndToEnd(unittest.TestCase):
    """MRS-1041ME line 7d: 'd. Total payments. (Add lines 7a, 7b and 7c.)'"""

    FORM = "MRS-1041ME"
    TOTAL_WIDGET = "Fidu 1041 Total payments"  # schema label = widget name

    def setUp(self):
        if not (FORMS / self.FORM / f"{self.FORM}.pdf").exists():
            self.skipTest("blank not fetched")
        self.case = json.loads(
            (FORMS / self.FORM / "examples" / "sample_case.json").read_text())

    def _widget(self, pdf_path):
        import fitz
        doc = fitz.open(pdf_path)
        try:
            for page in doc:
                for w in page.widgets() or []:
                    if w.field_name == self.TOTAL_WIDGET:
                        return w.field_value
        finally:
            doc.close()
        return None

    def test_omitted_total_is_computed_and_filled(self):
        del self.case["facts"]["total_payments"]
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, Path(td))
            self.assertTrue(r["ok"])
            by_key = {e["key"]: e for e in r["computed_fields"]}
            e = by_key["facts.total_payments"]
            self.assertEqual(e["kind"], "computed")
            self.assertEqual(e["value"], "3000")  # 1000 + 1000 + 1000
            self.assertEqual(
                e["formula_text"],
                "d. Total payments. (Add lines 7a, 7b and 7c.)")
            self.assertEqual(self._widget(r["out_pdf"]), "3000")

    def test_supplied_contradiction_written_as_is_with_warning(self):
        self.case["facts"]["total_payments"] = "999"
        with tempfile.TemporaryDirectory() as td:
            r = fill_via_mapping(self.FORM, self.case, Path(td))
            self.assertTrue(r["ok"])
            warns = [w for w in r["computation_warnings"]
                     if w["key"] == "facts.total_payments"]
            self.assertEqual(warns, [{
                "code": "COMPUTATION_MISMATCH",
                "key": "facts.total_payments",
                "supplied": "999", "computed": "3000",
                "formula_text": "d. Total payments. (Add lines 7a, 7b and 7c.)",
                "severity": "warning"}])
            # supplied value wins in the PDF — never enforced/overridden
            self.assertEqual(self._widget(r["out_pdf"]), "999")

    def test_mcp_fill_form_response_carries_both_surfaces(self):
        try:
            from tools.agent_server import _build
        except ImportError:
            self.skipTest("mcp not installed")
        fill_form = _build()._tool_manager.get_tool("fill_form").fn
        self.case["facts"]["total_payments"] = "999"
        with tempfile.TemporaryDirectory() as td:
            r = fill_form(self.FORM, self.case, td)
            self.assertTrue(r["ok"])
            self.assertEqual(r["computation_warnings"][0]["code"],
                             "COMPUTATION_MISMATCH")
        del self.case["facts"]["total_payments"]
        with tempfile.TemporaryDirectory() as td:
            r = fill_form(self.FORM, self.case, td)
            self.assertTrue(r["ok"])
            self.assertEqual(
                {e["key"]: e["value"] for e in r["computed_fields"]},
                {"facts.total_payments": "3000"})


if __name__ == "__main__":
    unittest.main()
