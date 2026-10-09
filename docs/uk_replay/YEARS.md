# Certified replay years

The supported calendar-year window for this lane is **2023 through 2030**,
inclusive. Calendar year Y proxies OBR fiscal year Y–(Y+1). Autumn Budget
2024 can therefore be run across its complete 2024–25 through 2029–30
costing window. This is support for a projection of one population, with
named vintage differences; it does not establish a population or forecast
matched to each historical event.

The population identity is committed in `data/uk/certified_bundle.json`:
`populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`, artifact
`populace_uk_2023.h5`, SHA-256
`f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833`.
The hash-verified cached HDF5 was also inspected directly with
`pandas.read_hdf(cached_path, "time_period").tolist()`, which returned
`["2023"]`. The start year therefore comes from the file's stored metadata.
The replay preflight verifies the digest and the runtime dataset file before
any simulation.

The following evidence comes from the installed **policyengine-uk 2.89.2**
wheel, read before setting the year window:

| Engine file and lines | What it establishes |
| --- | --- |
| `policyengine_uk/data/economic_assumptions.py`, lines 35–52 | `extend_single_year_dataset` takes its start from `int(dataset.time_period)` and defaults its end to 2030. It copies the input population into each year and then applies uprating. |
| Same file, lines 55–98 | The first year is unchanged. Subsequent years multiply the previous year's selected inputs by `1 + index_rel_change`. |
| Same file, lines 100–110 | Council tax, rent and student loan plans also have explicit custom year handling. |
| `policyengine_uk/simulation.py`, lines 407–455 | A legacy `Dataset` HDF5 file is read at its stored periods, converted to a `UKSingleYearDataset` at its first period, and passed to the same extension function. |
| Same file, lines 471–503 | The extended dataset establishes the entity structure from its first year and loads each year's columns as explicit year inputs using `set_input`. |
| `policyengine_uk/data/uprating_indices.yaml` | Earnings use average-earnings growth, self-employment income uses per-capita mixed-income growth, many other incomes use per-capita GDP, and household weights use the population index. This creates projected inputs from the original records. |
| `policyengine_uk/parameters/gov/economic_assumptions/yoy_growth.yaml`, header and 2025–2030 blocks | Historical growth through 2024 is outturn; 2025–2030 growth uses the **March 2026** OBR forecast. The announcement forecast is not reconstructed. |
| `policyengine_uk/tax_benefit_system.py`, lines 81–109 | The parameter-processing pipeline converts government parameters to fiscal-year values after uprating and backdating. |
| `policyengine_uk/utils/parameters.py`, lines 26–47 | `convert_to_fiscal_year_parameters` samples each government `Parameter` at 30 April of year Y and writes that value over the entire annual period Y, for 2015–2040. Raw YAML change dates alone therefore do not establish the processed world's effective dates. |
| `policyengine_uk/simulation.py`, lines 230–248 | Parameter changes reload the raw parameter tree, apply the reform, and then run the same parameter-processing pipeline. Dated reform schedules also undergo fiscal-year conversion. |

The engine also contains longer-run economic assumptions, but its ordinary
single-year dataset extension ends at 2030. A formula returning a number
outside that range would not establish supported population inputs.
`compute_uk_event.validate_years` therefore rejects 2022 and 2031, even if
an event registry mistakenly includes them. Costing years before 2023–24
require track 2's historical rules and per-year populations. They stay in
the source inventory: Spring Budget 2023 retains 170 FY2022–23 cells while
its executable window begins in CY 2023.

The annual calculation uses the requested population-input year explicitly,
while processed government policy parameters use the engine's 30 April
snapshot for that year. This is a calendar-year population and fiscal-year
policy combination; it does not reconstruct income and household records
from 6 April to 5 April. The construction guard samples 1 January, 6 April
and 31 December in the processed current-law tree. Authors must inspect
processed values rather than infer monthly effects from raw YAML dates.
Every staged comparison therefore retains
`cy_proxies_fy`, `baseline_vintage` and `population_vintage` tags.

The isolated Modal worker has now passed the existing managed-bundle
preflight and executed a nonzero private-school VAT replay for CY 2026.
Its artifact is byte-identical to the local CY 2026 artifact on the same
certified build and digest, despite Linux Python 3.12.13 versus local macOS
Python 3.12.14; see [the saved determinism evidence](DETERMINISM.md).
That observation confirms the managed projection path for this measure-year.
The supported 2023–2030 window still rests on the dataset metadata and engine
extension evidence above. Full Autumn Budget 2024 coverage requires its
complete 30-pair manifest; the focused check alone supplies one pair.

To inspect the evidence in a rebuilt pinned environment:

```bash
.venv-replay/bin/python - <<'PY'
import inspect
from policyengine_uk.data.economic_assumptions import extend_single_year_dataset
from policyengine_uk.simulation import Simulation
from policyengine_uk.utils.parameters import convert_to_fiscal_year_parameters
print(inspect.getsource(extend_single_year_dataset))
print(inspect.getsource(Simulation.build_from_dataset))
print(inspect.getsource(Simulation.build_from_multi_year_dataset))
print(inspect.getsource(convert_to_fiscal_year_parameters))
PY
```
