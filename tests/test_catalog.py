"""Catalog integrity: indices, manifest, and form folders agree."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMS = ROOT / "forms"


def _src():
    return json.loads((ROOT / "catalog" / "source_urls.json").read_text())


def _form_dirs():
    return sorted(d.name for d in FORMS.iterdir() if d.is_dir())


def test_form_folders_match_source_urls():
    assert set(_form_dirs()) == set(_src()["forms"])


def test_manifest_covers_source_urls():
    man = json.loads((ROOT / "catalog" / "pdf_manifest.json").read_text())["forms"]
    assert set(man) == set(_src()["forms"])
    for fid, e in man.items():
        sha = e.get("sha256", "")
        assert len(sha) == 64 and all(c in "0123456789abcdef" for c in sha), fid
        assert isinstance(e.get("bytes"), int) and e["bytes"] > 0, fid
        assert str(e.get("url", "")).startswith("http"), fid


def test_by_domain_partitions_every_form():
    src = _src()
    listed = {f for ids in src["domains"].values() for f in ids}
    assert listed == set(src["forms"])
    by_domain = json.loads((ROOT / "catalog" / "by_domain.json").read_text())["by_domain"]
    assert {f for g in by_domain.values() for f in g["form_ids"]} == set(src["forms"])


def test_forms_index_covers_every_folder():
    idx = json.loads((ROOT / "catalog" / "forms_index.json").read_text())
    assert {f["form_id"] for f in idx["forms"]} == set(_form_dirs())


def test_every_form_has_form_yaml_and_widgets():
    for fid in _form_dirs():
        assert (FORMS / fid / "form.yaml").exists(), f"{fid}: no form.yaml"
        # mapped forms carry a mapping; all forms carry a widget inventory.
        assert (FORMS / fid / "widgets.json").exists() or (FORMS / fid / "mapping.json").exists(), fid


def test_no_pdfs_committed():
    try:
        tracked = subprocess.run(
            ["git", "ls-files", "*.pdf"], cwd=ROOT,
            capture_output=True, text=True, check=True).stdout.split()
    except (FileNotFoundError, subprocess.CalledProcessError):
        tracked = []
    assert tracked == [], f"blank PDFs must not be committed: {tracked}"
