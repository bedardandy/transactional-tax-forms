# MRS-700SOV — Maine Estate Tax Statement of Value (Lien Discharge)

**Agency:** Maine Revenue Services  |  **Domain:** probate  |  **Status:** `mapped`
**Pages:** 2  |  **Fillable widgets:** 46  |  **Mapped:** 42 fields / 41 keys

> Not tax or legal advice. The fill output is a draft; verify every value against the current official form before filing.

## What an agent needs

Build a canonical fact object (JSON) using the keys in the table below — tax-native roles (`entity`, `decedent`, `executor`, `transferor`/`transferee`, `property`, …) plus `facts.<snake_case>` for the form's labeled line items. `examples/sample_case.json` exercises every mapped key with fictional placeholder values.

## Fill

```bash
python3 tools/fetch_pdfs.py --forms MRS-700SOV   # verified official blank
python3 -m engine.fill_via_mapping --form MRS-700SOV \
    --case forms/MRS-700SOV/examples/sample_case.json --out /tmp/out
```

## Canonical keys

| key | filled into (printed caption) |
|---|---|
| `decedent.date_of_death` | Social Security Number (SSN): Date of Death: |
| `decedent.domicile_state` | Residency Status: Resident Nonresident |
| `decedent.first_name` | decedent — first name |
| `decedent.last_name` | decedent — last name |
| `decedent.middle_name` | decedent — middle name |
| `decedent.ssn` | Social Security Number (SSN): |
| `executor.city` | executor — city |
| `executor.email` | executor — email |
| `executor.fax_area_code` | executor — fax area code |
| `executor.fax_number` | executor — fax number |
| `executor.first_name` | executor — first name |
| `executor.last_name` | executor — last name |
| `executor.middle_name` | executor — middle name |
| `executor.phone` | executor — phone |
| `executor.phone_area_code` | executor — phone area code |
| `executor.ssn` | executor — ssn |
| `executor.state` | executor — state |
| `executor.street_address` | executor — street address |
| `executor.zip` | executor — zip |
| `facts.contact_area_code` | facts — contact area code |
| `facts.contact_city` | facts — contact city |
| `facts.contact_email` | facts — contact email |
| `facts.contact_fax_area_code` | facts — contact fax area code |
| `facts.contact_fax_number` | facts — contact fax number |
| `facts.contact_first_name` | facts — contact first name |
| `facts.contact_last_name` | facts — contact last name |
| `facts.contact_mailing_address` | facts — contact mailing address |
| `facts.contact_middle_initial` | facts — contact middle initial |
| `facts.contact_phone` | facts — contact phone |
| `facts.contact_state` | facts — contact state |
| `facts.contact_zip` | facts — contact zip |
| `facts.representative_firm_name` | facts — representative firm name |
| `facts.spouse_name` | If married or widow(er), enter spouse’s name: |
| `facts.spouse_ssn` | If married or widow(er), enter spouse’s name: Spouse’s SSN: |
| `preparer.address` | preparer — address |
| `preparer.firm_name` | preparer — firm name |
| `preparer.name` | preparer — name |
| `preparer.phone` | preparer — phone |
| `preparer.ssn_or_ptin` | preparer — ssn or ptin |
| `signature` | signature |
| `today()` | today() (+1 more field) |
