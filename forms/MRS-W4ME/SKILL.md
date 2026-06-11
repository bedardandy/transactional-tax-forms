# MRS-W4ME — Employee's Maine Withholding Allowance Certificate

**Agency:** Maine Revenue Services  |  **Domain:** corporations  |  **Status:** `verified`
**Fields:** 28  |  **Mapped:** 17

## What an agent needs to fill this form

Provide a canonical fact object (JSON) with the taxpayer parties and the form's `facts.*` line items — see `mapping.json` for the exact keys this form consumes (these inherited Maine Revenue mappings use the court library's `parties.<role>` key shape) and `examples/sample_case.json` for a worked fictional example. The field table below lists every fillable widget; `mapping.json` routes each canonical key to a `field_id`.

## Manual selections (radio groups)

The engine **never writes radio groups** (soft lock). The fill result carries a yellow-light `radio_groups` entry per group below, with the option suggested from the case key — make the selection by hand on the output PDF before use.

| group | case key | options |
|---|---|---|
| `filing_status_single` | `facts.filing_status` | `Single or Head of Household` / `Married` / `Married, but withholding at higher single rate` |

## Computed lines (printed arithmetic)

This form prints arithmetic instructions, declared in `computations.json` and evaluated by the shared engine. Omit a computed key (with its inputs supplied) and the engine fills it from the printed formula (reported under `computed_fields`); supply it and your value is written **as-is** — a contradiction only adds a `COMPUTATION_MISMATCH` warning, never a block or an override.

| computed key | printed instruction |
|---|---|
| `facts.total_allowances_worksheet` | E. Add lines A through D. (Maximum number of allowances you may claim) |

## Field map

| field_id | type | page | printed label |
|---|---|---|---|
| `clear` | checkbox | 0 | Clear |
| `print` | checkbox | 0 | Print |
| `your_first_name` | text | 0 | Your first name |
| `m_i` | text | 0 | M.I |
| `last_name` | text | 0 | Last name |
| `your_social_security_number` | text | 0 | Your social security number |
| `home_address` | text | 0 | Home address |
| `city_or_town` | text | 0 | City or town |
| `state` | text | 0 | State |
| `zip_code` | text | 0 | Zip code |
| `filing_status_single` | radio | 0 | Filing status--single |
| `filing_status_single_dup1` | radio | 0 | Filing status--single |
| `filing_status_single_dup2` | radio | 0 | Filing status--single |
| `total_number_of_allowances` | text | 0 | Total number of allowances |
| `additional_amount` | text | 0 | Additional amount |
| `you_claimed_exempt` | text | 0 | You claimed exempt |
| `you_completed_federal_form_w4p` | text | 0 | You completed federal form W4p |
| `you_are_a_resident_employee_with_no_maine_tax_liability` | text | 0 | You are a resident employee with no Maine tax liability |
| `you_are_a_recipient_of_periodic_retirement_payments` | text | 0 | You are a recipient of periodic retirement payments |
| `your_spouse_id_a_member_of_the_military` | text | 0 | Your spouse id a member of the military |
| `tribal_member_exemption` | text | 0 | Tribal Member Exemption |
| `employee_s_payees_signature` | text | 0 | Employee's/payees signature |
| `date` | text | 0 | Date |
| `number_of_allowances_claimed_on_federal_form_w_4` | text | 0 | Number of allowances claimed on federal form W-4 |
| `enter_1_for_spouse` | text | 0 | enter 1 for spouse |
| `enter_1_for_hoh` | text | 0 | enter 1 for HOH |
| `number_of_children` | text | 0 | number of children |
| `add_lines_a_d` | text | 0 | add lines a-d |
