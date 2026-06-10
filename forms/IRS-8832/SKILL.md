# IRS-8832 — Entity Classification Election

**Agency:** IRS  |  **Domain:** corporations  |  **Status:** `opus-adjudicated`
**Pages:** 8  |  **Fillable widgets:** 70  |  **Mapped:** 53 fields / 14 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed field-by-field against each printed caption by Opus (corrections under `mapping.json.adjudication`). Fillable, but verify placement on the rendered output before relying on it.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms IRS-8832   # verified official blank
python3 -m engine.fill_via_mapping --form IRS-8832 \
    --case forms/IRS-8832/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `entity.ein` | entity — ein |
| `entity.legal_name` | entity — legal name |
| `entity.mailing_address` | entity — mailing address |
| `entity.street_address` | entity — street address |
| `facts.contact_person_name_and_title` | facts — contact person name and title |
| `facts.contact_person_phone` | facts — contact person phone |
| `facts.election_effective_date` | . . . . . . . . . ▶ |
| `facts.explanation_for_late_filing` | facts — explanation for late filing (+8 more fields) |
| `facts.foreign_country_of_organization` | organization ▶ |
| `facts.parent_corporation_ein` | b Employer identification number ▶ |
| `facts.parent_corporation_name` | a Name of parent corporation ▶ |
| `responsible_party.name` | a Name of owner ▶ |
| `responsible_party.ssn_itin_ein` | b Identifying number of owner ▶ |
| `today()` | today() (+31 more fields) |
