# uk_dwp harvest notes — 2026-08-02

Target: DWP statistics on gov.uk. All fetches via gov.uk content API +
assets.publishing.service.gov.uk with honest UA
(`PolicyEngine-Scorecard-harvester/0.1 ... contact: max@maxghenis.com`).
No bot-mitigation encountered; no bypasses; Stat-Xplore NOT touched (auth-gated,
per instructions).

**2,054 staged claims** in `claims_staged.jsonl` (concatenated by
`validate_and_concat.py` from per-source files, all re-runnable):
- `claims_takeup.jsonl` — 805 rows (stage_takeup.py)
- `claims_becl.jsonl` — 204 rows (stage_becl.py)
- `claims_hbai.jsonl` — 992 rows (stage_hbai.py)
- `claims_hbai_prior.jsonl` — 48 rows (stage_hbai_prior.py)
- `claims_uc.jsonl` — 5 rows (stage_uc.py)

Validation (validate_and_concat.py, against scorecard_db/models.py): all rows
in closed vocab or proposed_*; conditions str->str; **zero duplicate claim
keys**; 48 suppressed rows (all FYE 2021 take-up, `[x]` in source, staged with
status=suppressed per the model contract).

## Conventions used (UK FLEET rules)
- **period = FY ENDING calendar year** (DWP "FYE 2024" = Apr 2023–Mar 2024 →
  period 2024), `time_basis=fiscal_year`, verbatim `conditions.fy`
  ("FYE 2024" for take-up, "2023/24" for BECL/HBAI, matching each source's own
  label). ⚠️ policyengine-uk-data maps FY to its STARTING year (FY 2025-26 →
  2025) — ingest must reconcile via conditions.fy, not period.
- **GBP**: `proposed_unit: "gbp"` (UnitConcept lacks it), values normalized to
  absolute GBP with per-row `conversion` (e.g. "£ million x 1e6"), `value_raw`
  verbatim. value_kind "gbp" (analogue of usd).
- Rates staged as shares (/100), unrounded where the source is unrounded
  (HBAI gives 12+ significant figures — ideal for exact comparison).
- Counts: thousands x 1000, millions x 1e6, documented per row.
- Geography verbatim: gb / uk / england_wales per the source's own coverage
  statements (see devolution below).

## (1) Income-related benefits: estimates of take-up — 805 rows
Editions staged: **FYE 2024** (latest, published 2025-10-30) full series
FYE 2010 + FYE 2013–FYE 2024; **FYE 2023** (prior, published 2024-10-10)
headline year only. `conditions.edition` distinguishes (cross-edition revision
checks; FYE 2023 central caseload take-up identical across editions = no
revision).
- Coverage (benefits × editions): **Pension Credit** (PC1–PC10) and **Housing
  Benefit for pensioners** (HB1–HB2) in BOTH editions. Income-related ESA/JSA:
  **not published in either edition** (discontinued from the series — FYE 2022
  restart covers PC + HB-pensioners only). So the benefits×editions matrix is
  2×2, complete.
- Structure per benefit: caseload table (recipients; entitled non-recipients;
  caseload take-up %) + expenditure table (amount claimed £m; amount unclaimed
  £m; expenditure take-up %). Central/lower/upper staged as separate rows,
  `conditions.bound`; both rates share metric=participation_rate with
  `conditions.takeup_basis: caseload|expenditure` (per task spec).
- PC breakdowns: entitlement_group (all / guarantee_credit /
  savings_credit_only) all years; family_type (PC3) and age_group (PC7)
  caseload take-up for FYE 2024 only.
- Units: caseload figures are thousands of benefit units → unit_concept
  families. Expenditure-basis take-up rows carry proposed_unit gbp (share of
  entitled money claimed).
