"""Build data/uk/ab2026_measures.json (#230) from the pinned engine.

The Autumn Budget 2026 measure registry is generated, not typed, as the
AB2025 one is (pipeline/build_ab2025_registry.py): titles and exchequer
impacts come from the staged Table 6.1 rows, every `name_search` is computed
over the full parameter tree and variable list of the pinned engine, and every
`engine_baseline_2026` value is what that engine returns.

The pin is policyengine-uk 2.151.0, the engine the UK Autumn Budget dashboard
ran on Budget day (policyengine.py 6.11.1, whose certificate records
certified_for_model_version 2.151.0 on every published receipt). It is not
the certified populace pair the AB2025 registry follows: AB2026's
PolicyEngine counterparts are the dashboard's own published runs, so a
computability verdict has to be true of the engine those runs used.

Inputs:
  - an importable policyengine-uk == 2.151.0 (refuses any other version)
  - sources/harvest-uk-ab2026-2026-10-29/uk_hmt_tables/claims_staged.jsonl.gz
  - pipeline/ab2026_measure_keys.py

Usage:
    PYTHONPATH=. .venv-pe2151/bin/python pipeline/build_ab2026_registry.py
    PYTHONPATH=. .venv-pe2151/bin/python pipeline/build_ab2026_registry.py --check

Verdicts are authored below. Every mechanism a verdict names was read on
2026-10-29 from the engine at the pin or from the dashboard's source at
PolicyEngine/uk-autumn-budget-dashboard-2026@1eca3182.
"""

import gzip
import json
import re
import sys
from pathlib import Path

try:
    from pipeline import ab2026_measure_keys as K
    from pipeline.uk_engine_registry import engine_dumps
except ModuleNotFoundError:  # direct script invocation without PYTHONPATH
    import ab2026_measure_keys as K
    from uk_engine_registry import engine_dumps

REPO = Path(__file__).resolve().parent.parent
PIN = "2.151.0"
OUT = REPO / "data/uk/ab2026_measures.json"
KEYS_MD = REPO / "sources/harvest-uk-ab2026-2026-10-29/REGISTRY_KEYS.md"
STAGED = (
    REPO / "sources/harvest-uk-ab2026-2026-10-29/uk_hmt_tables/claims_staged.jsonl.gz"
)

ISSUE = "https://github.com/PolicyEngine/policyengine-scorecard/issues/230"
BUS_GAP = "https://github.com/PolicyEngine/policyengine-scorecard/issues/106"
DASHBOARD_REPO = "PolicyEngine/uk-autumn-budget-dashboard-2026"
DASHBOARD_MAIN = "1eca3182d6983b6375f401a3565ac56c25fa401e"
POLICY_YEARS = range(2027, 2032)  # the dashboard scores 2026-27 to 2031-32

RUN_IDENTITY = {
    "policyengine": "6.11.1",
    "certified_for_model_version": "2.151.0",
    "dataset_revision": "microcosm-uk-2024-25-national-20261025T091414Z-a6299504",
    "dataset_sha256": "b96a8cd625b645a409c063b1de5158532708a2f0d3c3897a794a8fb0bbd5064e",
    "basis": "static; OBR October 2026 EFO growth rates applied over policyengine-uk's March 2026 rates (receipt dashboard.basis)",
}


def _t61():
    lines, totals = {}, {}
    with gzip.open(STAGED, "rt") as fh:
        for raw in fh:
            r = json.loads(raw)
            c = r["conditions"]
            if c["table"] == "6.1" and c["row_type"] == "measure":
                e = lines.setdefault(
                    int(c["table_line"]),
                    {
                        "title": r["reform_hint"],
                        "head": c["head"],
                        "fiscal_head": c.get("fiscal_head"),
                        "heading": c["heading"],
                        "values": {},
                    },
                )
                e["values"][c["fy"]] = r["value_raw"]
            elif c["table"] == "6.1" and c["row_type"] == "total":
                totals.setdefault(r["reform_hint"], {})[c["fy"]] = r["value_raw"]
            elif c["table"] == "6.2" and c["table_line"] == "4":
                e = lines.setdefault("t62_4", {"title": r["reform_hint"], "values": {}})
                e["values"][c["fy"]] = r["value_raw"]
    return lines, totals


P, V = engine_dumps(pin=PIN)
T61, TOTALS = _t61()


def ns(pattern):
    rx = re.compile(pattern, re.I)
    ph = [p for p in P if rx.search(p) and not p.startswith("baseline.")]
    vh = [v for v in V if rx.search(v)]
    return (
        f"Searched BOTH the parameter tree and the VARIABLE list for /{pattern}/. "
        f"Parameters: {len(ph)} node(s) {ph[:6]}. Variables: {len(vh)} {vh[:6]}. "
        "Both are searched because a parameter-only search misses a variable "
        f"(#106). Re-run at policyengine-uk {PIN}."
    )


UPSTREAM = {
    "mileage": "policyengine-uk: business mileage and approved mileage allowance payments for employees' own cars and vans",
    "parental_allowance": "policyengine-uk: a Parental Allowance for fathers, partners and adopters (statutory_paternity_pay is the nearest variable)",
    "uc_surplus": "policyengine-uk: Universal Credit surplus earnings carried between assessment periods",
    "isa": "policyengine-uk: ISA subscriptions, a subscription limit, and Lifetime and first-time-buyer ISA withdrawals",
    "cgt_reliefs": "policyengine-uk: capital gains by relief (founders' and other business reliefs beyond BADR)",
    "estates": "policyengine-uk: estates, death benefits and their income tax treatment",
    "vat_categories": "policyengine-uk: consumption detailed enough to separate admissions to attractions and days out",
    "bus_age_fares": "policyengine-uk: a free-fare rule for children by age and month within the bus fare model",
    "student_loan_interest_cap": "policyengine-uk: a cap on Plan 2 and postgraduate (Plan 3) student loan interest",
    "bik": "policyengine-uk: company cars and their benefit-in-kind appropriate percentages",
    "hvcts_reliefs": "policyengine-uk: deferrals, discounts and exemptions within the high value council tax surcharge",
}

