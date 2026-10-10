# rulespec-uk as a source of 2010–2025 UK policy rules (issue #156, track 2)

Read-only scoping by a research worker, 2026-10-09.

**What was read**

- `TheAxiomFoundation/rulespec-uk` at `1c1101c` (2026-10-06), cloned at `/tmp/uk-replay-scope/rulespec-uk`. This is the main subject.
- `axiom-rules-engine` at `e8497a4`, `axiom-oracles` at `6092906` and `axiom-mappings` at `348e65c`. All three are shallow clones under `/tmp/uk-replay-scope/`.
- `policyengine.py` at `393762b`, already cloned.
- `policyengine-uk` **2.124.0**, the copy installed in `/tmp/uk-replay-scope/venv`. I used it only as the comparison baseline. Its parameter files were loaded raw with `policyengine_core.parameters.load_parameter_file`. I did not look at whether the model backdates values at run time.

Counts come from scripts in `/tmp/uk-replay-scope/agents/rulespec_uk_work/`:

- `extract.py` writes `rules.json`, one row per rule.
- `areas.py` writes `areas.json`, the per-area statistics.
- `diff_pe.py` writes `diff_pe.json`, the differential against PolicyEngine UK.
- `pe_hist.py` and `pe_hist2.py` print PolicyEngine UK parameter histories.

## Bottom line

1. **Every UK fiscal rule has exactly one version.** In the national `uk/` jurisdiction there are 1,491 rules:
   - 1,474 rules have one version.
   - 11 have none: they are relation rules (`data_relation` / `source_relation`).
   - 6 have two versions. None of those six is in a 2010–2022 policy area: Class 3 NIC goes 2025-04-06 → 2026-04-06, three Companies Act small-company thresholds, two UK GDPR penalty caps.

   So rulespec-uk has **no year-by-year history** for any tax or benefit parameter. Source: `rules.json` from `extract.py`.
2. **`effective_from` is not a vintage date.** Of the 600 parameter rules in `uk/`:
   - 250 carry the sentinel `'0001-01-01'`. A sentinel version answers every year, including 2010–2025, with today's value.
   - Others carry the date the parent instrument came into force, while the value is the 2026-27 one.
   - Others carry the date the current value took effect.

   There are concrete mis-datings, for example 2026-27 dividend rates dated 2024-04-06 and 2023 benefit-cap amounts dated 2013-04-29 (§1.4). The repo's own open issues #382, #351 and #423 describe the same problem.
3. **Retired schemes are essentially absent:**
   - Tax credits: only element-amount tables at 2024-04-06.
   - Income Support and income-based JSA: only capital tariff-income.
   - Additional State Pension: none.
   - Council Tax Benefit: none.
   - The two-child limit: not encoded, because it was revoked in 2026.
4. **There is no bridge that feeds rulespec-uk into policyengine-uk or policyengine.py.**
   - `axiom-oracles` compares the two engines. All 37 UK comparison suites run at **2026** only, and every one is `ci: manual`.
   - `axiom-mappings` has US data only.
   - `policyengine.py` runs Axiom only for Belgium.
5. **Verdict:** rulespec-uk cannot supply 2010–2022 parameter values that policyengine-uk lacks.
   - The installed policyengine-uk holds more history for **71 of the 74** parameters the oracle bridge maps between the two (§4).
   - The only places rulespec-uk reaches earlier than PolicyEngine UK's raw files are:
     - the 2% additional rates for Class 1 and Class 4 NIC, dated 2011-04-06;
     - the £500 Sure Start Maternity Grant, dated 2005-12-05;
     - the explicit £1,060 marriage-allowance transfer for 2015-16.

   Some structural formulas could serve as a reading aid, but they encode current law (§5).

---

## 1. Repository structure and the RuleSpec format

### 1.1 Layout (counted)

- `README.md:3-16` describes the repo: one UK country monorepo with jurisdiction roots (`uk/` and `uk-<council>/`). Atomic `rulespec/v1` modules sit under `{legislation,policies,regulations,statutes}/`, with ProgramSpecs under `<jurisdiction>/programs/`. Durable ids take the form `<jurisdiction>:<path>#<rule>`.
- The allowed roots are listed in `.axiom/repository-structure.yaml`: `uk` plus about 300 `uk-*` council roots. 100 `uk-*` directories exist in the clone.
- **`uk/` holds 641 YAML files** (counted with `find`):
  - 320 module files. 301 contain at least one rule; 19 have `rules: []`.
  - 320 companion `.test.yaml` files.
  - 1 ProgramSpec, `uk/programs/universal-credit/fy-2026-27.yaml`.
- **Council roots:** 100 module files, all named `council-tax-reduction.yaml`, one per council. They hold 2,905 rules: 2,859 versions dated `2026-04-01` and 26 sentinels.
- Toolchain pin: `.axiom/toolchain.toml` pins corpus release `uk-rulespec-2026-09-07`.
- CI: `.github/workflows/repository-checks.yml:17-28` calls the shared `TheAxiomFoundation/.github` workflow `validate-rulespec.yml` with pinned `axiom-encode`, `axiom-rules-engine` and `axiom-corpus` refs.
- Source snapshots: `data/corpus/sources/...` holds legislation.gov.uk XML snapshots (118 files under `data/corpus`). For example, `.../ukpga/2007/3/section-8.xml` line 2 carries `<dct:valid>2026-04-06</dct:valid>`. The source text is the point-in-time version as of 2026, not a historical one.

