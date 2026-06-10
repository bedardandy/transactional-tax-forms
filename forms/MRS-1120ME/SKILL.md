# MRS-1120ME — Maine Corporate Income Tax Return

**Agency:** Maine Revenue Services  |  **Domain:** corporations  |  **Status:** `verified`
**Fields:** 93  |  **Mapped:** 69

## What an agent needs to fill this form

Provide a canonical fact object (JSON) with the taxpayer parties and the form's `facts.*` line items — see `mapping.json` for the exact keys this form consumes (these inherited Maine Revenue mappings use the court library's `parties.<role>` key shape) and `examples/sample_case.json` for a worked fictional example. The field table below lists every fillable widget; `mapping.json` routes each canonical key to a `field_id`.

## Computed lines (printed arithmetic)

This form prints arithmetic instructions, declared in `computations.json` and evaluated by the shared engine. Omit a computed key (with its inputs supplied) and the engine fills it from the printed formula (reported under `computed_fields`); supply it and your value is written **as-is** — a contradiction only adds a `COMPUTATION_MISMATCH` warning, never a block or an override.

| computed key | printed instruction |
|---|---|
| `facts.adjusted_federal_taxable_income` | Adjusted federal taxable income (line 1 minus line 2 plus line 3) |
| `facts.total_payments_and_credits` | Total payments and credits (add lines 7a through 7e and subtract line 7f; if the result is negative, enter a minus sign to the left of the number) |
| `facts.total_tax` | Total tax (add lines 6a and 6b) |

## Field map