# The engine's exogenous incidence levers (descriptions read at the pin from
# parameters/gov/contrib/policyengine/budget/*.yaml). They spread a £ amount
# supplied as an input; none computes a measure's yield.
LEVERS = {
    "consumer": "gov.contrib.policyengine.budget.consumer_incident_tax_change ('Tax increase incident on consumers')",
    "corporate": "gov.contrib.policyengine.budget.corporate_incident_tax_change ('Tax increase incident on owners of capital')",
    "spending": "gov.contrib.policyengine.budget.other_public_spending ('Increase in non-NHS, non-education public spending, distributed by income decile as estimated by the ONS Effects of Taxes and Benefits dataset')",
}

measures = []


def entry(line, program, computability, **kw):
    t = T61[line]
    m = {
        "measure_key": K.key(line),
        "title": t["title"],
        "reported_status": "announced",
        "source_note": (
            f"HM Treasury, Budget 2026 Table 6.1 line {line} ({t['head']}"
            + (f", {t['fiscal_head']}" if t.get("fiscal_head") else "")
            + f"); exchequer impact GBP m by FY: {t['values']}"
        ),
        "table_61_line": line,
        "table_61_head": t["head"],
        "table_61_heading": t["heading"],
        "program": program,
        "computability": computability,
    }
    m.update(kw)
    measures.append(m)
    return m


def gap(why, pattern, *, upstream, nearest=None):
    d = {
        "pe_reform_delta": None,
        "why": why,
        "name_search": ns(pattern),
        "policyengine_uk_development_item": True,
        "upstream_item": UPSTREAM[upstream],
        "action_link": ISSUE,
    }
    if nearest:
        d["nearest_variable_and_why_it_does_not_work"] = nearest
    return d


def scope(why, pattern, link=None):
    return {
        "pe_reform_delta": None,
        "why": why,
        "name_search": ns(pattern),
        "out_of_model_scope": True,
        "action_link": link or ISSUE,
    }


def baseline(*paths):
    return {p: P[p] for p in paths}


def receipt(dash_id, artifact, sha, reform_sha, binding, generated_at):
    return {
        "repo": DASHBOARD_REPO,
        "commit": DASHBOARD_MAIN,
        "path": f"public/data/artifacts/{dash_id}/{artifact}/receipt.json",
        "receipt_file_sha256": sha,
        "reform_sha256": reform_sha,
        "reform_binding": binding,
        "generated_at": generated_at,
        **RUN_IDENTITY,
    }


def rates_up(paths):
    from policyengine_uk import CountryTaxBenefitSystem

    params = CountryTaxBenefitSystem().parameters
    out = {}
    for path in paths:
        node = params
        for part in path.split("."):
            node = getattr(node, part)
        out[path] = {
            str(y): round(float(node(f"{y}-04-06")) + 0.02, 6) for y in POLICY_YEARS
        }
    return out


# ---------------------------------------------------------------------------
# Executed on Budget day by the dashboard (seven published runs, one more run
# outside the release)
# ---------------------------------------------------------------------------