### 1.2 A module

Example: `uk/statutes/ukpga/2007/3/35.yaml`, the personal allowance.

- `format: rulespec/v1` (line 1).
- A `module:` block (lines 2-8) holds `proof_validation`, `source_verification.corpus_citation_path` and a prose `summary`. Some modules also have `status: deferred` and `deferred_outputs` with reasons (44 files). Example: `uk/statutes/ukpga/2007/3/6.yaml:3-20` defers the basic, higher and additional rates because "values are delegated to annual Finance Acts".
- An optional `imports:` list (46 files).
- `rules:` is a list. Each rule has:
  - `name`;
  - `kind` (`parameter` | `derived` | `data_relation` | `source_relation`);
  - `dtype`, and optionally `unit`, `entity`, `period`, `source`, `indexed_by`;
  - `metadata.proof.atoms[]`, which ties each version field to a `corpus_citation_path` plus a verbatim `excerpt` (lines 15-22);
  - `versions:`.
- **The effective-date field is `effective_from`.** Each entry in `versions:` is `{effective_from: 'YYYY-MM-DD', formula: <expression>}`, or `values: {key: amount}` for an indexed table.
  - Engine docs: `axiom-rules-engine/docs/rulespec-format.md:57-59` says each version has "`effective_from`, an optional inclusive `effective_to`, and either a `formula` … or, for indexed parameters, a `values` table".
  - **`effective_to` occurs 0 times under `uk/`** (counted over the cached text).
  - Indexed example: `uk/regulations/uksi/2013/376/80A.yaml:42-48` gives `values: {0: 16967, 1: 25323, 2: 14753, 3: 22020}`.
- Parameters are literal formulas. For example, `35.yaml:23-26` is `effective_from: '0001-01-01'` with formula `12570`.
- Derived rules are expressions over other rules and over inputs. `35.yaml:150-153` is:

  ```
  if individual_entitled_to_personal_allowance: ceil(max(0, personal_allowance_base_amount - (excess_income_reduction_fraction * max(0, adjusted_net_income - adjusted_net_income_reduction_threshold))) / allowance_rounding_multiple) * allowance_rounding_multiple else: 0
  ```

  Names not defined in the module are case inputs. Tests address them as `…#input.<name>` (`35.test.yaml:7-9`).
- Relation rules: `uk/statutes/ukpga/2007/3/23.yaml:12-18` is a `data_relation` (`predicate`, `arity`, `arguments`).

### 1.3 Tests and programs

- **Companion tests** are lists of `{name, period, input, output}`. Example: `35.test.yaml:1-12` uses `period_kind: tax_year`, `start`/`end`.
- Test periods across the 320 `uk/` test files, 1,124 cases in total:

  | Start year | Cases |
  |---|---|
  | 0001 | 7 |
  | 2013 | 45 |
  | 2014 | 3 |
  | 2015 | 1 |
  | 2020 | 2 |
  | 2021 | 17 |
  | 2022 | 3 |
  | 2023 | 3 |
  | 2024 | 432 |
  | 2025 | 50 |
  | 2026 | 551 |
  | 2027 | 4 |
  | 2028 | 1 |
  | 2030 | 5 |

- 21 test files contain a pre-2023 case. Those cases assert the single current value; see §1.4.
- **ProgramSpec:** `uk/programs/universal-credit/fy-2026-27.yaml` covers one period only (`period: 2026-04`, line 12).

### 1.4 What `effective_from` means in practice

**Engine semantics**

- `axiom-rules-engine/docs/bitemporal.md:3-7` says the query `period` "selects whichever version is live for the period being calculated".
- A rule queried before its first `effective_from` errors rather than returning a value. `src/engine.rs:158-162` defines `MissingDerivedFormulaVersion`, raised at `src/engine.rs:777-782`. `docs/execution-semantics.md:173-174` says "A rule before its commencement date fails the rows that reach it".
- The oracle bridge picks "the latest version with `effective_from <= period_start`" (`axiom-oracles/axiom_oracles/bridges/efrs_uk.py:4004-4015`).
- **Consequence:**
  - A sentinel (`0001-01-01`) single version returns today's value for 2010.
  - A single version dated in 2024 errors for 2010–2023.
  - No rule in the files sampled here changes value between 2010 and 2025, apart from the company and GDPR exceptions noted above (see HISTORICAL_RULES.md for the qualified statement).

**Distribution over the 600 `uk/` parameter rules, by earliest version date**

| Earliest version date | Parameter rules |
|---|---|
| `0001-01-01` sentinel | 250 |
| before 2010 | 33 |
| 2010–2022 | 82 |
| 2023–2025 | 60 |
| 2026 | 175 |

Each of the 82 rules dated 2010–2022 has only that one version, and each is the current value. The list is in the `areas.py` output.

**Mis-dated values (evidence, not inference)**

- **Dividend rates.**
  - `uk/statutes/ukpga/2007/3/8.yaml:23,39,55,71` sets 0%, 10.75%, 35.75% and 39.35%, all `effective_from: '2024-04-06'`.
  - `8.test.yaml:9-16` asserts `dividend_ordinary_rate: 0.1075` for tax year **2024-04-06 → 2025-04-05**.
  - The source snapshot it cites, `section-8.xml` line 2, is `<dct:valid>2026-04-06`.
  - PolicyEngine UK `parameters/gov/hmrc/income_tax/rates/dividends.yaml:10-19` has 0.075 from 2015, **0.0875 from 2022-04-01** and 0.1075 from **2026-04-06**.