- Metrics: participant_count, participation_gap_count (entitled
  non-recipients — in-vocab!), participation_rate; benefit_cost (amount
  claimed); proposed_metric **unclaimed_expenditure** (amount unclaimed, with
  bounds — the £ take-up gap; recurs 168x, worth a deliberate Metric
  extension).
- FYE 2021: suppressed `[x]` in source (COVID FRS), staged status=suppressed.
- calibration: PC rows = **seed_source** — policyengine-uk
  gov/dwp/pension_credit/takeup.yaml (0.7 from 2015) cites this publication
  series (verified this session). HB rows = held_out (PE-UK HB takeup is
  definitionally 1 — "no new claims"; DWP's measured HB-pensioner take-up
  ~85% is a genuine external comparator for that assumption).
- Not staged (available in artifacts): mean/median weekly amounts
  claimed/unclaimed (PC2/HB2), expenditure take-up by family type/age
  (PC4/6/8/10).

## (2) Benefit expenditure and caseload tables (BECL) — 204 rows
Artifact: Outturn and forecast tables, **Spring Forecast 2026** (published
2026-04-14; OBR Spring 2026 forecast-consistent). XLSX parsed cell-exact
(spot-verified 5 cells to full precision).
- Staged: FY 2019/20 → 2030/31 (outturn through 2024/25, forecast 2025/26+,
  designation read from the workbook's own header row →
  `conditions.basis: outturn|forecast`).
