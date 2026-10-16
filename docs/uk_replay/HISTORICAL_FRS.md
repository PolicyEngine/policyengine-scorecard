# Historical FRS requirements

Phase 0 source/code review, 11 October 2026. This is the input contract for
adapting FRS 2019–20 and 2020–21, not a claim that either survey already works
with the current builder. No survey microdata was downloaded, inspected or
built. [The supporting receipt](evidence/frs_requirements_code.json) records
the exact code files, hashes and reader column inventory used here.

## Survey availability and edition identity

| Survey | Statistical publication | Public microdata evidence | Replay use in this slice |
|---|---|---|---|
| FRS 2019–20 | 25 March 2021 | UKDS SN 8802. Its readme identifies a second edition in April 2025; the first microdata distribution date and first-edition file hashes remain unverified. | The [plan](PLAN.md) proposes it for Autumn Budget 2021 and Spring Statement 2022. Require evidence that the selected original microdata edition was available before each event. |
| FRS 2020–21 | 31 March 2022 | UKDS listed SN 8948 as a new dataset on 10 June 2022. This establishes public availability by that notice, not an exact original release-day/file receipt. | Proposed for Autumn Statement 2022. Both the statistics and the UKDS notice postdate the 23 March Spring Statement, so it cannot be that event's vintage-faithful survey. |