- **Benefit cap.**
  - `uk/regulations/uksi/2013/376/80A.yaml:42-48` gives £16,967 / £25,323 / £14,753 / £22,020 with `effective_from: '2013-04-29'`.
  - `80A.test.yaml:1-16` asserts £16,967 for **period 2013-05**.
  - PolicyEngine UK `parameters/gov/dwp/benefit_cap.yaml:5-39` has 2016-11-07 values of £15,410 / £13,400 / £23,000 / £20,000. The current amounts start only at 2023-04-01.
- **NIC additional rates.**
  - `uk/statutes/ukpga/1992/4/8.yaml:40` and `1992/4/15.yaml:76` set 2% from 2011-04-06, with no other version.
  - PolicyEngine UK raw values are 0.0325 (Class 1) and 0.035 (Class 4) from 2022-04-01 (`pe_hist.py` output).
  - rulespec-uk issue #423 (open) states the 2022-23 Class 4 rates were 9.73% / 2.73% under the Health and Social Care Levy (Repeal) Act 2022 s.2(2). It notes that this "modifies s.15 for the year without amending its text, so the point-in-time text never shows it". I have not checked which 2022-23 figure is right.
- **The repo's own issues.**
  - **#382** (open, 2026-09-30): sentinel-dated amounts "apply 2026-27 amounts to every earlier period", and rulespec-uk "has no 2025-26 DWP benefit rates".
  - **#351**: the reg 10 Class 1 limits are carried forward from 2026-27.
  - **#423**: "No limits before 2026-27 … A tax year before 2026-27 has no lower or upper profits limit."

---

## 2. Coverage by policy area

The figures below come from `areas.py`, which walks every `uk/` module and assigns it to an area by path.

- "Earliest" and "Latest" are the min and max non-sentinel `effective_from` over all rules in the area's files.
- "Sentinel" is the number of parameter rules dated `0001-01-01`.
- "Gaps": no parameter in any area has more than one version, apart from Class 3 NIC. So for every encoded area:
  - years **before** the earliest date have **no value**, and querying them errors;
  - years **after** it carry **one value**, today's;
  - sentinel rules carry today's value for every year.

  In practice, every year from 2010 to 2022 is either "no value" or "a 2026 value".

