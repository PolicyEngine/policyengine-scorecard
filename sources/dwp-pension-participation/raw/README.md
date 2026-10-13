# dwp-pension-participation raw artifacts

Fetched 2026-08-25 from GOV.UK via the content API attachment list for
`/government/statistics/workplace-pension-participation-and-savings-trends-2009-to-2025`
(first published 2026-07-30 — the current edition).

| file | source URL | sha256 |
|---|---|---|
| dwp_workplace_pension_participation_2009_2025.xlsx | https://assets.publishing.service.gov.uk/media/6a68b23acc35a9471da4c1cf/workplace-pension-participation-2009-2025.xlsx | 4d4bd871b23f9ef763101b4491bce437f3c02e622ce9394c857c0346fb326e41 |

The release also offers the same tables as ODS. The XLSX is vendored
because the repo's other spreadsheet adapters already read the
OpenXML shared-strings layout; the two are the same data.

## What is read

Block 1 of three sheets — the only block on each that carries a
descriptor:

- `1.3a` participation by **earnings band**
- `1.4` participation by **age band**
- `1.9a` participation by **region**

each split Public / Private / Overall, 2009-2025.

## What was surveyed and deliberately NOT kept

- **The five unlabelled side-by-side blocks on each sheet.** Every sheet
  states it "contains six tables presented next to each other", and row
  6 describes only the first ("Percentage of eligible employees
  participating"). The other five have no descriptor. A number whose
  meaning is inferred from its column position is not a claim, so they
  are tallied as unread rather than guessed at. They are readable once
  DWP labels them or the methodology note is transcribed deliberately.
- **The other 21 data sheets** — by sector, employer size, gender,
  working pattern, industry, occupation, and the savings-level tables.
  Each is its own population decision.

## Why the survey matters

DWP derives these from **ONS ASHE**, an employer survey of jobs in Great
Britain — the same survey behind the Low Pay Commission lane (#88), and
not the FRS the certified policyengine-uk world is built on. That
difference is the first divergence axis for any counterpart, and it is
carried on every row rather than left here.

## Geography

Great Britain, not the UK: ASHE excludes Northern Ireland. Rows carry
`GB`, and the repo's registry keeps that distinct from `UK` for the same
reason #91 keeps IFS's coverage-restricted analyses distinct.
