# Offline loader audit: development 6.2.5 bundle

The [machine-readable source receipt](OFFLINE_BUNDLE_AUDIT_dev-uk-data-1.56.16__pe-uk-2.102.3.json)
binds the installed loader, its packaged manifest, the engine source and
the development pin. The pin remains in ignored `.venv-replay-checks/dev6/`;
the production index contains only the historical 2.89.2 bundle.

Line references below are to the installed 6.2.5 wheel. This inspection
imports no engine, reads no credentials, makes no provider calls and runs no
simulation. Separate smoke receipts record executed behavior.

| Source and lines | Finding |
| --- | --- |
| `policyengine/core/tax_benefit_model_version.py:137–221` | `release_bundle` contains model/runtime loader, certified build, artifact digest and certification fields. The build ID `policyengine-uk-data-1.56.16` differs from HF tag `1.56.16`; both are checked separately. |
| `policyengine/provenance/dataset_materialization.py:90–121` | Repository type comes from the dataset reference or data package. This release uses **model**, not dataset. |
| Same file, `124–144, 260–334` | Managed materialization reuses `./data/<basename>` only after digest verification. On absent or wrong bytes it uses `requests.get`, independent of HF offline flags. The replay seeds that path from the cached artifact and blocks runtime socket connections. |
| `policyengine/tax_benefit_models/uk/model.py:418–442` | `materialize_dataset` supplies the exact runtime input and provenance. `reform=` and `scenario=` pass through to the country Microsimulation. |
| `policyengine/tax_benefit_models/common/model_version.py:68–91` | `runtime_dataset_source` is the materializer's local path, with model repo type, revision and hash. The adapter resolves this path while in the isolated materialization directory and requires equality to the file hashed before and after simulation. |
| `policyengine_uk/data/dataset_schema.py:53–61, 197–209` | HDFStore opens with `mode="r"`; a writable PyTables mirror is unnecessary. An isolated ignored per-key directory links the already cached H5 and saves disk space. |
| `policyengine/provenance/manifest.py:339–368` | Release-metadata fetching calls `requests.get` with a timeout and bypasses HF offline flags. Blocked sockets turn this into `DataReleaseManifestUnavailableError`. |
| Same file, `393–435` | Fallback returns packaged certification when `certified_for_model_version` equals runtime. Other cases may return an `unverified` certification; the replay refuses them. |

The package certifies UK 2.102.3 against data built originally with UK 2.89.2,
using `legacy_compatible_model_package`. Its global package pins supply
core 3.32.10. Registration checks those current packaged model/core pins,
the packaged digest, cached producer-declared artifact size, installed
versions and the stored data year, rather than mistaking producer build pins
for recertification pins.

One metadata discrepancy needs upstream review by the main session: the
packaged `release_manifest_revision` is `78788372fec47fc8df835bd32307ef61eaed83c2`,
whose cached root release manifest describes 1.57.4. The 1.56.16 tag resolves
to `a9e52499b6a6cca100a5ce4f36ca27b2e8a213df`, whose cached producer manifest
describes the exact 1.56.16 artifact. Registration records both authorities
and checks the matching producer artifact declaration for size; the runtime
socket block makes the packaged compatibility claim binding. No upstream
issue was filed. Recheck this metadata in the final release.

The cache allowlist is only
`models--policyengine--policyengine-uk-data-private/refs/1.56.16` plus
`snapshots/a9e52499b6a6cca100a5ce4f36ca27b2e8a213df/enhanced_frs_2024_25.h5`.
Modal mounts verified bytes directly at that snapshot path. No token,
credentials, other revision or dataset is forwarded. Package installation
occurs during image build; runtime network remains blocked.

The year and projection evidence is in the
[development years document](YEARS_dev-uk-data-1.56.16__pe-uk-2.102.3.md).