| Area | Module files (`uk/…`) | Params (sentinel) / derived | Earliest | Latest | Notes |
|---|---|---|---|---|---|
| **IT: personal allowance + taper** | `statutes/ukpga/2007/3/35.yaml`; `2021/26/5.yaml`; `2023/1/5.yaml` (+ `2026/11/10.yaml` source_relation) | 8 (4) / 3 | 2022-04-06 | 2026-04-06 | PA £12,570 is a sentinel in s.35. FA 2021 s.5 gives £12,570 / £37,700 from 2022-04-06. Taper £100k at ½ is a sentinel. |
| **IT: main bands and rates (rest of UK)** | `2007/3/10.yaml`, `2007/3/23.yaml`, `2026/11/1-3.yaml`, `statutes/income_tax/individual/pilot_worker_oracle_pipeline.yaml`. `2007/3/6.yaml` is deferred with `rules: []`. | 11 (0) / 24 | 2024-04-06 | 2026-04-06 | Rates 20 / 40 / 45% exist only for 2026-27 (FA 2026 s.2). BRL £37,700 is dated 2024-04-06. |
| **IT: Scottish** | `statutes/income_tax/individual/scottish_income_tax_oracle_pipeline.yaml`; `1998/46/80C.yaml` | 16 (3) / 17 | 2026-01-01 | 2026-01-01 | 2026-27 bands only: 19 / 20 / 21 / 42 / 45 / 48%. |
| **IT: savings and dividends** | `2007/3/8, 11D, 12, 12A, 12B, 13, 13A, 16.yaml`; `2026/11/9.yaml`; `savings_dividend_oracle_pipeline.yaml` | 29 (0) / 74 | 2024-04-06 | 2026-04-06 | 2026-27 values dated 2024 (§1.4). |
| **IT: age-related allowances, married couple's allowance** | none | — | — | — | Not encoded. MCA is mentioned only as an exclusion in `55B.yaml:15`. |
| **IT: marriage allowance** | `2007/3/55B.yaml` | 3 (0) / 3 | 2015-04-06 | 2016-04-06 | £1,060 for 2015-16; then 10% of PA rounded up to £10 from 2016-04-06. |
| **NIC Class 1 employee** | `1992/4/8.yaml`; `regulations/uksi/2001/1004/10.yaml`; `pilot_worker_class_1_nic_pipeline.yaml` | 8 (0) / 9 | 2011-04-06 | 2026-04-06 | Main 8% from 2024-04-06; additional 2% from 2011-04-06; LEL / PT / UEL / ST are 2026-27 only (reg 10: £129 / £242 / £967 / £96). |
| **NIC Class 1 employer** | `1992/4/9.yaml`; `pilot_worker_employer_secondary_nic_pipeline.yaml` | 3 (0) / 4 | 2025-04-06 | 2026-01-01 | 15% from 2025-04-06 only. |
| **NIC Class 2** | `1992/4/11.yaml` | 2 (0) / 3 | 2025-04-06 | 2025-04-06 | SPT £6,845, £3.50 a week. |
| **NIC Class 3** | `1992/4/13.yaml` | 1 (0) / 2 | 2025-04-06 | 2026-04-06 | The only multi-version tax parameter: £17.75 → £18.40. |
| **NIC Class 4** | `1992/4/15.yaml`; `uksi/2001/1004/100.yaml`; `pilot_worker_self_employed_nic_pipeline.yaml` | 8 (0) / 23 | 2011-04-06 | 2026-04-06 | LPL / UPL from 2026-04-06; 6% from 2024; 2% from 2011. |
| **Employment allowance** | none | — | — | — | Explicitly excluded (`pilot_worker_employer_secondary_nic_pipeline.yaml` summary, around line 24). |
| **Health and Social Care Levy** | none | — | — | — | Keyword search found no match. |
| **Tax credits (WTC, CTC)** | `regulations/uksi/2002/2005/schedule/2.yaml`; `2002/2007/7.yaml`; `2024/247/3.yaml` | 10 (0) / 4 | 2024-04-06 | 2024-04-06 | Element amounts only (§3). |
| **JSA** | `policies/govuk/contribution-based-jobseekers-allowance.yaml`; `uksi/1996/207/116.yaml` | 8 (1) / 6 | 1996-10-07 | 2026-04-06 | Capital tariff plus 2026-27 contribution-based rates. |
| **ESA** | `policies/esa_income_related_applicable_amount_pipeline.yaml`; `uksi/2008/794/118.yaml` | 12 (0) / 8 | 2008-10-27 | 2026-04-01 | Capital tariff plus a 2026-27 income-related pipeline. |
| **Income Support** | `uksi/1987/1967/53.yaml` | 5 (0) / 3 | 1988-04-11 | 1988-04-11 | Capital tariff only. |
| **Universal Credit** | `statutes/ukpga/2012/5/*.yaml` (excluding ss.77-79); `uksi/2013/376/**` (excluding regs 80A-82); `policies/universal_credit_composed_award_pipeline.yaml`; `universal_credit_award_reconciliation.yaml`; `programs/universal-credit/fy-2026-27.yaml` | 86 (41) / 269 across 79 files | 2013-04-29 | 2026-04-01 | Reg 36 amounts are sentinels (2026-27 values). Reg 24A, the two-child limit, is deferred (§3). |
| **Benefit cap** | `uksi/2013/376/80A.yaml`, `81.yaml`, `82.yaml` (also inside the UC pipeline) | 5 (3) / 11 | 2013-04-29 | 2013-04-29 | 2023 amounts dated 2013. |
| **Child Benefit** | `uksi/2006/965/2.yaml`; `statutes/ukpga/1992/4/141-143.yaml`; `statutes/child_benefit/pilot_child_benefit_oracle_pipeline.yaml` | 9 (5) / 23 | 2026-01-01 | 2026-01-01 | £27.05 / £17.90 are sentinels. |
| **HICBC** | `statutes/ukpga/2003/1/681B, 681D, 681E, 681G.yaml` (681H deferred); taper inside the CB pipeline | 2 (2) / 9 | none (sentinel only) | — | £60,000 is a sentinel (`681B.yaml:25`). The pipeline taper is 1% per £200, at 2026-01-01. |
| **State Pension** | `policies/govuk/state-pension.yaml`; `uksi/2026/148/article/4.yaml`, `article/6.yaml` | 5 (0) / 5 | 2010-04-06 | 2026-04-06 | 30-year basic SP rule from 2010-04-06; 35/10-year new SP rule from 2016-04-06; weekly rates are 2026-27 only (£184.90 / £241.30). No additional SP. |
| **Pension Credit** | `statutes/ukpga/2002/16/1-3.yaml`; `uksi/2002/1792/6.yaml`, `15.yaml`, `schedule/IIA.yaml`; `policies/govuk/pension-credit.yaml`; `policies/pension_credit_composed_award_pipeline.yaml` | 21 (9) / 35 | 2009-11-02 | 2026-04-06 | SMG £238.00 / £363.25 are sentinels. The deemed-income rule (£10k, £500 bands) is dated 2009-11-02. |
| **Housing Benefit** | `uksi/2006/213/52, 70, 71.yaml`; `uksi/2006/214/29, 50, 51.yaml`; `policies/housing_benefit_composed_entitlement_pipeline.yaml` | 33 (0) / 15 | 2006-03-06 | 2026-04-01 | 65% taper and capital rules dated 2006; personal allowances and non-dependant deductions 2026-27. **LHA is not encoded**: it is a supplied "maximum rent (LHA)" input (pipeline summary). |
| **Council tax, CTB, CTR** | CTR England: `uksi/2012/2885/**`, `uksi/2012/2886/**`, `policies/govuk/council-tax-reduction.yaml` (52 files). Scotland: `ssi/2012/319/**`, `ssi/2021/249/**` (17 files). Wales: `wsi/2013/3029/**` (15 files). Plus 100 `uk-<council>/…/council-tax-reduction.yaml`. | England 72 (67) / 100; Scotland 44 (28) / 49; Wales 53 (53) / 22 | England 2013-04-01; Scotland 2021-04-05; Wales none (sentinel only); councils 2026-04-01 | England 2013-04-01; Scotland 2026-01-01; councils 2026-04-01 | Council tax liability itself is not encoded. CTB is not encoded. |
| **Disability and carer benefits** | PIP: `uksi/2013/377/24.yaml`, `statutes/ukpga/2012/5/77-79.yaml`, `policies/govuk/personal-independence-payment.yaml`. DLA: `uksi/2026/148/article/14.yaml`, `policies/govuk/disability-living-allowance.yaml`. AA / SDA / CA rates: `uksi/2026/148/schedule/1.yaml`, `policies/attendance_allowance_composed_amount_pipeline.yaml`. CA: `policies/govuk/carers-allowance.yaml`. Scotland: `ssi/2023/302/5, 16.yaml`, `govuk/carer-support-payment.yaml`, `govuk/scottish-carer-supplement.yaml` | PIP 5 (1) / 12; DLA 6 (1) / 9; AA/SDA/CA 9 (0) / 2; CA 3 (2) / 3; Scotland 7 (2) / 5 | 2024-11-01 (CSP); otherwise 2026-04-06 | 2026-04-06 | 2026-27 rates only. |
| **VAT** | `statutes/ukpga/1994/23/2, 24, 25, 26, 29A.yaml`; `policies/govuk/vat.yaml` | 4 (0) / 8 | 1994-09-01 | 2011-01-04 | 20% from 2011-01-04 (`vat.yaml:34`); 5% from 2001-11-01 / 1994-09-01. No earlier standard rate. |
| **Fuel duty** | `statutes/ukpga/1979/5/6.yaml`; `policies/govuk/fuel-duty.yaml` | 5 (4) / 7 | 2011-03-23 | 2011-03-23 | Standing rate 57.95p. The temporary cut is a supplied input (`fuel-duty.yaml:7-21`). |
| **Alcohol and tobacco duties** | none | — | — | — | Not encoded. |
| **CGT** | `statutes/ukpga/1992/12/1H.yaml`, `1K.yaml`; `policies/govuk/capital-gains-tax.yaml` | 6 (3) / 12 | 2024-04-06 | 2025-04-06 | 18 / 24% and £3,000 AEA only. |
| **IHT** | none | — | — | — | Not encoded. |
| **SDLT** | none | — | — | — | Not encoded. |
| **LBTT** | `statutes/asp/2013/11/24.yaml`; `policies/govuk/lbtt.yaml` | 11 (2) / 7 | 2015-04-01 | 2024-12-05 | 2015 residential bands; ADS 8% only (2024-12-05). |
| **LTT** | `statutes/anaw/2017/1/24.yaml`; `policies/govuk/ltt.yaml` | 22 (3) / 7 | 2022-10-10 | 2024-12-11 | Main rates from 2022-10-10; higher rates from 2024-12-11. |

