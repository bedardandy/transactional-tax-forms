#!/usr/bin/env python3
"""Regenerate catalog/forms_index.json + catalog/by_domain.json from form data.

Reads each form's form.yaml plus catalog/source_urls.json (domain grouping) and
catalog/pdf_manifest.json (page counts), so the catalogs stay derived from the
per-form folders rather than hand-maintained. Run after adding or remapping a form.
"""
import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent


def load_yaml(p):
    return yaml.safe_load(pathlib.Path(p).read_text()) or {}


# Sibling libraries an agent working the full transaction will also need:
# this repo covers only the tax side of each domain.
COMPANION_REPOS = {
    "corporations": {
        "repo": "github.com/bedardandy/maine-corporation-forms",
        "for": "the Maine SoS entity filings (formation, amendment, annual report) the tax forms ride along with",
    },
    "real-estate": {
        "repo": "github.com/bedardandy/maine-court-forms",
        "for": "deed and court forms a Maine real-estate closing may also need",
    },
    "probate": {
        "repo": "github.com/bedardandy/maine-probate-forms",
        "for": "the Maine probate court filings (the estate's court side)",
    },
}


def main():
    src = json.loads((ROOT / "catalog" / "source_urls.json").read_text())
    man = json.loads((ROOT / "catalog" / "pdf_manifest.json").read_text())["forms"]
    dom = {i: d for d, ids in src["domains"].items() for i in ids}

    forms = []
    for fid in sorted(src["forms"]):
        y = load_yaml(ROOT / "forms" / fid / "form.yaml")
        forms.append({
            "form_id": fid, "title": y.get("title", fid), "agency": y.get("agency", ""),
            "domain": y.get("domain", dom.get(fid, "")),
            "num_pages": man.get(fid, {}).get("num_pages"),
            "status": y.get("status", "unmapped"),
        })
    (ROOT / "catalog" / "forms_index.json").write_text(
        json.dumps({"count": len(forms), "forms": forms}, indent=2) + "\n")

    by_domain = {}
    for d, ids in src["domains"].items():
        by_domain[d] = {
            "form_ids": sorted(ids),
            "forms": [{"form_id": f, "title": load_yaml(ROOT / "forms" / f / "form.yaml").get("title", f)}
                      for f in sorted(ids)],
        }
        if d in COMPANION_REPOS:
            by_domain[d]["companion_repo"] = COMPANION_REPOS[d]
    (ROOT / "catalog" / "by_domain.json").write_text(
        json.dumps({"by_domain": by_domain, "cross_listed": src.get("cross_listed", {})}, indent=2) + "\n")

    print(f"forms_index: {len(forms)} forms | "
          + " / ".join(f"{s} {n}" for s, n in
                        __import__("collections").Counter(f["status"] for f in forms).most_common()))


if __name__ == "__main__":
    main()
