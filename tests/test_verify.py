"""Drift detection: on-disk and upstream blanks must match the manifest hash.

Offline except the last class's PDF-dependent check — a synthetic manifest
and a stubbed downloader keep the rest network-free for CI.
"""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine import verify  # noqa: E402


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _manifest(blank: bytes):
    return {"forms": {"TEST_X": {
        "sha256": _sha(blank), "bytes": len(blank),
        "url": "https://example.test/TEST_X",
    }}}


class VerifyBlank(unittest.TestCase):
    def _write(self, root, blank):
        d = pathlib.Path(root) / "TEST_X"
        d.mkdir()
        (d / "TEST_X.pdf").write_bytes(blank)

    def test_match(self):
        blank = b"%PDF-1.7 the enriched revision\n"
        with tempfile.TemporaryDirectory() as td:
            self._write(td, blank)
            ok, detail = verify.verify_blank("TEST_X", forms_root=td, manifest=_manifest(blank))
            self.assertTrue(ok, detail)

    def test_detects_swap(self):
        blank = b"%PDF-1.7 the enriched revision\n"
        with tempfile.TemporaryDirectory() as td:
            self._write(td, b"%PDF-1.7 a DIFFERENT revision\n")
            ok, detail = verify.verify_blank("TEST_X", forms_root=td, manifest=_manifest(blank))
            self.assertFalse(ok)
            self.assertTrue("mismatch" in detail.lower() or "size" in detail.lower())

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as td:
            ok, detail = verify.verify_blank("TEST_X", forms_root=td, manifest=_manifest(b"x"))
            self.assertFalse(ok)
            self.assertIn("not present", detail)

    def test_strict_raises(self):
        with tempfile.TemporaryDirectory() as td:
            self._write(td, b"swapped")
            with self.assertRaises(verify.BlankRevisionError):
                verify.guard_blank("TEST_X", forms_root=td, mode="strict",
                                   manifest=_manifest(b"original"))

    def test_warn_does_not_raise(self):
        with tempfile.TemporaryDirectory() as td:
            self._write(td, b"swapped")
            with self.assertWarns(verify.BlankRevisionWarning):
                result = verify.guard_blank("TEST_X", forms_root=td, mode="warn",
                                            manifest=_manifest(b"original"))
            self.assertFalse(result)

    def test_off_skips(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertTrue(verify.guard_blank("TEST_X", forms_root=td, mode="off",
                                               manifest=_manifest(b"original")))


class CheckUpstream(unittest.TestCase):
    def test_classifies(self):
        import tools.check_upstream as cu
        upstream = b"%PDF-1.7 what the portal serves today\n"

        def fake_download(url, timeout, retries):
            if "gone" in url:
                raise OSError("404 Not Found")
            return upstream

        with mock.patch.object(cu, "_download", fake_download):
            self.assertEqual(cu.check_one(
                "A", {"sha256": _sha(upstream), "bytes": len(upstream), "url": "u"},
                1, 1)["status"], "ok")
            self.assertEqual(cu.check_one(
                "B", {"sha256": _sha(b"older"), "bytes": 5, "url": "u"},
                1, 1)["status"], "CHANGED")
            self.assertEqual(cu.check_one(
                "C", {"sha256": _sha(b"x"), "bytes": 1, "url": "gone"},
                1, 1)["status"], "GONE")


class RealManifest(unittest.TestCase):
    def test_every_entry_anchored(self):
        man = verify.load_manifest()
        self.assertTrue(man.get("forms"), "manifest has no forms")
        for fid, e in man["forms"].items():
            self.assertTrue(e.get("sha256") and len(e["sha256"]) == 64, fid)
            self.assertTrue(e.get("bytes"), fid)
            self.assertTrue(e.get("url", "").startswith("http"), fid)


class MappingBuiltAgainstStamps(unittest.TestCase):
    """Every fillable (non-pending) mapping is pinned to the manifest
    revision it was re-verified against (tools/verify_mapping_fields.py).
    Pending tiers — "remap-pending", recipe pointers with an empty map —
    are exempt: the engine refuses them at fill time anyway."""

    def test_every_fillable_mapping_is_stamped_with_manifest_sha(self):
        # Include the draft tier: the stamping invariant applies to any map
        # the engine can fill (drafts fill under allow_draft), so they must be
        # pinned too. Reviewed-only FILLABLE_STATUSES would skip today's 14
        # vision-mapped maps entirely.
        from engine.fill_via_mapping import DRAFT_STATUSES, FILLABLE_STATUSES
        fillable = FILLABLE_STATUSES | DRAFT_STATUSES
        manifest = json.loads(
            (ROOT / "catalog" / "pdf_manifest.json").read_text())["forms"]
        checked = 0
        for mp in sorted((ROOT / "forms").glob("*/mapping.json")):
            fid = mp.parent.name
            mapping = json.loads(mp.read_text())
            if (mapping.get("status") not in fillable
                    or not mapping.get("map")):
                continue  # pending/pointer: unstamped AND unfillable
            checked += 1
            with self.subTest(form=fid):
                self.assertEqual(
                    mapping.get("built_against_sha256"),
                    manifest[fid]["sha256"],
                    f"{fid}: fillable mapping must carry the manifest's "
                    "sha256 (re-verify + stamp with "
                    "tools/verify_mapping_fields.py, or mark remap-pending)")
        self.assertEqual(checked, 14)  # every mapped form today

    def test_verify_tool_passes_on_the_pinned_blanks(self):
        """PDF-dependent: skips when blanks are unfetched (CI)."""
        from tools.verify_mapping_fields import FORMS, MANIFEST, verify_form
        if not any(FORMS.glob("*/*.pdf")):
            self.skipTest("no local blank PDFs (CI / unfetched)")
        manifest = json.loads(MANIFEST.read_text())
        for d in sorted(FORMS.iterdir()):
            if not ((d / "mapping.json").exists()
                    and (d / f"{d.name}.pdf").exists()):
                continue
            with self.subTest(form=d.name):
                r = verify_form(d.name, manifest)
                self.assertTrue(r["ok"], r)


if __name__ == "__main__":
    unittest.main()
