# uk_ifs harvest notes — 2026-08-02

268 staged claims from 16 manifested artifacts. All rows source_model **ifs_taxben**
(research-institute lane), calibration_relationship held_out, values verbatim
(normalizations declared per row). GBP via `proposed_unit: gbp` / `gbp_per_year`;
UK fiscal years staged as `time_basis: fiscal_year`, `period` = start year,
`conditions.fy` label ("2029-30").

## Access recipe (documented for re-harvest)
- ifs.org.uk Drupal **page routes are Cloudflare-403** ("Just a moment") for curl AND
  WebFetch — challenge pages kept as evidence (doc_type blocked_403_challenge_html).
  robots.txt itself is permissive (standard Drupal disallows only /core/, /admin/ etc.).
- **Unlock: static `/sites/default/files/...` paths serve 200 to plain curl with honest
  UA** (TPC-style). PDFs and data xlsx all came from there, live.
- Page HTML (to discover file URLs + provenance): **Wayback snapshots** (availability
  API → snapshot; `id_` suffix for original bytes). No bot-mitigation bypassed.
- **IFS charts are Flourish embeds**: `public.flourish.studio/visualisation/<id>/embed`
  carries the full data JSON (`_Flourish_data`) + settings (title, £ prefix, axis
  titles, footer note). This is how the Budget 2025 decile chart was captured
  numerically. Data-item pages name the viz id. Recipe generalizes to every IFS
  data-item.
- Drupal `/media/<id>/download` routes (Taxlab spreadsheets) are 403 live and mostly
  NOT in Wayback → the one-click browser follow-up list.
- Old `output_url_files/` paths (pre-migration) 404 live; Wayback has original bytes.

## What was staged
1. **Budget 2025 decile chart** (22 rows, `avg_change_household_net_income`,
   gbp_per_year): 2026-27 and 2030-31, deciles Poorest..Richest + All, from Flourish
   viz 26495404. Scope note verbatim on every row — package includes two-child-limit
   scrapping, fuel duty freeze + 5p-cut-removal delay, three more years of threshold
   freezes, high-value council tax surcharge; EXCLUDES savings/dividend/property-income
   rises, salary-sacrifice reform, some energy reforms ("Including these would make the
   2030-31 picture more progressive"). **Excludes Scotland.**
   ⚠️ Income concept: x-axis is "Household income decile"; equivalisation and BHC/AHC
   are NOT stated in the captured chart or deck — flagged per row, do not assume until
   the underlying report states it.
2. **Green Budget 2025 Table 4.1** (28 revenue_change rows incl. deck £13bn): 27
   costed tax rises for 2029-30 (income tax, NICs, freezes, VAT, CT, capital, pensions,
   IHT, council tax [England only], fuel duty). "£6 billion" for abolishing the
   residence nil-rate band **visually verified** against rendered p.157.
   ⚠️ These are a MIX of sources (per table source line, carried verbatim in every
   row's `costing_basis`): HMRC Ready Reckoner projected to 2029-30 with OBR nominal
   GDP growth is the usual starting point; employer NICs + threshold-freeze rows
   combine HMRC estimates with TAXBEN; several rows from HMRC/OBR/MHCLG/Advani-Sturrock
   (per-row `row_source_note`). NOT pure TAXBEN, NOT administrative fact.
3. **Waters Budget-2025 deck claims** (5 rows): freeze extension £13bn by 2030-31
   (with verbatim uncertainty: ~25% chance >£21bn, ~25% <£8bn); freeze-as-a-whole
   taxpayer counts (5.2m into income tax, 4.8m into higher rate by 2030-31); two-child
   limit scrap £3.2bn cost 2029-30 + 560,000 families gaining (attribution flagged:
   may restate official costing — triangulation candidate).
4. **GB2024 Ch.6 Table 6.5** (109 rows): 12 child-poverty policy packages × {annual
   cost, 3 spending-share splits, child abs-poverty count & ppt reduction, cost per
   child lifted out, overall count & ppt} + the 23% simulated baseline rate.
   **Pure TAXBEN** ("Authors' calculations using Family Resources Survey 2022-23 and
   TAXBEN"). Steady-state at full two-child-limit rollout (staged period=2035 with
   explicit time_note — treat as counterfactual marker, not forecast year). NI
   excluded. Poverty reductions staged as NEGATIVE changes with printed magnitudes in
   value_raw. Headliner: remove two-child limit = £2,450m, −540k children (−4ppt),
   £4,510/child.
5. **GB2024 Fig 6.1 workbook** (104 rows, poverty_rate levels): child poverty
   1997-98..2022-23 × {relative, absolute} × {AHC, BHC}, full float precision from
   xlsx. Equivalisation/thresholds verbatim in every row (modified OECD; rel = 60%
   contemporaneous median; abs = 60% of 2010-11 median; ≤2003-04 excludes NI).
   ⚠️ These are FRS/HBAI-consistent calculations, NOT TAXBEN simulations — flagged
   per row; likely overlap DWP HBAI series → dedup vs uk_dwp at ingest.

## TAXBEN assumptions registry (#10) — verbatim from the 2021 guide
(TAXBEN_Guide_2021.pdf, sha256 b19a90c7…, retrieved via Wayback; full text in
downloads/TAXBEN_Guide_2021.txt. Quotes exact.)
- Static default: "TAXBEN calculates what the impact of policy reforms would be on
  households' finances if those households did not change their behaviour in response."
- Take-up: "TAXBEN analysis is usually done on an 'entitlements basis' — that is, we
  measure what net incomes would be if individuals claimed all the benefits that they
  are entitled to." (vs 'reported take-up basis' option; entitlements basis will
  "overstate … the impact of benefit reforms on actual incomes".)
- Taxes: "we analyse taxes on a 'liabilities basis' — we calculate what net incomes
  would be on the assumption that individuals do not evade tax."
- Incidence: "In TAXBEN analysis, we generally look at what would happen to incomes if
  all changes to taxes and benefits were fully incident on the directly affected
  households. This includes taxes such as VAT or employer National Insurance
  contributions."
- Top of the distribution: "tax reforms which only affect top earners cannot generally
  be modelled reliably using the survey data … Instead, for distributional analysis, we
  use the survey datasets … to estimate the frequency with which affected individuals
  appear in different deciles … We then use that frequency to break the official
  costing of the policy (before behavioural response, wherever that is available) into
  different deciles." ⚠️ IFS decile charts for top-end measures EMBED official costings.
- Disability & contributory benefits: "modell[ed] … on a reported take-up basis: only
  those who say that they claim are modelled as entitled."
- Scope: models income tax, NICs (employer and employee), council tax, VAT, most
  duties ("about three quarters of total government tax revenue" in 2017-18), almost
  all benefits/tax credits/state pensions. Does NOT model capital taxes (CGT, IHT,
  stamp duty), business taxes (corporation tax, business rates), or public services.
- Data: FRS (~20k households/yr, main source), LCFS (~5k, indirect taxes),
  Understanding Society/BHPS (panel). Systems since 1975 simulable.
- Aggregation: "into 'deciles', where we calculate the effect of reform on average
  incomes in the bottom 10% …" (deciles of household income; the guide does not state
  the equivalisation scale — GB2024 Fig 6.1 note separately confirms modified OECD for
  poverty analysis).