| field_id | type | page | printed label |
|---|---|---|---|
| `clear` | checkbox | 0 | Clear |
| `print` | checkbox | 0 | Print |
| `tax_year_begin` | text | 0 | Tax year begin |
| `tax_year_end` | text | 0 | Tax year end |
| `name_of_corporation` | text | 0 | Name of Corporation |
| `fed_business_code` | text | 0 | Fed Business Code |
| `990t_or_1120_h_check_box` | text | 0 | 990T or 1120-H check box |
| `address` | text | 0 | Address |
| `fed_employer_id_number` | text | 0 | Fed Employer ID Number |
| `state_of_incorporation` | text | 0 | State of Incorporation |
| `city_town_or_post_office` | text | 0 | City, Town or Post Office |
| `state` | text | 0 | State |
| `zip_code` | text | 0 | Zip Code |
| `parent_company_employer_id_number` | text | 0 | Parent Company Employer ID Number |
| `contact_person_s_first_name` | text | 0 | Contact Person's First Name |
| `contact_person_s_last_name` | text | 0 | Contact Person's Last Name |
| `area_code` | text | 0 | Area Code |
| `telephone_number` | text | 0 | Telephone Number |
| `address_change` | text | 0 | Address Change |
| `exemption_due_to_86_272` | text | 0 | Exemption due to 86-272 |
| `during_tax_year_member_of_combined_group_disposed_of_an_interest_in_a_pass_through_entity_doing_business_in_maine` | text | 0 | During tax year member of Combined Group disposed of an inte |
| `initial_return` | text | 0 | Initial Return |
| `amended_return` | text | 0 | Amended Return |
| `combined_return` | text | 0 | Combined return |
| `final_return` | text | 0 | Final Return |
| `final_business_date` | text | 0 | Final Business Date |
| `ceased` | text | 0 | ceased |
| `dissolved` | text | 0 | dissolved |
| `merged` | text | 0 | merged |
| `member_of_an_affiliated_group_filing_a_separate_return` | text | 0 | Member of an affiliated group filing a separate return |
| `based_on_a_pro_forma` | text | 0 | Based on a pro-forma |
| `ein_of_pass_through` | text | 0 | EIN of Pass-Through |
| `successein` | text | 0 | successEIN |
| `federal_consolidated_income` | text | 0 | Federal Consolidated Income (Fed Form1120, line 30) |
| `tentative_total_tax_filed_on_fed_form_7004` | text | 0 | Tentative Total Tax Filed on Fed Form 7004 |
| `federal_taxable_income` | text | 0 | Federal Taxable Income (Fed Form 1120, Line 30) |
| `total_subtractions` | text | 0 | Total Subtractions |
| `total_additions` | text | 0 | Total additions |
| `adjusted_federal_taxable_income` | text | 0 | Adjusted federal taxable income |
| `gross_tax` | text | 0 | Gross Tax |
| `maine_corporate_income_tax` | text | 0 | Maine Corporate Income Tax |
| `credit_recapture` | text | 0 | Credit Recapture |
| `total_tax` | text | 0 | Total Tax |
| `federal_ein_page_2` | text | 1 | Federal EIN page 2 |
| `maine_estimated_tax` | text | 1 | Maine Estimated Tax |
| `extension_payment` | text | 1 | Extension Payment |
| `tax_credits` | text | 1 | Tax credits |
| `income_tax_withheld` | text | 1 | Income Tax Withheld |
| `if_amended_enter_payments` | text | 1 | If amended, enter payments |
| `if_amended_enter_overpayments` | text | 1 | If amended , enter overpayments |
| `total_payments_and_credits` | text | 1 | Total payments and credits |
| `tax_due` | text | 1 | Tax due |
| `overpayment` | text | 1 | Overpayment |
| `check_here_if_2220me_box_5a_is_checked` | text | 1 | Check here if 2220ME box 5a is checked |
| `penalty_for_underpayment_of_estimated_tax` | text | 1 | Penalty for underpayment of estimated tax |
| `total_due` | text | 1 | Total due |
| `total_overpayment` | text | 1 | Total overpayment |
| `amount_of_line_11_to_be_credited` | text | 1 | Amount of line 11 to be Credited |
| `amount_of_line_11_to_be_refunded` | text | 1 | Amount of line 11 to be Refunded |
| `check_if_refund_will_go_to_an_account_outside_the_us` | text | 1 | Check if refund will go to an account outside the US |
| `routing_number` | text | 1 | Routing Number |
| `checking_account_number` | text | 1 | Checking Account Number |
| `federal_ein_page_3` | text | 2 | Federal EIN page 3 |
| `check_if_using_alternate_apportionment` | text | 2 | Check if using alternate apportionment |
| `total_sales_within_maine` | text | 2 | Total Sales within Maine |
| `total_sales_everywhere` | text | 2 | Total Sales Everywhere |
| `total_payroll_within_maine` | text | 2 | Total Payroll within Maine |
| `total_payroll_everywhere` | text | 2 | Total Payroll Everywhere |
| `total_property_within_maine` | text | 2 | Total Property within Maine |
| `total_property_everywhere` | text | 2 | Total Property Everywhere |
| `apportionment_factor` | text | 2 | Apportionment Factor |
| `gross_tax` | text | 2 | Gross Tax (form 1120ME line 6) |
| `maine_corp_income_tax` | text | 2 | Maine Corp Income Tax (line 5 x line 4 factor) |
| `tangible_personal_property` | text | 2 | Tangible Personal Property |
| `paid_prep` | text | 2 | Paid Prep (yes/no) |
| `paid_prep_dup1` | text | 2 | Paid Prep (yes/no) |
| `paid_preparer_s_name` | text | 2 | Paid Preparer's Name |
| `paid_preparer_s_phone_number` | text | 2 | Paid Preparer's Phone Number |
| `paid_preparer_s_pin` | text | 2 | Paid Preparer's Pin |
| `corporation_presidents_name` | text | 2 | Corporation Presidents Name |
| `presidents_social_security_number` | text | 2 | Presidents social security number |
| `treasurer_s_name` | text | 2 | Treasurer's Name |
| `treasurer_s_social_security_number` | text | 2 | Treasurer's social security number |
| `company_email_address` | text | 2 | Company Email Address |
| `date_officer_signed` | text | 2 | Date officer signed |
| `officer_signature` | text | 2 | Officer Signature |
| `officer_title` | text | 2 | Officer title |
| `officer_ssn` | text | 2 | Officer SSN |
| `date_preparer_signed` | text | 2 | Date preparer signed |
| `signature_and_address_of_preparer` | text | 2 | signature and address of Preparer |
| `preparer_ssn_or_ptin` | text | 2 | Preparer  SSN or PTIN |
| `clear_end` | checkbox | 2 | Clear - End |
| `print_end` | checkbox | 2 | Print - End |