Sources fetched: the [2019–20 statistics page](https://www.gov.uk/government/statistics/family-resources-survey-financial-year-2019-to-2020),
the [2020–21 statistics page and change history](https://www.gov.uk/government/statistics/family-resources-survey-financial-year-2020-to-2021),
[UKDS SN 8802 readme](https://doc.ukdataservice.ac.uk/doc/8802/read8802.htm),
and [UKDS's 10 June 2022 release notice](https://ukdataservice.ac.uk/2022/06/10/latest-data-collections-and-new-editions-10-june-2022/).
Statistical publication, microdata availability, survey fieldwork and later
revision are separate dates. A selector's statistical date alone does not
certify the bytes that a build later consumes. The edition, DOI, acquisition
receipt and per-table digests must also be pinned before acquisition/build.

## Code reviewed and current release

Read the local clones through `git show origin/main:<path>` without checkout
or source edits. The required `git -C <clone> fetch origin` was attempted for
both clones but the workspace sandbox refused `.git/FETCH_HEAD` writes
(`Operation not permitted`). Read-only `gh api .../commits/main` calls returned
the same SHAs as the local references:

- Microcosm: `90958612874e7a52174c4d89d7df3f0f030783ba`.
- UK-data: `2b9c1c2c64ced6e1d95fed1ed398a22627233669`.

The UK-data repository is described as archived in the task brief; the fetched
[GitHub repository metadata](https://api.github.com/repos/PolicyEngine/policyengine-uk-data)
returned `archived: false` at this inspection. The exact commit is the code
identity used here, independent of that hosting status. No pre-2024 UK-data
commit appeared in the available local history query; no early implementation
is inferred from that absence.

Both current pins select **FRS 2024–25**, survey/base year 2024, calibration
year 2025, UKDS SN 9563, DOI `10.5255/UKDA-SN-9563-1`. Microcosm additionally
pins private acquisition revision `a2039519d3b92aecc06c66dfd175cb46ac24cada`
and ZIP SHA-256
`05dd0069587dbd25e5719d355ce05fc0827d5edd58c24ece9ab85acd954a9aeb`.
These are code-declared identities; the private ZIP was not fetched.
Sources: [Microcosm release pin](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk/frs_release.json#L5),
[UK-data release pin](https://github.com/PolicyEngine/policyengine-uk-data/blob/2b9c1c2c64ced6e1d95fed1ed398a22627233669/policyengine_uk_data/datasets/frs_release.py#L48).

Microcosm validates `survey_year <= base_year < calibration_year` and the
country adapter binds the release to the raw-source pins and target period.
Changing a CLI year alone is insufficient. Sources:
[release validation](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_release.py#L112),
[country adapter](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/country_adapter.py#L35).

## Raw tables and columns the current readers use

The Microcosm spine loads **14 `.tab` files**. It verifies each whole file's
size and SHA-256 before parsing tab-delimited data, lowercases headers,
and coerces numeric fields. It preserves raw `JOB.SALSAC` text and
`BENEFITS.UCSTART` dates separately. Its downstream FRS stages reread some of
the same tables; they introduce no additional raw FRS table in the inspected
source-stage manifest. Sources:
[table list](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L44),
[file verification and parsing](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L394),
[source-stage manifest](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk/source_stages.json).

The following is a **reader requirement inventory**, not an observed schema
listing of the historical files. Every table needs `SERNUM` to join households;
person-linked tables need `PERSON`, and benefit-unit-linked tables need
`BENUNIT`. Normalization produces `household_id = SERNUM`,
`benunit_id = SERNUM * 100 + BENUNIT` and
`person_id = SERNUM * 1000 + PERSON`.
[Identity normalization](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L446).

| Raw table | Columns used beyond identity keys |
|---|---|
| `adult`, `child` | Union of person fields below. Adult and child headers differ: the reader concatenates them, rather than requiring every field on both tables. |
| `accounts` | `ACCOUNT`, `ACCINT`, `ACCTAX`, `INVTAX`. |
| `benefits` | `BENEFIT`, `BENAMT`, `VAR2`, `UCHOUSEL`, `UCSTART`. |
| `benunit` | `FAMTYPB2`, `DEPCHLDB`, `TOTCAPB4`, `HBOTHAMT`. `DEPCHLDB` has a child-table-count fallback. |
| `chldcare` | `CHAMT`, `COST`, `REGISTRD`. |
| `extchild` | `NHHAMT`. |
| `househol` | `GROSS4`, `GVTREGNO`, `PTENTYP2`, `TYPEACC`, `BEDROOM6`, `CTANNUAL`, `CTBAND`, `CTREBAMT`, `ADULTH`, `WATSEWRT`, `NIRATLIA`, `RT2REBAM`, `HHRENT`, `SUBRENT`, `MORTINT`, `STRUINS`, `CHRGAMT1`–`CHRGAMT9`, `HHSTAT`, `INTDATE`, `HRPNUM`, `CWATAMT1`, `CSEWAMT1`, `CWATAMTD`, `CTDISC`, `CT25D50D`, `CTREB`. |
| `job` | `DEDUC1`, `SPNAMT`, `SALSAC`, `ETYPE`, `JOBTYPE`, `SEEND`, `SEJBLONG`, `JOBBUS`. |
| `maint` | `MRUS`, `MRUAMT`, `MRAMT`. |
| `mortgage` | `RMORT`, `RMAMT`, `BORRAMT`, `MORTEND`. |
| `oddjob` | `OJAMT`, `OJNOW`. |
| `penprov` | `PENAMT`, `STEMPPEN`. |
| `pension` | `PENPAY`, `PTINC`, `PTAMT`, `POINC`, `POAMT`, `PENOTH`. |

The concatenated `adult`/`child` person reader uses:

- Structure and status: `AGE80`, `AGE`, `SEX`, `MARITAL`, `TOTHOURS`,
  `HOURTOT`, `HRPID`, `UPERSON`, `SPCREG1`, `EMPSTATI`, `MJOBSECT`, `SIC`,
  `RELHRP`, `R01`–`R14`.
- Income and expenses: `INEARNS`, `SEINCAM2`, `ROYYR1`–`ROYYR4`,
  `RENTPROF`, `MNTUS1`, `MNTUSAM1`, `MNTAMT1`, `MNTAMT2`, `ALLPAY2`–`ALLPAY4`,
  `CHAMTERN`, `CHAMTTST`, `APAMT`, `APDAMT`, `PAREAMT`, `REDAMT`, `SLREPAMT`,
  `SSPADJ`, `SMPADJ`, `TUBORR`, `ACCSSAMT`, `ACCSSPD`, `GRTDIR1`, `GRTDIR2`,
  `HEARTVAL`, `FSBVAL`, `FSFVVAL`, `FSMVAL`, `SRENTAMT`, `CVPAY`, `CONVBL`.
- Education: `FTED` or `EDUCFT`, `TYPEED2`, `EDUCQUAL`, `TRAIN` or `TRAIN2`,
  `ADEMA`/`ADEMAAMT` or `EDUMA`/`EDUMAAMT`, `CHEMA`/`CHEMAAMT`.
- UC start-up inputs: `SAMESIT`, `SDEMP01`–`SDEMP12`, in addition to
  `EMPSTATI` and `SEINCAM2` above.

The core income/benefit/expense mappings are in
[the spine, lines 581 onward](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L581).
Later raw reads are explicit in
[relationships](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_relationships.py#L91),
[employment](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_employment.py#L91),
[education](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_education.py#L165),
[council tax](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_council_tax.py#L149),
and [FRS HMRC constituents](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_hmrc_source.py#L180).

An absent column does not have one universal treatment. The spine's `_number`
returns zero for many absent columns; capital uses `-1` for unavailable
`TOTCAPB4`; shared-rent, UC start-up, Scottish-water and employment reads
require named fields. Access-fund payments require `ACCSSPD` when any positive
amount is present. Thus a historical port needs an explicit availability and
meaning map, including an exclusion/blocker where an input cannot be observed.
Do not let zero filling imply that a historic population observed a quantity.
Sources: [zero/sentinel handling](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L1058),
[shared rent](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L1093),
[UC start-up](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L1255),
[access fund](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L1395).

UK-data's `create_frs` reads all `.tab` files in the supplied directory and
directly uses the same 14 core tables. It lowercases/coerces columns and
preserves `SALSAC` text. Its additional or alternative raw reads include
`HOUSEHOL.RTANNUAL`, `HOUSEHOL.CSEWAMT`, `BENUNIT.TOTCAPB3` and
the `ADEMA`/`EDUMA`, `FTED`/`EDUCFT` alternatives. Its input map and historical
branches are evidence for the adapter, rather than compatibility certification.
[UK-data ingest](https://github.com/PolicyEngine/policyengine-uk-data/blob/2b9c1c2c64ced6e1d95fed1ed398a22627233669/policyengine_uk_data/datasets/frs.py#L828).

## Known changes and requirements for the older releases

| Difference | Evidence and consequence |
|---|---|
| Northern Ireland rates | UK-data explicitly reads `RTANNUAL` for `survey_year < 2021`, and `NIRATLIA` otherwise. This supplies a code-evidenced mapping for both requested survey years. Microcosm currently reads `NIRATLIA` directly; the historical adapter must select the old field and verify its units. [Branch](https://github.com/PolicyEngine/policyengine-uk-data/blob/2b9c1c2c64ced6e1d95fed1ed398a22627233669/policyengine_uk_data/datasets/frs.py#L1250). |
| Full-time education | UK-data accepts `FTED`, then `EDUCFT`, with a comment dating the rename to 2022–23; Microcosm accepts both. Use the older code path only after checking the selected 2019–20/2020–21 metadata. [UK-data branch](https://github.com/PolicyEngine/policyengine-uk-data/blob/2b9c1c2c64ced6e1d95fed1ed398a22627233669/policyengine_uk_data/datasets/frs.py#L1006). |
| Training and EMA | Microcosm distinguishes `TRAIN` from the recoded 2024–25 `TRAIN2`, and permits `ADEMA`/`ADEMAAMT` or `EDUMA`/`EDUMAAMT`. The exact older release headers and code domains remain unverified. [Reader alternatives](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_education.py#L182). |
| Benefit-unit capital | UK-data documents `TOTCAPB4` as introduced in 2019–20 and retains a `TOTCAPB3` fallback. Microcosm consumes `TOTCAPB4` with a missing sentinel. This is a code/documentation observation, not a check of old rows or the adequacy of financial capital for each benefit. [UK-data capital reader](https://github.com/PolicyEngine/policyengine-uk-data/blob/2b9c1c2c64ced6e1d95fed1ed398a22627233669/policyengine_uk_data/datasets/frs.py#L793). |
| Scottish water and council tax | The current Microcosm function documents `CWATAMT1`/`CSEWAMT1` as the 2024–25 replacement for older `CWATAMT`/`CSEWAMT`; it requires the current fields and discount codes. UK-data still reads `CSEWAMT` and `CWATAMTD`. The older value definitions/discount treatment need source-metadata review. [Current assembly](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L1489). |
| Survey-derived versus administrative-linked benefits | DWP says the current 2024–25 release replaces responses for major benefits/tax credits with administrative information. Current code additionally requires `BENEFITS.UCSTART` and `UCHOUSEL`. Their availability in the original historical editions is unknown; a recent linked back-series must not silently stand in for event-time data. [Current DWP methodology](https://www.gov.uk/government/statistics/family-resources-survey-financial-year-2024-to-2025/family-resources-survey-background-information-and-methodology). |
| FRS 2019–20 later edition | UKDS says the April 2025 second edition populated `HOUSEHOL.IMDE`, `IMDN`, `IMDS`, `IMDW`, `IMD_E`, `IMD_NI`, `IMD_S`, `IMD_W`. These fields are not consumed by the inspected FRS readers, but their alteration demonstrates that a survey-year label is not a file identity. [Edition readme](https://doc.ukdataservice.ac.uk/doc/8802/read8802.htm). |

The public [2020–21 questionnaire change summary](https://doc.ukdataservice.ac.uk/doc/8802/mrdoc/pdf/8802_frs_future_changes_summary_of_changes_2020_21.pdf)
also records new rent-arrears, water-provider, free-childcare, student-loan
tuition, SSP-day, Scottish Child Payment and pandemic-support questions;
changed assets/savings categories and EMA routing; and temporary suspension of
household-expenditure/debt questions. It expressly excludes processing changes.
Consequently it does not establish the resulting old `.tab` column inventory
or how fields such as `SSPADJ`, `TUBORR`, `ACCOUNT` and `STEMPPEN` were derived.
That remains a schema/meaning check before ingestion.

The [2020–21 report](https://www.gov.uk/government/statistics/family-resources-survey-financial-year-2020-to-2021/family-resources-survey-financial-year-2020-to-2021)
describes telephone interviewing and a reduced sample during the pandemic.
These are population/measurement changes in addition to schema differences;
preserving a column name does not reconstruct an employment transition or
pandemic support entitlement. The current UC start-up helper documents a rule
from September 2020; its use for a 2019–20 seed requires a separate dated-rule
review, even if all necessary columns exist.

## Access and work still required

UKDS's SN 8802 readme requires registered-user access under the End User
Licence; commercial use requires owner approval. The exact SN 8948 edition's
licence, archive header listing and original release identity were not obtained
here: its public catalogue renders client-side and attempted study-information
and readme URLs were inaccessible to the browser tool. Confirm those terms
before acquisition; public statistics/metadata access does not authorize
redistribution of raw survey files.

Microcosm's inspected CLI accepts a local `--frs-raw-dir`; its source manifest
labels the tabs `licensed_microdata` and requires hashes. Its private
Hugging Face pin names an acquisition repository, not evidence that this lane
has rights or credentials to its contents. Obtain authorized access through
UKDS or the already-authorized internal source process, retain the licence and
acquisition receipt privately, and commit public provenance rather than records.
[CLI input](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/spine_build.py#L250).

Each historical port needs an edition-specific table/header/value-label map,
old missing-value conventions, dates, monetary periods and benefit codes;
replacement release/source-stage/country pins; and independently reviewed
derivation choices for unavailable inputs. The existing `TIME_PERIOD = "2024"`
in the raw spine must be made release-specific for a historical build.
Disability derivation evaluates rates at the release's survey year; legacy
proxies also read engine parameters. Pin the engine that performs those steps,
then certify the final scoring population with the engine that will run it.
[Spine period](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_spine.py#L61),
[disability year rule](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_disability.py#L100),
[legacy engine inputs](https://github.com/PolicyEngine/microcosm/blob/90958612874e7a52174c4d89d7df3f0f030783ba/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_legacy_proxies.py#L64).

The current FRS pin's notes retain newer SPI 2022–23, WAS round 8, LCFS
2023–24 and ETB donors. Historical donor editions, release dates and rights
therefore need their own review; a historical FRS pin alone cannot establish
an event-time population. The exact historical headers/code domains,
original survey-byte digests, donor availability, numerical compatibility,
projection bridges and certification remain unverified. The next phase should
resolve these through public metadata and authorized schema inspection before
any population build.