entry(
    1,
    "household_energy_payment",
    "expressible",
    construction="executed_by_dashboard",
    dashboard_measure_id="household_energy_payment_2026",
    pe_reform_delta=None,
    pe_modifier={
        "module": "src/uk_budget_data/budget_measures/household_energy_payment_2026.py",
        "function": "household_energy_payment_2026",
        "arguments": {
            "amount": 100,
            "year": 2026,
            "country": "ENGLAND",
            "bands": ["A", "B", "C", "D"],
        },
        "replaced_variables": ["ebr_council_tax_rebate"],
        "reads_variables": ["council_tax_band", "country"],
        "parameter_legs": [],
        "receipt": receipt(
            "household_energy_payment_2026",
            "101a07dc7238a10e",
            "0fb0414b45435799fb50afa9d79c2c7af8998de2ee406d8da6c1561bd46298d4",
            "ceede8365a9462ac389dc5210882ea23850babfed6e5bff8cf264e774cd616ad",
            "code_revision",
            "2026-10-28T17:07:18.666809+00:00",
        ),
    },
    engine_baseline_2026=baseline(
        "gov.treasury.energy_bills_rebate.council_tax_rebate.amount"
    ),
    note="The modifier adds £100 in 2026-27 to the native ebr_council_tax_rebate formula for bands A to D in England; the native rebate's own parameter is 0 at the pin, so the payment is the whole effect. Scotland, Wales and Northern Ireland get a Barnett share instead, not modelled.",
)
entry(
    2,
    "vat",
    "expressible",
    construction="executed_by_dashboard",
    dashboard_measure_id="domestic_electricity_zero_vat",
    pe_reform_delta=None,
    pe_modifier={
        "module": "src/uk_budget_data/budget_measures/zero_vat_on_domestic_electricity.py",
        "function": "zero_vat_on_domestic_electricity",
        "arguments": {
            "rate_change_2026": -0.028342979605206865,
            "rate_change_2027": -0.011149919361563782,
            "geography": "GB",
            "geography_2027": "UK",
        },
        "replaced_variables": [],
        "reads_variables": ["electricity_consumption"],
        "parameter_legs": [],
        "receipt": receipt(
            "domestic_electricity_zero_vat",
            "2d9c65726915303e",
            "e464b000c2af360654462efd05180d0fed272728911dc7292d932b99117246ca",
            "5ee4d8844432367d5557df38ee89e23b206e2c1236bce2451b0336ada02b58b6",
            "code_revision",
            "2026-10-28T17:08:09.754595+00:00",
        ),
    },
    engine_baseline_2026=baseline("gov.hmrc.vat.reduced_rate"),
    note="The modifier lowers the VAT rate on electricity_consumption by 5 points times the share of each fiscal year's use that falls in the zero-rated period (about 57% of 2026-27 in Great Britain; about 22% of 2027-28 across the UK). Electricity only, not gas.",
)
entry(
    3,
    "fuel_duty",
    "expressible",
    construction="executed_by_dashboard",
    dashboard_measure_id="fuel_duty_rise_deferral",
    pe_reform_delta=None,
    pe_modifier={
        "module": "src/uk_budget_data/reforms.py (_create_fuel_duty_rise_deferral) + src/uk_budget_data/budget_measures/pump_vat_on_fuel_duty_deferral.py",
        "function": "fuel_duty_deferral_rates + pump_vat_on_fuel_duty_deferral",
        "arguments": {},
        "replaced_variables": [],
        "reads_variables": ["petrol_spending", "diesel_spending"],
        "parameter_legs": ["gov.hmrc.fuel_duty.petrol_and_diesel"],
        "receipt": receipt(
            "fuel_duty_rise_deferral",
            "e077f8d4b70440c8",
            "2f547d91b455b7e84cf8495cbfd0475ca626d7f1b4a95605de869cf61d52a30f",
            "1dae41af83e4402f6b3af756d7dcdcc1dd525883dd32c3c8b9050456f52310f1",
            "code_revision",
            "2026-10-28T17:06:46.194418+00:00",
        ),
    },
    engine_baseline_2026=baseline("gov.hmrc.fuel_duty.petrol_and_diesel"),
    note="Day-weighted annual fuel duty rates (fuel_duty_deferral_rates), plus the VAT on the lower pump price through a modifier on petrol and diesel spending.",
)
entry(
    7,
    "carers_allowance",
    "expressible",
    construction="executed_by_dashboard",
    dashboard_measure_id="carers_allowance_earnings_taper",
    pe_reform_delta=None,
    pe_modifier={
        "module": "src/uk_budget_data/budget_measures/carers_allowance_earnings_taper.py",
        "function": "carers_allowance_earnings_taper",
        "arguments": {"start_year": 2030, "first_year_share": 0.5, "taper_rate": 1.0},
        "replaced_variables": ["carers_allowance_pre_overlap"],
        "reads_variables": [
            "carers_allowance_earnings",
            "care_hours",
            "would_claim_carers_allowance",
            "carers_allowance_reported",
        ],
        "parameter_legs": [],
        "receipt": receipt(
            "carers_allowance_earnings_taper",
            "9458905cefca3e88",
            "0852c433f5f76cd2e7b27f1bcf6721610d8e36e80b5f416727901e8125d273f6",
            "f45943c11aed787c570af3cc82d11af9cf181ce0877b5cb9350a9bc1e2f84dc8",
            "code_revision",
            "2026-10-28T17:08:00.734195+00:00",
        ),
    },
    engine_baseline_2026=baseline(
        "gov.dwp.carers_allowance.earnings_limit",
        "gov.dwp.carers_allowance.min_hours",
        "gov.dwp.carers_allowance.min_age",
    ),
    note="A 100% taper above the Weekly Earnings Limit (16 hours at the National Living Wage) in England and Wales, half of 2030-31 counted because the start date within that year is not set.",
)
entry(
    15,
    "income_tax",
    "expressible",
    construction="executed_by_dashboard",
    dashboard_measure_id="trading_allowance_raise",
    pe_reform_delta={
        "gov.hmrc.income_tax.allowances.trading_allowance": {
            str(y): 3000 for y in POLICY_YEARS
        }
    },
    delta_kind="absolute_value_by_year",
    pe_modifier={
        "module": "src/uk_budget_data/reforms.py",
        "function": "_create_trading_allowance_raise",
        "arguments": {},
        "replaced_variables": [],
        "reads_variables": [],
        "parameter_legs": ["gov.hmrc.income_tax.allowances.trading_allowance"],
        "receipt": receipt(
            "trading_allowance_raise",
            "eddde823a65b7be4",
            "59db02ec313c62f8c194580c806e782431f67a0f3b08df34adb91445a1eb9221",
            "cdcc8b19d5234afe31ae857db16a8f2d6a18578a1d7da1c890b3c5f21832c268",
            "content",
            "2026-10-28T17:07:22.701184+00:00",
        ),
    },
    engine_baseline_2026=baseline("gov.hmrc.income_tax.allowances.trading_allowance"),
    note="The data hold profits, not gross trading receipts, so the engine relieves a profit up to £3,000 in full and gives no relief above it (the dashboard's own description).",
)
entry(
    52,
    "income_tax",
    "expressible",
    construction="executed_by_dashboard",
    dashboard_measure_id="state_pension_income_tax_protection",
    pe_reform_delta=None,
    pe_modifier={
        "module": "src/uk_budget_data/budget_measures/pension_tax_allowance.py",
        "function": "pension_tax_allowance",
        "arguments": {
            "first_year": 2027,
            "last_year": 2029,
            "basic_rate": 0.2,
            "taper_divisor": 3,
            "weekly_rounding": 0.05,
        },
        "replaced_variables": [
            "income_tax",
            "uc_income_tax_on_earnings",
            "uc_income_tax_on_trade",
        ],
        "reads_variables": ["total_income", "is_SP_age"],
        "parameter_legs": [],
        "receipt": receipt(
            "state_pension_income_tax_protection",
            "1bfeed3c27a3c9b9",
            "4f20f3c69f9ddb3b7894d3281e9416774a1e12d747de1e573629570871b3e960",
            "65a95c811e5d6c6dd0b54255dd20ab1439c542994f1918778b93769c14199524",
            "code_revision",
            "2026-10-28T17:08:11.348926+00:00",
        ),
    },
    engine_baseline_2026=baseline(
        "gov.dwp.state_pension.new_state_pension.amount",
        "gov.hmrc.income_tax.allowances.personal_allowance.amount",
    ),
    note="A non-refundable income tax reduction for people over State Pension age: 20% of the full new State Pension above the personal allowance, withdrawn £1 for every £3 of total income above the full new State Pension, 2027-28 to 2029-30.",
)
entry(
    61,
    "income_tax",
    "expressible",
    construction="executed_by_dashboard",
    dashboard_measure_id="property_income_rates_up",
    pe_reform_delta=rates_up(
        [
            f"gov.hmrc.income_tax.rates.property.{b}"
            for b in ("basic", "higher", "additional")
        ]
    ),
    delta_kind="absolute_value_by_year",
    pe_modifier={
        "module": "src/uk_budget_data/reforms.py",
        "function": "property_income_rates_up",
        "arguments": {},
        "replaced_variables": [],
        "reads_variables": [],
        "parameter_legs": [
            f"gov.hmrc.income_tax.rates.property.{b}"
            for b in ("basic", "higher", "additional")
        ],
        "receipt": receipt(
            "property_income_rates_up",
            "7bf77b35e33233e0",
            "20df7073b4481a5f5b0073c6949e0d0c2894adac88d6e70778946456b2fe899d",
            "d46bf10b10b298db4059d7b6a2dccac7997e09afec0a88542c2059ea70646aa0",
            "content",
            "2026-10-28T17:10:45.376537+00:00",
        ),
    },
    engine_baseline_2026=baseline(
        *[
            f"gov.hmrc.income_tax.rates.property.{b}"
            for b in ("basic", "higher", "additional")
        ]
    ),
    note="Current law's property rates plus 2 points from 2027 (pe_reform_delta computed at the pin from each year's 6 April value). Scottish taxpayers' property income follows Scottish rates; finance cost relief follows the property basic rate UK-wide.",
)
entry(
    62,
    "income_tax",
    "expressible",
    construction="delta_on_current_law",
    dashboard_measure_id="savings_income_rates_up",
    pe_reform_delta=rates_up(
        [
            f"gov.hmrc.income_tax.rates.savings.{b}"
            for b in ("basic", "higher", "additional")
        ]
    ),
    delta_kind="absolute_value_by_year",
    engine_baseline_2026=baseline(
        *[
            f"gov.hmrc.income_tax.rates.savings.{b}"
            for b in ("basic", "higher", "additional")
        ]
    ),
    note="Registered by the dashboard but not in its published release, so there is no published receipt to cite; tranche 3 computes it from this delta.",
)