Other `uk/` content outside the areas above:

- Cost-of-living payments: `statutes/ukpga/2022/38/1, 5.yaml` (£326 + £324, £150) and `2023/7/1, 5.yaml` (£301 / £300 / £299, £150).
- Winter Fuel Payment: `uksi/2025/969/3.yaml`.
- Student loans, TV licence, NMW/NLW (`uksi/2015/621/4, 4A.yaml`, 2026-04-01 only).
- Tax-Free Childcare, SMP / SPP / MA pilots, SSMG, Healthy Start, Best Start Foods, Scottish Child Payment, Child Winter Heating.
- Pensions tax: `2004/12/190, 228, 228ZA.yaml`.
- Business-rates proxy, Companies Act s.382, UK GDPR s.157.

## 3. Retired schemes: what formulas exist

- **Tax credits.** Only element amounts exist, all at 2024-04-06:
  - WTC Sch 2 (`uksi/2002/2005/schedule/2.yaml:30-125`): £2,435 basic, £3,935 disabled, £1,015 30-hour, £2,500 second adult, £2,500 lone parent, £1,705 severely disabled. `wtc_worker_element_amount` is deferred.
  - CTC family element £545 (`uksi/2002/2007/7.yaml:25`).
  - The 2024 uprating of the child, disabled and severely disabled elements: £3,455 / £4,170 / £5,850 (`uksi/2024/247/3.yaml`).

  There is **no** Tax Credits Act 2002 entitlement formula, no income threshold or taper, no childcare element and no income rules. Keyword search for a 41% rate or a threshold returned 0 hits. Open issues confirm it: #51 "statute and main regs unencoded", #419 and #422 (tax credit income). **Completeness: very low.**
- **Legacy benefits.**
  - **Income Support:** capital tariff income only (`uksi/1987/1967/53.yaml`). Issue #52 is "Income support: only one regulation encoded"; #382 asks for IS and income-based JSA personal allowances.
  - **Income-based JSA:** capital tariff only (`uksi/1996/207/116.yaml`).
  - **Contribution-based JSA:** 2026-27 age-related amounts (£75.65 / £95.55) in `policies/govuk/contribution-based-jobseekers-allowance.yaml`.
  - **Income-related ESA:** a 2026-27 applicable-amount and award pipeline (`policies/esa_income_related_applicable_amount_pipeline.yaml`). It covers the Sch 4 personal allowance, support and WRA components, and SDP and carer premiums; housing costs are supplied. Plus the capital tariff (`uksi/2008/794/118.yaml`).
  - **Contributory ESA:** none.
- **Pre-2016 State Pension.** `policies/govuk/state-pension.yaml:102-131` computes basic SP as `category_a_basic_retirement_pension_weekly_rate * min(1, qualifying_years / 30)` for people who reached SPA before 2016-04-06.
  - The rate is 2026-27 only: £184.90 from SI 2026/148 art 4.
  - There is **no** additional State Pension (SERPS / S2P), no Category B or D, and no pre-2010 qualifying-year rule. Keyword search for "additional state pension|SERPS|S2P" returned 0 hits.
