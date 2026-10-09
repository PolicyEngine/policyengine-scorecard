# Offline certified-bundle loader audit

This engine-free inspection checked the installed `policyengine==5.0.2` source, its packaged UK bundle manifest, the cached UK release JSON, and the committed [bundle pin](../../data/uk/certified_bundle.json). The [machine-readable receipt](OFFLINE_BUNDLE_AUDIT.json) records source hashes and exact checks. It did not import the engine, call a provider, read credentials, or rehash the 1.3 GB artifact; numerical preflight independently verifies those bytes before simulation.

The packaged fallback preserves the exact release identity: `policyengine-uk==2.89.2`, build `populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`, dataset URI `hf://policyengine/populace-uk-private/populace_uk_2023.h5@populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`, and digest `f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833`. All match the committed pin and cached release metadata. The cached release additionally declares `policyengine-core==3.27.1`. For this release, fetching the remote manifest changes only `compatibility_basis` from `built_with_model_package` to `exact_build_model_version`, and `certified_by` from `policyengine.py bundle certification` to null in `release_bundle`; the build ID, URI, digest, and model fields stay identical.

`policyengine.provenance.manifest.get_data_release_manifest` calls `requests.get` directly with a 30-second timeout. It does not consult Hugging Face offline flags or the cached release JSON. A network error enters the package's existing fallback to its bundled certification, provided the runtime model version matches. A remote worker should force the offline flags, block runtime network, and forward no Hugging Face token. Image package installation happens before the runtime network block. The cached release JSON can accompany an audit receipt, but the current compute CLI does not read it.

The managed loader retains the certified URI while using the generic runner's hash-checked local mirror at `data/uk/policyengine-local/policyengine_uk_data/storage/populace_uk_2023.h5`. Set `POLICYENGINE_UK_DATA_REPO` to that mirror root through the existing compute code; explicit unmanaged dataset paths are unnecessary.

Only these HF cache entries are required, under `datasets--policyengine--populace-uk-private`:

| Entry | Exact value |
| --- | --- |
| `refs/populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` | `a75a9a831d6b07aaffbd09713f2a1124f5c0f08f` |
| `snapshots/a75a9a831d6b07aaffbd09713f2a1124f5c0f08f/populace_uk_2023.h5` | The exact certified H5; preserve its blob symlink or copy the bytes directly |
| `blobs/f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833` | Required only when retaining that symlink |

Exclude `refs/main`, other revisions, calibration artifacts, other dataset repositories, and token/configuration files. The installed package supplies its own bundled manifest; changing that manifest would change the inspected source identity.
