#!/usr/bin/env python3
"""Vision-grounded mapping for tax forms: assign canonical keys by what SHOWS.

IRS/XFA forms carry opaque field names (``f1_1[0]``) with no alt-text, so this
renders each page with a numbered red marker on every fillable widget and asks
the Qwen-VL cluster to map each marker to a canonical fact-key by the PRINTED
label beside it. Writes mapping.json (status ``vision-mapped`` — a draft tier,
review before production), schema.json, and fields.csv for the form.

    MCF_LLM_ENDPOINTS=http://host:8080/v1 python3 tools/vision_map.py --forms IRS-SS-4

Needs the blank PDF on disk (tools/fetch_pdfs.py) and the local Qwen-VL cluster.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import os
import pathlib
import re
import sys

import fitz
import openai

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENDPOINTS = os.environ.get("MCF_LLM_ENDPOINTS", "http://localhost:8080/v1").split(",")
VL_MODEL = os.environ.get("MCF_VL_MODEL", "qwen3.6-27b")
MAX_PAGES = 8
FILLABLE = ("Text", "CheckBox", "RadioButton")

# Canonical roles for transactional tax forms. facts.* is the open escape hatch.
ROLES = ("entity", "responsible_party", "owner", "officer", "shareholder",
         "decedent", "executor", "fiduciary", "estate", "trust", "beneficiary",
         "transferor", "transferee", "property", "preparer", "facts")
_ATTR = r"[a-z0-9_]+"
_KEY_RE = re.compile(rf"^(?:({'|'.join(ROLES)})\.{_ATTR}(?:\.{_ATTR})?|today\(\)|signature)$")


def _key_ok(key: str) -> bool:
    return bool(_KEY_RE.match(key or ""))


SYSTEM = """\
You read a rendered page of a U.S. tax form (IRS or Maine Revenue Services).
Each fillable field has a small red number at its top-left and a red box around
it. For each numbered field, look at the PRINTED LABEL next to that box and
assign the canonical fact-key the field asks for. Judge ONLY by the visible
printed label and position — ignore any internal field name.

Canonical keys (use these exactly; do not invent role names):
- entity.<attr>: the business/applicant entity. attr in {legal_name, trade_name,
  ein, mailing_address, mailing_city, mailing_state, mailing_zip,
  street_address, county, state_of_formation, formation_date, entity_type,
  naics, phone}.
- responsible_party.<attr>: the person responsible / principal officer. attr in
  {name, ssn_itin_ein, title}.
- decedent.<attr>: {name, ssn, date_of_death, domicile_county, domicile_state}.
- executor.<attr> / fiduciary.<attr>: {name, address, ssn_or_ein, phone, title}.
- estate.<attr> / trust.<attr>: {name, ein, date_created}.
- transferor.<attr> (seller/grantor) / transferee.<attr> (buyer/grantee):
  {name, address, ssn_or_ein}.
- property.<attr>: {address, town, county, map_block_lot, book_page, type,
  purchase_price, transfer_date}.
- facts.<snake_case> for any labeled value with no home above (e.g.
  facts.total_tax, facts.number_of_employees, facts.election_effective_date).
- today() for a bare "Date" line by a signature; signature for a signature line.

Rules: map only fields whose printed label clearly indicates a data value. Leave
a number out if it's a checkbox option, an attestation/instruction, or you can't
read a clear label. A box on a "Name" line is a name (never a date); a box on a
"Date of death" line is decedent.date_of_death.