- **Council Tax Benefit (abolished in 2013).** Not encoded. The only reference is a CTR transitional helper, `applicant_treated_as_entitled_to_council_tax_benefit_for_relevant_period`, in `uksi/2012/2886/appendix/3/paragraph/4.yaml`. CTR (2013 onward) is encoded as current text; most parameters are sentinels.
- **Housing Benefit (still live for some claimants).** Encoded:
  - the 65% taper (`uksi/2006/214/51.yaml`);
  - maximum HB at 100% of eligible rent (`213/70.yaml`, `214/50.yaml`);
  - capital tariffs;
  - a 2026-27 pipeline.

  LHA is a supplied input. Issue #108 (pension-age applicable amount) is open.
- **UC two-child limit (2017–2026).** Not encoded.
  - `uksi/2013/376/24A.yaml` has `status: deferred` and its summary is elided text.
  - `policies/universal_credit_composed_award_pipeline.yaml:47-50` says the limit "is not applied: it was revoked from 6 April 2026".

## 4. Consumption and validation

**No bridge into policyengine-uk or policyengine.py**

- `policyengine.py`: the only Axiom-backed model is Belgium (`src/policyengine/tax_benefit_models/be/model.py:1-6`, "Unlike the US and UK model versions, Belgium runs on the Axiom rules engine"). A grep for `axiom|rulespec` under `src/policyengine/tax_benefit_models/uk*` returned nothing.
- `axiom-mappings`, "the shared map between Axiom RuleSpec concepts and PolicyEngine variables" (`README.md:3`), has data for `us/` only (`axiom_mappings/data/` = `taxonomy.yaml`, `us/`). Its `pins.yaml` pins only `policyengine_us` and `rulespec_us`.
- `PolicyEngine/policyengine-axiom`, named as a consumer in that README, did not resolve through `gh repo view`.

**axiom-oracles: comparison only, not data supply**

- The bridge is `axiom_oracles/bridges/efrs_uk.py` (7,438 lines) plus `bridges/mappings/uk.yaml`. The mapping has 304 rows: 133 `not_comparable`, 90 `parameter_value`, 79 `direct_variable`, 2 `derived_expression`.
- It runs policyengine-uk and the Axiom engine side by side and diffs their outputs. It does not write rulespec values into PolicyEngine UK.

**Which years are validated: 2026 only**

- There are 37 `comparisons/uk-*.yaml` suites, all at period or year **2026**. Examples:
  - `uk-tax-benefits-efrs.yaml:46-50`: `year: 2026`, `dataset: enhanced_frs_2023_24`, `policyengine_uk_version: 2.88.56`.
  - `uk-income-tax-dividend-ukmod.yaml:38-46`: period 2026-04-06, `euromod_system: UK_2026`.
  - `uk-vat.yaml:40`.
- **12 suites target PolicyEngine UK:** AA, business rates, CGT, CTR, fuel duty, LBTT/LTT, tax-benefits-efrs, TFC, TV licence, UC-efrs, VAT, WFP.
- **25 suites target UKMOD** (`euromod-synthetic-compare`).
- **All 37 are `ci: manual`.** `uk-tax-benefits-efrs.yaml:18-28` says that suite is "Not CI-runnable": the pinned Populace UK artifact is in a private Hugging Face repo, and the org token is broken.
- **No validation exists for any year 2010–2025.**
- `docs/uk-coverage-matrix.md` in axiom-oracles inventories an older rulespec-uk (HEAD `91cecab2`, "163 rule files"). It is a stale document, not mechanism evidence.

**Differential I ran: `diff_pe.py`**

It compared all 90 `parameter_value` rows against policyengine-uk 2.124.0's raw parameter files.

- 74 rows are literal rulespec parameters; the other 16 are derived rules.
- **0 value mismatches** at rulespec's own effective dates. Sentinels were compared at 2026-04-06.
- For **71 of 74**, PolicyEngine UK's history starts on or before rulespec's earliest dated version. The median PolicyEngine UK row has 4 distinct value dates in 2010–2022; rulespec has none.
- Only 3 rows have a rulespec date earlier than PolicyEngine UK's raw start:
  - `1992/4/8#additional_primary_percentage`: 2011-04-06 vs PolicyEngine UK 2015-04-01;
  - `1992/4/15#additional_class_4_percentage`: same dates;
  - `2005/3061/5#sure_start_maternity_grant_amount`: 2005-12-05 vs PolicyEngine UK 2022-01-01.
- Areas outside the mapping:
  - **VAT:** PolicyEngine UK has 1973→2011 history including 15% (2008-12-01) and 17.5% (2010-01-01); rulespec has only 20% from 2011.
  - **Fuel duty:** PolicyEngine UK has 2010-04-01 onward, including the 2022 cut; rulespec has only the standing 57.95p.
  - **Benefit cap:** PolicyEngine UK has 2016 and 2023 values; rulespec only the 2023 values. These are all from `pe_hist.py`.

**In-repo validation**

