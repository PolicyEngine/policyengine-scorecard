# uk_ippr: IPPR, Autumn Budget 2026

This family stages IPPR's three responses to the Budget on 28 October 2026, found on the ippr.org media-office listing:

- "‘Unfinished business’ on economic reform after sound Budget, says IPPR";
- "IPPR North reacts to Andy Burnham’s first Budget";
- "IPPR Scotland reacts to Andy Burnham's first Budget".

The listing shows nothing on 29 October. The source slug is `ippr`, as in the AB2025 `uk_ippr` family.

**Working files.** `stage.py`, the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-a/uk_ippr/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The lane's local primaries folder (`.ab2026-primaries/uk_ippr/`) was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

`stage.py` holds the rows as data and rewrites `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. `stage.py --verify` checks each primary's sha256 and finds every quote in its page's text. Result: 0 problems.

- **Rows:** 3 (restated 2, own 1).
- **Primaries:** 3.

## Access recipe

- **The listing:** the media-office listing (https://www.ippr.org/media-office, pages 1 and 2) was fetched on 2026-10-29 to find the responses. `/news-and-media` returns 404, and `/articles` lists no Budget piece.
- **The releases:** all three were fetched directly (`curl -sSL`, browser User-Agent, HTTP 200), "Unfinished business" at 16:17Z and the North and Scotland releases at 16:35Z.
- **`dateModified` is a render time, not an edit:** each page's JSON-LD showed a `dateModified` on 29 October (16:04Z, 16:21Z, 16:34Z), after its 28 October `datePublished`. Review B's fetches on 4 November show 14:39–14:46Z that day with byte-identical length, and two fetches of the same page 30 minutes apart differ only in that field and Cloudflare's email tokens. So the field records when the page was served, and no edit after publication is shown. The copies hashed are the fetches above. Nothing came from a local copy.

## Rows by primary and measure key

| primary | sha256 | rows |
|---|---|--:|
| ‘Unfinished business’ … says IPPR | `f834beaad7802472…` | 2 |
| IPPR North reacts … | `9b1e6ee72f3af251…` | 1 |
| IPPR Scotland reacts … | `9f328d542179e8f8…` | 0 |

| measure_key | rows |
|---|--:|
| `null` (1 with a proposed key, 2 context) | 3 |

## The three rows

1. **"It will lower inflation by at least 0.2 percentage points"** (Carsten Jung, on "the cost of living support announced today").
   - Staged as `cpi_inflation_effect`, 0.2, `range_low`, with `sign_convention: "as worded: positive = reduction in CPI inflation"`: IPPR prints the magnitude unsigned, README rule 10 keeps the producer's sign, and "at least" makes it a lower bound (changed on 4 November, review B finding 1). Context, with no proposed key: IPPR's words do not define the scope (changed on 3 November, thinktanks-a review finding 1).
   - IPPR names no source and no period. The OBR's EFO paragraph 3.10 says the fuel duty changes and the temporary VAT cut on domestic electricity (Table 6.1 lines 2 and 3) "reduce CPI inflation by 0.22 percentage points in the second quarter of 2027". So the row is `restated` with `parse_confidence: medium`, at `period` 2027 (`point_in_time`).
2. **"the £18 billion annual taxpayer losses at the Bank of England"** (Carsten Jung).
   - Staged as `apf_indemnity_losses`, the AB2025 uk_ippr proposal, which staged IPPR's "£22 billion" the same way. `restated`, source not stated.
   - It has no year, so it sits at the scoring year 2026-27 with a `year_note`. This is context with no measure key.
3. **"Five per cent of income tax devolved to mayors would see an additional £4billion"** (IPPR North).
   - IPPR North's own estimate of an option beyond the Budget's commitment on income tax devolution. Proposed key `ab2026_option__income_tax_5pc_share_devolved_to_mayors`, proposed metric `devolved_revenue` (gbp).
   - It has no year, so it sits at the scoring year with a `year_note`. The release links the paper "Devolution that delivers: Fiscal power for regional growth".

## Proposed keys and their scope

- **`ab2026_option__income_tax_5pc_share_devolved_to_mayors`:** "Five per cent of income tax devolved to mayors". No Table 6.1 line. The Budget made commitments "on devolving business rates and a share of income tax to England's mayors" (line 21 covers the business rates share) without setting a 5% share.

## Not staged, and why

- **Design, not estimates** (README rule 8: spending allocations, financing remits and payment amounts are a measure's design):
  - IPPR North's "£285million of good growth funds" is HM Treasury's allocation ("£285 million in 2027-28, comprising £165 million to support places with a mayor … to establish Good Growth Funds and £120 million of incubator capital funding for areas transitioning towards a devolution deal"), restated. It is a spending allocation, and part of Table 6.1 line 20, whose costing (−£340m in 2027-28) also includes the subsidy on the £1.5bn finance. The reworked uk_hmt_redbook family does not stage HM Treasury's £285m either (rule 8).
  - IPPR North's "£1.5billion borrowing facilities for building infrastructure" is the size of HM Treasury's lending facility for Mayoral Strategic Authorities, a financing remit; the reworked uk_hmt_redbook family stages no `policy_parameter` row and does not stage it either.
  - IPPR Scotland's "Bill support of £100 for households in lower council tax bands" is the Household Energy Payment's amount.
- **IPPR Scotland** prints no other number, so it gives 0 rows; it is manifested for the tally.
- **Pre-Budget IPPR releases about this Budget,** outside the assigned "responses of 28–29 October". Each was fetched and hashed on 2026-10-29, and each is a candidate for a follow-up if the family is to include pre-Budget options, as AB2025's did:
  - 27 October, "Chancellor’s £20bn to invest would cost less than £1 billion in headroom: IPPR analysis" (sha256 `e26f9b14989f14af…`): £20bn of NWF and BBB investment costing under £1bn in debt interest and running costs in 2029-30.
  - 15 October, "Get started with tax reform to pay for priorities…" (sha256 `97750268ba93a3b6…`):
    - a £16bn package: CGT reform about £10bn, deferring Bank of England losses £5bn, a bank windfall surcharge £1bn;
    - headroom down £7-15bn, and a buffer above £20bn;
    - an online sales tax raising £1.5bn;
    - a £2,000 energy price ceiling;
    - the £200 a month LHA shortfall.
    The Budget's bank surcharge and the gambling and online-retail measures overlap these options.
  - 8 October, "Tax online sales to fund a high street business rate cut" (sha256 `fa570119927dcc54…`):
    - at least £1.5bn a year from a 2% online sales tax;
    - average savings of £1,400 and £2,500;
    - multipliers cut from 38.2p and 43p to 28.2p and 41p;
    - property taxes at 10.5% of revenue against an OECD average of 5.1%;
    - business rates of £27.6bn.
  The papers behind them were not fetched: "Cost of living, economic growth and stability: How to make this autumn budget a success", "Bricks vs clicks", "Devolution that delivers" and "Beyond headroom".

## Review fixes, 3 November 2026

The thinktanks-a review (`harvest-staging/ab2026/reviews/verify-thinktanks-a.md` on the staging branch) approved this family with one fix, applied in an explicit block at the end of `stage.py`'s rows:

- **Finding 1:** row 0 (−0.2pp CPI) is context. Jung says only "The cost of living support announced today", and Quilter-Pinner "action to support families with the cost of living". The lines 2 and 3 scope came from matching the OBR's paragraph 3.10, which is our inference, and README rule 3 says the scope must be the producer's. So the proposed key `ab2026__package_cost_of_living_support` is withdrawn, the reform hint and note stay, and `value_kind` is `range_high`.
- **Verification:** no primary was re-opened (the session's network policy refused ippr.org); the contract checker reports 3 rows, 0 problems, and a re-run of `stage.py` reproduces both files byte for byte.

## Review fixes, 4 November 2026

Review B (PR #231, issue comment 6635498758) approved this family with fixes; review A's K-7(f) asked for the same NOTES correction as its second item. This session re-opened no primary.

- **Finding 1 (coordinator's call: take the fix):** row 0 stores 0.2, `range_low`, `sign_convention: "as worded: positive = reduction in CPI inflation"`, as the OBR and red book CPI rows keep the magnitude (`uk_obr_tables` row 2653).
- **Finding 2 and K-7(f):** "Not staged" no longer says the red book stages HM Treasury's £285m or the £1.5bn as `policy_parameter`; the reworked red book stages neither. The access recipe reads JSON-LD `dateModified` as a render time, not an edit.