# ---------------------------------------------------------------------------
# Expressible at the pin, not run on Budget day
# ---------------------------------------------------------------------------

entry(
    60,
    "capital_gains_tax",
    "expressible",
    construction="delta_on_current_law",
    pe_reform_delta={
        "gov.hmrc.cgt.badr.lifetime_limit": {str(y): 500000 for y in POLICY_YEARS}
    },
    delta_kind="absolute_value_by_year",
    engine_baseline_2026=baseline("gov.hmrc.cgt.badr.lifetime_limit"),
    head_variables=["capital_gains_tax", "capital_gains_badr"],
    note="capital_gains_tax reads gov.hmrc.cgt.badr.lifetime_limit at the pin (variables/gov/hmrc/capital_gains_tax/capital_gains_tax.py). Not run on Budget day.",
)


def _cap_history():
    from policyengine_uk import CountryTaxBenefitSystem

    node = CountryTaxBenefitSystem().parameters.gov.dft.bus.fares.cap
    return {
        v.instant_str: ("inf" if v.value == float("inf") else v.value)
        for v in reversed(node.values_list)
        if v.instant_str >= "2023"
    }


entry(
    4,
    "bus_fares",
    "partial",
    # a reversal once the pre-measure world is known; until then no
    # construction is claimed
    intended_construction="reversal_on_certified_world",
    pe_reform_delta=None,
    engine_baseline_2026=baseline("gov.dft.bus.fares.cap"),
    engine_parameter_history={"gov.dft.bus.fares.cap": _cap_history()},
    missing=(
        "The pre-measure 2027 cap. The engine already carries the measure: "
        "gov.dft.bus.fares.cap is £2 from 1 January 2027 to 1 January 2028 "
        "(its metadata cites DfT's '£2 bus fares from January 2027'). A "
        "counterpart reverses it, which needs the cap 2027 would have had "
        "without the measure; the parameter has one upstream revision "
        "(policyengine-uk c8d1f89a9d, 5 October 2026) and records no "
        "pre-announcement path. Supersedes data/uk/bus_fares_gap.json's "
        "not_expressible verdict at 2.89.2, which predates the bus model."
    ),
    action_link=BUS_GAP,
)

# ---------------------------------------------------------------------------
# Household-facing, not expressible: policyengine-uk development items
# ---------------------------------------------------------------------------

