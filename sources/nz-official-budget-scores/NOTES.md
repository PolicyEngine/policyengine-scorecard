# New Zealand official Budget scores

This package starts the New Zealand reform-score lane with two measures that
have both a separable official fiscal score and Axiom rule mechanics suitable
for a first replication candidate:

- Budget 2026's temporary $50-per-week increase to the in-work tax credit.
- Budget 2025's Working for Families abatement-threshold and rate changes.

The source tables report operating impacts in NZD millions under Vote Revenue
(IRD–Crown), in each case under the New Spending heading. The adapter normalizes
them to raw NZD as `operating_cost_change`: positive is an increase in operating
cost, and a source dash is represented numerically as zero while remaining
verbatim in `source_display`. Budget 2025's detailed fiscal recommendation
labels its figures “$m - increase/(decrease)” and shows that the WFF total
contains Family Tax Credit, In-Work Tax Credit, Minimum Family Tax Credit, and
small debt-impairment components. It is therefore not mislabeled as a pure
transfer-entitlement delta.

Fiscal-year claims use the end-year convention: FY2025-26 has `period=2026`.
Each published operating total is a separate window claim whose period equals
the end of the window.

Every claim is held out. No Axiom or PolicyEngine result is attached in this
package. The rules are pinned to `rulespec-nz` main at
`a17f1adc84b3fb23210d91e408e72ae6c37af6a3`; population scoring follows after
the New Zealand Microcosm build. Readiness and RuleSpec locations live in
publication provenance rather than claim conditions, so workflow progress or
module refactors do not re-key the external Treasury claims.

These are rule-encoded replication candidates, not completed like-for-like
scores. Two bridges remain explicit before attaching a comparable result:

- The Budget 2026 IWTC policy can terminate before 31 March 2027 if 91 petrol
  remains below NZ$3/litre for four consecutive weeks. A replication must name
  its petrol-price path. The official profile also includes NZ$30 million in
  FY2027-28 after the maximum entitlement window, so annual comparisons require
  an official-to-model fiscal/payment-timing bridge.
- The Budget 2025 detailed fiscal recommendation decomposes the operating total
  beyond the two abatement parameters. The Vote Revenue Estimates pin the
  implementation commencement only to April 2026, so the reform descriptor
  records `effective_month=2026-04` without inferring a day. A comparison must
  reproduce or separately account for the non-entitlement components.

The compact excerpts in `source-pages.txt` were visually checked against Budget
2026 PDF page 55 (printed B.19 page 49), Budget 2025 PDF page 72 (printed B.19
page 66), the Budget 2025 fiscal recommendation PDF page 16 (printed page 14),
and the Vote Revenue Estimates PDF page 21 (printed page 307). The complete PDFs
remain at the official Treasury URLs and are pinned by SHA-256 in
`manifest.jsonl` rather than vendored.

Excluded from this first tranche: Budget 2025 Best Start changes and Budget
2026 Accommodation Supplement, Temporary Additional Support, and social-rent
packages. They remain candidates, but are not labeled fully scoreable here
until their input mapping or every integrated package component is proved.