- Companion tests: 1,124 cases (§1.3). CI runs the shared `validate-rulespec.yml`.
- `tests/test_oracle_coverage_pending.py:1-14, 59-108` is a ratchet. It skips when `axiom-encode` is not installed; strict mode only runs under `AXIOM_RELEASE_GATE=1`.
- `validation_baselines/numeric_occurrence_coverage.json` is empty (`[]`).
- **`known-validation-gaps.yaml`:**
  - 12 waived combined-validator failures, each expiring 2027-01-03, owner `@MaxGhenis`.
  - Issue #68 covers 5 GOV.UK modules that "need upstream source verification": carer-support-payment, carers-allowance, DLA, pension-credit, scottish-child-payment.
  - Issue #137 (numeric grounding debt) covers 7: cb-JSA, PIP, scottish-carer-supplement, the HB and UC pipelines, `uksi/2013/376/34.yaml` and `2006/46/382.yaml`.
  - `docs/ENCODING-GAPS.md:9-24` explains the reg 34 entity waiver and the generator constants (`52`, `710.00`, `1000000`).
- **`oracle-coverage-pending.yaml`:** issue #101, 3,106 entries (2,982 `manual`, 124 `bulk`), dated 2026-07-07 to 2026-08-03.
  - 252 entries are `uk:`, across 64 modules.
  - The largest clusters are the England working-age CTR scheme (SI 2012/2886, 30 modules) and the GOV.UK wrappers for fuel duty, TV licence and cb-JSA.
  - The remainder are council roots, led by uk-harrow (110).
  - These are outputs not yet classified against any oracle. None of them concerns historical years.

## 5. Verdict per area: can rulespec-uk supply 2010–2022 values or retired-scheme formulas that policyengine-uk lacks?

- **Personal allowance, bands, rates, Scottish, savings/dividend:** **no.** Single 2024-or-later or sentinel values, and mis-dated (§1.4). PolicyEngine UK raw history starts in 2015 (PA, UK bands, NI thresholds) and 2017 (Scotland), so neither source covers 2010–2014.
- **PA taper:** **no.** Sentinel; PolicyEngine UK `maximum_ANI` has been present since 2009-07-21.
- **Age-related allowances, MCA:** **no.** Not encoded.
- **Marriage allowance:** **partially.** The s.55B formula and the explicit 2015-16 £1,060 transfer (`55B.yaml:74`). PolicyEngine UK's raw `marriage_allowance.max` starts 2016-04-01.
- **NIC Class 1 employee and Class 4:** **partially, trivially.**
  - The 2% additional rate from 2011-04-06 predates PolicyEngine UK's raw 2015 start, but it is wrong for 2022-23 per #423.
  - There are no thresholds or main rates before 2024 or 2026.
- **Class 1 employer, Class 2, Class 3, employment allowance, HSCL:** **no.**
- **Tax credits:** **no.** Only 2024 element amounts; PolicyEngine UK's WTC elements run from 2002 with 14 dates in 2010–2022.
- **JSA, ESA, IS:** **no** for amounts. Capital-tariff rules are dated to 1988 / 1996 / 2008, but the values match PolicyEngine UK's (6,000 / 16,000 / 250 / £1 from 2015).
- **UC:** **no** for values; sentinel or 2026-27. The structure follows current law, without the two-child limit.
- **Benefit cap:** **no.**
- **Child Benefit, HICBC:** **no.**
- **State Pension:** **partially.** Qualifying-year rules: 30 years from 2010, 35/10 years from 2016. No rates before 2026, no additional SP.
- **Pension Credit:** **no** for amounts. The £10k / £500 deemed-income rule is dated 2009-11-02, but it is time-invariant.
- **Housing Benefit:** **no** for amounts. The taper and capital rules are time-invariant; LHA is absent.
- **Council tax, CTB, CTR:** **no.** No CTB and no council tax; CTR is current text.
- **Disability and carer benefits:** **no.**
- **VAT and fuel duty:** **no.** PolicyEngine UK history is richer.
- **Alcohol, tobacco, IHT, SDLT:** **no.** Not encoded.
- **CGT:** **no.** 2024 and later only.
- **LBTT and LTT:** **no.** PolicyEngine UK has LBTT from 2015-04-01, and rulespec has a single version per band.
- **Unknown:** whether the Axiom corpus holds historical point-in-time UK text that the encoder could use. #423 says the amending SIs for Class 4 are "not in the corpus", and `data/corpus` here holds only 2026-dated snapshots.

## Summary table

"Retired-scheme formula?" is only filled in where the scheme was retired or abolished between 2010 and 2026.