entry(
    5,
    "income_tax",
    "not_expressible",
    **gap(
        "No business mileage or mileage allowance payments: the approved rates are a tax-free amount per business mile, and the search finds no mileage in the engine.",
        r"mileage|business_travel|approved_mileage",
        upstream="mileage",
    ),
)
entry(
    6,
    "parental_pay",
    "not_expressible",
    **gap(
        "A new benefit with no parameter or variable at the pin.",
        r"parental_allowance|paternity|parental_leave",
        upstream="parental_allowance",
        nearest={
            "variable": "statutory_paternity_pay",
            "why_not": "an existing statutory payment; the new Parental Allowance is a separate benefit with its own rules, none of which the engine carries",
        },
    ),
)
entry(
    8,
    "universal_credit",
    "not_expressible",
    **gap(
        "No surplus earnings rule: the search finds no parameter or variable for it.",
        r"surplus",
        upstream="uc_surplus",
    ),
)
entry(
    11,
    "savings",
    "not_expressible",
    **gap(
        "No ISA subscription or subscription limit: the engine holds ISA balances and interest, not subscriptions, so a limit has nothing to bind.",
        r"(^|[._])isa([._]|$)|individual_savings|subscri",
        upstream="isa",
        nearest={
            "variable": "cash_isa",
            "why_not": "a holding, not an annual subscription",
        },
    ),
)
entry(
    26,
    "capital_gains_tax",
    "not_expressible",
    **gap(
        "No founders' gains: the engine's relief-specific gains variable is capital_gains_badr (Business Asset Disposal Relief), and nothing identifies qualifying founders of high-growth companies.",
        r"founder|capital_gains_badr|investors_relief",
        upstream="cgt_reliefs",
    ),
)
entry(
    38,
    "savings",
    "not_expressible",
    **gap(
        "No first-time-buyer ISA, and no ISA subscriptions to move into one.",
        r"first_time|(^|[._])isa([._]|$)",
        upstream="isa",
    ),
)
entry(
    39,
    "savings",
    "not_expressible",
    **gap(
        "The engine's withdrawal charge (gov.hmrc.isa.lifetime.withdrawal_charge, 0.25 at the pin) is read only by lifetime_isa_countable_capital, the means-test value of a Lifetime ISA. The engine has no withdrawal or home purchase, so it cannot apply a lower charge to first-time buyers above the £450,000 cap; lowering the parameter would instead revalue every holder's countable capital.",
        r"withdrawal_charge|first_time|home_purchase",
        upstream="isa",
        nearest={
            "variable": "lifetime_isa_countable_capital",
            "why_not": "applies the charge to a holder's balance for means tests; the measure changes the charge on one kind of withdrawal",
        },
    ),
)
entry(
    53,
    "income_tax",
    "not_expressible",
    **gap(
        "The measure changes when pension and lump sum death benefits are taxed after a member dies (the two-year rule). The engine has no death event; its one death-benefit variable, pension_annual_allowance_taxable_lump_sum_death_benefits, is an input with no formula and no rule about timing after a death.",
        r"death|bereave|lump_sum",
        upstream="estates",
    ),
)
entry(
    66,
    "vat",
    "not_expressible",
    **gap(
        "The engine's consumption variables are by spending category (e.g. recreation_consumption); none isolates admissions to family days out, the base of this reduced rate.",
        r"recreation|attraction|admission|day_out",
        upstream="vat_categories",
        nearest={
            "variable": "recreation_consumption",
            "why_not": "a whole spending category; the measure covers only part of it",
        },
    ),
)
entry(
    67,
    "bus_fares",
    "not_expressible",
    **gap(
        "Free travel enters the bus model only as bus_pass_eligible, a dataset input whose documentation says it 'is not a pass-eligibility calculator'; no rule gives free travel to children aged 5 to 15, and the measure runs for one month (August 2026).",
        r"bus_fare|fare_allocation|bus_pass|concession",
        upstream="bus_age_fares",
    ),
)
entry(
    83,
    "student_loans",
    "not_expressible",
    **gap(
        "No interest cap: plan_2_interest_rate is RPI plus up to gov.hmrc.student_loans.interest_rates.plan_2.additional_rate (3%), and postgraduate_interest_rate (Plan 3) is RPI plus postgraduate_additional_rate (3%); neither formula has a ceiling.",
        r"student_loan.*interest|interest_rates\.plan_2|postgraduate_additional_rate",
        upstream="student_loan_interest_cap",
    ),
)
entry(
    86,
    "income_tax",
    "not_expressible",
    **gap(
        "No company cars or benefit-in-kind appropriate percentages: the search's only hits are council tax discount percentages.",
        r"company_car(?!ries)|benefit_in_kind|appropriate_percentage",
        upstream="bik",
    ),
)
entry(
    93,
    "council_tax",
    "not_expressible",
    **gap(
        "The engine carries the surcharge (gov.hmrc.council_tax.high_value_surcharge, variable high_value_council_tax_surcharge) but no deferral, discount or exemption within it.",
        r"high_value|surcharge|deferr",
        upstream="hvcts_reliefs",
    ),
)

# ---------------------------------------------------------------------------
# Out of the household model's scope
# ---------------------------------------------------------------------------

SPEND = (
    "Public spending ({what}), out of the household model's scope. The engine's spending channel, "
    + LEVERS["spending"]
    + ", distributes a £ amount supplied as an input, so scoring this line through it would restate HM Treasury's figure, not estimate it."
)
BUSINESS = (
    "A tax on businesses ({what}), out of the household model's scope: it changes what companies owe. The engine's corporate channel, "
    + LEVERS["corporate"]
    + ", spreads a £ change supplied as an input, so it would restate the costing rather than estimate it. The name search records what the engine holds."
)
RATES = (
    "A business rates measure ({what}), out of the household model's scope. The engine carries business rates only as a household incidence, "
    "business_rates ('Total incidence from exposure to business rates via corporate shareholdings'), and its business rates parameters are "
    "revenue statistics (gov.hmrc.business_rates.statistics.revenue.*): it has no properties, reliefs or thresholds for the measure to change, "
    "so its £ change would have to be supplied as an input, restating the costing."
)
INDIRECT = (
    "An indirect tax or duty collected from businesses ({what}), out of the household model's scope. The engine's consumer channel, "
    + LEVERS["consumer"]
    + ", spreads a £ change supplied as an input, so it would restate the costing rather than estimate it. The name search records what the engine holds."
)
FINANCE = "Lending, guarantees, investment or a financial transaction ({what}): no household tax or benefit rule changes."
ENFORCE = "An enforcement, compliance or administrative change ({what}): the rules households face do not change."
REGULATE = "A regulatory change ({what}) with no tax or benefit rule for households."
DETAINED = "A change to the {what}: the search finds no parameter or variable for hospital detention, prison or offending, so the engine cannot identify the people it affects."