Return ONLY compact JSON: {"map":{"3":"entity.legal_name","7":"today()"}}."""


def _slug(name: str, used: set) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (name or "field").lower()).strip("_") or "field"
    base, i = s, 2
    while s in used:
        s = f"{base}_{i}"; i += 1
    used.add(s)
    return s


def _caption(rect, words, is_cb):
    x0, y0, x1, y1 = rect
    ymid = (y0 + y1) / 2
    row = [w for w in words if w[1] <= ymid <= w[3]]
    side = ([w for w in row if w[0] >= x1 - 2] if is_cb
            else [w for w in row if w[2] <= x0 + 2])
    side.sort(key=lambda w: w[0])
    seg = side[:8] if is_cb else side[-10:]
    return re.sub(r"\s+", " ", " ".join(w[4] for w in seg)).strip()[:120]


def _vl_map(client, png: bytes) -> dict:
    b64 = base64.b64encode(png).decode()
    r = client.chat.completions.create(
        model=VL_MODEL, max_tokens=2500, temperature=0.0,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": SYSTEM},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}]}],
        extra_body={"chat_template_kwargs": {"enable_thinking": False}})
    txt = r.choices[0].message.content or "{}"
    try:
        return json.loads(txt).get("map", {})
    except json.JSONDecodeError:
        i, j = txt.find("{"), txt.rfind("}")
        return json.loads(txt[i:j + 1]).get("map", {}) if i != -1 else {}


def map_form(fid: str, client) -> dict:
    fdir = ROOT / "forms" / fid
    doc = fitz.open(str(fdir / f"{fid}.pdf"))
    rows, used = [], set()           # (field_id, widget_name, caption, type, page, rect)
    for pno in range(min(doc.page_count, MAX_PAGES)):
        words = doc[pno].get_text("words")
        for w in (doc[pno].widgets() or []):
            t = w.field_type_string
            if not any(t.startswith(k) for k in FILLABLE):
                continue
            r = tuple(round(c, 1) for c in w.rect)
            is_cb = "Check" in t or "Radio" in t
            rows.append((_slug(w.field_name, used), w.field_name,
                         _caption(r, words, is_cb),
                         "checkbox" if "Check" in t else "radio" if "Radio" in t else "text",
                         pno, r))
    valid = {r[0] for r in rows}
    mp, dropped, n = {}, [], 1
    for pno in range(min(doc.page_count, MAX_PAGES)):
        page = doc[pno]
        legend = {}
        on_page = [r for r in rows if r[4] == pno]
        if not on_page:
            continue
        for fidx, _wn, _cap, _t, _p, rect in on_page:
            rr = fitz.Rect(rect)
            page.draw_rect(rr, color=(1, 0, 0), width=0.7)
            page.insert_text((max(rr.x0 - 11, 1), max(rr.y0 + 7, 8)), str(n),
                             fontsize=8, color=(1, 0, 0))
            legend[n] = fidx
            n += 1
        png = page.get_pixmap(dpi=150).tobytes("png")
        try:
            answer = _vl_map(client, png)
        except Exception as e:  # noqa: BLE001
            dropped.append(("page", pno, repr(e)[:60])); continue
        for marker, key in answer.items():
            try:
                f = legend.get(int(marker))
            except (ValueError, TypeError):
                f = None
            if f in valid and _key_ok(key):
                mp[f] = key
            else:
                dropped.append((marker, key))
    doc.close()

    with open(fdir / "fields.csv", "w", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["field_id", "label", "caption", "type", "page", "rect"])
        for f, wn, cap, t, pno, rect in rows:
            wr.writerow([f, wn, cap, t, pno, ",".join(str(c) for c in rect)])
    schema = {"form_id": fid, "fields": [
        {"field_id": f, "label": wn, "caption": cap, "type": t, "page": pno, "rect": list(rect)}
        for f, wn, cap, t, pno, rect in rows]}
    (fdir / "schema.json").write_text(json.dumps(schema, indent=2) + "\n")
    (fdir / "mapping.json").write_text(json.dumps(
        {"form_id": fid, "status": "vision-mapped", "model": VL_MODEL,
         "note": "Vision-grounded draft mapping (tools/vision_map.py); review before production.",
         "map": mp}, indent=2) + "\n")
    return {"form_id": fid, "widgets": len(rows), "mapped": len(mp), "dropped": len(dropped)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Vision-map tax forms from the blank PDF")
    ap.add_argument("--forms", required=True, help="comma list")
    args = ap.parse_args()
    client = openai.OpenAI(base_url=ENDPOINTS[0], api_key="none", timeout=300)
    for fid in [f.strip() for f in args.forms.split(",") if f.strip()]:
        if not (ROOT / "forms" / fid / f"{fid}.pdf").exists():
            print(f"  {fid}: no local PDF (run tools/fetch_pdfs.py --forms {fid})"); continue
        r = map_form(fid, client)
        print(f"  {fid}: {r['widgets']} widgets, {r['mapped']} mapped, {r['dropped']} dropped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
