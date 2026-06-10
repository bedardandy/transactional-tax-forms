# IRS-1041 — U.S. Income Tax Return for Estates and Trusts

**Agency:** IRS  |  **Domain:** probate  |  **Status:** `opus-adjudicated`
**Pages:** 3  |  **Fillable widgets:** 173  |  **Mapped:** 79 fields / 78 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed field-by-field against each printed caption by Opus (corrections under `mapping.json.adjudication`). Fillable, but verify placement on the rendered output before relying on it.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms IRS-1041   # verified official blank
python3 -m engine.fill_via_mapping --form IRS-1041 \
    --case forms/IRS-1041/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `entity.mailing_address` | entity — mailing address |
| `entity.mailing_city` | Pooled income fund |
| `entity.mailing_state` | Pooled income fund |
| `entity.mailing_zip` | Pooled income fund |
| `estate.date_created` | Qualified disability trust |
| `estate.ein` | Simple trust |
| `estate.name` | Simple trust |
| `facts.account_number` | e Account number |
| `facts.account_type_checking` | Checking Savings |
| `facts.account_type_savings` | facts — account type savings |
| `facts.add_lines_10_15b` | . . . . . . . . . 16 |
| `facts.add_lines_18_21` | . . . . . . . . . 22 |
| `facts.adjusted_total_income` | 16 from line 9 . . . . . 17 (+1 more field) |
| `facts.alternative_minimum_tax` | (Form 1041), line 54) . . . . . 1c |
| `facts.amount_credited` | Amount of line 29 to be: a Credited to 2026 |
| `facts.amount_from_form_4255` | . . . . . . . . . 1d |
| `facts.amount_refunded` | ; b Refunded . . . . . . 30b |
| `facts.attorney_accountant_fees` | . . . . . . . . . 14 |
| `facts.business_income_loss` | . . . . . . . . . 3 |
| `facts.capital_gain_loss` | . . . . . . . . . 4 |
| `facts.charitable_deduction` | . . . . . . . . . 13 |
| `facts.check_amended_return` | Amended return Net operating loss carryback |
| `facts.check_change_fiduciary` | Change in fiduciary Change in fiduciary’s name Change |
| `facts.check_change_fiduciary_address` | Change in fiduciary’s address |
| `facts.check_change_fiduciary_name` | Change in fiduciary’s name Change in fiduciary’s address |
| `facts.check_change_trust_name` | Change in trust’s name Change in fiduciary Change |
| `facts.check_described_4947a1` | Described in sec. 4947(a)(1). Check here |
| `facts.check_described_4947a2` | Described in sec. 4947(a)(2) |
| `facts.check_final_return` | Final return Amended return Net operating loss carryback |
| `facts.check_form_4952` | . . . . . . . . |
| `facts.check_initial_return` | Initial return Final return Amended return Net operating |
| `facts.check_nol_carryback` | Net operating loss carryback |
| `facts.check_not_private_foundation` | facts — check not private foundation |
| `facts.check_section_645_election` | G(2) Trust TIN |
| `facts.country` | Pooled income fund |
| `facts.current_year_net_965_tax` | 965-A, Part II, column (k) (see instructions) . . 25a |
| `facts.estate_tax_deduction` | certain generation-skipping taxes (attach computation) . . . . 19 |
| `facts.estimated_tax_penalty` | . . . . . . . . . 27 |
| `facts.exemption` | . . . . . . . . . 21 |
| `facts.farm_income_loss` | . . . . . . . . . 6 |
| `facts.fiduciary_fees` | 67(e), see instructions . . . . . . 12 |
| `facts.first_installment_1062` | tax liability. Enter amount from Form 1062, line 15 25b |
| `facts.fiscal_year_beginning` | that apply: For calendar year 2025 or fiscal year beginning |
| `facts.fiscal_year_ending` | year 2025 or fiscal year beginning , 2025, and ending |
| `facts.fiscal_year_ending_year` | or fiscal year beginning , 2025, and ending , 20 |
| `facts.income_distribution_deduction` | line 15). Attach Schedules K-1 (Form 1041) . . 18 |
| `facts.interest_deduction` | . . . . . . . . . 10 |
| `facts.interest_income` | . . . . . . . . . 1 |
| `facts.may_irs_discuss_no` | facts — may irs discuss no |
| `facts.may_irs_discuss_yes` | Yes No |
| `facts.net_operating_loss_deduction` | . . . . . . . . . 15b |
| `facts.number_of_schedules_k1` | facts — number of schedules k1 |
| `facts.ordinary_gain_loss` | . . . . . . . . . 7 |
| `facts.other_amounts_distributed` | . . . . . . . . . 10 |
| `facts.other_deductions` | schedule). See instructions for deductions allowable under section 67(e) 15a |
| `facts.other_income` | 8 Other income. List type and amount 8 |
| `facts.other_income_type` | 8 Other income. List type and amount |
| `facts.overpayment` | lines 24, 25a, 25b, and 27, enter amount overpaid 29 |
| `facts.preparer_name` | facts — preparer name |
| `facts.qualified_business_income_deduction` | . . . . . . . . . 20 |
| `facts.qualified_dividends_beneficiaries` | b Qualified dividends allocable to: (1) Beneficiaries |
| `facts.qualified_dividends_estate` | Qualified dividends allocable to: (1) Beneficiaries (2) Estate or trust |
| `facts.rents_royalties` | trusts, etc. Attach Schedule E (Form 1040) . . 5 |
| `facts.routing_number` | c Routing number |
| `facts.suite_no` | facts — suite no |
| `facts.tax_due` | 25a, 25b, and 27, enter amount owed . . 28 |
| `facts.tax_on_lump_sum_distributions` | . . . . . . . . . 1b |
| `facts.tax_on_taxable_income` | . . . . . . . . . 1a |
| `facts.taxable_income` | . . . . . . . . . 23 |
| `facts.taxes` | . . . . . . . . . 11 |
| `facts.total_income` | . . . . . . . . . 9 |
| `facts.total_ordinary_dividends` | . . . . . . . . . 2a |
| `facts.total_payments` | . . . . . . . . . 26 |
| `facts.total_tax` | . . . . . . . . . 24 |
| `facts.total_tax_computation` | . . . . . . . . . 1e |
| `facts.trust_tin` | . . . . . . . G(2) Trust TIN |
| `fiduciary.name` | Qualified disability trust |
| `signature` | signature |
