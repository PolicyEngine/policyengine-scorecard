# Observed byte determinism

Two actual fresh replays of
`autumn_budget_2024__private_school_vat_20pct`, calendar year 2026, on Modal
produced exactly the same numerical artifact bytes as the original shared-Mac
run and its preserved canonical observation. All four SHA-256 values are:

```text
48666307c1ff045f07b39510c1dc22ab46cbd4d814320c34572d69e0a55ea931
```

The recorded gain to the Exchequer is £1,292,278,978.386702. No fields differ,
and no rounding or normalization was used in the comparison. The
[committed verification receipt](../../results/uk/events/DETERMINISM_VERIFICATION.json)
retains the original hash observation, canonical path, uploaded input
commitments, full Modal request/runtime/output receipts and inspected run
metadata.

The observation used registry SHA-256
`77b9087c3aeb9858f53dbb965d6e59632b5e75e5f05ff74774eec95e026b5d8b`.
An [immutable artifact copy](../../results/uk/events/determinism/private_school_vat_2026_registry_77b9087c.json)
preserves those exact bytes. Later classification corrections change registry
identity and artifact metadata, so this proof remains tied to its original
frozen inputs rather than asserting a future canonical file has the same SHA.

Each remote run computed a fresh certified baseline and alternate; neither
used `--resume`. Observed timings in seconds are retained exactly:

| Run | Baseline extraction | Alternate | Outer execution |
|---|---:|---:|---:|
| Modal repeat 1 | 70.739016909 | 124.811115315 | 212.35146286399998 |
| Modal repeat 2 | 82.78241082900001 | 134.181459868 | 237.268073717 |

Both runtimes were Linux x86_64 with Python 3.12.13,
policyengine 5.0.2, policyengine-core 3.27.1 and policyengine-uk 2.89.2.
Runtime network access was blocked and one worker was used. The uploaded
bundle's SHA-256 was verified before engine import and again by the managed
runner; the receipt binds the request, frozen inputs and returned file hashes.

Each request and artifact grid contains exactly this one pair. The
registry's full Autumn Budget 2024 grid contains thirty pairs, and both remote
manifests correctly record `full_event_complete=false`. This is observed
determinism for the selected pair; event coverage and subsequent reruns are
tracked separately. The inner run log's generic "local managed simulation"
label describes the reused CLI; the outer Modal receipt identifies where it
actually executed.

To reproduce later, use fresh output and download names, follow the control
environment setup in [RECIPE.md](RECIPE.md), and respect the shared limit of
two simultaneous simulations:

```bash
PYTHONPATH=. .venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_event --event autumn_budget_2024 --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --output-dir .venv-replay-checks/modal/ab24/another_repeat --download-root .venv-replay-checks/modal-downloads/another_repeat --execute
```

Compare the downloaded artifact's bytes or SHA-256 with
`results/uk/events/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2026.json`
using the same registry identity and frozen environment. For the original
registry recorded here, use the immutable artifact copy linked above.
Keep operational run logs and receipts separate from the deterministic
numerical artifact.

## Current registry execution

A fresh third Modal execution uses the corrected registry SHA-256
`89784d34920fb2d6aae702fb4028f84d7bf87f1694df77a0c9c5d255edbcdd34`.
Its [receipt](../../results/uk/events/DETERMINISM_CURRENT_REGISTRY.json) and
[immutable artifact](../../results/uk/events/determinism/private_school_vat_2026_registry_89784d34.json)
preserve artifact SHA-256
`4aa3bc9f868865aa47e5d5f384930e74fde425e0dd443ab3e2ad4354b7943fc9`.
The only field differing from the historic artifact is `registry_sha256`;
every numerical field remains identical. No rounding or normalization was
used, and all returned-file, request and input-manifest hashes were checked.

This request again covers one of thirty pairs and records
`full_event_complete=false`. Baseline extraction took 77.743541202 seconds,
the alternate took 133.628836524 seconds, and the inner runner took
224.84171834 seconds. A second fresh execution under these same current inputs
is still required for a current-registry byte-determinism observation; the
full-event run is tracked separately until its artifacts return.