- Employer-NICs incidence in Budget-2025 deck (separate, verbatim slide note):
  "Assumes rise in employer NICs is incident on employees".
- Green Budget costings caveat (GB2025 Table 4.1 note): HMRC Ready Reckoner "typically
  incorporates the direct impact of a measure on the tax base to which it is being
  applied, or to closely related tax bases [but not] effects on other tax bases and
  wider economic factors"; most other sources "purely 'mechanical' estimates".

## Triangulation set (IFS vs OBR/HMT, same measures)
- **Two-child limit scrapping** — IFS deck: £3.2bn cost 2029-30, 560k families; IFS
  GB2024 steady state: £2,450m, −540k children. vs OBR Autumn Budget 2025 policy
  costing + HMT distributional analysis + DWP poverty estimate (deck cites "Gov't
  estimates … 450,000 / 3.1ppt" — NOT staged, it's the government's number).
- **Threshold freeze extension to April 2031** — IFS £13bn by 2030-31 (w/ uncertainty
  band) vs OBR's certified costing of the same measure. IFS £10.4bn (GB2025, freeze to
  April 2030, pre-Budget hypothetical) is a variant, not the enacted measure.
- **Fuel duty** — Budget package includes freeze + 5p-cut delay (in decile rows);
  GB2025 has 10% rise = £2.4bn hypothetical. vs OBR fuel-duty costings.
- **High value council tax surcharge** — in IFS decile package; OBR/HMT costed it.
- **Employer NICs / VAT / CT ready-reckoner rows** overlap HMRC's own Ready Reckoner
  (uk_hmrc lane) — expected NEAR-DUPES by construction (IFS projects HMRC numbers
  forward); adjudicate as vintage/projection differences, not model disagreement.
- **Fig 6.1 poverty levels** overlap DWP HBAI (uk_dwp) — same-microdata restatement.

## Gaps / follow-ups (one click each in a real browser)
- Taxlab **revenue composition spreadsheet** (/media/9899/download) + IFS Fiscal Facts
  parameter workbooks — Cloudflare-403, not in Wayback. P4 (mode-1 levels) therefore
  UNFILLED except via other lanes (OBR/HMRC cover the same levels with better
  provenance).
- **Indirect & capital taxes deck** downloaded but not staged (mostly charts; needs
  the same Flourish-id hunt via its data-items).
- GB2025 full report has more parsable tables (Ch.3 public finances; Ch.8 disability
  benefits) — full-report text is in downloads/ for a second pass.
- Two-child-limit standalone pieces ("The two-child limit: poverty, incentives and
  cost", Mar 2025 comment; 670k-children projection) — pages archived in Wayback,
  not yet pulled.
- IFS **data-items index** (ifs.org.uk/data-items) would enumerate every Flourish viz
  id → systematic numeric capture of all IFS budget/event charts. Needs browser or
  Wayback crawl.
- Autumn Budget 2025 decile chart: pin down equivalisation/BHC-AHC from the underlying
  IFS budget-analysis report when accessible.

## Parse confidence
High throughout: Flourish values machine-read from embed JSON; Table 4.1 from layout
text with one visual verification (RNRB £6bn); Table 6.5 all 12 rows column-checked
against prose restatements (540k/£4,510/£2.5bn long-run figure cross-consistent);
Fig 6.1 machine-read from xlsx at full float precision. No OCR anywhere.
