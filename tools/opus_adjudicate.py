#!/usr/bin/env python3
"""Opus adjudication pass over vision-mapped (draft) mappings.

The Qwen-VL cluster produces draft mappings fast but errs on ambiguous fields.
This sends each field's printed caption + the draft canonical key to Opus (via
the local ``claude`` CLI, session-auth — the env ANTHROPIC_API_KEY is an OAuth
token rejected by the Messages API, so it is stripped) and asks Opus to correct
keys that don't match the caption. Corrections are applied to mapping.json and
the status is promoted to ``opus-adjudicated``.

    python3 tools/opus_adjudicate.py --forms ME-RETTD,IRS-SS-4

Text-only (caption-grounded); no images, no cluster.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

VOCAB = """\
entity.{legal_name,trade_name,ein,mailing_address,mailing_city,mailing_state,
  mailing_zip,street_address,county,state_of_formation,formation_date,
  entity_type,naics,phone}
responsible_party.{name,ssn_itin_ein,title}
decedent.{name,ssn,date_of_death,domicile_county,domicile_state,address}
executor.{name,address,ssn_or_ein,phone,title}  fiduciary.{name,address,ssn_or_ein,phone,title}
estate.{name,ein,date_created}  trust.{name,ein,date_created}
transferor.{name,address,ssn_or_ein}  transferee.{name,address,ssn_or_ein,mailing_address,mailing_city,mailing_state,mailing_zip}
property.{address,town,county,map_block_lot,book_page,type,purchase_price,transfer_date}
facts.<snake_case>   today()   signature"""

SYSTEM = (
    "You audit a DRAFT field-mapping for a U.S. tax form. A vision model assigned "
    "each fillable field a canonical fact-key. Catch keys that do not match the "
    "field's printed caption and correct them, using ONLY this controlled "
    "vocabulary (facts.<snake_case> for any labeled value with no clean home):\n"
    + VOCAB +
    "\n\nReturn ONLY compact JSON: {\"corrections\":{\"<field_id>\":\"<correct_key>\"},"
    "\"remove\":[\"<field_id>\"],\"notes\":\"<one line>\"}. Include a field_id in "
    "\"corrections\" ONLY if you are changing its key; in \"remove\" if it should "
    "not be mapped at all (e.g. it's an instruction or a checkbox option). Judge "
    "by the caption: a 'City/Town' caption is never a last_name; a 'Date of death' "
    "caption is decedent.date_of_death; a name line is a name. If every key is "
    "right, return empty corrections.")


def _caption_from_schema(fdir):
    """field_id -> printed caption (vision_map.py wrote a caption column)."""
    caps = {}
    fcsv = fdir / "fields.csv"
    if fcsv.exists():
        for row in csv.DictReader(open(fcsv)):
            caps[row["field_id"]] = (row.get("caption") or row.get("label") or "").strip()
    return caps


def _opus(system: str, user: str, timeout: float = 1500.0) -> str:
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    prompt = system + "\n\n---\n\n" + user
    p = subprocess.run(
        ["claude", "-p", "--output-format", "json"],
        input=prompt, capture_output=True, text=True, env=env, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {p.stderr[:200]}")
    return json.loads(p.stdout)["result"]


def _parse_json(txt: str) -> dict:
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        i, j = txt.find("{"), txt.rfind("}")
        return json.loads(txt[i:j + 1]) if i != -1 else {}


def adjudicate(fid: str) -> dict:
    fdir = ROOT / "forms" / fid
    mapping = json.loads((fdir / "mapping.json").read_text())
    mp = mapping["map"]
    caps = _caption_from_schema(fdir)
    title = ""
    fy = fdir / "form.yaml"
    if fy.exists():
        for line in fy.read_text().splitlines():
            if line.startswith("title:"):
                title = line.split("title:", 1)[1].strip().strip('"')
    lines = [f"{f} | caption={caps.get(f,'')!r} | draft_key={k}" for f, k in mp.items()]
    user = f"Form: {fid} — {title}\n\nFields (field_id | caption | draft_key):\n" + "\n".join(lines)
    out = _parse_json(_opus(SYSTEM, user))
    corr = out.get("corrections", {}) or {}
    rem = out.get("remove", []) or []
    applied = {f: corr[f] for f in corr if f in mp and corr[f] != mp[f]}
    removed = [f for f in rem if f in mp]
    for f, k in applied.items():
        mp[f] = k
    for f in removed:
        mp.pop(f, None)
    mapping["map"] = mp
    mapping["status"] = "opus-adjudicated"
    mapping["adjudication"] = {"model": "claude-opus (cli)", "corrected": applied,
                               "removed": removed, "notes": out.get("notes", "")}
    (fdir / "mapping.json").write_text(json.dumps(mapping, indent=2) + "\n")
    return {"form_id": fid, "fields": len(mp), "corrected": len(applied),
            "removed": len(removed), "notes": out.get("notes", "")[:90]}


def main() -> int:
    ap = argparse.ArgumentParser(description="Opus adjudication of vision-mapped drafts")
    ap.add_argument("--forms", required=True, help="comma list")
    args = ap.parse_args()
    for fid in [f.strip() for f in args.forms.split(",") if f.strip()]:
        try:
            r = adjudicate(fid)
            print(f"  {fid}: {r['fields']} fields, {r['corrected']} corrected, "
                  f"{r['removed']} removed | {r['notes']}")
        except Exception as e:  # noqa: BLE001
            print(f"  {fid}: ADJUDICATION FAILED: {repr(e)[:120]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
