"""tools.opus_adjudicate._opus — the claude-CLI envelope guard.

The CLI can report a failure inside a returncode-0 JSON envelope
(``is_error``/``subtype``). Without an is_error check the adjudicator would
consume the error payload as if it were a result, silently skipping the
correction pass and leaving the draft mapping fillable. Mirrors the sibling
corp repo's claude_cli.py guard.
"""
import json
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import opus_adjudicate  # noqa: E402


def _fake_run(stdout="", returncode=0, stderr=""):
    def run(*args, **kwargs):
        return types.SimpleNamespace(
            stdout=stdout, stderr=stderr, returncode=returncode)
    return run


class OpusEnvelopeGuard(unittest.TestCase):
    def setUp(self):
        self._orig = opus_adjudicate.subprocess.run

    def tearDown(self):
        opus_adjudicate.subprocess.run = self._orig

    def test_is_error_envelope_raises(self):
        opus_adjudicate.subprocess.run = _fake_run(
            stdout=json.dumps({"is_error": True, "subtype": "error_max_turns",
                               "result": "hit the limit"}))
        with self.assertRaises(RuntimeError) as ctx:
            opus_adjudicate._opus("sys", "user")
        self.assertIn("error_max_turns", str(ctx.exception))

    def test_nonzero_rc_raises(self):
        opus_adjudicate.subprocess.run = _fake_run(
            stdout="", returncode=1, stderr="boom")
        with self.assertRaises(RuntimeError):
            opus_adjudicate._opus("sys", "user")

    def test_non_json_output_raises(self):
        opus_adjudicate.subprocess.run = _fake_run(stdout="not json at all")
        with self.assertRaises(RuntimeError) as ctx:
            opus_adjudicate._opus("sys", "user")
        self.assertIn("non-JSON", str(ctx.exception))

    def test_missing_result_field_raises(self):
        opus_adjudicate.subprocess.run = _fake_run(
            stdout=json.dumps({"is_error": False, "cost_usd": 0.01}))
        with self.assertRaises(RuntimeError):
            opus_adjudicate._opus("sys", "user")

    def test_ok_envelope_returns_result(self):
        opus_adjudicate.subprocess.run = _fake_run(
            stdout=json.dumps({"is_error": False, "result": "the answer"}))
        self.assertEqual(opus_adjudicate._opus("sys", "user"), "the answer")


if __name__ == "__main__":
    unittest.main()
