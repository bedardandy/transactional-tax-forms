"""Fill smoke over mapped forms that have a local blank PDF.

PDF-dependent: blanks are fetched on demand and not shipped, so each case skips
when its blank is absent — runs in full locally, no-ops in CI. Catches engine /
mapping crashes the offline tests can't see.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.fill_via_mapping import fill_via_mapping  # noqa: E402

FORMS = ROOT / "forms"


def _mapped_forms_with_blank():
    out = []
    for d in sorted(FORMS.iterdir()):
        if not d.is_dir():
            continue
        if (d / "mapping.json").exists() and (d / f"{d.name}.pdf").exists():
            out.append(d.name)
    return out


class FillSmoke(unittest.TestCase):
    def test_mapped_forms_fill_without_crash(self):
        forms = _mapped_forms_with_blank()
        if not forms:
            self.skipTest("no local blank PDFs (CI / unfetched)")
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            for fid in forms:
                with self.subTest(form=fid):
                    ex = FORMS / fid / "examples" / "sample_case.json"
                    case = json.loads(ex.read_text()) if ex.exists() else {}
                    r = fill_via_mapping(fid, case, out / fid)
                    self.assertTrue(r.get("ok") or r.get("skipped"),
                                    f"{fid}: {r.get('error')}")


if __name__ == "__main__":
    unittest.main()
