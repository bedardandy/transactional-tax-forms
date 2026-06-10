# ME-RETTD — Maine Real Estate Transfer Tax Declaration

**Agency:** Maine Revenue Services  |  **Domain:** real-estate  |  **Status:** `opus-adjudicated`
**Pages:** 4  |  **Fillable widgets:** 91  |  **Mapped:** 74 fields / 21 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed field-by-field against each printed caption by Opus (corrections under `mapping.json.adjudication`). Fillable, but verify placement on the rendered output before relying on it.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms ME-RETTD   # verified official blank
python3 -m engine.fill_via_mapping --form ME-RETTD \
    --case forms/ME-RETTD/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `facts.adjusted_assessed_value` | 6b. Adjusted assessed value............................................................... |
| `facts.special_circumstances_explanation` | facts — special circumstances explanation |
| `property.address` | property — address |
| `property.county` | 1. County |
| `property.map_block_lot` | property — map block lot (+11 more fields) |
| `property.purchase_price` | price (If the transfer is a gift, enter “0”).............................................. |
| `property.town` | 2. Municipality (+8 more fields) |
| `property.transfer_date` | property — transfer date |
| `property.type` | No maps exist erty being sold (see instructions). |
| `transferee.mailing_address` | transferee — mailing address |
| `transferee.mailing_city` | transferee — mailing city |
| `transferee.mailing_state` | transferee — mailing state |
| `transferee.mailing_zip` | transferee — mailing zip |
| `transferee.name` | transferee — name (+9 more fields) |
| `transferee.ssn_or_ein` | transferee — ssn or ein (+7 more fields) |
| `transferor.address` | transferor — address |
| `transferor.mailing_city` | transferor — mailing city |
| `transferor.mailing_state` | transferor — mailing state |
| `transferor.mailing_zip` | transferor — mailing zip |
| `transferor.name` | transferor — name (+9 more fields) |
| `transferor.ssn_or_ein` | transferor — ssn or ein (+9 more fields) |
