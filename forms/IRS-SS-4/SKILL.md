# IRS-SS-4 — Application for Employer Identification Number (EIN)

**Agency:** IRS  |  **Domain:** corporations  |  **Status:** `opus-adjudicated`
**Pages:** 2  |  **Fillable widgets:** 89  |  **Mapped:** 44 fields / 43 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed field-by-field against each printed caption by Opus (corrections under `mapping.json.adjudication`). Fillable, but verify placement on the rendered output before relying on it.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms IRS-SS-4   # verified official blank
python3 -m engine.fill_via_mapping --form IRS-SS-4 \
    --case forms/IRS-SS-4/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `decedent.ssn` | Sole proprietor (SSN) Estate (SSN of decedent) |
| `entity.county` | entity — county |
| `entity.ein` | instructions for each line. Keep a copy for your records. |
| `entity.formation_date` | entity — formation date |
| `entity.legal_name` | entity — legal name |
| `entity.mailing_address` | entity — mailing address |
| `entity.mailing_city` | entity — mailing city |
| `entity.phone` | Name and title (type or print clearly) |
| `entity.state_of_formation` | applicable) where incorporated |
| `entity.street_address` | entity — street address |
| `entity.trade_name` | entity — trade name |
| `executor.name` | executor — name |
| `facts.accounting_year_closing_month` | facts — accounting year closing month |
| `facts.agricultural_employees` | facts — agricultural employees |
| `facts.banking_purpose` | for applying (check only one box) Banking purpose (specify purpose) |
| `facts.corp_form_number` | Corporation (enter form number to be filed) |
| `facts.designee_address` | facts — designee address |
| `facts.designee_fax` | facts — designee fax |
| `facts.designee_name` | facts — designee name |
| `facts.designee_phone` | facts — designee phone |
| `facts.first_date_wages_paid` | . . . . . . . . . . |
| `facts.foreign_country` | applicable) where incorporated |
| `facts.group_exemption_number` | Other (specify) Group Exemption Number (GEN) if any |
| `facts.household_employees` | facts — household employees |
| `facts.new_business_type` | Started new business (specify type) |
| `facts.new_org_type` | business (specify type) Changed type of organization (specify new type) |
| `facts.nonprofit_org_specify` | Other nonprofit organization (specify) |
| `facts.number_of_llc_members` | No LLC members . . . . . . . |
| `facts.other_activity_specify` | Real estate Manufacturing Finance & insurance Other (specify) |
| `facts.other_employees` | facts — other employees |
| `facts.other_entity_type_specify` | Other (specify) |
| `facts.other_reason_specify` | Other (specify) |
| `facts.pension_plan_type` | with IRS withholding regulations Created a pension plan (specify type) |
| `facts.plan_administrator_tin` | Partnership Plan administrator (TIN) |
| `facts.previous_ein` | If “Yes,” write previous EIN here |
| `facts.principal_line_of_merchandise` | facts — principal line of merchandise |
| `facts.sole_proprietor_ssn` | Sole proprietor (SSN) |
| `facts.street_city_state_zip` | facts — street city state zip |
| `facts.trust_type` | box and see line 13.) Created a trust (specify type) |
| `responsible_party.name` | Name and title (type or print clearly) (+1 more field) |
| `responsible_party.ssn_itin_ein` | responsible party — ssn itin ein |
| `today()` | Signature Date |
| `trust.ein` | (enter form number to be filed) Trust (TIN of grantor) |
