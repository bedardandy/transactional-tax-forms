# Integrating: the canonical fact object

Every fill in this repo goes through one boundary: a form's `mapping.json`
maps each fillable widget to a **canonical fact-key**, and the engine
(`engine/fill_via_mapping.py`, or the MCP `fill_form` tool) resolves those
keys against a **canonical fact object** — a plain nested JSON dict your host
system (intake form, docassemble interview, agent, …) builds per matter.

```bash
python3 -m engine.fill_via_mapping --form IRS-SS-4 --case case.json --out out/
```

## Resolution semantics

- A key like `entity.legal_name` walks the object: `case["entity"]["legal_name"]`.
- `today()` is computed at fill time (mm/dd/yyyy); never supply it.
- Values may be strings or numbers; ISO dates (`2025-01-15`) are rendered the
  way the forms expect (`01/15/2025`).
- `first_name` / `middle_name` / `last_name` are derived from a role's
  `full_name` when not supplied explicitly, so `full_name` alone covers
  split-name boxes.
- Checkbox-mapped keys are checked only on an affirmative token
  (`yes`/`true`/`x`/`1`); any other value leaves the box unchecked.
- Unresolved keys are reported in the result (`unresolved`), not fabricated.

## Two key models (for now)

Read each form's `mapping.json` for the exact keys it consumes; every mapped
form also ships an `examples/sample_case.json` that exercises all of them.

**Tax-native roles** — the vision-mapped/opus-adjudicated tier
(`IRS-*`, `ME-RETTD`), the direct-mapped `MRS-700SOV`, and facts-only forms
(`MRS-900ME`):

| role | attributes seen in shipped mappings |
|---|---|
| `entity` | `legal_name`, `trade_name`, `ein`, `mailing_address`, `mailing_city`, `mailing_state`, `mailing_zip`, `street_address`, `county`, `state_of_formation`, `formation_date`, `phone` |
| `responsible_party` | `name`, `ssn_itin_ein`, `title` |
| `decedent` | `name`, `ssn`, `date_of_death`, `domicile_county`, `domicile_state`, `address` |
| `executor` / `fiduciary` | `name`, `address`, `ssn_or_ein`, `phone` |
| `estate` / `trust` | `name`, `ein`, `date_created` |
| `transferor` / `transferee` | `name`, `address`, `mailing_address`, `mailing_city`, `mailing_state`, `mailing_zip`, `ssn_or_ein` |
| `property` | `address`, `town`, `county`, `map_block_lot`, `purchase_price`, `transfer_date`, `type` |
| `facts.<snake_case>` | the form's labeled line items (amounts, elections, counts) |
| `signature`, `today()` | signature line; computed date |

**Court-shaped roles** — the five Maine Revenue mappings inherited from
[`maine-court-forms`](https://github.com/bedardandy/maine-court-forms)
(`MRS-706ME`, `MRS-1120ME`, `MRS-941ME`, `MRS-W4ME`, and — for its carried
fiduciary fields — `MRS-1041ME`). These predate the tax-native roles and name parties by
litigation role; migrating them is a roadmap item:

| key | shape |
|---|---|
| `parties.<role>` | `full_name`, `first_name`, `middle_name`, `last_name`, `address`, `city`, `state`, `zip`, `phone`, `email` — roles seen: `plaintiff`, `attorney` (what each role means per form is in that form's `SKILL.md` / `examples/README.md`; e.g. on MRS-706ME `parties.plaintiff` is the decedent) |
| `party` | the single filing party (same attributes, plus `signature`) |
| `facts.<snake_case>` | the form's labeled line items |

## Minimal example (tax-native)

```json
{
  "entity": {"legal_name": "Example LLC", "ein": "00-0000000",
              "mailing_address": "123 Main St", "mailing_city": "Portland",
              "mailing_state": "ME", "mailing_zip": "04101"},
  "responsible_party": {"name": "Riley J. Example", "ssn_itin_ein": "000-00-0000"},
  "facts": {"number_of_llc_members": "1"}
}
```
