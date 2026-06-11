"""Yellow-light layers: manual radio groups + paradox constraints.

Offline parts validate the shipped artifacts (mapping.json "manual" blocks,
constraints.json) against each form's schema/mapping; the fill part is
PDF-dependent and skips when the blank is unfetched (CI), like the fill
smoke."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from maine_forms_engine.constraints import evaluate, load_constraints  # noqa: E402

FORMS = ROOT / "forms"

# The known radio groups this repo maps as "fill": "manual"
# (form -> [(schema field_id, printed option labels)]).
EXPECTED_MANUAL = {
    "MRS-1041ME": [
        ("do_you_want_to_allow_someone_to_discuss_return_with_mrs",
         ["Yes", "No"]),
    ],
    "MRS-700SOV": [
        ("residency_status", ["Resident", "Nonresident"]),
    ],
    "MRS-706ME": [
        ("decedents_residency", ["Resident", "Nonresident"]),
        ("marital_status_of_decedent",
         ["Married with surviving spouse", "Widow/Widower",
          "Single / Divorced"]),
    ],
    "MRS-W4ME": [
        ("filing_status_single",
         ["Single or Head of Household", "Married",
          "Married, but withholding at higher single rate"]),
    ],
}


def _forms_with(name):
    return sorted(d.name for d in FORMS.iterdir()
                  if d.is_dir() and (d / name).exists())


class ManualRadioMappings(unittest.TestCase):
    def test_known_radio_groups_are_declared_manual(self):
        for fid, groups in EXPECTED_MANUAL.items():
            mapping = json.loads((FORMS / fid / "mapping.json").read_text())
            for group_fid, options in groups:
                with self.subTest(form=fid, field=group_fid):
                    spec = (mapping.get("manual") or {}).get(group_fid)
                    self.assertIsNotNone(
                        spec, f"{fid}: {group_fid} not in manual")
                    self.assertEqual(spec["fill"], "manual")
                    self.assertEqual(spec["options"], options)
                    self.assertTrue(spec.get("key"))
                    # never also routed through the writable map
                    self.assertNotIn(group_fid, mapping.get("map") or {})

    def test_manual_blocks_are_well_formed_radio_fields(self):
        for fid in _forms_with("mapping.json"):
            mapping = json.loads((FORMS / fid / "mapping.json").read_text())
            manual = mapping.get("manual") or {}
            if not manual:
                continue
            schema = json.loads((FORMS / fid / "schema.json").read_text())
            types = {f["field_id"]: f.get("type")
                     for f in schema.get("fields", [])}
            for group_fid, spec in manual.items():
                with self.subTest(form=fid, field=group_fid):
                    self.assertEqual(spec.get("fill"), "manual")
                    self.assertGreaterEqual(len(spec.get("options") or []), 2)
                    self.assertEqual(types.get(group_fid), "radio")

    def test_sample_case_resolves_a_suggestion(self):
        from engine.fill_via_mapping import resolve_mapping
        for fid, groups in EXPECTED_MANUAL.items():
            case = json.loads(
                (FORMS / fid / "examples" / "sample_case.json").read_text())
            res = resolve_mapping(fid, case)
            entries = {e["field_id"]: e for e in res.get("manual_fields", [])}
            for group_fid, _ in groups:
                with self.subTest(form=fid, field=group_fid):
                    self.assertIn(group_fid, entries, fid)
                    e = entries[group_fid]
                    self.assertEqual(e["action"],
                                     "manual selection required")
                    self.assertIn(e["suggested"], e["options"], fid)


class ConstraintsArtifacts(unittest.TestCase):
    def test_shipped_constraints_reference_mapped_keys(self):
        found = _forms_with("constraints.json")
        self.assertIn("MRS-1041ME", found)
        self.assertIn("IRS-1041", found)
        for fid in found:
            cons = load_constraints(FORMS / fid)
            mapping = json.loads((FORMS / fid / "mapping.json").read_text())
            mapped = set((mapping.get("map") or {}).values())
            for group in cons.get("mutually_exclusive", []):
                keys = group["keys"] if isinstance(group, dict) else group
                with self.subTest(form=fid, keys=keys):
                    self.assertGreaterEqual(len(keys), 2)
                    for k in keys:
                        self.assertIn(k, mapped, f"{fid}: {k} not mapped")

    def test_paradox_fires_and_single_choice_is_clean(self):
        cons = load_constraints(FORMS / "MRS-1041ME")
        both = {"facts": {"resident_estate_or_trust": "yes",
                          "nonresident_estate_or_trust": "yes"}}
        w = evaluate(cons, both)
        self.assertEqual([x["code"] for x in w], ["MUTUALLY_EXCLUSIVE"])
        self.assertEqual(w[0]["severity"], "warning")
        one = {"facts": {"resident_estate_or_trust": "yes",
                         "entity_type_simple_trust": "x"}}
        self.assertEqual(evaluate(cons, one), [])


class FillSurfacesYellowLights(unittest.TestCase):
    """PDF-dependent: skips when the blank is unfetched (CI)."""

    def test_fill_reports_untouched_radio_with_suggestion(self):
        import fitz
        from engine.fill_via_mapping import fill_via_mapping
        for fid, groups in EXPECTED_MANUAL.items():
            if not (FORMS / fid / f"{fid}.pdf").exists():
                self.skipTest(f"no local blank for {fid} (CI / unfetched)")
            case = json.loads(
                (FORMS / fid / "examples" / "sample_case.json").read_text())
            with tempfile.TemporaryDirectory() as td:
                r = fill_via_mapping(fid, case, Path(td))
                self.assertTrue(r["ok"], r)
                entries = {e["field_id"]: e for e in r["radio_groups"]}
                for group_fid, _ in groups:
                    with self.subTest(form=fid, field=group_fid):
                        self.assertIn(group_fid, entries)
                        self.assertIn(entries[group_fid]["suggested"],
                                      entries[group_fid]["options"])
                        # post-fill expectation: the radio group is
                        # untouched — every button still off, none
                        # deleted, NOT an error
                        self.assertNotIn(group_fid, r["missing_widgets"])
                doc = fitz.open(r["out_pdf"])
                radios = [w for page in doc for w in page.widgets() or []
                          if w.field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON]
                self.assertTrue(radios, fid)
                for w in radios:
                    self.assertIn(w.field_value, (None, "", "Off"))
                doc.close()


if __name__ == "__main__":
    unittest.main()