SCOPE = {
    9: (SPEND, "books for children aged 0 to 5", r"early_years|childcare|book"),
    10: (
        INDIRECT,
        "tariffs on food products, heating oil and fertiliser",
        r"tariff|customs|import",
    ),
    12: (
        RATES,
        "business rates relief for pubs and venues",
        r"business_rates|non_domestic|nndr",
    ),
    13: (
        RATES,
        "small business rate relief thresholds",
        r"business_rates|small_business|non_domestic",
    ),
    14: (
        RATES,
        "business rates transitional support",
        r"business_rates|transitional|non_domestic",
    ),
    16: (INDIRECT, "tariff suspensions on business inputs", r"tariff|customs|import"),
    17: (INDIRECT, "Climate Change Levy rates", r"climate_change_levy|ccl"),
    18: (INDIRECT, "red diesel duty", r"red_diesel|rebated|fuel_duty"),
    19: (
        INDIRECT,
        "alcohol duty small producer relief",
        r"alcohol_duty|small_producer",
    ),
    20: (
        FINANCE,
        "Good Growth Funds for mayoral authorities",
        r"growth_fund|mayor|combined_authorit",
    ),
    21: (
        SPEND,
        "business rates retention by mayoral authorities",
        r"business_rates|retention|mayor",
    ),
    22: (SPEND, "local apprenticeship services", r"apprentice"),
    23: (SPEND, "regional growth projects", r"regional|regeneration"),
    24: (
        FINANCE,
        "Cambridge Development Corporation",
        r"development_corporation|cambridge",
    ),
    25: (SPEND, "strategic authorities' capacity", r"strategic_authorit|mayor"),
    27: (
        BUSINESS,
        "R&D relief claim forms",
        r"research_and_development|r_and_d|rd_relief",
    ),
    28: (
        BUSINESS,
        "Enterprise Management Incentives share options",
        r"enterprise_management|share_option|emi",
    ),
    29: (FINANCE, "British Business Bank", r"business_bank"),
    30: (FINANCE, "National Wealth Fund", r"wealth_fund"),
    31: (SPEND, "artificial intelligence", r"artificial_intelligence|\bai\b"),
    32: (SPEND, "public EV charging costs", r"charg|electric_vehicle"),
    33: (SPEND, "rough sleeping", r"rough_sleep|homeless"),
    34: (SPEND, "reprioritised housing budgets", r"rough_sleep|homeless"),
    35: (SPEND, "social and affordable homes", r"social_housing|affordable"),
    36: (
        INDIRECT,
        "VAT on land sold to social housing providers",
        r"vat|social_housing",
    ),
    37: (
        FINANCE,
        "an equity loan scheme for first-time buyers",
        r"equity_loan|help_to_buy|first_time",
    ),
    40: (SPEND, "defence", r"defen[cs]e"),
    41: (SPEND, "defence", r"defen[cs]e"),
    42: (SPEND, "defence administration", r"defen[cs]e"),
    43: (SPEND, "air defence for Ukraine", r"ukraine|defen[cs]e"),
    44: (FINANCE, "UK Export Finance", r"export_finance"),
    45: (ENFORCE, "HMRC measures to close the tax gap", r"tax_gap|compliance|evasion"),
    46: (ENFORCE, "online marketplace VAT liability", r"marketplace|online_sales"),
    47: (ENFORCE, "DWP fraud and error controls", r"fraud|error"),
    48: (
        DETAINED,
        "benefit entitlements of serious offenders detained in hospital in Great Britain",
        r"hospital|prison|detain|offender",
    ),
    49: (BUSINESS, "the distributions framework", r"distribution|dividend"),
    50: (BUSINESS, "Advance Corporation Tax", r"corporation_tax|advance_corporation"),
    51: (
        INDIRECT,
        "the VAT reverse charge on imported services",
        r"reverse_charge|vat",
    ),
    54: (BUSINESS, "the taxation of foreign sovereign investors", r"sovereign|foreign"),
    55: (
        BUSINESS,
        "the Bank Corporation Tax Surcharge",
        r"bank_surcharge|corporation_tax|bank_levy",
    ),
    56: (INDIRECT, "Machine Games Duty", r"gambling|machine_games|gaming"),
    57: (
        RATES,
        "business rates reliefs for vape shops and adult gaming centres",
        r"business_rates|vape",
    ),
    58: (
        BUSINESS,
        "capital allowances",
        r"capital_allowance|writing_down|first_year_allowance",
    ),
    59: (INDIRECT, "VAT on private hire operators' fares", r"private_hire|taxi|vat"),
    63: (
        SPEND,
        "civil service administration budgets",
        r"civil_service|administration",
    ),
    64: (SPEND, "a civil service AI fund", r"civil_service"),
    65: (
        INDIRECT,
        "Vehicle Excise Duty on heavy goods vehicles",
        r"heavy_goods|hgv|vehicle_excise",
    ),
    68: (
        BUSINESS,
        "the foreign permanent establishment exemption",
        r"permanent_establishment|corporation_tax",
    ),
    69: (
        BUSINESS,
        "the Electricity Generator Levy",
        r"generator_levy|electricity_generator",
    ),
    70: (
        SPEND,
        "the British Industrial Competitiveness Scheme",
        r"industrial|competitiveness",
    ),
    71: (INDIRECT, "Carbon Price Support rates", r"carbon_price|carbon"),
    72: (
        SPEND,
        "the Youth Guarantee and apprenticeships",
        r"youth_guarantee|apprentice",
    ),
    73: (SPEND, "the Union Learning Fund", r"union_learning|skills"),
    74: (FINANCE, "investment for growth", r"investment|growth"),
    75: (FINANCE, "the Growth Guarantee Scheme", r"guarantee"),
    76: (RATES, "business rates retention in Leeds", r"business_rates|retention"),
    77: (
        INDIRECT,
        "tariffs and contributions under the UK-India agreement",
        r"tariff|customs|double_contribution",
    ),
    78: (INDIRECT, "steel tariffs and quotas", r"tariff|steel"),
    79: (BUSINESS, "stamp taxes on shares", r"stamp_duty|stamp_tax|securities"),
    80: (RATES, "business rates relief for EV charge points", r"business_rates|charg"),
    81: (SPEND, "misogyny prevention programmes", r"misogyny|violence"),
    82: (SPEND, "infected blood compensation", r"infected_blood|compensation"),
    84: (SPEND, "Landfill Tax costs of illegal waste clearances", r"landfill|waste"),
    85: (
        SPEND,
        "the NHS and the Violence against Women and Girls Strategy",
        r"nhs|violence",
    ),
    87: (
        REGULATE,
        "licensing of supported housing",
        r"supported_housing|exempt_accommodation",
    ),
    88: (INDIRECT, "VAT on donated medicines", r"vat|medicine"),
    89: (INDIRECT, "VAT on medical deputies' staffing supplies", r"vat|staffing"),
    90: (INDIRECT, "the Landfill Communities Fund credit cap", r"landfill"),
    91: (
        REGULATE,
        "registration of franchised higher education providers",
        r"higher_education|franchise|student",
    ),
    92: (
        SPEND,
        "local authority high needs budgets",
        r"high_needs|special_educational|send",
    ),
    94: (
        ENFORCE,
        "the timing of mandatory payrolling of benefits in kind",
        r"benefit_in_kind|payroll",
    ),
    95: (
        INDIRECT,
        "customs duty relief on low value imports",
        r"customs|low_value|import",
    ),
    96: (
        INDIRECT,
        "the Emissions Trading Scheme's coverage of energy from waste",
        r"emissions_trading|\bets\b|carbon",
    ),
    97: (
        BUSINESS,
        "corporation tax on gas distribution revenue",
        r"corporation_tax|gas_distribution",
    ),
    98: (
        BUSINESS,
        "double taxation relief for investors in US LLCs",
        r"double_taxation|foreign_income|llc",
    ),
}

