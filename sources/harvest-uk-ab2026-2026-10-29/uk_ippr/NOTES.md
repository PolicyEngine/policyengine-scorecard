# uk_ippr: IPPR, Autumn Budget 2026

In this family we stage IPPR's three responses to the Budget on 28 October 2026, which we found on the ippr.org media-office listing:

- "‘Unfinished business’ on economic reform after sound Budget, says IPPR";
- "IPPR North reacts to Andy Burnham’s first Budget";
- "IPPR Scotland reacts to Andy Burnham's first Budget".

IPPR lists nothing on 29 October. We use the source slug `ippr`, as in the AB2025 `uk_ippr` family.

We keep `stage.py`, the file these notes mean wherever they say `stage.py`, on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-a/uk_ippr/stage.py`. This branch adds only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The lane never committed its local primaries folder (`.ab2026-primaries/uk_ippr/`), and we commit no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

We wrote the rows into `stage.py` as data, and it rewrites `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. `stage.py --verify` checks each primary's sha256 and finds every quote in its page's text; it reports 0 problems.

- Rows: 3 (restated 2, own 1).
- Primaries: 3.

## How we fetched the releases

- We fetched the media-office listing (https://www.ippr.org/media-office, pages 1 and 2) on 2026-10-29 to find the responses. IPPR's `/news-and-media` returns 404, and its `/articles` lists no Budget piece.
- We fetched all three releases directly (`curl -sSL`, browser User-Agent, HTTP 200): "Unfinished business" at 16:17Z and the North and Scotland releases at 16:35Z.
- We read each page's JSON-LD `dateModified` as a render time, not an edit. On 29 October each page showed a `dateModified` that day (16:04Z, 16:21Z, 16:34Z), after its 28 October `datePublished`. Review B's fetches on 4 November show 14:39–14:46Z that day with byte-identical length. Two fetches of the same page 30 minutes apart differ only in that field and Cloudflare's email tokens. So IPPR's server stamps the field when it serves the page, and we found no sign of an edit after publication. We hashed the copies from the fetches above and took nothing from a local copy.

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
   - We stage it as `cpi_inflation_effect`, 0.2, `range_low`, with `sign_convention: "as worded: positive = reduction in CPI inflation"`. IPPR prints the magnitude unsigned, README rule 10 keeps the producer's sign, and "at least" makes it a lower bound; we made this change on 4 November, after review B finding 1. We stage it as context, with no proposed key, because IPPR's words do not define the scope; we made that change on 3 November, after thinktanks-a review finding 1.
   - IPPR names no source and no period. In the EFO's paragraph 3.10, the OBR says the fuel duty changes and the temporary VAT cut on domestic electricity (Table 6.1 lines 2 and 3) "reduce CPI inflation by 0.22 percentage points in the second quarter of 2027". We therefore mark the row `restated`, with `parse_confidence: medium`, at `period` 2027 (`point_in_time`).
2. **"the £18 billion annual taxpayer losses at the Bank of England"** (Carsten Jung).
   - We stage it as `apf_indemnity_losses`, the AB2025 uk_ippr proposal, under which we staged IPPR's "£22 billion" the same way. We mark it `restated`, source not stated.
   - Jung gives no year, so we put it at the scoring year 2026-27 with a `year_note`. We stage it as context with no measure key.
3. **"Five per cent of income tax devolved to mayors would see an additional £4billion"** (IPPR North).
   - IPPR North estimates, on its own account, an option beyond the Budget's commitment on income tax devolution. We propose the key `ab2026_option__income_tax_5pc_share_devolved_to_mayors` and the metric `devolved_revenue` (gbp).
   - IPPR North gives no year, so we put it at the scoring year with a `year_note`. The release links the paper "Devolution that delivers: Fiscal power for regional growth".

## Proposed keys and their scope

- **`ab2026_option__income_tax_5pc_share_devolved_to_mayors`:** "Five per cent of income tax devolved to mayors". HM Treasury prints no Table 6.1 line for it. The Budget made commitments "on devolving business rates and a share of income tax to England's mayors" (line 21 covers the business rates share) without setting a 5% share.

## Not staged, and why

- We left out design, not estimates, under README rule 8, which treats spending allocations, financing remits and payment amounts as a measure's design:
  - IPPR North's "£285million of good growth funds" restates HM Treasury's allocation ("£285 million in 2027-28, comprising £165 million to support places with a mayor … to establish Good Growth Funds and £120 million of incubator capital funding for areas transitioning towards a devolution deal"). HM Treasury makes it a spending allocation and costs it within Table 6.1 line 20, whose costing (−£340m in 2027-28) also includes the subsidy on the £1.5bn finance. In the reworked uk_hmt_redbook family we don't stage HM Treasury's £285m either (rule 8).
  - IPPR North's "£1.5billion borrowing facilities for building infrastructure" gives the size of HM Treasury's lending facility for Mayoral Strategic Authorities, a financing remit. In the reworked uk_hmt_redbook family we stage no `policy_parameter` row and leave it out there too.
  - IPPR Scotland's "Bill support of £100 for households in lower council tax bands" gives the Household Energy Payment's amount.
- IPPR Scotland prints no other number, so we stage 0 rows from it; we manifest it for the tally.
- We left out IPPR's pre-Budget releases about this Budget, which fall outside the assigned "responses of 28–29 October". We fetched and hashed each on 2026-10-29, and each could seed a follow-up if the family should include pre-Budget options, as AB2025's did:
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
  We didn't fetch the papers behind them: "Cost of living, economic growth and stability: How to make this autumn budget a success", "Bricks vs clicks", "Devolution that delivers" and "Beyond headroom".

## Review fixes, 3 November 2026

The thinktanks-a reviewer (`harvest-staging/ab2026/reviews/verify-thinktanks-a.md` on the staging branch) approved this family with one fix, which we applied in an explicit block at the end of `stage.py`'s rows:

- Finding 1: we made row 0 (−0.2pp CPI) context. Jung says only "The cost of living support announced today", and Quilter-Pinner "action to support families with the cost of living". We had taken the lines 2 and 3 scope by matching the OBR's paragraph 3.10, our own inference, and README rule 3 requires the producer's scope. So we withdrew the proposed key `ab2026__package_cost_of_living_support`, kept the reform hint and note, and set `value_kind` to `range_high`.
- We re-opened no primary, because the session's network policy refused ippr.org. The contract checker reports 3 rows, 0 problems, and when we re-run `stage.py` it reproduces both files byte for byte.

## Review fixes, 4 November 2026

Review B (PR #231, issue comment 6635498758) approved this family with fixes, and review A's K-7(f) asked for the same NOTES correction as its second item. We re-opened no primary in this session.

- Finding 1, where the coordinator chose to take the fix: we now store 0.2, `range_low`, `sign_convention: "as worded: positive = reduction in CPI inflation"` on row 0, as the OBR and red book CPI rows keep the magnitude (`uk_obr_tables` row 2653).
- Finding 2 and K-7(f): under "Not staged" we no longer say that the red book family stages HM Treasury's £285m or the £1.5bn as `policy_parameter`; in the reworked red book family we stage neither. In the section on how we fetched the releases, we now read JSON-LD `dateModified` as a render time, not an edit.
