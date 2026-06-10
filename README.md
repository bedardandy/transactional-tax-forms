# Transactional Tax Forms — Open Automation Library

Fill the tax forms that ride along with a business formation, a real-estate
closing, or an estate — Maine Revenue Services forms and federal IRS forms,
one self-contained folder per form, filled deterministically from structured
case data.

This is a sibling of [`maine-corporation-forms`](https://github.com/bedardandy/maine-corporation-forms),
[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms), and
[`maine-probate-forms`](https://github.com/bedardandy/maine-probate-forms): same
form-by-form layout, same fetch-on-demand + drift-detection model, same
deterministic fill engine. The blank PDFs are **fetched on demand from the
official source and never redistributed** (see [Getting the blanks](#getting-the-blanks)).

> ⚠️ **Not legal or tax advice — for professional use only.** This is software
> that produces *draft* forms. It is meant to be used solely as one component of
> a broader workflow that is implemented, supervised, and reviewed by a licensed
> attorney or qualified tax professional — not as a do-it-yourself substitute for
> professional advice. Output is a draft that may be wrong; verify every form
> against the current official source and applicable law before filing. See
> [**DISCLAIMER**](DISCLAIMER.md).

## Scope — organized by transaction

| Domain | Forms |
|---|---|
| **Corporations** | IRS SS-4 (EIN), IRS 2553 (S-corp election), IRS 8832 (entity classification), MRS 1120ME (corporate income), MRS 941ME / 900ME (withholding), MRS W-4ME |
| **Real estate** | ME RETTD (real estate transfer tax declaration) |
| **Probate / estates** | IRS 706 (federal estate tax), IRS 1041 (estates & trusts income), IRS 56 (fiduciary notice), MRS 706ME (Maine estate tax), MRS 700-SOV (statement of value), MRS 1041ME (fiduciary income) |

SS-4 and 706 are cross-listed (an estate also needs an EIN). See
`catalog/by_domain.json`.

## Status

14 forms. The seven Maine Revenue forms were mapped in `maine-court-forms` and
lifted here; the rest are fetched and inventoried, with mappings in progress.

- **Mapped & verified (5):** MRS 706ME, 1120ME, 941ME, 900ME, W-4ME —
  widget-survival confirmed against the current maine.gov blanks.
- **Re-map pending (2):** MRS 1041ME (current maine.gov blank drifted from the
  mapped revision — 44 of 117 widgets renamed) and MRS 700-SOV (was recipe-tier
  in `maine-court-forms` with an empty field map; needs a direct map).
- **Opus-adjudicated (7):** IRS SS-4 (44 fields), 2553 (23), 8832 (53), 706
  (146), 1041 (79), 56 (33), ME RETTD (74). Drafted from the rendered form by the
  Qwen-VL cluster (`tools/vision_map.py`), then reviewed field-by-field against
  each printed caption by Opus (`tools/opus_adjudicate.py`), which corrected 86
  keys and removed 15 non-data widgets — most notably realigning IRS-1041's
  shifted income/deduction lines (68 fixes) and IRS-SS-4's over-split
  city/state/zip block (9). Each form records its corrections under
  `mapping.json.adjudication`. The big returns map identity/party fields; some
  numbered line items remain `facts.*`. ME-RETTD + IRS-SS-4 fill end-to-end.

> **Two canonical models, for now.** The five inherited Maine Revenue forms use
> the court library's `parties.<role>` model; the vision-mapped forms above use
> the tax-native roles (`entity`, `responsible_party`, `decedent`, `executor`,
> `fiduciary`, `transferor`/`transferee`, `property`). Unifying the two is a
> roadmap item; until then, read each form's `mapping.json` for its keys.

## Getting the blanks

Blank forms are **not redistributed** here. Maine forms are public records of
Maine Revenue Services; federal forms are public-domain U.S. Government works.
Fetch on demand; each download is verified byte-for-byte against
`catalog/pdf_manifest.json`:

```bash
python3 tools/fetch_pdfs.py                    # all forms
python3 tools/fetch_pdfs.py --forms MRS-706ME  # a subset
```

## Staying current — detecting a revised form

Every mapping is built against one specific revision of the blank, pinned by
SHA-256 in the manifest. Agencies re-issue forms yearly; when the bytes change,
field layouts can move and a fill built on the old mapping lands values in the
wrong place. Two guards:

```bash
python3 tools/check_upstream.py            # re-probe official URLs; flag CHANGED / GONE
```

`check_upstream` re-downloads each blank, hashes it, and reports drift; it is
read-only and exits non-zero on any change, so it runs as a weekly early-warning
(`.github/workflows/drift.yml`). At **fill time** the engine checks the on-disk
blank against the manifest — `TTF_VERIFY_BLANK=warn` (default), `strict`, or
`off` (`MCF_VERIFY_BLANK` is honored as a fallback) — so a re-issued blank
can't be filled unnoticed.

## Quickstart — fill a form

```bash
pip install -r requirements.txt                # PyMuPDF
python3 tools/fetch_pdfs.py --forms MRS-706ME  # download the blank, verified
python3 -m engine.fill_via_mapping --form MRS-706ME --case forms/MRS-706ME/examples/sample_case.json --out out/706me.pdf
```

The engine resolves each form's `mapping.json` against a canonical fact object
and writes the filled AcroForm. Unmapped forms (status `unmapped`) carry a
`widgets.json` inventory but no `mapping.json` yet.

## Layout

```
forms/<FORM_ID>/
  form.yaml          metadata: title, agency, domain, page/widget counts, status
  widgets.json       raw AcroForm widget inventory (name, type, page, rect) — mapping input
  mapping.json       canonical fact-key -> widget (mapped forms)
  schema.json        JSON Schema for the fill data (mapped forms)
  fields.csv         reviewable field inventory (mapped forms)
  SKILL.md / README  per-form guide (mapped forms)
catalog/
  source_urls.json   form_id -> official URL + domain grouping
  pdf_manifest.json  per-form sha256 + bytes + pages for fetching/verifying blanks
  forms_index.json   master list (generated)
  by_domain.json     forms grouped by transaction domain (generated)
engine/              deterministic AcroForm fill engine (PyMuPDF)
  fill_via_mapping.py  form_filler.py  field_split.py  text_fit.py  verify.py
tools/
  fetch_pdfs.py       download verified blanks
  build_manifest.py   fetch + hash + dump widget inventory
  check_upstream.py   re-probe official URLs; flag revised forms
  vision_map.py       Qwen-VL draft mapping from the rendered form
  opus_adjudicate.py  Opus caption-grounded review of the drafts
  infer_labels.py     heuristic widget-caption inventory
  gen_catalog.py      regenerate the catalogs
  agent_server.py     MCP server (find_forms / get_form / fill_form)
.mcp.json             MCP registration; AGENTS.md / CLAUDE.md — agent guide
```

## License

Apache-2.0. See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