PROGRAM = {
    SPEND: "public_spending",
    BUSINESS: "business_tax",
    INDIRECT: "indirect_tax",
    FINANCE: "financial_transactions",
    ENFORCE: "compliance_and_administration",
    REGULATE: "regulation",
    RATES: "business_rates",
    DETAINED: "benefits",
}

for line, (template, what, pattern) in SCOPE.items():
    entry(
        line,
        PROGRAM[template],
        "not_expressible",
        **scope(template.format(what=what), pattern),
    )

# Table 6.2 line 4 has no Table 6.1 line of its own.
t = T61["t62_4"]
measures.append(
    {
        "measure_key": K.PREFIX + K.TABLE_62[4],
        "title": t["title"],
        "reported_status": "announced",
        "source_note": f"HM Treasury, Budget 2026 Table 6.2 line 4 (financial transactions, no Table 6.1 line); cash impact GBP m by FY: {t['values']}",
        "table_62_line": 4,
        "program": "financial_transactions",
        "computability": "not_expressible",
        **scope(
            FINANCE.format(what="Sovereign AI"), r"sovereign|artificial_intelligence"
        ),
    }
)

# ---------------------------------------------------------------------------
# Packages
# ---------------------------------------------------------------------------

BY_LINE = {m["table_61_line"]: m for m in measures if "table_61_line" in m}
for slug, spec in K.PACKAGES.items():
    lines = spec["lines"]
    if lines is None:  # Table 6.1's own Tax/Spend split
        head = "Tax" if "tax" in slug else "Spend"
        lines = sorted(l for l, m in BY_LINE.items() if m["table_61_head"] == head)
    legs = [K.key(l) for l in lines]
    comp = [BY_LINE[l]["computability"] for l in lines]
    expressible = [K.key(l) for l, c in zip(lines, comp) if c == "expressible"]
    m = {
        "measure_key": K.package_key(slug),
        "title": spec["title"],
        "reported_status": "announced",
        "source_note": (
            f"HM Treasury, Budget 2026 Table 6.1 row '{spec['table_61_row']}'; GBP m by FY: {TOTALS[spec['table_61_row']]}"
            if spec["table_61_row"]
            else "A composition of Table 6.1 lines that producers score together; see `package_of`."
        ),
        "program": "package",
        "construction": "package_of_registry_measures",
        "package_of": legs,
        "pe_reform_delta": None,
    }
    if all(c == "expressible" for c in comp):
        m["computability"] = "expressible"
        m["engine_baseline_2026"] = {}
        if slug == "package_policyengine_seven":
            m["pe_modifier"] = {
                "module": "src/uk_budget_data/reforms.py",
                "function": "AUTUMN_BUDGET_2026_COMBINED_COMPONENTS",
                "arguments": {},
                "replaced_variables": [],
                "reads_variables": [],
                "parameter_legs": [],
                "receipt": receipt(
                    "combined--f91fe847275730cb",
                    "4faed20984703c7d",
                    "a00d0614eeed1c5cfaa63353d08a604a433bf881329bfd2d7b60c1681c243e67",
                    "09498c7b550716444725ef211725c894bc0efa13bd6c855efb8bdadc93b0e834",
                    "code_revision",
                    "2026-10-28T17:54:34.931664+00:00",
                ),
            }
            m["note"] = (
                "Run as one simulation of all seven measures (the combined run), not as a sum of the seven runs."
            )
        else:
            m["note"] = (
                "Every leg is expressible; a counterpart is the legs' runs combined, stated as constructed."
            )
    else:
        m["computability"] = "partial"
        m["missing"] = (
            f"{len(lines) - len(expressible)} of {len(lines)} legs are not expressible "
            "(see each leg's verdict); a PolicyEngine number covers only "
            f"the {len(expressible)} expressible legs: {expressible}"
        )
        m["expressible_legs"] = expressible
    measures.append(m)


