# Development bundle: calendar years and loader path

This is source evidence for the already-certified **policyengine 6.2.5 /
policyengine-uk 2.102.3 / core 3.32.10 / uk-data 1.56.16** adapter check.
It is not a registered production replay or an event result. The development
pin and observations live under ignored `.venv-replay-checks/dev6/`.

The cached `enhanced_frs_2024_25.h5` has SHA-256
`e433e532b17bd8ce76030156285816e33d44e93edabd2204adbef71d19a68712`,
126,553,300 bytes, and `time_period` = `[2024]`. Reading the cached 1.58.0
artifact's table independently also returned `[2024]`; its 128,369,110 bytes
and digest from the task were confirmed during registration-source inspection.
No simulation used that uncertified pairing.

The following line references are to the installed wheels in
`.venv-replay-dev6/lib/python3.12/site-packages/`; their hashes and selected
line text are bound in the [offline loader audit](OFFLINE_BUNDLE_AUDIT_dev-uk-data-1.56.16__pe-uk-2.102.3.json).

| File and lines | Verified behavior |
| --- | --- |
| `policyengine_uk/data/economic_assumptions.py:35–53` | The extension begins at `int(dataset.time_period)` and defaults to 2030. It applies engine uprating to copies of the original population. |
| `policyengine_uk/simulation.py:461–473` | A single-year input goes through that extension, then loads the resulting multi-year dataset. |
| `policyengine_uk/simulation.py:475–511` | Entity structure comes from the first year; each projected year's inputs are set explicitly. The managed check requires first year 2024 and the requested year present. |
| `policyengine_uk/utils/scenario.py:113–158` | A dictionary reform updates the processed parameter tree with `target.update`; it does not reload or fiscally process that tree. Dated windows therefore retain the 1 January rule implemented by `annual_reform`. |
| `policyengine_uk/simulation.py:134–136, 214–218` | `reform=` becomes a Scenario; its modifier runs after loading data. |
| `policyengine_uk/utils/parameters.py:78–123` | Default government conversion still samples 30 April. New exceptions support `fiscal_year_blend` (day-weighted 6 April–5 April) and `preserve_calendar_dates` (skip conversion). CGT's three rates and fuel-duty LPG/natural-gas parameters carry `fiscal_year_blend`; tobacco/alcohol rates carry `preserve_calendar_dates`. Reinspect the final pin before reusing these constructions. |
| `policyengine_uk/simulation.py:177–179, 214–218` | The default UC modifier precedes the dictionary modifier, so the UC health scenario still needs to refresh the fixed inputs after its parameter update. |
| `policyengine_uk/scenarios/uc_reform.py:69–96` | UC health inputs are fixed for 2026–2029. Standard-allowance uplifts now occur in the formula, rather than in this modifier. |
| `policyengine/tax_benefit_models/uk/model.py:397–443` | `managed_microsimulation` forwards `**kwargs` to the country Microsimulation and passes the materialized source dataset, then adds runtime provenance. |
| `policyengine/tax_benefit_models/uk/model.py:276–349` | The separate year-file wrapper preserves the observed data year and its tables. The replay uses the original managed dataset directly, so it never treats a projected year file as observed data (the issue addressed by [policyengine.py#557](https://github.com/PolicyEngine/policyengine.py/pull/557)). |

This development window is **2024–2030**. Registry years, requested execution
years, Modal requests and staging derive it from the selected pin. Source FY
cells beginning before 2024 stay in the same source-row accounting exactly
once, labelled `outside_bundle_window` in a new-bundle stage. In particular,
FY2023–24 counterparts available on the legacy population cease to be
computable on this population. Calendar Y continues to proxy FY Y–(Y+1),
with explicit population, baseline and period axes.

Current policyengine-uk main was also read at
`e89b8abcf524de48e590b9680e1a04288d30eacd` (2026-10-10):
[`data/economic_assumptions.py:55–74`](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/data/economic_assumptions.py#L55)
still defaults the extension to 2030. This observation does not certify the
future model/core versions. Register the final loader release and repeat the
code and construction audit once policyengine.py#555 merges.

The CGT main-rate construction changes on this development engine: its
October 2024 change is blended into CY2024 by `gov/hmrc/cgt/basic_rate.yaml:14`
(and the higher/additional-rate files). The new registry therefore restores
the pre-announcement rates from 1 January 2024 against that blended certified
world, rather than deferring the annual reversal to 2025. Its construction
digest changes and the old pooled-gains/residential-scope limitation remains.
This is a construction observation, not a computed event effect.