| Area | Module paths (`uk/…`) | Earliest | Latest | Retired-scheme formula? | Usable for 2010–2022 replay? |
|---|---|---|---|---|---|
| IT: PA + taper | `statutes/ukpga/2007/3/35`, `2021/26/5`, `2023/1/5` | 2022-04-06 (+ sentinels) | 2026-04-06 | n/a | No |
| IT: bands/rates (rUK) | `2007/3/10`, `2007/3/23`, `2026/11/1-3`, `income_tax/individual/pilot_worker_oracle_pipeline` (`2007/3/6` deferred) | 2024-04-06 | 2026-04-06 | n/a | No |
| IT: Scottish | `income_tax/individual/scottish_income_tax_oracle_pipeline`, `1998/46/80C` | 2026-01-01 | 2026-01-01 | n/a | No |
| IT: savings/dividends | `2007/3/8, 11D, 12, 12A, 12B, 13, 13A, 16`, `2026/11/9`, `savings_dividend_oracle_pipeline` | 2024-04-06 | 2026-04-06 | n/a | No (mis-dated) |
| IT: age allowances / MCA | — | — | — | No | No |
| IT: marriage allowance | `2007/3/55B` | 2015-04-06 | 2016-04-06 | n/a | Partial (2015-16 £1,060 + formula) |
| NIC Class 1 employee | `1992/4/8`, `uksi/2001/1004/10`, `pilot_worker_class_1_nic_pipeline` | 2011-04-06 | 2026-04-06 | n/a | Partial, trivial (2% additional rate only) |
| NIC Class 1 employer | `1992/4/9`, `pilot_worker_employer_secondary_nic_pipeline` | 2025-04-06 | 2026-01-01 | n/a | No |
| NIC Class 2 | `1992/4/11` | 2025-04-06 | 2025-04-06 | No (compulsory Class 2 to 2023-24 absent, per open issue #353) | No |
| NIC Class 3 | `1992/4/13` | 2025-04-06 | 2026-04-06 | n/a | No |
| NIC Class 4 | `1992/4/15`, `uksi/2001/1004/100`, `pilot_worker_self_employed_nic_pipeline` | 2011-04-06 | 2026-04-06 | No (pre-2024 reg 100 Class 2 steps absent, per #423) | Partial, trivial (2% additional rate only) |
| Employment allowance | — | — | — | n/a | No |
| HSCL | — | — | — | No | No |
| Tax credits | `uksi/2002/2005/schedule/2`, `uksi/2002/2007/7`, `uksi/2024/247/3` | 2024-04-06 | 2024-04-06 | Element tables only; no award formula | No |
| JSA | `govuk/contribution-based-jobseekers-allowance`, `uksi/1996/207/116` | 1996-10-07 | 2026-04-06 | Capital tariff only (income-based) | No |
| ESA | `esa_income_related_applicable_amount_pipeline`, `uksi/2008/794/118` | 2008-10-27 | 2026-04-01 | IR pipeline at 2026-27 rates + capital tariff | No |
| Income Support | `uksi/1987/1967/53` | 1988-04-11 | 1988-04-11 | Capital tariff only | No |
| Universal Credit | `ukpga/2012/5/*`, `uksi/2013/376/**`, `universal_credit_composed_award_pipeline`, `programs/universal-credit/fy-2026-27` | 2013-04-29 (+ 41 sentinels) | 2026-04-01 | Two-child limit absent | No |
| Benefit cap | `uksi/2013/376/80A, 81, 82` | 2013-04-29 | 2013-04-29 | No | No (mis-dated) |
| Child Benefit | `uksi/2006/965/2`, `ukpga/1992/4/141-143`, `child_benefit/pilot_child_benefit_oracle_pipeline` | 2026-01-01 (+ sentinels) | 2026-01-01 | n/a | No |
| HICBC | `ukpga/2003/1/681B, 681D, 681E, 681G` (+ CB pipeline) | sentinel only | — | n/a | No |
| State Pension | `govuk/state-pension`, `uksi/2026/148/article/4, 6` | 2010-04-06 | 2026-04-06 | Basic SP formula (2026 rate); no additional SP | Partial (qualifying-year rules only) |
| Pension Credit | `ukpga/2002/16/1-3`, `uksi/2002/1792/6, 15, schedule/IIA`, `govuk/pension-credit`, `pension_credit_composed_award_pipeline` | 2009-11-02 | 2026-04-06 | n/a | No |
| Housing Benefit (+ LHA) | `uksi/2006/213/52, 70, 71`, `uksi/2006/214/29, 50, 51`, `housing_benefit_composed_entitlement_pipeline` | 2006-03-06 | 2026-04-01 | Taper and capital rules; LHA absent | No |
| Council tax / CTB / CTR | CTR: `uksi/2012/2885/**`, `uksi/2012/2886/**`, `ssi/2012/319/**`, `ssi/2021/249/**`, `wsi/2013/3029/**`, `govuk/council-tax-reduction`, 100 council modules | 2013-04-01 (England), 2021-04-05 (Scotland), sentinel (Wales), 2026-04-01 (councils) | 2026-04-01 | CTB: none | No |
| Disability / carer benefits | `uksi/2013/377/24`, `ukpga/2012/5/77-79`, `uksi/2026/148/article/14`, `uksi/2026/148/schedule/1`, `govuk/{pip, dla, carers-allowance, carer-support-payment, scottish-carer-supplement}`, `attendance_allowance_composed_amount_pipeline`, `ssi/2023/302/5, 16` | 2024-11-01 | 2026-04-06 | No | No |
| VAT | `ukpga/1994/23/2, 24, 25, 26, 29A`, `govuk/vat` | 1994-09-01 | 2011-01-04 | n/a | No (PolicyEngine UK richer) |
| Fuel duty | `ukpga/1979/5/6`, `govuk/fuel-duty` | 2011-03-23 | 2011-03-23 | n/a | No (PolicyEngine UK richer) |
| Alcohol / tobacco | — | — | — | n/a | No |
| CGT | `ukpga/1992/12/1H, 1K`, `govuk/capital-gains-tax` | 2024-04-06 | 2025-04-06 | n/a | No |
| IHT | — | — | — | n/a | No |
| SDLT | — | — | — | n/a | No |
| LBTT | `asp/2013/11/24`, `govuk/lbtt` | 2015-04-01 | 2024-12-05 | n/a | No |
| LTT | `anaw/2017/1/24`, `govuk/ltt` | 2022-10-10 | 2024-12-11 | n/a | No |