def registry():
    lines = sorted(m["table_61_line"] for m in measures if "table_61_line" in m)
    assert lines == sorted(K.TABLE_61), "every Table 6.1 line exactly once"
    counts = {}
    for m in measures:
        counts[m["computability"]] = counts.get(m["computability"], 0) + 1
    return {
        "schema_version": 1,
        "fiscal_event": "autumn_budget_2026",
        "event_date": "2026-10-28",
        "chancellor": "John Healey",
        "administration": "Burnham government (from 2026-07-20)",
        "registry_rule": (
            "One entry per measure ANNOUNCED at Autumn Budget 2026: every HM Treasury Table 6.1 line "
            "(including the lines a household model cannot touch), the one Table 6.2 financial "
            "transaction with no Table 6.1 line, and the packages producers score. It is the port's "
            "key space (#230): every staged AB2026 claim carries conditions.measure_key from this "
            "file, and every measure carries a computability verdict against the engine the Budget-day "
            "runs used. It stages NO value claims; values live in the harvest under their producers "
            "(sources/harvest-uk-ab2026-2026-10-29/)."
        ),
        "measure_key_rule": (
            "ab2026__<slug>, written out per Table 6.1 line in pipeline/ab2026_measure_keys.py so a "
            "reworded title cannot move a key; ab2026__package_<slug> for packages; ab2026_option__<slug> "
            "for options costed by others. The pre-event registry (data/uk/budget_2026_measures.json, "
            "#96) keeps its own keys; pre_event_outcomes records what became of each."
        ),
        "verification_note": (
            "Every pe_reform_delta and parameter_legs path was RESOLVED against an installed "
            f"policyengine-uk {PIN} on 2026-10-29, and engine_baseline_2026 records what that engine "
            "returns for 2026-06-01. Every not_expressible verdict carries a name_search COMPUTED over "
            f"the pinned engine's parameter tree ({len(P)} leaves) and variable list ({len(V)}), never "
            "typed. Mechanisms named in a verdict were read from the engine's source at the pin or from "
            f"the dashboard's source at {DASHBOARD_REPO}@{DASHBOARD_MAIN[:8]}."
        ),
        "engine_pin": {
            "policyengine_uk": PIN,
            "resolved_on": "2026-10-29",
            "pin_meaning": (
                "The pin follows the Budget-day runs: every published receipt of the UK Autumn Budget "
                "dashboard records policyengine 6.11.1 with certified_for_model_version 2.151.0, and those "
                "runs are AB2026's PolicyEngine counterparts (tranche 3). It is NOT the certified populace "
                "pair data/uk/certified_pairs.json holds (policyengine 6.11.0, policyengine-uk 2.132.6); "
                "tranche 3 adds a 6.11.1 pair record before any counterpart is ingested."
            ),
            "budget_day_runs": RUN_IDENTITY,
        },
        "computability": {
            "expressible": "every leg is a resolvable parameter at the pin, or the measure was executed by a receipt-pinned dashboard modifier (construction executed_by_dashboard)",
            "partial": "some legs resolve; the missing ones are named in `missing`",
            "not_expressible": "the engine has no representation; `why` names the gap, `name_search` records the computed search, `action_link` says where it goes",
        },
        "construction_vocabulary": {
            "executed_by_dashboard": "the measure ran on Budget day as a dashboard reform; pe_modifier names the module, function, arguments, the engine variables it replaces or reads, its parameter legs, and the published receipt (path, file sha256, reform sha256, run identity)",
            "delta_on_current_law": "pe_reform_delta applied to current law at the pin",
            "reversal_on_certified_world": "the measure is already in the engine's current law; a counterpart executes the pre-measure world as baseline (#56 convention)",
            "package_of_registry_measures": "a composition of registry measures (`package_of`, a list of keys, as in AB2025); a PolicyEngine number covers the expressible legs, stated as constructed",
        },
        "exogenous_levers_note": (
            "The engine carries exogenous incidence levers that spread a £ amount supplied as an input: "
            + "; ".join(LEVERS.values())
            + ". Feeding a Table 6.1 figure through one restates HM Treasury's costing rather than "
            "estimating it, so no lever makes a line expressible here."
        ),
        "action_link_rule": "Every not_expressible measure links to #230, which lists the upstream development items; the bus fare cap's partial verdict links to #106, the bus gap record.",
        "pre_event_outcomes": PRE_EVENT,
        "triage": {
            **counts,
            "executed_by_dashboard": sum(
                1 for m in measures if m.get("construction") == "executed_by_dashboard"
            ),
            "policyengine_uk_development_item": sum(
                1 for m in measures if m.get("policyengine_uk_development_item")
            ),
            "out_of_model_scope": sum(
                1 for m in measures if m.get("out_of_model_scope")
            ),
            "announced": sum(
                1 for m in measures if m["reported_status"] == "announced"
            ),
        },
        "measures": measures,
    }


# What became of each measure the pre-event registry (#96) recorded as under
# consideration. "Not in Table 6.1 or 6.4" is a statement about those two
# tables, read in full, nothing more.
PRE_EVENT = {
    "ab2026__property_income_tax_rate_rise": "announced: Table 6.1 line 61 ("
    + K.key(61)
    + ")",
    "ab2026__bank_profit_surcharge_increase": "announced: Table 6.1 line 55 ("
    + K.key(55)
    + "), temporary, 3% to 6% for 15 months",
    "ab2026__business_rates_warehouse_up_pub_down": "partly: Table 6.1 line 12 raises pubs' relief ("
    + K.key(12)
    + "); no warehouse surcharge line in Table 6.1 or 6.4",
    "ab2026__high_value_council_tax_surcharge": "an AB2025 measure; Table 6.1 line 93 changes its reliefs ("
    + K.key(93)
    + ") and Table 6.4 line 11 recosts it",
    "ab2026__cgt_align_with_income_tax_rates": "not in Table 6.1 or 6.4",
    "ab2026__cgt_remove_uplift_on_death": "not in Table 6.1 or 6.4",
    "ab2026__pension_tax_free_lump_sum_restriction": "not in Table 6.1 or 6.4",
    "ab2026__ni_extended_to_investment_property_pension_income": "not in Table 6.1 or 6.4",
    "ab2026__personal_allowance_freeze_extension": "not in Table 6.1 or 6.4",
    "ab2026__wealth_tax_2pc_above_10m": "not in Table 6.1 or 6.4",
    "ab2026__council_tax_and_sdlt_to_land_value_tax": "not in Table 6.1 or 6.4",
    "ab2026__online_sales_levy": "not in Table 6.1 or 6.4 (line 46, online marketplace liability, is a VAT collection measure, not a levy)",
    "ab2026__vape_duty_increase": "not in Table 6.1 or 6.4 (line 57 removes business rates reliefs for vape shops)",
    "ab2026__ated_increase_and_sdlt_envelope_close": "not in Table 6.1 or 6.4",
}


def keys_md(reg):
    out = [
        "# Autumn Budget 2026 registry keys",
        "",
        "Generated by `pipeline/build_ab2026_registry.py` from `data/uk/ab2026_measures.json`; do not edit.",
        "Every staged row's `measure_key` is one of these, or (Table 6.4 recostings only) a key from the",
        "earlier event's registry named in `conditions.recosting_of`.",
        "",
        "| key | Table 6.1 line | computability | title |",
        "|---|--:|---|---|",
    ]
    for m in reg["measures"]:
        line = m.get("table_61_line") or (
            f"6.2/{m['table_62_line']}" if m.get("table_62_line") else ""
        )
        out.append(
            f"| `{m['measure_key']}` | {line} | {m['computability']} | {m['title'].replace('|', '/')} |"
        )
    return "\n".join(out) + "\n"


def main(argv=None):
    reg = registry()
    text = json.dumps(reg, indent=1, ensure_ascii=False) + "\n"
    md = keys_md(reg)
    if argv and "--check" in argv:
        ok = OUT.read_text() == text and KEYS_MD.read_text() == md
        print("byte-identical" if ok else "DIFFERS")
        return 0 if ok else 1
    OUT.write_text(text)
    KEYS_MD.parent.mkdir(parents=True, exist_ok=True)
    KEYS_MD.write_text(md)
    print(f"wrote {OUT.relative_to(REPO)}: {len(measures)} measures, {reg['triage']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
