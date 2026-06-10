# Transactional Tax Forms — agent guide (CLAUDE.md; same as AGENTS.md)

A form-by-form automation library for the tax forms filed alongside business
formations, real-estate closings, and estates — Maine Revenue Services forms
(`MRS-*`, `ME-*`) and federal IRS forms (`IRS-*`). You can drive it to **fill a
tax form from a structured case-data object**.

When the user says *"use this project to prepare \<tax form / transaction\>"*:

1. **Route by domain:** read `catalog/by_domain.json` (corporations /
   real-estate / probate) or `catalog/forms_index.json` to pick the form.
2. **Understand:** read `forms/<ID>/form.yaml` (title, agency, domain, status).
   - `status: mapped` — deterministic `mapping.json` (human-verified or
     machine fill-verified — the form's `mapping.json.note` says which);
     fillable now.
   - `status: opus-adjudicated` — Qwen-VL draft reviewed/corrected by Opus
     (corrections under `mapping.json.adjudication`); fillable, verify placement.
   - `status: remap-pending` — the upstream blank drifted; mapping is stale
     (none currently; the engine also self-checks via `built_against_sha256`).
   - `status: unmapped` — only `widgets.json` (raw AcroForm inventory) exists;
     not yet fillable.
3. **Fetch the blank:** `python3 tools/fetch_pdfs.py --forms <ID>` (verified
   against `catalog/pdf_manifest.json`).
4. **Build the case data** (canonical fact object — see
   `docs/integrations/README.md` and the form's `examples/sample_case.json`)
   and fill:
   `python3 -m engine.fill_via_mapping --form <ID> --case case.json --out out/`.
5. **Verify & report:** open the output, surface the form's `status`, any
   unresolved fields, and that it must be verified before filing.

**Or use the MCP server** (`python3 tools/agent_server.py`): exposes
`find_forms` / `get_form` / `fill_form` — register with
`claude mcp add transactional-tax-forms -- python3 tools/agent_server.py`.

## Companion repos

This repo covers only the **tax** side of each transaction. An agent working
the full matter will also need the sibling libraries (same layout, same fill
engine; `catalog/by_domain.json` carries the same pointers per domain):

- Real-estate closings → deed/court forms:
  [maine-court-forms](https://github.com/bedardandy/maine-court-forms)
- Corporate transactions → Maine SoS entity filings:
  [maine-corporation-forms](https://github.com/bedardandy/maine-corporation-forms)
- Probate/estates → probate court filings:
  [maine-probate-forms](https://github.com/bedardandy/maine-probate-forms)

## Rules
- **Not tax or legal advice.** Filled output is a draft; say so, and say it must
  be verified against the official form before filing.
- **Respect the manifest guard.** The engine warns if the on-disk blank is not
  the revision the mapping was built against (`TTF_VERIFY_BLANK`; `MCF_VERIFY_BLANK` works as a fallback). Don't suppress
  it without re-verifying the mapping.
- **Don't redistribute the blanks.** Maine forms are public records; IRS forms
  are public domain — but this repo ships metadata only, fetched on demand.
- **Adding / remapping a form:** capture its widgets with
  `tools/build_manifest.py --forms <ID>`, write `mapping.json` + `schema.json`,
  set `form.yaml` `status: mapped`, then `tools/gen_catalog.py`.
- Licensed Apache-2.0 (`LICENSE`, `NOTICE`).
