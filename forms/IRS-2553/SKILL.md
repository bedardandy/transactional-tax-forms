# IRS-2553 — Election by a Small Business Corporation (S corporation)

**Agency:** IRS  |  **Domain:** corporations  |  **Status:** `opus-adjudicated`
**Pages:** 4  |  **Fillable widgets:** 100  |  **Mapped:** 23 fields / 17 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed field-by-field against each printed caption by Opus (corrections under `mapping.json.adjudication`). Fillable, but verify placement on the rendered output before relying on it.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms IRS-2553   # verified official blank
python3 -m engine.fill_via_mapping --form IRS-2553 \
    --case forms/IRS-2553/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `entity.ein` | entity — ein (+3 more fields) |
| `entity.formation_date` | entity — formation date |
| `entity.legal_name` | entity — legal name (+3 more fields) |
| `entity.mailing_address` | entity — mailing address |
| `entity.phone` | entity — phone |
| `entity.state_of_formation` | entity — state of formation |
| `entity.street_address` | entity — street address |
| `facts.election_effective_date` | year) (see instructions) . . . . . . ▶ |
| `facts.fiscal_year_52_53_week_month` | 52-53-week year ending with reference to the month of ▶ |
| `facts.fiscal_year_end` | (2) Fiscal year ending (month and day) ▶ |
| `facts.income_beneficiary_name` | facts — income beneficiary name |
| `facts.income_beneficiary_ssn` | facts — income beneficiary ssn |
| `facts.stock_transfer_date` | year) . . . . . . . . ▶ |
| `responsible_party.name` | responsible party — name |
| `responsible_party.title` | Here ▲ |
| `trust.ein` | trust — ein |
| `trust.name` | trust — name |