- Benefits: state_pension (exp + caseload), universal_credit (exp + household
  caseload), uc_and_equivalents (exp), pension_credit (exp + caseload), dla,
  pip, attendance_allowance (exp + caseload, total and in_payment),
  child_benefit (exp; BECL line is "Child Benefit, One Parent Benefit &
  Guardian's Allowance" — component condition records this), personal_tax_credits (exp).
  Child Benefit has **no caseload row** in BECL (expenditure only, Non-DWP
  Welfare sheet) — HMRC Child Benefit statistics are the caseload source
  (→ uk_hmrc lane).
- ⚠️ Devolution (verbatim from Notes tab): DLA/PIP/AA figures are
  **England & Wales only from FY 2020/21** (Scottish transfer 1 April 2020) —
  staged geography=england_wales for those years, gb for 2019/20, with
  per-row geography_note. All other benefits GB.
- ⚠️ Caseload semantics (verbatim Notes): "Caseload figures represent an
  average over the full financial year" — per-row time_note. Explains e.g.
  UC households 5.473M (FY 2024/25 average) vs 7.2M (Feb 2026 point-in-time
  from the UC release).
- calibration: staged held_out with a VERIFIED note — pe-uk-data
  targets/sources/obr.py consumes benefit expenditure and caseload forecasts
  from the OBR March 2026 EFO; BECL is OBR-consistent → likely
  consumed_as_target reclass at ingest for matching benefits.

## (3) HBAI headline poverty — 992 + 48 rows
Artifact: HBAI summary results ODS, FYE 2025 edition (published 2026-03-26).
- Staged: tables 1.3a/b (all individuals), 1.4a/b (children), 1.5a/b
  (working-age adults), 1.6a/b (pensioners): rates AND counts, full series
  FYE 1995–FYE 2025, relative & absolute × BHC & AHC (income_concept and
  poverty_measure MANDATORY conditions on every row). Rates unrounded
  percentages → shares; counts millions → persons. poverty_rate in-vocab;
  counts as proposed_metric **poverty_count** (496 rows — Metric extension
  candidate).
- equivalisation condition verbatim-grounded: FYE 2025 methodology report —
  "The main equivalence scales now used in HBAI are the modified OECD scales";
  AHC uses the OECD companion scale → equivalisation=modified_oecd /
  modified_oecd_companion_ahc.
- ⚠️ **Absolute line re-anchor** (Notes sheet Note 3, verbatim): from the
  2024/25 publication the absolute fixed reference year is **FYE 2025 for
  2021/22–2024/25**; years before 2021/22 remain anchored at **FYE 2011**;
  from summer 2026 DWP will re-anchor 2018/19–2020/21 too. Per-row
  `conditions.poverty_line_anchor: fye_2025|fye_2011`. (Consequence: absolute
  = relative exactly in FYE 2025, both 15.911572...% BHC.)
- ⚠️ **Break in series / admin-linkage** (sheet 1_3a header note): from
  2021/22 HBAI uses integrated survey + benefit admin data → those rows carry
  data_vintage=admin_linked_frs + series_note.
- **Cross-edition methodology divergence (diagnosis seed)**: prior edition
  (FYE 2024, published 2025-03-27, survey-only) staged for FYE 2022–2024
  rates (48 rows, edition=fye_2024, data_vintage=survey_frs). Same year, same
  measure, same publisher: all-individuals BHC relative FYE 2024 = **17.23%
  (survey-only) vs 15.18% (admin-linked restatement)** — a ~2pp
  methodology-not-policy gap; the direct UK analogue of a vintage diagnosis.
  populace-UK is FRS-based, so which vintage PE matches is itself diagnostic.
- Geography: FRS (GB) for FYE 1995–2002, FRS (UK) from FYE 2003 (col-0 series
  markers) → geography per row.
- calibration: held_out with note — HBAI and PE-UK share FRS microdata;
  agreement is same-input replication, not independent validation.
- Headline spot-checks vs main report HTML: individuals BHC FYE 2025 16%
  (report) vs 15.91% staged (unrounded) ✓; child AHC relative 27.4%,
  pensioner AHC 13.9%.
- Not staged (in artifacts): material deprivation & combined low-income tables
  (1.4c–h, 1.5c–h, 1.6c), disability splits (1.7a–h), Gini/quintile medians
  (1.2b), full data-tables zip (not downloaded; summary ODS suffices for
  headlines).

## (4) UC statistics — 5 rows
Latest release: "Universal Credit quarterly statistics, 29 April 2013 to
12 February 2026" (published 2026-05-12). Detailed tables are on Stat-Xplore
(auth — not attempted). Headline counts staged verbatim from release text
(rounded 0.1M, conversion noted): households on UC Feb 2026 = 7.2M; households
with payment = 6.7M (93%); people on UC Feb 2026 = 8.3M, Feb 2025 = 7.5M;
people on UC in employment Jan 2026 = 3.1M. GB. point_in_time with
conditions.month. Households series produced three months in arrears; recent
months provisional.

## Proposed vocabulary (recurring, for the deliberate-extension worklist)
- proposed_unit **gbp** (500 rows) — per UK FLEET convention.
- proposed_metric **poverty_count** (496) — level counts (Metric has only
  poverty_count_change).
- proposed_metric **unclaimed_expenditure** (168) — take-up gap in money.
- Conditions vocab introduced: bound (central|lower|upper), takeup_basis
  (caseload|expenditure), edition, entitlement_group, family_type, age_group,
  basis (outturn|forecast), fy, income_concept (bhc|ahc), poverty_measure,
  poverty_line_anchor, equivalisation, data_vintage, subgroup, component,
  month.

## Blockers / follow-ups
- Stat-Xplore: households-on-UC by month/region/family-type tables need the
  guest/auth API — not attempted per instructions. Release-text headlines
  staged instead.
- HBAI full data-tables zip (69MB-ish, directional/regional detail) not
  pulled — summary ODS covers all headline needs.
- Income-related ESA/JSA take-up: genuinely not published anymore (not a
  fetch failure).
- BECL prior vintage (Autumn/2025 edition) not staged — Spring 2026 is the
  current baseline analogue; add if forecast-vintage comparisons wanted.
- Pension Credit weekly amounts + take-up by marital/tenure axes available in
  artifacts, unstaged (time box).
- period-int convention clash with pe-uk-data (ending vs starting year) —
  resolve once at ingest via conditions.fy.
