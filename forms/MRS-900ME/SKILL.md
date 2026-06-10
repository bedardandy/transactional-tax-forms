# MRS-900ME — Payment Voucher for Maine Income Tax Withheld

**Agency:** Maine Revenue Services  |  **Domain:** corporations  |  **Status:** `verified`
**Fields:** 15  |  **Mapped:** 13

## What an agent needs to fill this form

Provide a canonical fact object (JSON) with the taxpayer parties and the form's `facts.*` line items — see `mapping.json` for the exact keys this form consumes (these inherited Maine Revenue mappings use the court library's `parties.<role>` key shape) and `examples/sample_case.json` for a worked fictional example. The field table below lists every fillable widget; `mapping.json` routes each canonical key to a `field_id`.

## Field map

| field_id | type | page | printed label |
|---|---|---|---|
| `clear` | checkbox | 0 | Clear |
| `print` | checkbox | 0 | Print |
| `withholding_account_number` | text | 0 | Withholding account number |
| `amount_remitted` | text | 0 | Amount remitted |
| `business_name` | text | 0 | Business name |
| `quarter_begin_date` | text | 0 | Quarter begin date |
| `quarter_end_date` | text | 0 | Quarter end date |
| `date_wages_non_wages_paid` | text | 0 | Date wages/non-wages paid |
| `amount_withheld1` | text | 0 | Amount withheld1 |
| `date_wages_non_wages_paid1` | text | 0 | Date wages/non-wages paid1 |
| `amount_withheld2` | text | 0 | Amount withheld2 |
| `date_wages_non_wages_paid2` | text | 0 | Date wages/non-wages paid2 |
| `amount_withheld3` | text | 0 | Amount withheld3 |
| `contact_person` | text | 0 | Contact person |
| `contact_persons_number` | text | 0 | Contact persons number |
