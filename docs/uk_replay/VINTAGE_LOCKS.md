# Source vintage locks

The first phase-0 slice locks public source bytes for Spring Statement 2022,
Autumn Statement 2022 and Autumn Budget 2021. Each event has one receipt for
economy, receipts, expenditure, policy measures, a historical official
forecasts database (HOFD) row, and the matching DWP benefit expenditure and
caseload edition. These are source identities, not calibrated targets or
certified populations.

For Spring Statement 2022, the policy-measures workbook explicitly includes
the Treasury scorecard (`TA.2`) and decisions outside it (`TA.3`). Autumn
Statement 2022's locked combined charts/tables workbook includes aggregate
Government decision effects (`T.1`), plus macro and fiscal change tables;
individual scorecard rows were not verified in that workbook. The complete
individual comparison rows remain in the separately pinned policy measures
database used by the existing [inventory](INVENTORY.md).

The contract is [vintage_lock.v1.json](schemas/vintage_lock.v1.json). Each
receipt records the original URL, exact Wayback `id_` replay and capture
timestamp, retrieval time, bytes, SHA-256, media type and workbook sheets.
Archive response headers and workbook creation/modification properties are
retained when available. An unavailable receipt retains the requested replay
and each failed attempt, with a reason and null byte metadata; its requested
timestamp is not evidence that a capture exists.

`capture_status` is `launch`, `later_revision` or `unknown`. A publication-day
capture is useful evidence, but cannot by itself rule out an earlier same-day
correction. The March 2022 economy and receipts filenames include `-1` and
`-2`; no first-release byte equivalence is asserted. The matching DWP editions
were published after the fiscal events. Their forecast identity is distinct
from both their later publication date and any later archive capture date.
Autumn Budget 2021's receipts workbook has a verified modification timestamp
on 28 October 2021, after the event, so it is classified `later_revision`.
Whether its numeric cells differ from the launch workbook remains unverified.

The HOFD receipt pins the March 2025 database edition, explicitly a later
cross-vintage publication. Its `selection.forecast_label` chooses the event's
historical forecast. `verified_rows` retains actual label coordinates and
source cells read from the fetched workbook, including footnote suffixes.
The later database's `Outturn data*` rows are never selected. This does not
establish that every historical cell is byte-identical to its original 2021
or 2022 publication.

`sha256` identifies a complete fetched workbook. `receipt_sha256` binds the
whole lock's metadata: UTF-8 JSON with sorted keys, compact separators and
`ensure_ascii=False`, excluding only `receipt_sha256` itself. A selector binds
this receipt digest and the source-role byte digests. A changed URL, retrieval
receipt, selected row or revision assessment therefore requires a new selector
binding, even if source bytes stay the same.

## Collection and offline validation

Run from the repository root with the documented Python environment:

```bash
python data/uk/events/collect_vintage_locks.py --scratch-dir /tmp/uk-vintage-locks
python data/uk/events/collect_vintage_locks.py --check
```

Collection uses only public OBR/GOV.UK assets through Wayback `id_` replay
URLs, with user agent `policyengine-scorecard-research/1.0`. It makes one
request at a time, pauses four seconds between requests and redirects, and
backs off on throttling or temporary failures. Redirects must retain an
allowlisted public publisher inside a Wayback `id_` URL. Complete HTTP 200
responses and readable xlsx/ods sheet metadata are required. Source bytes stay
in an explicitly supplied scratch directory outside the repository; only
receipts are committed. Each completed source receipt is saved before
continuing the queue.

`--check` validates committed schemas, dates, role completeness, unique byte
digests within an event, archive URL/timestamp/original agreement, failure
metadata and canonical receipt digests. It opens no network connection and
does not require the scratch files. Re-hashing retained source bytes is a
separate collection audit; offline validation cannot reconstruct uncommitted
downloads.

The OBR replay queue and access constraints come from
[archive_obr.md at the checkpoint](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/docs/uk_replay/research/archive_obr.md),
and DWP edition metadata from
[archive_govuk.md at the checkpoint](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/docs/uk_replay/research/archive_govuk.md).
The collector does not contact `obr.uk` directly or script the UK Government
Web Archive. The Autumn Budget 2021 DWP attachment was recovered from its
[publication-day GOV.UK page capture](https://web.archive.org/web/20211119154331id_/https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2021),
then downloaded from the matching captured attachment. Every locked source's
exact capture URL is retained in its event receipt.

[The policy-world source-cell receipt](evidence/vintage_policy_world_sources.json)
retains selected titles, units, year headers, programme labels, grouped
spending changes and pre/post macro labels from the fetched workbooks. It
preserves source label anomalies and the Scottish Block Grant caveat. It is
supporting evidence for the [policy-world proposal](POLICY_WORLD_CONTRACT.md),
not a complete pre-measures level bridge or a target registry.
