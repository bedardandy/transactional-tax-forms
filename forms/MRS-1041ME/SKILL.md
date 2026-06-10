# MRS-1041ME — Maine Fiduciary Income Tax Return

**Agency:** Maine Revenue Services  |  **Domain:** probate  |  **Status:** `mapped`
**Pages:** 3  |  **Fillable widgets:** 129  |  **Mapped:** 123 fields / 121 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms MRS-1041ME   # verified official blank
python3 -m engine.fill_via_mapping --form MRS-1041ME \
    --case forms/MRS-1041ME/examples/sample_case.json --out /tmp/out
```

## Manual selections (radio groups)

The engine **never writes radio groups** (soft lock). The fill result carries a yellow-light `radio_groups` entry per group below, with the option suggested from the case key — make the selection by hand on the output PDF before use.

| group | case key | options |
|---|---|---|
| `do_you_want_to_allow_someone_to_discuss_return_with_mrs` | `facts.third_party_designee` | Yes / No |

## Computed lines (printed arithmetic)

This form prints arithmetic instructions, declared in `computations.json` and evaluated by the shared engine. Omit a computed key (with its inputs supplied) and the engine fills it from the printed formula (reported under `computed_fields`); supply it and your value is written **as-is** — a contradiction only adds a `COMPUTATION_MISMATCH` warning, never a block or an override.

| computed key | printed instruction |
|---|---|
| `facts.adjusted_maine_income_tax` | 6. Adjusted Maine income tax. (Line 4 plus or minus line 5.) |
| `facts.net_fiduciary_adjustment` | 3 Net Fiduciary Adjustment. (Subtract line 2i from line 1j — see instructions [may be a negative amount].) |
| `facts.total_additions` | j Total Additions. (Add lines 1a through 1i.) |
| `facts.total_amount_due` | c. TOTAL AMOUNT DUE. (Add lines 8a and 8b.) |
| `facts.total_payments` | d. Total payments. (Add lines 7a, 7b and 7c.) |
| `facts.total_subtractions` | i Total Subtractions. (Add lines 2a through 2h.) |

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `facts.additions_bonus_depreciation_addback` | facts — additions bonus depreciation addback |
| `facts.additions_capital_investment_credit_bonus_depreciation_addback` | facts — additions capital investment credit bonus depreciation addback |
| `facts.additions_installment_sale_gains` | facts — additions installment sale gains |
| `facts.additions_mainepers_contributions` | facts — additions mainepers contributions |
| `facts.additions_municipal_state_bond_income` | from municipal and state bonds, other than Maine. ........................................ |
| `facts.additions_net_operating_loss_adjustment` | b Net Operating Loss Adjustment. (Attach schedule.) ...................................... |
| `facts.additions_other` | facts — additions other |
| `facts.additions_qbi_deduction_addback` | facts — additions qbi deduction addback |
| `facts.adjusted_maine_income_tax` | facts — adjusted maine income tax |
| `facts.adjustments_to_tax` | 5. Adjustments to tax. (From Schedule A, line 19.) ....................................... |
| `facts.amended_return` | Amended Return |
| `facts.beneficiary_1_maine_source_income` | facts — beneficiary 1 maine source income |
| `facts.beneficiary_1_name` | facts — beneficiary 1 name |
| `facts.beneficiary_1_percent` | (a) B- $ |
| `facts.beneficiary_1_share_of_income` | facts — beneficiary 1 share of income |
| `facts.beneficiary_1_ssn_or_ein` | facts — beneficiary 1 ssn or ein |
| `facts.beneficiary_1_state_of_domicile` | facts — beneficiary 1 state of domicile |
| `facts.beneficiary_2_maine_source_income` | facts — beneficiary 2 maine source income |
| `facts.beneficiary_2_name` | (b) B- |
| `facts.beneficiary_2_percent` | (b) B- $ |
| `facts.beneficiary_2_share_of_income` | (b) B- $ |
| `facts.beneficiary_2_ssn_or_ein` | (b) B- $ % |
| `facts.beneficiary_2_state_of_domicile` | (b) B- $ % |
| `facts.beneficiary_3_maine_source_income` | (c) B- $ % $ |
| `facts.beneficiary_3_name` | (c) B- |
| `facts.beneficiary_3_percent` | (c) B- $ |
| `facts.beneficiary_3_share_of_income` | (c) B- $ |
| `facts.beneficiary_3_ssn_or_ein` | (c) B- $ % |
| `facts.beneficiary_3_state_of_domicile` | (c) B- $ % |
| `facts.beneficiary_4_maine_source_income` | (d) B- $ % $ |
| `facts.beneficiary_4_name` | (d) B- |
| `facts.beneficiary_4_percent` | (d) B- $ |
| `facts.beneficiary_4_share_of_income` | (d) B- $ |
| `facts.beneficiary_4_ssn_or_ein` | (d) B- $ % |
| `facts.beneficiary_4_state_of_domicile` | (d) B- $ % |
| `facts.beneficiary_5_maine_source_income` | (e) B- $ % $ |
| `facts.beneficiary_5_name` | (e) B- |
| `facts.beneficiary_5_percent` | (e) B- $ |
| `facts.beneficiary_5_share_of_income` | (e) B- $ |
| `facts.beneficiary_5_ssn_or_ein` | (e) B- $ % |
| `facts.beneficiary_5_state_of_domicile` | (e) B- $ % |
| `facts.checking_account_number` | account outside the |
| `facts.contact_area_code` | facts — contact area code |
| `facts.contact_first_name` | facts — contact first name |
| `facts.contact_last_name` | facts — contact last name |
| `facts.contact_phone` | facts — contact phone |
| `facts.credit_other_jurisdiction_allowable_credit` | facts — credit other jurisdiction allowable credit |
| `facts.credit_other_jurisdiction_income_taxed` | facts — credit other jurisdiction income taxed |
| `facts.credit_other_jurisdiction_limit_amount` | ____________ multiplied by ________% on line 3 above. .......................... 4a |
| `facts.credit_other_jurisdiction_limit_maine_tax` | a Form 1041ME, page 1, line 4 $ |
| `facts.credit_other_jurisdiction_limit_percent` | Form 1041ME, page 1, line 4 $ ____________ multiplied by |
| `facts.credit_other_jurisdiction_maine_taxable_income` | facts — credit other jurisdiction maine taxable income |
| `facts.credit_other_jurisdiction_name` | facts — credit other jurisdiction name |
| `facts.credit_other_jurisdiction_percent_taxed` | facts — credit other jurisdiction percent taxed |
| `facts.credit_other_jurisdiction_taxes_paid` | facts — credit other jurisdiction taxes paid |
| `facts.decedent_ssn` | one box): |
| `facts.designee_area_code` | Designee Designee’s name Phone no. ( |
| `facts.designee_name` | Designee Designee’s name |
| `facts.designee_phone` | Designee Designee’s name Phone no. ( ) |
| `facts.designee_pin` | Designee’s name Phone no. ( ) Personal Identiﬁ cation number |
| `facts.entity_type_bankruptcy_estate_ch11` | Bankruptcy estate |
| `facts.entity_type_bankruptcy_estate_ch7` | Bankruptcy estate |
| `facts.entity_type_complex_trust` | Bankruptcy estate |
| `facts.entity_type_decedents_estate` | Decedent’s estate Qualiﬁ ed Funeral Trust (QFT) Qualiﬁ |
| `facts.entity_type_esbt` | Bankruptcy estate |
| `facts.entity_type_pooled_income` | Bankruptcy estate |
| `facts.entity_type_qualified_disability_trust` | Qualiﬁ ed Bankruptcy estate |
| `facts.entity_type_qualified_funeral_trust` | Qualiﬁ ed Funeral Trust (QFT) Qualiﬁ ed Bankruptcy |
| `facts.entity_type_simple_trust` | Bankruptcy estate |
| `facts.estate_ein` | facts — estate ein |
| `facts.estate_name` | facts — estate name |
| `facts.estate_or_trust_name` | (f) E/T- |
| `facts.estate_or_trust_percent` | (f) E/T- $ |
| `facts.estate_or_trust_share_of_income` | (f) E/T- $ |
| `facts.estate_trust_created_date` | facts — estate trust created date |
| `facts.estate_trust_ein` | facts — estate trust ein (+1 more field) |
| `facts.estimated_tax_payments` | extension payments. (Include any real estate withholding tax payments.) ....7b |
| `facts.federal_taxable_income` | facts — federal taxable income |
| `facts.fiduciary_adjustment` | Fiduciary Adjustment: Resident estates and trusts only. (See instructions.) .............. |
| `facts.final_return` | facts — final return |
| `facts.form_2210me_box_checked` | ............. 8b .00 |
| `facts.initial_return` | facts — initial return |
| `facts.maine_income_tax` | tax. (From tax table on page 2 of instructions.) ......................................... |
| `facts.maine_income_tax_withheld` | facts — maine income tax withheld |
| `facts.maine_taxable_income` | or trust - Schedule NR, line 9, Column B.) ............................................... |
| `facts.net_fiduciary_adjustment` | — see instructions [may be a negative amount].) ......... 3 |
| `facts.nonresident_estate_or_trust` | facts — nonresident estate or trust |
| `facts.overpayment_amount` | line 7d is greater than line 6, enter OVERPAYMENT. ....................................... |
| `facts.overpayment_credited_amount` | to next year’s estimated tax. ....... 10a |
| `facts.penalty` | facts — penalty |
| `facts.preparer_name` | facts — preparer name |
| `facts.preparer_phone` | facts — preparer phone |
| `facts.preparer_ssn_or_ptin` | facts — preparer ssn or ptin |
| `facts.refund_account_outside_us` | facts — refund account outside us |
| `facts.refund_amount` | to next year’s estimated tax. ....... 10a .00 REFUNDED............10b |
| `facts.refundable_tax_credits` | c. Refundable tax credits. (From Schedule A, line 4.) .................................... |
| `facts.resident_estate_or_trust` | facts — resident estate or trust |
| `facts.routing_number` | Check this box if this |
| `facts.subtractions_bonus_depreciation_section_179_recapture` | facts — subtractions bonus depreciation section 179 recapture |
| `facts.subtractions_mainepers_pickup_contributions` | been previously taxed by the state. (See instructions.) .................................. |
| `facts.subtractions_medical_cannabis_expenses` | e Medical Marijuana Business Expenses. (See instructions.) ............................... |
| `facts.subtractions_net_operating_loss_recapture` | f Net Operating Loss recapture. (See instructions) ....................................... |
| `facts.subtractions_other` | facts — subtractions other |
| `facts.subtractions_social_security_railroad_benefits` | ts included in federal taxable income (See instructions.) ....... 2b |
| `facts.subtractions_us_government_bond_interest` | Government Bond interest included in federal taxable income. ............................. |
| `facts.tax_balance_due` | is greater than line 7d, enter TAX BALANCE DUE. .......................................... |
| `facts.tax_period_end` | 2 0 2 0 to |
| `facts.tax_period_start` | (mm dd yyyy) |
| `facts.total_additions` | facts — total additions |
| `facts.total_amount_due` | 8b.) Make checks payable to Treasurer, State of Maine. 8c |
| `facts.total_maine_source_income` | (g) Total $ 100% $ |
| `facts.total_payments` | facts — total payments |
| `facts.total_share_of_income` | facts — total share of income |
| `facts.total_subtractions` | facts — total subtractions |
| `party.address` | party — address |
| `party.city` | party — city |
| `party.full_name` | party — full name |
| `party.ssn_or_ein` | party — ssn or ein |
| `party.state` | party — state |
| `party.zip` | party — zip |
| `today()` | today() (+1 more field) |
