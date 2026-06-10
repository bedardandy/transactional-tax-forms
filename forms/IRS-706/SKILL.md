# IRS-706 — United States Estate (and GST) Tax Return

**Agency:** IRS  |  **Domain:** probate  |  **Status:** `opus-adjudicated`
**Pages:** 5  |  **Fillable widgets:** 316  |  **Mapped:** 146 fields / 101 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

Status `opus-adjudicated`: a Qwen-VL draft mapping reviewed field-by-field against each printed caption by Opus (corrections under `mapping.json.adjudication`). Fillable, but verify placement on the rendered output before relying on it.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms IRS-706   # verified official blank
python3 -m engine.fill_via_mapping --form IRS-706 \
    --case forms/IRS-706/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `decedent.date_of_death` | decedent — date of death |
| `decedent.domicile_county` | decedent — domicile county (+6 more fields) |
| `decedent.domicile_state` | decedent — domicile state |
| `decedent.name` | decedent — name (+1 more field) |
| `decedent.ssn` | decedent — ssn (+2 more fields) |
| `executor.address` | executor — address (+8 more fields) |
| `executor.name` | executor — name (+1 more field) |
| `executor.ssn_or_ein` | executor — ssn or ein (+1 more field) |
| `facts.account_number` | d Account number |
| `facts.add_lines_3c_and_4` | . . . . . . . . . 5 |
| `facts.adjusted_taxable_gifts` | . . . . . . . . . 4 |
| `facts.adjustment_to_applicable_credit_amount` | . . . . . . . . . 10 |
| `facts.allowable_amount_of_deductions` | . . . . . . . . . 18 |
| `facts.allowable_applicable_credit_amount` | . . . . . . . . . 11 |
| `facts.alternate_value_estimated_value_of_assets_subject_to_special_rule` | subject to the special rule of Reg. section 20.2010-2(a)(7)(ii) 10 |
| `facts.alternate_value_total_annuities` | . . . . . . . . . 9 |
| `facts.alternate_value_total_gross_estate` | . . . . . . . . . 11 |
| `facts.alternate_value_total_gross_estate_less_exclusion` | . . . . . . . . . 13 |
| `facts.alternate_value_total_insurance_on_decedents_life` | life. Schedule D, line 4. Attach Form(s) 712 . 4 |
| `facts.alternate_value_total_jointly_owned_property` | . . . . . . . . . 5 |
| `facts.alternate_value_total_mortgage_notes_and_cash` | 4 . . . . . . . . 3 |
| `facts.alternate_value_total_other_miscellaneous_property` | 7 . . . . . . . . 6 |
| `facts.alternate_value_total_powers_of_appointment` | . . . . . . . . . 8 |
| `facts.alternate_value_total_qualified_conservation_easement_exclusion` | easement exclusion. Schedule U, line 20 . . . 12 |
| `facts.alternate_value_total_real_estate` | . . . . . . . . . 1 |
| `facts.alternate_value_total_stocks_and_bonds` | . . . . . . . . . 2 |
| `facts.alternate_value_total_transfers_during_decedents_lifetime` | Schedule G, line 5 . . . . . 7 |
| `facts.amount_surviving_spouse_received` | facts — amount surviving spouse received |
| `facts.amount_unascertainable_beneficiaries` | . . . . . . . . . 5c |
| `facts.applicable_credit_amount` | . . . . . . . . . 9e |
| `facts.applicable_exclusion_amount` | and 9c . . . . . . . 9d |
| `facts.basic_exclusion_amount` | . . . . . . . . . 9a |
| `facts.beneficiary_amount_received` | facts — beneficiary amount received (+4 more fields) |
| `facts.beneficiary_identifying_number` | facts — beneficiary identifying number (+4 more fields) |
| `facts.beneficiary_name` | facts — beneficiary name (+4 more fields) |
| `facts.beneficiary_relationship` | facts — beneficiary relationship (+4 more fields) |
| `facts.case_number` | facts — case number |
| `facts.court_location` | facts — court location |
| `facts.court_name` | facts — court name |
| `facts.credit_for_foreign_death_taxes` | . . . . . . . . . 13 |
| `facts.credit_for_pre_1977_federal_gift_taxes` | under section 2012 . . . . . . 15 |
| `facts.credit_for_tax_on_prior_transfers` | Schedule Q (Form 706) . . . . . 14 |
| `facts.death_certificate_issuing_authority` | facts — death certificate issuing authority |
| `facts.death_certificate_number` | facts — death certificate number |
| `facts.decedent_occupation` | facts — decedent occupation |
| `facts.ein_of_entity_with_transferred_interest` | EIN for the entity in which an interest was transferred/sold: |
| `facts.estimated_value_of_assets_subject_to_special_rule` | subject to the special rule of Reg. section 20.2010-2(a)(7)(ii) 10 |
| `facts.estimated_value_of_deductible_assets_subject_to_special_rule` | special rule of Reg. section 20.2010-2(a)(7)(ii) . . . 23 |
| `facts.federal_gift_tax_ir_office` | facts — federal gift tax ir office |
| `facts.federal_gift_tax_period_covered` | facts — federal gift tax period covered |
| `facts.firm_address` | Firm’s address |
| `facts.firm_ein` | Use Only Firm’s name Firm’s EIN |
| `facts.firm_name` | Use Only Firm’s name |
| `facts.firm_phone` | Firm’s address Phone no. |
| `facts.former_marriage_end_date` | facts — former marriage end date (+3 more fields) |
| `facts.former_spouse_name` | facts — former spouse name (+3 more fields) |
| `facts.former_spouse_ssn` | facts — former spouse ssn (+3 more fields) |
| `facts.generation_skipping_transfer_taxes` | 706), Part II, line 11 . . . . 19 |
| `facts.gross_estate_tax` | . . . . . . . . . 8 |
| `facts.marital_credit` | . . . . . . . . . 16 |
| `facts.net_estate_tax` | . . . . . . . . . 18 |
| `facts.overpayment` | . . . . . . . . . 23a |
| `facts.preparer_date` | Preparer self-employed |
| `facts.preparer_name` | facts — preparer name |
| `facts.prior_payments` | . . . . . . . . . 21 |
| `facts.restored_exclusion_amount` | . . . . . . . . . 9c |
| `facts.routing_number` | b Routing number |
| `facts.state_death_tax_deduction` | . . . . . . . . . 3b |
| `facts.tax_due` | . . . . . . . . . 22 |
| `facts.tax_due_or_refund` | . . . . . . . . . 12 |
| `facts.taxable_estate` | . . . . . . . . . 3c |
| `facts.tentative_tax` | . . . . . . . . . 6 |
| `facts.tentative_taxable_estate` | . . . . . . . . . 3a |
| `facts.tentative_total_allowable_deductions` | on Part II, line 2 . . . . 24 |
| `facts.total_allowable_deductions` | . . . . . . . . . 2 |
| `facts.total_amount_of_property_interests_for_marital_deduction` | deduction is being claimed. Schedule M, line 14 . 21 |
| `facts.total_annuities` | . . . . . . . . . 9 |
| `facts.total_benefits_received` | . . . . . . . . . 5d |
| `facts.total_charitable_public_and_similar_gifts_and_beqeusts` | . . . . . . . . . 22 |
| `facts.total_credits` | . . . . . . . . . 17 |
| `facts.total_debts_of_the_decedent` | . . . . . . . . . 15 |
| `facts.total_deductions_items_14_through_16` | . . . . . . . . . 17 |
| `facts.total_expenses_incurred_in_administering_property_not_subject_to_claims` | Schedule L, line 8 . . . . . 20 |
| `facts.total_from_attachment` | . . . . . . . . . 5b |
| `facts.total_funeral_expenses_and_administration_expenses` | administering property subject to claims. Schedule J, line 12 14 |
| `facts.total_gift_tax_paid_or_payable` | . . . . . . . . . 7 |
| `facts.total_gross_estate` | . . . . . . . . . 1 (+1 more field) |
| `facts.total_gross_estate_less_exclusion` | . . . . . . . . . 13 |
| `facts.total_insurance_on_decedents_life` | life. Schedule D, line 4. Attach Form(s) 712 . 4 |
| `facts.total_jointly_owned_property` | . . . . . . . . . 5 |
| `facts.total_mortgage_notes_and_cash` | 4 . . . . . . . . 3 |
| `facts.total_mortgages_and_liens` | the decedent. Schedule K, line 10 . . . 16 |
| `facts.total_net_losses_during_administration` | . . . . . . . . . 19 |
| `facts.total_other_miscellaneous_property` | 7 . . . . . . . . 6 |
| `facts.total_powers_of_appointment` | . . . . . . . . . 8 |
| `facts.total_qualified_conservation_easement_exclusion` | easement exclusion. Schedule U, line 20 . . . 12 |
| `facts.total_real_estate` | . . . . . . . . . 1 |
| `facts.total_stocks_and_bonds` | . . . . . . . . . 2 |
| `facts.total_transfer_taxes` | . . . . . . . . . 20 |
| `facts.total_transfers_during_decedents_lifetime` | Schedule G, line 5 . . . . . 7 |
| `facts.year_domicile_established` | facts — year domicile established |
