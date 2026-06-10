# IRS-56 — Notice Concerning Fiduciary Relationship

**Agency:** IRS  |  **Domain:** probate  |  **Status:** `opus-adjudicated`
**Pages:** 2  |  **Fillable widgets:** 64  |  **Mapped:** 33 fields / 24 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed field-by-field against each printed caption by Opus (corrections under `mapping.json.adjudication`). Fillable, but verify placement on the rendered output before relying on it.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms IRS-56   # verified official blank
python3 -m engine.fill_via_mapping --form IRS-56 \
    --case forms/IRS-56/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `decedent.address` | decedent — address |
| `decedent.date_of_death` | 1b, or 1d is checked, enter the date of death: |
| `decedent.domicile_county` | decedent — domicile county |
| `decedent.name` | decedent — name |
| `decedent.ssn` | decedent — ssn |
| `facts.authority_description` | g Other. Describe: |
| `facts.authority_period` | and list the specific years or periods within your authority: (+1 more field) |
| `facts.court_address` | facts — court address |
| `facts.court_city_state_zip` | facts — court city state zip |
| `facts.court_name` | facts — court name |
| `facts.date_of_appointment` | of appointment, taking office, or assignment or transfer of assets: (+1 more field) |
| `facts.docket_number` | facts — docket number |
| `facts.identifying_number` | facts — identifying number |
| `facts.other_form_number` | 1040 or 1040-SR f 1041 g 1120 h Other (list): |
| `facts.other_tax_type` | Excise Other (describe): |
| `facts.place_of_other_proceedings` | facts — place of other proceedings |
| `facts.proceeding_date` | facts — proceeding date |
| `facts.proceeding_initiated_date` | facts — proceeding initiated date |
| `facts.proceeding_time` | facts — proceeding time |
| `facts.reason_for_termination` | c Other. Describe: (+1 more field) |
| `fiduciary.address` | fiduciary — address (+3 more fields) |
| `fiduciary.name` | fiduciary — name (+2 more fields) |
| `fiduciary.phone` | fiduciary — phone (+1 more field) |
| `signature` | signature |
