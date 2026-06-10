# MRS-706ME sample case — key shape

`sample_case.json` is a fictional Maine estate tax fact pattern. Every name,
SSN (`000-00-xxxx`), and dollar amount is a placeholder; replace all of them
with real case data before any actual use.

**Why the role keys look court-shaped.** This form's `mapping.json` was
inherited from the `maine-court-forms` library, whose canonical model names
parties by litigation role. The estate roles ride on those keys, so the keys
are unavoidable until the mapping is migrated to the tax-native roles:

| key in sample_case.json | who it is on Form 706ME |
|---|---|
| `parties.plaintiff` | the **decedent** (name, last domicile address) |
| `party` | the **personal representative** (and `party.signature` signs) |
| `parties.attorney` | the **authorized estate representative** (counsel/firm contact) |
| `facts.*` | the return's line items (estate values, tax, preparer block) |
| `matter.filing_date` | unused by this mapping; date lines come from `today()` |

First/middle/last name boxes are derived from each role's `full_name` by the
engine, so supplying `full_name` alone covers the split-name fields.
