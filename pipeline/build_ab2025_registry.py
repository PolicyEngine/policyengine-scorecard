"""Build data/uk/ab2025_measures.json (#136) from the pinned engine.

The Autumn Budget 2025 measure registry is GENERATED, not typed: every
`name_search` string is computed over the full parameter tree and variable
list of an installed policyengine-uk 2.89.2 (the certified bundle's pin), and
every `engine_baseline_2026` value is what that engine returns. The AB2026
registry's first version published two false gaps from guessed paths and #106
nearly published a false bus gap from a parameter-only search; generating the
searches removes the hand from the loop.

Inputs:
  - an importable policyengine-uk == 2.89.2 (refuses any other version)
  - sources/harvest-uk-2026-08-02/uk_hmt/claims_staged.jsonl.gz (Table 4.1
    titles and exchequer impacts, verbatim)
  - data/uk/certified_bundle.json (the pin)

Usage:
    .venv-pe289/bin/python pipeline/build_ab2025_registry.py          # rewrites the registry
    .venv-pe289/bin/python pipeline/build_ab2025_registry.py --check  # byte-identical or exit 1

Measure verdicts and reversal constructions are authored below; the engine
facts they rest on (frozen-through-2030 income tax thresholds, NI thresholds
uprating from 2028, the halved UC health element for all claimants, the
collapsed fuel-duty path) were read at the pin on 2026-09-24.
"""

import gzip
import importlib.metadata
import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PIN = "2.89.2"
BUNDLE = json.load(open(REPO / "data/uk/certified_bundle.json"))
OUT = REPO / "data/uk/ab2025_measures.json"

DATES = [f"{y}-06-01" for y in range(2025, 2032)]


def _engine_dumps():
    """(parameter path -> 2026 value, variable name -> info, year probe)."""
    import policyengine_uk
    from policyengine_core.parameters import Parameter, ParameterNode, ParameterScale

    installed = importlib.metadata.version("policyengine-uk")
    if installed != PIN:
        raise SystemExit(
            f"policyengine-uk {installed} installed, registry pinned to {PIN}"
        )
    system = policyengine_uk.CountryTaxBenefitSystem()
    params = {}

    def leaf(node, d="2026-06-01"):
        try:
            v = node(d)
        except Exception:
            return None
        if isinstance(v, float) and math.isinf(v):
            return "inf"
        if isinstance(v, float) and math.isnan(v):
            return None
        return v if isinstance(v, (int, float, str, bool)) else type(v).__name__

    def walk(node, prefix=""):
        if isinstance(node, ParameterScale):
            for i, b in enumerate(node.brackets):
                for attr in ("threshold", "rate", "amount"):
                    p = getattr(b, attr, None)
                    if p is not None:
                        params[f"{prefix}[{i}].{attr}"] = leaf(p)
            return
        if isinstance(node, Parameter):
            params[prefix] = leaf(node)
            return
        if isinstance(node, ParameterNode):
            for k in node.children:
                walk(node.children[k], f"{prefix}.{k}" if prefix else k)

    walk(system.parameters)
    variables = {
        n: {
            "entity": v.entity.key,
            "doc": (v.documentation or v.label or "")[:160],
        }
        for n, v in system.variables.items()
    }
    return params, variables


def _t41_lines():
    rows = [
        json.loads(l)
        for l in gzip.open(
            REPO / "sources/harvest-uk-2026-08-02/uk_hmt/claims_staged.jsonl.gz", "rt"
        )
    ]
    lines = {}
    for r in rows:
        c = r.get("conditions") or {}
        if c.get("fiscal_event") != "Budget 2025" or c.get("row_type") != "measure":
            continue
        e = lines.setdefault(
            str(c.get("scorecard_line")),
            {
                "line": c.get("scorecard_line"),
                "title": r["reform_hint"],
                "head": c.get("head"),
                "values": {},
            },
        )
        e["values"][c["fiscal_year"]] = r["value_raw"]
    return lines


P, V = _engine_dumps()
T41 = _t41_lines()

ISSUE = "https://github.com/PolicyEngine/policyengine-scorecard/issues/136"
PENSIONS = "https://github.com/PolicyEngine/policyengine-scorecard/issues/98"
MACRO = "https://github.com/PolicyEngine/policyengine-scorecard/issues/55"
CASES = "https://github.com/PolicyEngine/policyengine-scorecard/issues/63"
PIN = "2.89.2"

# CPI and RPI April indices at the pin (gov.economic_assumptions.indices.obr.*),
# read 2026-09-24; the reversal paths are derived from these, so they are
# recorded rather than re-read (a moved index would silently move a world).
CPI = {
    2026: 1.64763,
    2027: 1.68058,
    2028: 1.71419,
    2029: 1.74847,
    2030: 1.78344,
    2031: 1.81911,
}
RPI = {
    2025: 1.72117,
    2026: 1.77453,
    2027: 1.82777,
    2028: 1.87895,
    2029: 1.93344,
    2030: 1.97791,
    2031: 2.0234,
}


def r10(x):
    return int(round(x / 10.0)) * 10


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
    "vehicles": "policyengine-uk: vehicle ownership by fuel type and annual mileage inputs on the bundle (eVED, road pricing, EV VED)",
    "isa": "policyengine-uk: ISA holdings, subscriptions and a subscription-limit parameter",
    "pcls": "policyengine-uk: pension commencement (tax-free) lump sum and its cap (#98)",
    "estates": "policyengine-uk: estates, bequests and inheritance tax (nil-rate bands, APR/BPR)",
    "cgt_death": "policyengine-uk: a death event and the CGT base-cost uplift on death",
    "ni_base": "policyengine-uk: an NI base extension switch (rental, investment and pension income)",
    "partnership": "policyengine-uk: partnership/LLP identification within self-employment income",
    "uc_deductions": "policyengine-uk: UC deductions (advances, debts, third-party) and a deductions cap",
    "fsm": "policyengine-uk: a formula and eligibility parameters for free_school_meals (currently an input)",
    "claim_history": "policyengine-uk: claim-start history so new-claimant rules (UC health element) can be applied to new claimants only",
}

measures = []


def announced(line, key, program, computability, **kw):
    t = T41[str(line)]
    m = {
        "measure_key": f"ab2025__{key}",
        "title": t["title"].strip(),
        "reported_status": "announced",
        "source_note": f"HM Treasury, Budget 2025 Table 4.1 line {line} ({t['head']}); exchequer impact GBP m by FY: {t['values']}",
        "table_41_line": line,
        "table_41_head": t["head"],
        "program": program,
        "computability": computability,
        "obr_pmd_measure_key": kw.pop(
            "obr_pmd_measure_key", f"autumn_budget_2025__{key}"
        ),
    }
    m.update(kw)
    measures.append(m)
    return m


def option(key, title, program, computability, producers, source_note, **kw):
    """An option another producer costed for this Budget.

    ``**kw`` carries the entry's optional fields (pe_reform_delta, delta_kind,
    engine_baseline_2026, head_variables, note, …) and, on the IFS Green Budget
    options, ``related_reckoner_reforms``: the HMRC ready-reckoner lines
    (reform keys of the uk_hmrc reckoner claims already in the DB,
    ingest_uk_externals) that score the same lever. The IFS Green Budget
    Table 4.1 yields ARE those reckoner numbers (restated, dropped under #86),
    so the option joins the reckoner rows instead of re-staging them.
    """
    m = {
        "measure_key": f"ab2025_option__{key}",
        "title": title,
        "reported_status": "option_costed_by_others",
        "source_note": source_note,
        "producers": producers,
        "program": program,
        "computability": computability,
        "obr_pmd_measure_key": None,
    }
    m.update(kw)
    measures.append(m)
    return m


def gap(why, pattern, *, scope=False, upstream=None, link=None, nearest=None):
    d = {"pe_reform_delta": None, "why": why, "name_search": ns(pattern)}
    if scope:
        d["out_of_model_scope"] = True
        d["action_link"] = link or ISSUE
    else:
        d["policyengine_uk_development_item"] = True
        d["upstream_item"] = UPSTREAM[upstream]
        d["action_link"] = link or ISSUE
    if nearest:
        d["nearest_variable_and_why_it_does_not_work"] = nearest
    return d


def scope_gap(why, pattern, link=None):
    return gap(why, pattern, scope=True, link=link)


# ---------------------------------------------------------------------------
# Announced measures: HMT Budget 2025 Table 4.1, all 88 lines
# ---------------------------------------------------------------------------

# --- household-facing, expressible (mostly already in the certified baseline) ---

pa_path = "gov.hmrc.income_tax.allowances.personal_allowance.amount"
hrt_path = "gov.hmrc.income_tax.rates.uk[1].threshold"
pt_path = "gov.hmrc.national_insurance.class_1.thresholds.primary_threshold"
uel_path = "gov.hmrc.national_insurance.class_1.thresholds.upper_earnings_limit"
lpl_path = "gov.hmrc.national_insurance.class_4.thresholds.lower_profits_limit"
upl_path = "gov.hmrc.national_insurance.class_4.thresholds.upper_profits_limit"
st_path = "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold"

idx_pa = {str(y): r10(12570 * CPI[y] / CPI[2027]) for y in (2028, 2029, 2030)}
idx_hrt = {str(y): r10(37700 * CPI[y] / CPI[2027]) for y in (2028, 2029, 2030)}
idx_pt = {str(y): round(241.73 * CPI[y] / CPI[2027], 2) for y in (2028, 2029, 2030)}
idx_uel = {str(y): round(966.73 * CPI[y] / CPI[2027], 2) for y in (2028, 2029, 2030)}
idx_lpl = {str(y): r10(12570 * CPI[y] / CPI[2027]) for y in (2028, 2029, 2030)}
idx_upl = {str(y): r10(50270 * CPI[y] / CPI[2027]) for y in (2028, 2029, 2030)}
idx_st = {str(y): round(96 * CPI[y] / CPI[2027], 2) for y in (2028, 2029, 2030)}
# the two-year option's 2030-31 values: the 2027-28 level uprated ONCE by the
# path's own 2030 step (April 2030 CPI / April 2029 CPI)
_once = CPI[2030] / CPI[2029]
once_pa = r10(12570 * _once)
once_hrt = r10(37700 * _once)
once_pt = round(241.73 * _once, 2)
once_uel = round(966.73 * _once, 2)
once_lpl = r10(12570 * _once)
once_upl = r10(50270 * _once)

announced(
    46,
    "personal_tax_thresholds_freeze_to_2031",
    "income_tax",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__personal_tax_and_nics_threshold_freeze_extension",
    construction="reversal_on_certified_world",
    pe_reform_delta={
        # NI legs: the certified engine uprates these from April 2028 (class 4 from
        # April 2027), so the measure's NI legs are a FORWARD delta, frozen at the
        # 2027-28 values through 2030-31.
        pt_path: {"2028": 241.73, "2029": 241.73, "2030": 241.73},
        uel_path: {"2028": 966.73, "2029": 966.73, "2030": 966.73},
        lpl_path: {"2027": 12570, "2028": 12570, "2029": 12570, "2030": 12570},
        upl_path: {"2027": 50270, "2028": 50270, "2029": 50270, "2030": 50270},
    },
    delta_kind="absolute_value_by_year",
    pe_baseline_modifier={
        # IT legs are IN the certified baseline (frozen through 2030-31, uprating
        # resumes 2031); the pre-Budget world indexes them by CPI from April 2028.
        pa_path: idx_pa,
        hrt_path: idx_hrt,
        pt_path: idx_pt,
        uel_path: idx_uel,
        lpl_path: idx_lpl,
        upl_path: idx_upl,
    },
    engine_baseline_2026={
        pa_path: 12570,
        hrt_path: 37700,
        pt_path: 241.73,
        uel_path: 966.73,
        lpl_path: 12570,
        upl_path: 50270,
    },
    engine_path_2028_2031={
        pa_path: "12570 / 12570 / 12570 / 12821.41 (frozen to April 2031, then uprated)",
        pt_path: "246.56 / 251.50 / 256.53 / 261.66 (UPRATED from April 2028: the NI leg of the measure is not carried)",
        lpl_path: "13077.80 in 2028; already 12821.38 in 2027 (uprated from April 2027, which also breaks the pre-existing freeze to April 2028)",
    },
    already_in_baseline="income tax legs only",
    baseline_integrity_note=(
        "MIXED. gov.hmrc.income_tax.* thresholds are frozen through 2030-31 at the pin (uprating resumes 2031-04-06), so the income "
        "tax legs are in the certified world and are scored by REVERSAL (pe_baseline_modifier indexes them by CPI from April 2028). "
        "The NI thresholds are NOT frozen at the pin: primary threshold and UEL uprate from April 2028 and the class 4 limits from "
        "April 2027, so the NI legs are scored as a forward delta on the certified world. Rates of CPI indexation are the engine's own "
        "gov.economic_assumptions.indices.obr.consumer_price_index path (dashboard used cpih); thresholds rounded to GBP 10."
    ),
    head_variables=[
        "income_tax",
        "ni_class_1_employee",
        "ni_class_1_employer",
        "ni_class_4",
    ],
    derivation="pre-Budget path = 2027-28 value x CPI(April y)/CPI(April 2027), y = 2028..2030, rounded to GBP 10 (weekly NI thresholds to pence)",
)

announced(
    47,
    "employer_nics_secondary_threshold_freeze_to_2031",
    "national_insurance",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__employer_nics_secondary_threshold_freeze_extension",
    construction="reversal_on_certified_world",
    pe_reform_delta={st_path: 96},
    delta_kind="absolute_value",
    pe_baseline_modifier={st_path: idx_st},
    engine_baseline_2026={st_path: 96},
    already_in_baseline=True,
    note="Frozen at GBP 96/week (GBP 5,000 a year) through 2030-31 at the pin, uprated from 2031-04-06. Pre-Budget world indexes it by CPI from April 2028. OBR assumes incidence shared between wages and profits; PE's employer-NI incidence parameters are the assumptions axis (gov.contrib.policyengine.employer_ni.*).",
    head_variables=["ni_class_1_employer", "ni_employer"],
)

announced(
    48,
    "student_loans_plan2_threshold_freeze",
    "student_loans",
    "expressible",
    construction="reversal_on_certified_world",
    pe_reform_delta={"gov.hmrc.student_loans.thresholds.plan_2": 29385},
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.hmrc.student_loans.thresholds.plan_2": {
            str(y): int(round(29385 * RPI[y] / RPI[2026])) for y in (2027, 2028, 2029)
        }
    },
    engine_baseline_2026={"gov.hmrc.student_loans.thresholds.plan_2": 29385},
    already_in_baseline=True,
    caveat="Engine-expressible (plan_2 threshold frozen 2027-2029 at the pin, uprating resumes 2030; student_loan_repayment has a formula). Coverage of student_loan_plan on the certified populace-uk bundle is confirmed at compute, not here. HMT's 2026-27 GBP 5,915m is the one-off loan-book revaluation, which no household microsimulation reproduces: only the repayment legs (2027-28 onward) are comparable.",
    head_variables=["student_loan_repayment"],
    derivation="pre-Budget path = 29385 x RPI(April y)/RPI(April 2026), y = 2027..2029 (Plan 2 thresholds uprate by RPI)",
)

announced(
    49,
    "property_income_separate_rates",
    "income_tax",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__property_income_separate_rates",
    construction="reversal_on_certified_world",
    pe_reform_delta={
        "gov.hmrc.income_tax.rates.property.basic": 0.22,
        "gov.hmrc.income_tax.rates.property.higher": 0.42,
        "gov.hmrc.income_tax.rates.property.additional": 0.47,
    },
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.hmrc.income_tax.rates.property.basic": {
            "2027": 0.20,
            "2028": 0.20,
            "2029": 0.20,
            "2030": 0.20,
        },
        "gov.hmrc.income_tax.rates.property.higher": {
            "2027": 0.40,
            "2028": 0.40,
            "2029": 0.40,
            "2030": 0.40,
        },
        "gov.hmrc.income_tax.rates.property.additional": {
            "2027": 0.45,
            "2028": 0.45,
            "2029": 0.45,
            "2030": 0.45,
        },
    },
    engine_baseline_2026={
        "gov.hmrc.income_tax.rates.property.basic": 0.2,
        "gov.hmrc.income_tax.rates.property.higher": 0.4,
        "gov.hmrc.income_tax.rates.property.additional": 0.45,
    },
    already_in_baseline=True,
    note="The subtree carries 0.22/0.42/0.47 from 2027-01-01 at the pin (baseline_integrity.json announced__property_income_tax_rates, verdict carried). HMT's costing includes landlord incorporation and rent/house-price responses; PE is static.",
    head_variables=["income_tax"],
)

announced(
    50,
    "dividend_rates_plus_2pp",
    "income_tax",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__dividend_income_rate_increase",
    construction="reversal_on_certified_world",
    pe_reform_delta={
        "gov.hmrc.income_tax.rates.dividends[0].rate": 0.1075,
        "gov.hmrc.income_tax.rates.dividends[1].rate": 0.3575,
    },
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.hmrc.income_tax.rates.dividends[0].rate": {
            str(y): 0.0875 for y in range(2026, 2031)
        },
        "gov.hmrc.income_tax.rates.dividends[1].rate": {
            str(y): 0.3375 for y in range(2026, 2031)
        },
    },
    engine_baseline_2026={
        "gov.hmrc.income_tax.rates.dividends[0].rate": 0.1075,
        "gov.hmrc.income_tax.rates.dividends[1].rate": 0.3575,
    },
    already_in_baseline=True,
    note="Ordinary 8.75->10.75 and upper 33.75->35.75 from 2026-04-06 at the pin; additional rate unchanged at 39.35. #56 records the dividend band thresholds lagging the main bands before 2026-04-06 (policyengine-uk#1822), which does not affect 2026-27 onward.",
    head_variables=["income_tax", "dividend_income_tax"],
)

announced(
    51,
    "savings_rates_plus_2pp_and_starter_limit_held",
    "income_tax",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__savings_income_rates_and_starter_limit",
    construction="reversal_on_certified_world",
    pe_reform_delta={
        "gov.hmrc.income_tax.rates.savings.basic": 0.22,
        "gov.hmrc.income_tax.rates.savings.higher": 0.42,
        "gov.hmrc.income_tax.rates.savings.additional": 0.47,
        "gov.hmrc.income_tax.rates.savings_starter_rate.allowance": 5000,
    },
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.hmrc.income_tax.rates.savings.basic": {
            "2027": 0.20,
            "2028": 0.20,
            "2029": 0.20,
            "2030": 0.20,
        },
        "gov.hmrc.income_tax.rates.savings.higher": {
            "2027": 0.40,
            "2028": 0.40,
            "2029": 0.40,
            "2030": 0.40,
        },
        "gov.hmrc.income_tax.rates.savings.additional": {
            "2027": 0.45,
            "2028": 0.45,
            "2029": 0.45,
            "2030": 0.45,
        },
    },
    engine_baseline_2026={
        "gov.hmrc.income_tax.rates.savings.basic": 0.2,
        "gov.hmrc.income_tax.rates.savings.higher": 0.4,
        "gov.hmrc.income_tax.rates.savings.additional": 0.45,
        "gov.hmrc.income_tax.rates.savings_starter_rate.allowance": 5000,
    },
    already_in_baseline=True,
    note="Rates 0.22/0.42/0.47 from 2027 at the pin. The starting-rate limit is GBP 5,000 throughout; 'maintain to April 2031' is a hold against an indexation counterfactual HMT scores at GBP 5m/55m, so the reversal leaves it at 5,000 (no indexed path is published to reverse to). ISA-composition behavioural responses are outside a static run.",
    head_variables=["income_tax", "savings_income_tax"],
)

announced(
    52,
    "salary_sacrifice_pension_nics_cap_2000",
    "national_insurance",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__salary_sacrifice_pension_nics_cap",
    construction="reversal_on_certified_world",
    pe_reform_delta={"gov.hmrc.national_insurance.salary_sacrifice_pension_cap": 2000},
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": {
            "2029": None,
            "2030": None,
        }
    },
    uncapped_sentinel="inf, recorded as null in JSON — the pre-Budget world has no cap (data/uk/nics_salary_sacrifice_reform.json convention)",
    engine_baseline_2026={
        "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": None
    },
    already_in_baseline=True,
    note="Cap of GBP 2,000 from 2029-04-06 at the pin (inf before). The assumption sweep (broad-base haircut ON by default at 0.0016, employee reduction OFF) and the divergence axes are specified in data/uk/nics_salary_sacrifice_reform.json (ab2025__salary_sacrifice_ni_cap); this registry entry is the port's key for the same measure.",
    also_specified_in="data/uk/nics_salary_sacrifice_reform.json",
    head_variables=[
        "salary_sacrifice_pension_ni_employee",
        "salary_sacrifice_pension_ni_employer",
        "salary_sacrifice_broad_base_haircut",
        "national_insurance",
    ],
)

announced(
    54,
    "high_value_council_tax_surcharge",
    "council_tax",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__high_value_council_tax_surcharge",
    construction="reversal_on_certified_world",
    pe_reform_delta={
        "gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": 2500
    },
    delta_kind="absolute_value",
    pe_baseline_modifier={
        f"gov.hmrc.council_tax.high_value_surcharge.amount[{i}].amount": {
            "2028": 0,
            "2029": 0,
            "2030": 0,
        }
        for i in (1, 2, 3, 4)
    },
    engine_baseline_2026={
        "gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": 2500,
        "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": 3500,
        "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": 5000,
        "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": 7500,
    },
    already_in_baseline=True,
    note="Schedule 2,500/3,500/5,000/7,500 at 2m/2.5m/3.5m/5m from 2028 (formula returns 0 before 2028), uprated from 2029 (baseline_integrity.json ab2025__high_value_council_tax_surcharge, verdict carried). Credibility annotation, not a gap: main_residence_value above GBP 2m is WAS-imputed on the bundle; Tax Policy Associates' Land Registry constituency split and the OBR's 2 Apr 2026 band counts (71k/54k/25k/15k) are the external checks on the base.",
    head_variables=["high_value_council_tax_surcharge"],
)

announced(
    6,
    "uc_child_element_remove_two_child_limit",
    "universal_credit",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__uc_child_element_remove_two_child_limit",
    construction="reversal_on_certified_world",
    pe_reform_delta={
        "gov.dwp.universal_credit.elements.child.limit.child_count": None,
        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": None,
    },
    uncapped_sentinel="inf (limit removed), recorded as null in JSON",
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.dwp.universal_credit.elements.child.limit.child_count": {
            str(y): 2 for y in range(2026, 2031)
        },
        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": {
            str(y): 2 for y in range(2026, 2031)
        },
    },
    engine_baseline_2026={
        "gov.dwp.universal_credit.elements.child.limit.child_count": None,
        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": None,
    },
    already_in_baseline=True,
    baseline_world="pre_ab2025",
    note="2 in 2025, inf from 2026-04-06 at the pin. The reinstated world pre_ab2025 is already registered (baselines.py) and executed (sources/campaign-20260802/uk_runs/two_child_reinstate_2026.json). Two PE legs exist: calibrated take-up (UC delta GBP 1.104bn 2026, 0.56-0.59x OBR) and forced full take-up (GBP 1.850bn, ~0.98x); HMT's costing adds 11%/22% extra take-up and a benefit-cap interaction. The take-up/caseload axis is the reconciliation (obr_divergence_axes.json).",
    head_variables=["universal_credit", "child_tax_credit"],
)

announced(
    3,
    "fuel_duty_freeze_extension_2026_27",
    "fuel_duty",
    "expressible",
    construction="reversal_on_certified_world",
    pe_reform_delta={"gov.hmrc.fuel_duty.petrol_and_diesel": 0.5345},
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.hmrc.fuel_duty.petrol_and_diesel": {
            "2026-03-23": 0.5795,
            **{
                f"{y}-04-01": round(0.5795 * RPI[y] / RPI[2025], 4)
                for y in range(2026, 2031)
            },
        }
    },
    engine_baseline_2026={"gov.hmrc.fuel_duty.petrol_and_diesel": 0.5345},
    already_in_baseline="collapsed",
    baseline_integrity_note="The pin holds 0.5345 through 2026 and steps to 0.5925 at 2027-03 — the staggered +1p (Sep 2026) / +2p (Dec 2026) / +2p (Mar 2027) path is collapsed into one step, and 0.5925 is not 0.5795 + RPI. Recorded, not corrected here: a compute run states the path it executed.",
    note="Pre-Budget world per the OBR pre-measures forecast: 5p cut ends 23 March 2026 (57.95ppl) and RPI uprating from 1 April 2026 and each April after ('cancel uprating for 2026-27' is a leg of the measure). The November dashboard held 0.58 flat in 2026 instead; that construction difference is an axis on its numbers, not on these.",
    head_variables=["fuel_duty"],
    derivation="pre-Budget path = 0.5795 x RPI(April y)/RPI(April 2025), y = 2026..2030",
)

announced(
    4,
    "rail_fares_freeze_2026",
    "rail_fares",
    "expressible",
    construction="reversal_on_certified_world",
    pe_reform_delta={"gov.dft.rail.fare_index": 1.217},
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.dft.rail.fare_index": {
            "2026": 1.288,
            "2027": 1.342,
            "2028": 1.394,
            "2029": 1.449,
            "2030": 1.449,
        }
    },
    engine_baseline_2026={"gov.dft.rail.fare_index": 1.217},
    already_in_baseline=True,
    note="Counterfactual = gov.dft.rail.prior_law_fare_index (1.288/1.342/1.394/1.449), the same construction as data/uk/rail_fares_reform.json (ab2026__rail_fares_freeze, which resolves at this pin). HMT books this under benefits in kind / public services; PE's head variables are household subsidy allocations.",
    also_specified_in="data/uk/rail_fares_reform.json",
    head_variables=["rail_subsidy_spending", "dft_subsidy_spending"],
)

announced(
    84,
    "winter_fuel_payment_income_test_35000",
    "winter_fuel_payment",
    "expressible",
    obr_pmd_measure_key="autumn_budget_2025__winter_fuel_payment_income_test",
    construction="reversal_on_certified_world",
    pe_reform_delta={
        "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": True
    },
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": {
            str(y): False for y in range(2025, 2031)
        }
    },
    engine_baseline_2026={
        "gov.dwp.winter_fuel_payment.eligibility.taxable_income_test.use_maximum_taxable_income": True
    },
    already_in_baseline=True,
    note="The pin carries the GBP 35,000 taxable-income passport (maximum_taxable_income = 35000, use_maximum_taxable_income = True, England and Wales) on top of the means-tested-benefit passport. Mechanism differs from HMRC's: the engine applies an eligibility cut-off, HMRC pays everyone over State Pension age and claws back above GBP 35,000 through the tax system — the household outcome is the same, the timing is not. Line 84 costs the June 2025 U-turn against the AB2024 restriction to Pension Credit recipients, which is what the modifier restores.",
    head_variables=["winter_fuel_allowance"],
)

announced(
    85,
    "uc_standard_allowance_and_health_element_rebalancing",
    "universal_credit",
    "partial",
    obr_pmd_measure_key="autumn_budget_2025__uc_standard_and_health_protections",
    construction="reversal_on_certified_world",
    pe_reform_delta={"gov.dwp.universal_credit.rebalancing.active": True},
    delta_kind="absolute_value",
    pe_baseline_modifier={
        "gov.dwp.universal_credit.rebalancing.active": {
            str(y): False for y in range(2026, 2031)
        }
    },
    engine_baseline_2026={"gov.dwp.universal_credit.rebalancing.active": True},
    already_in_baseline="for all claimants",
    missing="Existing-claimant protection. At the pin the halved health element (gov.dwp.universal_credit.elements.disabled.amount 423.27 -> 217.26 from 2026; rebalancing.new_claimant_health_element = 217.26) is applied by uc_LCWRA_element to EVERY claimant with limited capability, because the bundle carries no claim-start date. The standard-allowance uplift (rebalancing.standard_allowance_uplift 0.023 -> 0.048) is fully carried. The Universal Credit Act 2025 legislated this before the Budget; Table 4.1 line 85 is the protection package.",
    policyengine_uk_development_item=True,
    upstream_item=UPSTREAM["claim_history"],
    action_link=ISSUE,
    head_variables=["universal_credit", "uc_LCWRA_element", "uc_standard_allowance"],
)

announced(
    83,
    "pip_not_proceeding_with_ss2025_eligibility_reforms",
    "pip",
    "partial",
    pe_reform_delta=None,
    missing="The announcement-baseline leg (#13). Relative to current law the measure is a null change: gov.dwp.pip.* carries the unreformed award rates, and the Spring Statement 2025 four-point daily-living rule was never a parameter, so the world HMT scores against (the abandoned reform) cannot be executed. Scoring it needs the counterfactual world, not a lever.",
    policyengine_uk_development_item=False,
    out_of_model_scope=False,
    action_link=ISSUE,
    name_search=ns(r"pip|personal_independence|daily_living|four_point"),
    note="Neither a development item nor out of scope: the engine expresses PIP; what is missing is a registered baseline world for the reform that did not happen.",
)

announced(
    1,
    "renewables_obligation_exchequer_funded_75pct",
    "energy_bills",
    "partial",
    pe_reform_delta=None,
    missing="The Renewables Obligation share of an electricity bill is not a parameter. The engine has electricity_consumption (LCFS-imputed, NEED-calibrated) and a flat energy_bills_credit lever (gov.treasury.energy_bills_rebate.energy_bills_credit), so the measure is a CONSTRUCTION: bill x domestic RO share (~41%, HMT) x 75%, or the ~GBP 150 average as a flat credit. Either is stated as constructed, never comparable.",
    construction_note="electricity_consumption x 0.41 x 0.75 per household, or energy_bills_credit = the HMT average; head variable domestic_energy_consumption",
    policyengine_uk_development_item=False,
    action_link=ISSUE,
    name_search=ns(r"renewables|energy_bills|electricity_consumption|levy"),
    head_variables=["electricity_consumption", "energy_bills_rebate"],
)

announced(
    2,
    "warm_homes_plan_and_warm_home_discount_expansion",
    "energy_bills",
    "partial",
    pe_reform_delta=None,
    missing="No Warm Home Discount parameter or variable at the pin. The GBP 150 rebate to households on qualifying means-tested benefits is a CONSTRUCTION on benefit receipt using the flat energy_bills_credit lever; the Warm Homes Plan capital funding has no household incidence.",
    policyengine_uk_development_item=False,
    action_link=ISSUE,
    name_search=ns(r"warm_home|whd|energy_bills_rebate|energy_bills_credit"),
    head_variables=["energy_bills_rebate"],
)

# --- household-facing, NOT expressible: engine development items ---

announced(
    71,
    "eved_mileage_supplement_electric_and_phev",
    "vehicle_excise_duty",
    "not_expressible",
    **gap(
        "No mileage, no fuel-type split and no vehicle excise duty at the pin. The bundle carries num_vehicles and owns_vehicle (WAS-imputed, NTS-calibrated) but not whether a vehicle is electric or a plug-in hybrid, nor annual mileage, and there is no VED parameter tree to attach a per-mile supplement to. OBR's supplementary note (2 Apr 2026) sizes the base at 5.5m cars x 8,000 miles.",
        r"electric_vehicle|mileage|vehicle|excise|ved\b|_ev_|per_mile",
        upstream="vehicles",
        nearest={
            "variable": "num_vehicles",
            "entity": "household",
            "why_not": "A count of vehicles imputed from WAS; it carries no fuel type and no mileage, so neither the base (EV/PHEV) nor the rate (per mile) can be applied to it.",
        },
    ),
)

announced(
    79,
    "supporting_savers_help_to_save_and_cash_isa_limit",
    "savings",
    "not_expressible",
    **gap(
        "No ISA holdings, no subscription flows and no subscription-limit parameter at the pin. The engine has tax_free_savings_income (an income INPUT from tax-free accounts) but no stock of ISA cash, no annual subscription and no under-65 test, so the GBP 12,000 cash-ISA limit and the permanent Help to Save scheme have no lever.",
        r"(^|[_.])isa([_.]|$)|help_to_save|tax_free_savings|subscription",
        upstream="isa",
        nearest={
            "variable": "tax_free_savings_income",
            "entity": "person",
            "why_not": "Income from tax-free accounts, an input with no formula; a limit on annual cash subscriptions needs the subscription flow and the account balance, neither of which exists.",
        },
    ),
)

announced(
    55,
    "iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031",
    "inheritance_tax",
    "not_expressible",
    **gap(
        "No estates, bequests or inheritance tax at the pin: the parameter tree has no nil-rate band, residence nil-rate band or agricultural/business property relief, and no variable represents a death or an estate.",
        r"inherit|estate|probate|nil_rate|bequest|death|agricultural|business_property",
        upstream="estates",
    ),
)

announced(
    80,
    "apr_bpr_unused_allowance_transferable_between_spouses",
    "inheritance_tax",
    "not_expressible",
    **gap(
        "Inheritance tax relief on agricultural and business property: no estates or IHT at the pin (see the nil-rate-band entry).",
        r"inherit|estate|agricultural|business_property|relief_transfer",
        upstream="estates",
    ),
)

# --- household-facing, NOT expressible: out of the household model's scope ---

announced(
    60,
    "gambling_duties_rgd_40_remote_betting_25",
    "gambling_duties",
    "not_expressible",
    **scope_gap(
        "No gambling expenditure, gambling duty or gaming variable at the pin; the consumption module carries LCFS categories (alcohol_and_tobacco_consumption, recreation_consumption) with no gambling split, and the duty is levied on operators' gross gaming yield, not on a household base the engine holds.",
        r"gambl|betting|gaming|lottery|horserace|machine_games",
    ),
)

announced(
    14,
    "motability_vat_on_advance_payments_and_ipt",
    "indirect_tax",
    "not_expressible",
    **scope_gap(
        "No Motability lease, insurance premium tax or scheme-specific VAT base at the pin; Motability participation is not on the bundle.",
        r"motability|insurance_premium|ipt\b|lease",
    ),
)

announced(
    68,
    "non_reimbursed_homeworking_expenses_relief_removed",
    "income_tax",
    "not_expressible",
    **scope_gap(
        "No homeworking-expenses relief or claimant identification at the pin (HMRC's TIIN: ~300,000 homeworkers at GBP 62 / GBP 124 a year). The relief is a claim-level administrative item below the survey's resolution.",
        r"homework|working_from_home|home_office|expenses_relief",
    ),
)

announced(
    7,
    "uc_surplus_earnings_threshold_2500_extended",
    "universal_credit",
    "not_expressible",
    **scope_gap(
        "The surplus-earnings rule is a monthly assessment-period carry-over; the engine models UC on an annual basis with no assessment-period earnings history, and no surplus-earnings parameter exists.",
        r"surplus|assessment_period|earnings_threshold",
    ),
)

announced(
    8,
    "child_benefit_16_19_illness_disability_12_hour_rule_exemption",
    "child_benefit",
    "not_expressible",
    **scope_gap(
        "Child Benefit's qualifying-young-person conditions exist (education_or_training conditions, age limits) but the 12-hour weekly rule and an illness/disability exemption from it are administrative detail below the survey's resolution: no hours-of-study or non-standard-setting flag on the bundle.",
        r"child_benefit\.eligibility|qualifying_young_person|twelve_hour|12_hour|hours_of_study",
    ),
)

announced(
    10,
    "housing_benefit_cliff_edge_supported_and_temporary_accommodation",
    "housing_benefit",
    "not_expressible",
    **scope_gap(
        "No supported-housing or temporary-accommodation tenure flag on the bundle; Housing Benefit income disregards exist as parameters but the population the measure targets cannot be identified.",
        r"supported_housing|temporary_accommodation|exempt_accommodation|housing_benefit\.means_test\.income",
    ),
)

announced(
    9,
    "carers_allowance_overpayments_review",
    "carers_allowance",
    "not_expressible",
    **scope_gap(
        "Administrative review of historic overpayments (2015-2025 earnings-averaging guidance); no overpayment history on the bundle and no parametric representation.",
        r"carer|overpayment",
    ),
)
announced(
    11,
    "dwp_fraud_and_error_uc_targeted_case_review_extended",
    "administration",
    "not_expressible",
    **scope_gap(
        "Administrative fraud-and-error yield; no parametric representation of case reviews.",
        r"fraud|error|case_review|targeted",
    ),
)
announced(
    12,
    "dwp_fraud_and_error_pension_credit_accuracy_reviews",
    "administration",
    "not_expressible",
    **scope_gap(
        "Administrative accuracy reviews of Pension Credit claims; no parametric representation.",
        r"fraud|error|accuracy|review",
    ),
)
announced(
    13,
    "health_and_disability_benefits_operations",
    "administration",
    "not_expressible",
    **scope_gap(
        "Operational delivery (face-to-face assessments, WCA reassessment capacity, PIP award-review frequency); the engine expresses award rates and eligibility, not assessment throughput.",
        r"assessment|reassess|award_review|wca",
    ),
)
announced(
    15,
    "hb_and_pension_credit_administration_brought_together",
    "administration",
    "not_expressible",
    **scope_gap(
        "Administrative consolidation of pensioner Housing Benefit and Pension Credit; the yield is a take-up-and-accuracy effect of joint administration with no parametric lever.",
        r"administration|consolidat|merge",
    ),
)
announced(
    16,
    "nics_class_2_abroad_removed_and_class_3_residency_requirement",
    "national_insurance",
    "not_expressible",
    **scope_gap(
        "Voluntary Class 2/3 contributions by people living abroad; the bundle is UK-resident households and carries no contributions history.",
        r"class_2|class_3|voluntary|abroad|contributions_history",
    ),
)
announced(
    5,
    "nhs_prescription_charges_frozen_2026",
    "benefits_in_kind",
    "not_expressible",
    **scope_gap(
        "NHS prescription charges are not modelled; the engine allocates NHS SPENDING as a benefit in kind (nhs_spending and its components) with no charge on the household side.",
        r"prescription|nhs_charge|nhs_spending",
    ),
)
announced(
    53,
    "cgt_employee_ownership_trust_relief_cut_to_50pct",
    "capital_gains_tax",
    "not_expressible",
    **scope_gap(
        "Disposals to employee ownership trusts are business disposals; capital_gains is a single realised-gains variable with no disposal type or relief split.",
        r"employee_ownership|eot|cgt|capital_gains|relief",
    ),
)
announced(
    56,
    "trust_charges_cap_and_post_departure_trade_profits",
    "trusts",
    "not_expressible",
    **scope_gap(
        "Excluded-property trust charges and post-departure trade profits: no trusts, no non-domicile status and no emigration event at the pin.",
        r"trust|domicile|non_dom|departure",
    ),
)
announced(
    22,
    "vct_income_tax_relief_reduced",
    "income_tax",
    "not_expressible",
    **scope_gap(
        "Venture Capital Trust income tax relief is not modelled: no VCT subscription variable and no relief parameter.",
        r"venture|vct|eis|investment_relief",
    ),
)
announced(
    21,
    "vct_and_eis_investment_limits_increased",
    "income_tax",
    "not_expressible",
    **scope_gap(
        "VCT/EIS scheme limits: company-side investment limits with no household base at the pin.",
        r"venture|vct|eis",
    ),
)
announced(
    62,
    "toms_private_hire_vehicles_excluded",
    "indirect_tax",
    "not_expressible",
    **scope_gap(
        "Tour Operators' Margin Scheme VAT on private-hire services: an operator-side VAT scheme; household VAT is modelled on LCFS consumption categories with no private-hire split.",
        r"private_hire|tour_operator|toms|taxi",
    ),
)
announced(
    73,
    "expensive_car_supplement_threshold_for_zevs_50000",
    "vehicle_excise_duty",
    "not_expressible",
    **scope_gap(
        "Vehicle excise duty is not modelled and vehicle purchase price is not on the bundle.",
        r"expensive_car|vehicle_excise|ved\b|car_purchase",
    ),
)
announced(
    74,
    "employee_car_ownership_schemes_bik_delayed",
    "income_tax",
    "not_expressible",
    **scope_gap(
        "Company-car / employee-car-ownership benefit in kind is not modelled; no company-car variable on the bundle.",
        r"company_car|car_ownership|benefit_in_kind|bik",
    ),
)
announced(
    77,
    "phev_emissions_standard_and_bik_easement",
    "income_tax",
    "not_expressible",
    **scope_gap(
        "Company-car benefit in kind by emissions band is not modelled.",
        r"phev|emissions_standard|benefit_in_kind|company_car",
    ),
)
announced(
    78,
    "student_finance_lle_launch_and_loan_outlay",
    "student_loans",
    "not_expressible",
    **scope_gap(
        "Lifelong Learning Entitlement loan outlay: a loan-issuance policy, not a repayment rule; the engine models repayments on income by plan type.",
        r"lifelong|lle|loan_outlay|student_finance",
    ),
)
announced(
    82,
    "ppf_and_fas_pre_1997_inflation_protection",
    "pensions",
    "not_expressible",
    **scope_gap(
        "Pension Protection Fund / Financial Assistance Scheme indexation of pre-1997 pensions: scheme-specific, no PPF membership flag on the bundle.",
        r"ppf|pension_protection|financial_assistance|pre_1997",
    ),
)
announced(
    81,
    "british_coal_staff_superannuation_scheme_reserve_transfer",
    "pensions",
    "not_expressible",
    **scope_gap(
        "One-off transfer of a scheme's investment reserve to its members; scheme membership is not on the bundle.",
        r"coal|superannuation|reserve_transfer",
    ),
)
announced(
    65,
    "db_pension_scheme_surplus_extraction",
    "pensions",
    "not_expressible",
    **scope_gap(
        "Employer-side defined-benefit surplus rules; no scheme-level representation.",
        r"surplus|defined_benefit|scheme",
    ),
)
announced(
    86,
    "loan_charge_review_response",
    "income_tax",
    "not_expressible",
    **scope_gap(
        "Disguised-remuneration loan charge settlements: a historic-liability administrative measure with no bundle population.",
        r"loan_charge|disguised|remuneration",
    ),
)
announced(
    87,
    "compensation_payments_post_office_capture_and_infected_blood",
    "spending",
    "not_expressible",
    **scope_gap(
        "Compensation schemes for identified individuals; no bundle population.",
        r"compensation|post_office|infected_blood",
    ),
)
announced(
    88,
    "tariffs_changes_since_spring_2025",
    "customs",
    "not_expressible",
    **scope_gap(
        "Customs tariffs; no import price incidence module.", r"tariff|customs|import"
    ),
)
announced(
    63,
    "low_value_imports_customs_reform",
    "customs",
    "not_expressible",
    **scope_gap(
        "Customs treatment of low-value imports; no import price incidence module.",
        r"customs|import|low_value",
    ),
)
announced(
    58,
    "apd_higher_rate_extended_to_private_jets",
    "indirect_tax",
    "not_expressible",
    **scope_gap(
        "Air passenger duty is not modelled and private-jet travel is not on the bundle.",
        r"air_passenger|apd|aviation|private_jet",
    ),
)
announced(
    66,
    "landfill_tax_lower_rate_increase",
    "indirect_tax",
    "not_expressible",
    **scope_gap(
        "Landfill tax is a producer-side environmental tax with no household incidence module.",
        r"landfill|waste",
    ),
)
announced(
    67,
    "sdil_threshold_cut_and_milk_based_drinks",
    "indirect_tax",
    "not_expressible",
    **scope_gap(
        "The Soft Drinks Industry Levy is a producer-side levy; the consumption module has no sugary-drinks category and no levy pass-through.",
        r"soft_drink|sugar|sdil|levy",
    ),
)
announced(
    64,
    "ets_expansion_to_international_maritime",
    "environmental_tax",
    "not_expressible",
    **scope_gap(
        "UK ETS on maritime routes: an emitter-side carbon price with no household incidence path at the pin (the contrib carbon tax is a separate, off-by-default lever).",
        r"emission|ets\b|carbon_price|maritime|shipping",
    ),
)
announced(
    69,
    "cbam_indirect_emissions_removed",
    "environmental_tax",
    "not_expressible",
    **scope_gap(
        "Carbon border adjustment on imports: producer-side, no household incidence path.",
        r"cbam|carbon_border|indirect_emissions",
    ),
)
announced(
    57,
    "writing_down_allowances_14pct_and_40pct_fya",
    "corporation_tax",
    "not_expressible",
    **scope_gap(
        "Corporation tax capital allowances; business-side.",
        r"writing_down|capital_allowance|first_year_allowance|corporation",
    ),
)
announced(
    70,
    "advanced_corporation_tax_shadow_act_abolished",
    "corporation_tax",
    "not_expressible",
    **scope_gap(
        "Shadow ACT restrictions; business-side corporation tax.",
        r"corporation|act\b|shadow",
    ),
)
announced(
    20,
    "emi_eligibility_extended_to_scale_ups",
    "corporation_tax",
    "not_expressible",
    **scope_gap(
        "Enterprise Management Incentives: company share-option scheme eligibility; no household base.",
        r"emi\b|share_option|enterprise_management",
    ),
)
announced(
    23,
    "uk_listing_relief_sdrt",
    "stamp_taxes",
    "not_expressible",
    **scope_gap(
        "Stamp Duty Reserve Tax relief on newly listed securities; no securities-transaction base (stamp duty at the pin is land tax).",
        r"sdrt|reserve_tax|listing|securities",
    ),
)
announced(
    18,
    "business_rates_transitional_relief_and_supplement",
    "business_rates",
    "not_expressible",
    **scope_gap(
        "Per-property business rates schemes; the engine holds only an aggregate business_rates incidence via corporate shareholdings (gov.hmrc.business_rates.statistics.revenue.*), not the rating list.",
        r"business_rate|transitional|multiplier|rateable",
    ),
)
announced(
    19,
    "business_rates_rhl_lower_multipliers_and_high_value_multiplier",
    "business_rates",
    "not_expressible",
    **scope_gap(
        "Per-property retail, hospitality and leisure multipliers; only aggregate business-rates incidence exists at the pin.",
        r"business_rate|multiplier|retail|hospitality",
    ),
)
announced(
    35,
    "business_rates_retention_gla_and_pilots",
    "business_rates",
    "not_expressible",
    **scope_gap(
        "Local-government revenue retention arrangements; no household incidence.",
        r"business_rate|retention",
    ),
)
announced(
    28,
    "vat_relief_business_donations_of_goods_to_charity",
    "vat",
    "not_expressible",
    **scope_gap(
        "Business-side VAT relief on donated goods; household VAT is modelled on consumption only.",
        r"vat|donation|charity",
    ),
)
announced(
    29,
    "cross_border_vat_grouping_reverted",
    "vat",
    "not_expressible",
    **scope_gap(
        "Corporate VAT grouping rules; business-side.",
        r"vat_group|cross_border|grouping",
    ),
)
announced(
    59,
    "hmrc_further_measures_to_close_the_tax_gap",
    "administration",
    "not_expressible",
    **scope_gap(
        "Compliance yield from HMRC operational investment; no parametric representation.",
        r"tax_gap|compliance|enforcement",
    ),
)
announced(
    75,
    "fya_zero_emission_cars_and_charge_points_extended",
    "corporation_tax",
    "not_expressible",
    **scope_gap(
        "Corporation tax first-year allowances; business-side.",
        r"first_year_allowance|zero_emission|charge_point|capital_allowance",
    ),
)

# --- spending lines: out of scope (no household incidence in a tax-benefit model) ---
for line, key, why, pat in [
    (
        17,
        "rebuilding_britain_capital_investment",
        "Capital investment (Lower Thames Crossing and other projects); public-services spending with no household tax-benefit incidence.",
        r"capital_investment|infrastructure",
    ),
    (
        24,
        "jobs_and_skills_youth_guarantee_and_levy",
        "Youth Guarantee, Growth and Skills Levy and employment support: departmental spending, no household transfer modelled.",
        r"youth|guarantee|skills_levy|apprentice",
    ),
    (
        25,
        "planning_capacity_and_capability",
        "Departmental spending on the planning system.",
        r"planning",
    ),
    (
        26,
        "british_business_bank_growth_guarantee_scheme",
        "Loan-guarantee scheme for businesses.",
        r"guarantee_scheme|business_bank",
    ),
    (
        27,
        "illegal_high_street_operations_taskforce",
        "Enforcement spending.",
        r"taskforce|trading_standards|insolvency",
    ),
    (
        30,
        "national_level_regulation_food_businesses",
        "Regulatory-burden funding for large food businesses.",
        r"regulation|food_business",
    ),
    (31, "fisheries_and_coastal_growth_fund", "Sector fund.", r"fisheries|coastal"),
    (
        32,
        "innovation_in_wales_semiconductor_cluster",
        "Sector investment.",
        r"semiconductor|innovation",
    ),
    (
        33,
        "northern_ireland_post_brexit_trade_support",
        "Trade support spending.",
        r"trade_support|northern_ireland",
    ),
    (
        34,
        "kernow_industrial_growth_fund",
        "Regional fund.",
        r"kernow|cornwall|growth_fund",
    ),
    (
        36,
        "port_talbot_brownfield_remediation",
        "Land remediation spending.",
        r"port_talbot|remediation|brownfield",
    ),
    (
        37,
        "rdel_efficiencies_and_savings",
        "Departmental resource savings (RDEL); no household incidence.",
        r"rdel|efficienc",
    ),
    (
        38,
        "nhs_england_abolition_funding_brought_forward",
        "NHS administrative restructuring; the engine allocates NHS spending as a benefit in kind at the aggregate, not by administrative programme.",
        r"nhs_england|abolition",
    ),
    (
        39,
        "nhs_technology_investment",
        "NHS capital/technology spending.",
        r"nhs_technology|productivity",
    ),
    (
        40,
        "home_office_people_smuggling_funding",
        "Enforcement spending.",
        r"home_office|smuggling",
    ),
    (
        41,
        "systems_and_compliance_investment_hmrc_dwp",
        "Investment in HMRC/DWP systems and compliance; yields sit in other lines.",
        r"compliance|systems",
    ),
    (42, "national_year_of_reading_book_funding", "Schools spending.", r"reading|book"),
    (43, "playground_refurbishment_funding", "Local capital spending.", r"playground"),
    (
        44,
        "environmental_regeneration_grant_scheme",
        "Grant scheme for public bodies.",
        r"regeneration|remediation|water_company",
    ),
    (
        45,
        "uk_eu_sps_agreement_defra_costs",
        "Departmental implementation costs.",
        r"defra|sanitary|phytosanitary",
    ),
    (
        61,
        "gambling_commission_illegal_market_funding",
        "Regulator funding.",
        r"gambling_commission|illegal_market",
    ),
    (
        72,
        "electric_car_grant_and_charging_infrastructure",
        "Purchase grant and charging capital; vehicle purchases are not on the bundle (the SMF's grant-adjusted figure is an OBR restatement).",
        r"electric_car_grant|charging|grant",
    ),
    (
        76,
        "sizewell_c_rab_levy_reclassification",
        "Regulated Asset Base levy accounting on energy bills: a classification change; the household bill incidence of the RAB levy is not separated in electricity_consumption.",
        r"sizewell|regulated_asset|rab_levy|nuclear",
    ),
]:
    announced(line, key, "spending", "not_expressible", **scope_gap(why, pat))

# --- package totals ---
for key, title, head in [
    ("package_total_policy_decisions", "Total policy decisions (Table 4.1)", "Total"),
    (
        "package_total_tax_policy_decisions",
        "Total tax policy decisions (Table 4.1)",
        "Tax",
    ),
    (
        "package_total_spending_policy_decisions",
        "Total spending policy decisions (Table 4.1)",
        "Spend",
    ),
]:
    measures.append(
        {
            "measure_key": f"ab2025__{key}",
            "title": title,
            "reported_status": "announced",
            "source_note": "HM Treasury, Budget 2025 Table 4.1 totals rows",
            "table_41_head": head,
            "program": "package",
            "computability": "partial",
            "pe_reform_delta": None,
            "construction": "package_of_registry_measures",
            "package_of": "every ab2025__ measure in this registry with the matching table_41_head",
            "missing": "The package total sums measures the household model cannot express (business taxes, administrative yields, departmental spending). A PE package number is the sum of the expressible household legs only, stated as constructed with the omitted lines listed; it is never compared to the Table 4.1 total as if like-for-like.",
            "action_link": ISSUE,
            "obr_pmd_measure_key": None,
        }
    )

# Like-for-like packages other producers scored
measures.append(
    {
        "measure_key": "ab2025__package_ifs_decile_chart_scope",
        "title": "IFS 27 Nov 2025 decile chart package: the Budget's tax and benefit measures affecting household incomes, 2026-27 and 2030-31",
        "reported_status": "announced",
        "source_note": "IFS 'Autumn Budget 2025: initial response' event, 27 Nov 2025 (Flourish visualisation 26495404); scope note on the chart lists the measures included and excluded",
        "program": "package",
        "computability": "partial",
        "pe_reform_delta": None,
        "construction": "package_of_registry_measures",
        "package_of": [
            "ab2025__uc_child_element_remove_two_child_limit",
            "ab2025__personal_tax_thresholds_freeze_to_2031",
            "ab2025__dividend_rates_plus_2pp",
            "ab2025__savings_rates_plus_2pp_and_starter_limit_held",
            "ab2025__property_income_separate_rates",
            "ab2025__salary_sacrifice_pension_nics_cap_2000",
            "ab2025__fuel_duty_freeze_extension_2026_27",
            "ab2025__winter_fuel_payment_income_test_35000",
            "ab2025__uc_standard_allowance_and_health_element_rebalancing",
        ],
        "missing": "The exact composition is the IFS chart's own scope note (read at harvest and carried on the claim); the energy-bill and rail legs are stated per that note. A PE package is stated as constructed until the composition is confirmed leg by leg.",
        "action_link": ISSUE,
        "obr_pmd_measure_key": None,
    }
)
measures.append(
    {
        "measure_key": "ab2025__package_ukmod_wp3_26",
        "title": "UKMOD (CeMPA WP 3/26) Autumn Budget 2025 package: income tax threshold freezes, UC two-child limit removal, Winter Fuel Allowance restrictions, Pension Credit reductions",
        "reported_status": "announced",
        "source_note": "ISER CeMPA working paper 3/26 (Frimpong, 18 Feb 2026) on UKMOD B2025.09, FRS 2023-24: static scoring of the package over 2026-2030, fixed-line poverty; staged as harvest family uk_ukmod_ab2025",
        "program": "package",
        "computability": "partial",
        "pe_reform_delta": None,
        "construction": "package_of_registry_measures",
        "package_of": [
            "ab2025__personal_tax_thresholds_freeze_to_2031",
            "ab2025__uc_child_element_remove_two_child_limit",
            "ab2025__winter_fuel_payment_income_test_35000",
        ],
        "package_note": "The paper names four components; three are registry measures. Its 'Pension Credit reductions' has no Table 4.1 line and is carried in the paper's own words on every row (reform_hint), not as a registry measure.",
        "missing": "The Pension Credit leg is not a registry measure; UKMOD's poverty statistics hold the 2026 baseline line fixed (ukmod_b2025_09_fixed_baseline_line, #13), so a PE counterpart states the line it used.",
        "action_link": ISSUE,
        "obr_pmd_measure_key": None,
    }
)

# ---------------------------------------------------------------------------
# Options scored for this Budget by other producers (185 claims in the inventory)
# ---------------------------------------------------------------------------
ifs = "IFS Green Budget 2025 chapter 4 'Options for tax increases' (13 Oct 2025), Table 4.1"
rf_cod = "Resolution Foundation 'Call of duties' (23 Sep 2025) Table 2 and 'Black holes and consolidations' (4 Nov 2025) Table 1"


def o(key, title, program, comp, producers, source_note, **kw):
    return option(key, title, program, comp, producers, source_note, **kw)


# income tax and NICs rates
o(
    "income_tax_basic_rate_plus_1p",
    "Income tax basic rate 20% to 21%",
    "income_tax",
    "expressible",
    ["ifs", "aj_bell", "tax_policy_associates"],
    f"{ifs}; AJ Bell pre-Budget worked examples; TPA Budget calculator",
    pe_reform_delta={"gov.hmrc.income_tax.rates.uk[0].rate": 0.21},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.hmrc.income_tax.rates.uk[0].rate": 0.2},
    head_variables=["income_tax"],
    related_reckoner_reforms=["trr_income_tax_change_basic_rate_by_1p"],
)
o(
    "income_tax_all_rates_plus_1p",
    "All income tax rates +1ppt (20/40/45 to 21/41/46)",
    "income_tax",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.hmrc.income_tax.rates.uk[0].rate": 0.21,
        "gov.hmrc.income_tax.rates.uk[1].rate": 0.41,
        "gov.hmrc.income_tax.rates.uk[2].rate": 0.46,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.income_tax.rates.uk[0].rate": 0.2,
        "gov.hmrc.income_tax.rates.uk[1].rate": 0.4,
        "gov.hmrc.income_tax.rates.uk[2].rate": 0.45,
    },
    head_variables=["income_tax"],
    note="IFS also costs the higher and additional rates alone; those are the [1]/[2] legs of this entry, staged with their own reform_hint.",
    related_reckoner_reforms=[
        "trr_income_tax_change_basic_rate_by_1p",
        "trr_income_tax_change_higher_rate_by_1p",
        "trr_income_tax_increase_additional_rate_by_1p_yield",
    ],
)
o(
    "income_tax_basic_rate_plus_2p",
    "Income tax basic rate 20% to 22%",
    "income_tax",
    "expressible",
    ["aj_bell"],
    "AJ Bell pre-Budget worked examples (rumoured option)",
    pe_reform_delta={"gov.hmrc.income_tax.rates.uk[0].rate": 0.22},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.hmrc.income_tax.rates.uk[0].rate": 0.2},
    head_variables=["income_tax"],
)
o(
    "income_tax_plus_2p_employee_nics_minus_2p_switch",
    "2p switch: all income tax rates +2p, employee NI main and additional rates -2p",
    "income_tax",
    "expressible",
    ["resolution_foundation", "ippr", "tax_policy_associates"],
    f"{rf_cod}; RF 'It's personal (taxation)' (27 Oct 2025); IPPR 'Fairness first' (19 Nov 2025); TPA calculator",
    pe_reform_delta={
        "gov.hmrc.income_tax.rates.uk[0].rate": 0.22,
        "gov.hmrc.income_tax.rates.uk[1].rate": 0.42,
        "gov.hmrc.income_tax.rates.uk[2].rate": 0.47,
        "gov.hmrc.national_insurance.class_1.rates.employee.main": 0.06,
        "gov.hmrc.national_insurance.class_1.rates.employee.additional": 0.0,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.income_tax.rates.uk[0].rate": 0.2,
        "gov.hmrc.income_tax.rates.uk[1].rate": 0.4,
        "gov.hmrc.income_tax.rates.uk[2].rate": 0.45,
        "gov.hmrc.national_insurance.class_1.rates.employee.main": 0.08,
        "gov.hmrc.national_insurance.class_1.rates.employee.additional": 0.02,
    },
    head_variables=["income_tax", "ni_class_1_employee"],
    note="RF's variant leaves self-employed and rental income at the higher IT rate with no NI offset (the incidence on pensioners is its point); IPPR's is a plain 2p/2p switch. Staged with their own reform_hints; one registry key because the lever set is the same.",
)
o(
    "nics_employee_and_self_employed_rates_plus_1p",
    "Employee NICs 8% to 9% and 2% to 3%; self-employed 6% to 7% and 2% to 3%",
    "national_insurance",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.hmrc.national_insurance.class_1.rates.employee.main": 0.09,
        "gov.hmrc.national_insurance.class_1.rates.employee.additional": 0.03,
        "gov.hmrc.national_insurance.class_4.rates.main": 0.07,
        "gov.hmrc.national_insurance.class_4.rates.additional": 0.03,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.national_insurance.class_1.rates.employee.main": 0.08,
        "gov.hmrc.national_insurance.class_1.rates.employee.additional": 0.02,
        "gov.hmrc.national_insurance.class_4.rates.main": 0.06,
        "gov.hmrc.national_insurance.class_4.rates.additional": 0.02,
    },
    head_variables=["ni_class_1_employee", "ni_class_4"],
    related_reckoner_reforms=[
        "trr_national_insurance_change_class_1_employee_main_rate_by_1_percentage_point",
        "trr_national_insurance_change_class_1_employee_additional_rate_by_1_percentage_point",
        "trr_national_insurance_change_class_4_main_rate_by_1_percentage_point",
        "trr_national_insurance_change_class_4_additional_rate_by_1_percentage_point",
        "trr_national_insurance_change_class_1_employer_rate_by_1_percentage_point",
    ],
)
o(
    "nics_abolish_upper_earnings_and_profits_limits",
    "Abolish the NICs upper earnings limit and upper profits limit (main rate all the way up)",
    "national_insurance",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.hmrc.national_insurance.class_1.rates.employee.additional": 0.08,
        "gov.hmrc.national_insurance.class_4.rates.additional": 0.06,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.national_insurance.class_1.rates.employee.additional": 0.02,
        "gov.hmrc.national_insurance.class_4.rates.additional": 0.02,
    },
    head_variables=["ni_class_1_employee", "ni_class_4"],
    note="Expressed by setting the above-UEL rates equal to the main rates rather than moving the limit.",
)
o(
    "nics_on_earnings_over_state_pension_age",
    "Charge employee NICs on the earnings of people over State Pension age",
    "national_insurance",
    "partial",
    ["ifs"],
    ifs,
    pe_reform_delta=None,
    missing="The over-SPA exemption is inside the Class 1 employee formula, not a parameter; the option is a formula-level construction (remove the is_SP_age exemption).",
    action_link=ISSUE,
    name_search=ns(r"state_pension_age|over_state|is_SP_age|ni_exempt"),
    head_variables=["ni_class_1_employee"],
)
o(
    "personal_tax_threshold_freeze_two_more_years_to_2030",
    "Extend the income tax and NICs threshold freezes by two years to April 2030",
    "income_tax",
    "expressible",
    ["ifs", "resolution_foundation", "ippr", "fabian_society", "rathbones", "cebr"],
    f"{ifs}; IFS 'How are frozen tax thresholds reshaping who pays personal taxes?' (14 Nov 2025); {rf_cod}; IPPR 'Fairness first'; Fabian Society (computed with PolicyEngine, Oct 2025); Rathbones; Cebr",
    construction="two_year_variant_of_ab2025__personal_tax_thresholds_freeze_to_2031",
    # Executed as a delta on a MODIFIED baseline (both worlds simulated):
    # the baseline world is the pre-Budget path (every threshold CPI-indexed
    # from April 2028, as for the announced measure); the reform world holds
    # the 2027-28 values through 2029-30 and uprates them once in 2030-31 by
    # the path's own 2030 step. Current law (frozen to 2031) is neither world.
    pe_reform_delta={
        pa_path: {"2028": 12570, "2029": 12570, "2030": once_pa},
        hrt_path: {"2028": 37700, "2029": 37700, "2030": once_hrt},
        pt_path: {"2028": 241.73, "2029": 241.73, "2030": once_pt},
        uel_path: {"2028": 966.73, "2029": 966.73, "2030": once_uel},
        lpl_path: {"2028": 12570, "2029": 12570, "2030": once_lpl},
        upl_path: {"2028": 50270, "2029": 50270, "2030": once_upl},
    },
    delta_kind="absolute_value_by_year",
    pe_baseline_modifier={
        pa_path: {k: v for k, v in idx_pa.items()},
        hrt_path: {k: v for k, v in idx_hrt.items()},
        pt_path: {k: v for k, v in idx_pt.items()},
        uel_path: {k: v for k, v in idx_uel.items()},
        lpl_path: {k: v for k, v in idx_lpl.items()},
        upl_path: {k: v for k, v in idx_upl.items()},
    },
    engine_baseline_2026={
        pa_path: 12570,
        hrt_path: 37700,
        pt_path: 241.73,
        uel_path: 966.73,
        lpl_path: 12570,
        upl_path: 50270,
    },
    note="The announced measure is three years (to April 2031). This option is the two-year variant every pre-Budget producer costed. Scored as a delta on a modified baseline: the baseline world is the pre-Budget CPI-indexed path from April 2028 for all six IT/NI thresholds; the reform world holds them at 2027-28 values for 2028-29 and 2029-30 and uprates them once in 2030-31 (the path's own 2030 CPI step), so 2030-31 carries the level effect of the two frozen years, not a third frozen year. The Fabian Society's GBP 11.7bn was computed with PolicyEngine (same_assumptions, not different_model).",
    head_variables=["income_tax", "ni_class_1_employee", "ni_class_4"],
)
o(
    "hrt_and_uel_cut_to_46000_by_2029_30",
    "Cut the higher-rate threshold and NI upper earnings limit from GBP 50,270 to GBP 46,000 by 2029-30",
    "income_tax",
    "expressible",
    ["resolution_foundation"],
    "RF 'Black holes and consolidations' (4 Nov 2025)",
    pe_reform_delta={hrt_path: 33430, uel_path: 884.62},
    delta_kind="absolute_value",
    engine_baseline_2026={hrt_path: 37700, uel_path: 966.73},
    head_variables=["income_tax", "ni_class_1_employee"],
    note="HRT parameter is the basic-rate band width: 46,000 - 12,570 = 33,430. UEL weekly = 46,000/52.",
)

# capital income
o(
    "dividend_rates_all_plus_1p",
    "All dividend tax rates +1ppt",
    "income_tax",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.hmrc.income_tax.rates.dividends[0].rate": 0.1175,
        "gov.hmrc.income_tax.rates.dividends[1].rate": 0.3675,
        "gov.hmrc.income_tax.rates.dividends[2].rate": 0.4035,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.income_tax.rates.dividends[0].rate": 0.1075,
        "gov.hmrc.income_tax.rates.dividends[1].rate": 0.3575,
        "gov.hmrc.income_tax.rates.dividends[2].rate": 0.3935,
    },
    head_variables=["dividend_income_tax"],
    note="IFS scored +1ppt on the pre-Budget rates (8.75/33.75/39.35); the pin already carries the announced +2ppt, so the option is applied on top of the announced rates and the claim's own baseline (pre-Budget) is carried on the row.",
)
o(
    "dividend_basic_rate_to_16_5pct",
    "Raise the basic (ordinary) rate of dividend tax from 8.75% to 16.5%",
    "income_tax",
    "expressible",
    ["resolution_foundation"],
    rf_cod,
    pe_reform_delta={"gov.hmrc.income_tax.rates.dividends[0].rate": 0.165},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.hmrc.income_tax.rates.dividends[0].rate": 0.1075},
    head_variables=["dividend_income_tax"],
)
o(
    "savings_interest_rates_all_plus_1p",
    "All interest (savings) income tax rates +1ppt",
    "income_tax",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.hmrc.income_tax.rates.savings.basic": 0.21,
        "gov.hmrc.income_tax.rates.savings.higher": 0.41,
        "gov.hmrc.income_tax.rates.savings.additional": 0.46,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.income_tax.rates.savings.basic": 0.2,
        "gov.hmrc.income_tax.rates.savings.higher": 0.4,
        "gov.hmrc.income_tax.rates.savings.additional": 0.45,
    },
    head_variables=["savings_income_tax"],
)
o(
    "cgt_higher_rate_plus_1p_and_plus_10p",
    "CGT higher rate +1ppt (24 to 25) and +10ppt (24 to 34)",
    "capital_gains_tax",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.hmrc.cgt.higher_rate": 0.25,
        "gov.hmrc.cgt.additional_rate": 0.25,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.cgt.higher_rate": 0.24,
        "gov.hmrc.cgt.additional_rate": 0.24,
    },
    head_variables=["capital_gains_tax"],
    behavioural_note="gov.simulation.capital_gains_responses.elasticity is 0 at the pin (static); IFS's numbers include a realisations response, so the elasticity sweep in data/uk/cgt_alignment_reform.json is the comparable leg.",
    related_reckoner_reforms=[
        "trr_capital_gains_tax_increase_higher_capital_gains_tax_rate_by_1_percentage_point",
        "trr_capital_gains_tax_increase_higher_capital_gains_tax_rate_by_10_percentage_points",
    ],
)
o(
    "cgt_equalise_with_income_tax_plus_investment_allowance",
    "Equalise CGT rates with income tax, with a normal-return (investment) allowance",
    "capital_gains_tax",
    "partial",
    ["ippr", "demos"],
    "IPPR 'Fairness first' (19 Nov 2025); Demos 'Solving the Tax Puzzle' proposal 3",
    pe_reform_delta=None,
    missing="Rate alignment is expressible (cgt basic/higher/additional to 0.20/0.40/0.45, data/uk/cgt_alignment_reform.json); the normal-return allowance (a deduction from gains at a risk-free rate) has no lever and needs a construction on capital_gains.",
    action_link=ISSUE,
    name_search=ns(r"cgt|capital_gain|investment_allowance|normal_return"),
    head_variables=["capital_gains_tax"],
)
o(
    "cgt_end_uplift_on_death",
    "End the CGT base-cost uplift on death",
    "capital_gains_tax",
    "not_expressible",
    ["resolution_foundation", "ippr", "demos"],
    f"{rf_cod} (one of two 'loopholes'); IPPR 'Fairness first'; Demos proposal 5",
    **gap(
        "The engine models CGT on gains realised within the year and has no death event, no bequest and no base-cost uplift, so there is no parameter to move and no household event to attach the measure to (same finding as ab2026__cgt_remove_uplift_on_death).",
        r"death|bequest|inherit|uplift|probate",
        upstream="cgt_death",
    ),
)
o(
    "cgt_exit_tax_on_emigration",
    "CGT settling-up charge on emigration (rebasing on arrival, deemed disposal on departure)",
    "capital_gains_tax",
    "not_expressible",
    ["resolution_foundation", "demos"],
    f"{rf_cod}; Demos proposal 4",
    **scope_gap(
        "No migration event, no residence history and no accrued-but-unrealised gains stock at the pin.",
        r"emigra|departure|arrival|residence|unrealised",
    ),
)
o(
    "abolish_business_asset_disposal_relief",
    "Abolish business asset disposal relief",
    "capital_gains_tax",
    "not_expressible",
    ["ifs"],
    ifs,
    **scope_gap(
        "capital_gains is a single realised-gains variable with no split by disposal type, so relief on business disposals cannot be identified.",
        r"badr|business_asset|disposal|entrepreneur",
    ),
)

# pensions
o(
    "pension_tax_relief_capped_at_basic_rate",
    "Cap income tax relief on pension contributions at 20%",
    "pensions",
    "partial",
    ["ifs"],
    ifs,
    pe_reform_delta=None,
    missing="pension_contributions_relief reduces taxable income at the marginal rate by formula; a flat-rate relief needs a formula construction (relief = contributions x 0.20 as a tax credit), not a parameter.",
    action_link=ISSUE,
    name_search=ns(r"pension_contribution|relief"),
    head_variables=["income_tax", "pension_contributions_relief"],
)
o(
    "employer_nics_on_employer_pension_contributions",
    "Employer NICs on employer pension contributions (1% and full rate variants)",
    "national_insurance",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.contrib.policyengine.employer_ni.exempt_employer_pension_contributions": False
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.contrib.policyengine.employer_ni.exempt_employer_pension_contributions": True
    },
    head_variables=["ni_employer"],
    note="The exemption switch exists at the pin (True). The full-rate variant flips it; the 1% variant is the switch plus a rate construction. IFS's employer-contribution variants ('with an allowance') are conditions on the row.",
)
o(
    "salary_sacrifice_employer_nics_at_half_rate",
    "Employer NI on salary-sacrificed pension contributions at half the usual rate",
    "national_insurance",
    "partial",
    ["resolution_foundation"],
    rf_cod,
    pe_reform_delta=None,
    missing="The pin models a CAP on salary-sacrificed contributions (salary_sacrifice_pension_cap) with the excess returned to NI-able income at the full rate; a half-rate charge on the whole sacrificed amount needs a rate lever the cap variables do not have.",
    action_link=ISSUE,
    name_search=ns(r"salary_sacrifice"),
    head_variables=["salary_sacrifice_pension_ni_employer"],
)
o(
    "salary_sacrifice_nics_cap_2000_rumoured",
    "Salary-sacrifice NICs cap of GBP 2,000 (pre-Budget, reported)",
    "national_insurance",
    "expressible",
    ["aj_bell", "hargreaves_lansdown"],
    "AJ Bell and Hargreaves Lansdown pre-Budget worked examples of the reported cap",
    construction="same_lever_as_ab2025__salary_sacrifice_pension_nics_cap_2000",
    pe_reform_delta={"gov.hmrc.national_insurance.salary_sacrifice_pension_cap": 2000},
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.national_insurance.salary_sacrifice_pension_cap": None
    },
    uncapped_sentinel="inf in 2026 at the pin, recorded as null",
    head_variables=[
        "salary_sacrifice_pension_ni_employee",
        "salary_sacrifice_pension_ni_employer",
    ],
    note="The announced measure is the same cap from April 2029; the pre-Budget examples assumed immediate effect. Worked examples are mode-3 material (#63), tallied at ingest.",
)
o(
    "pension_tax_free_lump_sum_cut_to_100000",
    "Cut the pension tax-free lump sum from GBP 268,275 to about GBP 100,000",
    "pensions",
    "not_expressible",
    ["fabian_society"],
    "Fabian Society pre-Budget proposals (Oct 2025)",
    **gap(
        "VERIFIED at the pin: gov.hmrc.pensions has no tax-free lump sum parameter; lump_sum_income is a generic input with no formula and nothing to cap (#98).",
        r"lump|commencement|tax_free_cash|pcls",
        upstream="pcls",
        link=PENSIONS,
        nearest={
            "variable": "lump_sum_income",
            "entity": "person",
            "why_not": "A generic lump-sum income input with no formula; a restriction is a cap on a particular kind of lump sum and there is nothing here to cap.",
        },
    ),
)
o(
    "pension_annual_allowance_cut_to_40000",
    "Cut the pension annual allowance from GBP 60,000 to GBP 40,000",
    "pensions",
    "expressible",
    ["fabian_society"],
    "Fabian Society pre-Budget proposals (Oct 2025)",
    pe_reform_delta={"gov.hmrc.income_tax.allowances.annual_allowance.default": 40000},
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.income_tax.allowances.annual_allowance.default": 60000
    },
    head_variables=["income_tax", "pension_annual_allowance"],
)
o(
    "nics_equivalent_on_large_pension_incomes",
    "NICs-equivalent charge on large private pension incomes",
    "national_insurance",
    "partial",
    ["fabian_society"],
    "Fabian Society pre-Budget proposals (Oct 2025)",
    pe_reform_delta=None,
    missing="private_pension_income exists; an NI-type charge on it is a new base with no parameter (NI base extension switch).",
    policyengine_uk_development_item=True,
    upstream_item=UPSTREAM["ni_base"],
    action_link=ISSUE,
    name_search=ns(r"pension_income|ni_base|national_insurance\.(class_1|class_4)"),
)

# inheritance tax
o(
    "iht_rate_to_41pct_and_abolish_residence_nil_rate_band",
    "Inheritance tax rate 40% to 41%; abolish the residence nil-rate band",
    "inheritance_tax",
    "not_expressible",
    ["ifs", "centax"],
    f"{ifs}; CenTax IHT alternatives",
    **gap(
        "No estates, bequests or inheritance tax at the pin.",
        r"inherit|estate|nil_rate|bequest|death",
        upstream="estates",
    ),
    related_reckoner_reforms=[
        "trr_inheritance_tax_increase_standard_rate_for_estates_left_on_death_by_1_percentage_point"
    ],
)

# council tax and property
o(
    "council_tax_double_bands_g_and_h_england",
    "Double council tax bills for bands G and H in England",
    "council_tax",
    "partial",
    ["ifs", "tax_policy_associates", "public_first"],
    f"{ifs}; Tax Policy Associates (open-source model, Sep 2025); Public First (FRS 2023-24)",
    pe_reform_delta=None,
    missing="No band-multiplier parameter at the pin. council_tax_band and the council_tax liability exist on the bundle, so the option is a CONSTRUCTION: scale council_tax by 2 where band is G or H (England), via a simulation modifier; stated as constructed.",
    action_link=ISSUE,
    name_search=ns(r"council_tax|band_[a-h]|multiplier|relativit"),
    head_variables=["council_tax"],
)
o(
    "council_tax_bands_f_g_plus_50pct_h_plus_100pct_recycled_to_a_d",
    "Council tax bands F and G +50%, H +100% of the band-D multiplier, recycling GBP 1bn to cut bands A-D by 2.7%",
    "council_tax",
    "partial",
    ["ippr"],
    "IPPR 'Towards a fair and proportional property tax' (14 Nov 2025) and technical appendix; 'Fairness first'",
    pe_reform_delta=None,
    missing="Same construction as the G/H doubling: band-level scaling of council_tax via a modifier, no multiplier parameter.",
    action_link=ISSUE,
    name_search=ns(r"council_tax|multiplier|band"),
    head_variables=["council_tax"],
)
o(
    "council_tax_plus_1pct_and_scotland_relativities",
    "Council tax +1% on all bills; copy Scotland's 2017 higher-band relativities",
    "council_tax",
    "partial",
    ["ifs"],
    ifs,
    pe_reform_delta=None,
    missing="Uniform scaling of council_tax is a construction (no rate parameter); the Scottish relativities are band-level scaling as above.",
    action_link=ISSUE,
    name_search=ns(r"council_tax|relativit|multiplier"),
    head_variables=["council_tax"],
)
o(
    "proportional_property_tax_on_values_over_2m",
    "Proportional property tax: 1% on value GBP 2m-3m and 2% above GBP 3m (Demos); full proportional property tax (IPPR, cited)",
    "property_tax",
    "partial",
    ["demos", "ippr"],
    "Demos proposal 6; IPPR 'Pulling down the ladder' (2021, cited in the 2025 appendix)",
    pe_reform_delta=None,
    missing="main_residence_value is on the bundle (WAS-imputed above GBP 2m, the same credibility annotation as the surcharge) and the surcharge formula is the template; a value-proportional charge is a construction on main_residence_value with no parameter.",
    action_link=ISSUE,
    name_search=ns(
        r"main_residence_value|property_tax|proportional|high_value_surcharge"
    ),
    head_variables=["high_value_council_tax_surcharge"],
)
o(
    "non_uk_resident_sdlt_surcharge_2_to_6pct",
    "Non-UK-resident SDLT surcharge 2% to 6%",
    "stamp_taxes",
    "not_expressible",
    ["ippr"],
    "IPPR property-tax technical appendix (14 Nov 2025)",
    **scope_gap(
        "SDLT on residential transactions exists at the pin, but buyer residence status is not on the bundle.",
        r"sdlt|non_resident|surcharge|stamp_duty",
    ),
)
o(
    "second_homes_200pct_premium_for_non_uk_residents",
    "Additional 200% council tax premium on second homes owned by non-UK residents",
    "council_tax",
    "not_expressible",
    ["demos"],
    "Demos proposal 7",
    **scope_gap(
        "No second-home ownership by non-residents on a UK-resident household bundle.",
        r"second_home|premium|empty_home|non_resident",
    ),
)

# consumption taxes
o(
    "vat_main_rate_20_to_21_reduced_5_to_6_zero_rated_1pct",
    "VAT: main rate 20% to 21%; reduced rate 5% to 6%; 1% VAT on zero-rated products",
    "vat",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={
        "gov.hmrc.vat.standard_rate": 0.21,
        "gov.hmrc.vat.reduced_rate": 0.06,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.hmrc.vat.standard_rate": 0.2,
        "gov.hmrc.vat.reduced_rate": 0.05,
    },
    head_variables=["vat"],
    note="The zero-rated leg has no rate parameter (zero-rated consumption is the residual of full and reduced-rate consumption); expressed as a construction on the LCFS-imputed consumption categories. VAT incidence is the consumption module's imputation, stated on the row.",
    related_reckoner_reforms=[
        "trr_vat_change_standard_rate_by_1_percentage_point",
        "trr_vat_change_reduced_rate_by_1_percentage_point",
    ],
)
o(
    "vat_registration_threshold_cut_to_30000",
    "Cut the VAT registration threshold from GBP 90,000 to GBP 30,000 over four years",
    "vat",
    "not_expressible",
    ["resolution_foundation"],
    rf_cod,
    **scope_gap(
        "A business-side registration threshold; the household VAT module has no trader population.",
        r"vat_threshold|registration_threshold|vat\.",
    ),
)
o(
    "nil_rate_vat_on_domestic_electricity",
    "Nil-rate VAT on domestic electricity (RF); remove VAT on domestic energy (NIESR)",
    "vat",
    "partial",
    ["resolution_foundation", "niesr"],
    "RF 'Splitting the bill' (16 Oct 2025); NIESR Autumn 2025 Outlook",
    pe_reform_delta=None,
    missing="gov.hmrc.vat.reduced_rate (5%) covers all reduced-rated consumption; a fuel-only zero rate needs the electricity_consumption / gas_consumption split applied by construction. The Ofgem-cap 0% VAT on electricity Oct 2026 - Mar 2027 is a later fact (chronicle #257), not this pin's baseline.",
    action_link=ISSUE,
    name_search=ns(r"vat|electricity_consumption|gas_consumption|reduced_rate"),
    head_variables=["vat"],
)
o(
    "fuel_duty_plus_10pct_or_freeze_to_2029_30",
    "Fuel duty +10% (to 65.65ppl in 2026-27), or freeze at current levels to 2029-30",
    "fuel_duty",
    "expressible",
    ["ifs"],
    ifs,
    pe_reform_delta={"gov.hmrc.fuel_duty.petrol_and_diesel": 0.6565},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.hmrc.fuel_duty.petrol_and_diesel": 0.5345},
    head_variables=["fuel_duty"],
    note="Two variants on one lever; each staged claim names its own. The freeze variant is the announced measure's shape extended to 2029-30.",
)
o(
    "fuel_duty_new_uprating_regime_3pct_quarterly",
    "New fuel duty uprating regime: fixed 3% a year in quarterly steps, 5p cut unwound over ~10 quarters",
    "fuel_duty",
    "expressible",
    ["resolution_foundation"],
    rf_cod,
    pe_reform_delta={
        "gov.hmrc.fuel_duty.petrol_and_diesel": {
            "2026-04-01": 0.5345,
            "2026-07-01": 0.54,
            "2027-04-01": 0.5723,
        }
    },
    delta_kind="absolute_value_by_date",
    engine_baseline_2026={"gov.hmrc.fuel_duty.petrol_and_diesel": 0.5345},
    head_variables=["fuel_duty"],
    note="Path re-derived from RF's description at compute; the dated values here are illustrative of the schedule shape and are replaced by the executed path in the run artifact.",
)
o(
    "end_fuel_duty_freeze_and_start_road_pricing",
    "End the fuel duty freeze and introduce road pricing",
    "fuel_duty",
    "not_expressible",
    ["smf"],
    "Social Market Foundation pre-Budget options",
    **gap(
        "Ending the freeze is expressible (fuel_duty lever); road pricing is not: no mileage on the bundle.",
        r"road_pricing|mileage|per_mile|vehicle",
        upstream="vehicles",
    ),
)
o(
    "ved_reform_for_evs_distance_and_weight_based",
    "Reform VED for future EVs (distance- and weight-based), end the 'pavement tax', cut public-charging VAT",
    "vehicle_excise_duty",
    "not_expressible",
    ["resolution_foundation"],
    rf_cod,
    **gap(
        "No VED, no EV flag, no mileage or vehicle weight at the pin.",
        r"ved\b|vehicle_excise|electric_vehicle|mileage|weight",
        upstream="vehicles",
    ),
)
o(
    "gambling_duties_consolidated_or_raised",
    "Gambling duties: consolidate to a 25% rate (RF); RGD to 50%, GBD to 25% excl. horse racing, MGD to 50% (IPPR, Demos, SMF, Fabians)",
    "gambling_duties",
    "not_expressible",
    ["resolution_foundation", "ippr", "demos", "smf", "fabian_society"],
    f"{rf_cod}; IPPR 'Reforming gambling taxation' (6 Aug 2025); Demos proposal 8; SMF; Fabian Society",
    **scope_gap(
        "No gambling expenditure, gambling duty or gaming yield at the pin (see the announced gambling-duty entry).",
        r"gambl|betting|gaming|lottery|machine_games",
    ),
)
o(
    "sugar_and_salt_reformulation_tax",
    "Sugar and Salt Reformulation Tax (GBP 4/kg sugar, GBP 8/kg salt) replacing the Soft Drinks Industry Levy",
    "indirect_tax",
    "not_expressible",
    ["resolution_foundation"],
    rf_cod,
    **scope_gap(
        "Producer-side levy with no household consumption category for sugar or salt content.",
        r"sugar|salt|soft_drink|levy|reformulation",
    ),
)
o(
    "uk_ets_extended_to_eu_scope_aviation_and_shipping",
    "Broaden the UK ETS to EU scope on aviation and shipping",
    "environmental_tax",
    "not_expressible",
    ["resolution_foundation"],
    rf_cod,
    **scope_gap(
        "Emitter-side carbon price with no household incidence path at the pin.",
        r"emission|ets\b|aviation|shipping|carbon",
    ),
)
o(
    "alcohol_minimum_unit_tax",
    "Minimum unit tax on alcohol (36p MUT alongside 65p MUP; two-rate variant with 46p on spirits)",
    "indirect_tax",
    "not_expressible",
    ["smf"],
    "Social Market Foundation pre-Budget options",
    **scope_gap(
        "No alcohol duty at the pin; alcohol_and_tobacco_consumption is a combined LCFS expenditure category with no unit content.",
        r"alcohol|beer|wine|spirit|minimum_unit|duty",
    ),
)
o(
    "insurance_premium_tax_on_private_medical_insurance_20pct",
    "Insurance premium tax on private medical insurance 12% to 20%",
    "indirect_tax",
    "not_expressible",
    ["fabian_society"],
    "Fabian Society pre-Budget proposals (Oct 2025)",
    **scope_gap(
        "No insurance premium tax and no private-medical-insurance holding on the bundle.",
        r"insurance_premium|ipt\b|medical_insurance|private_medical",
    ),
)
o(
    "corporation_tax_plus_1p_and_bank_surcharge",
    "Corporation tax main rate 25% to 26%; bank surcharge 3% to 4% (IFS) or restored to 8% (Fabians)",
    "corporation_tax",
    "not_expressible",
    ["ifs", "fabian_society"],
    f"{ifs}; Fabian Society bank-windfall proposals",
    **scope_gap(
        "Corporation tax and the bank surcharge are business-side taxes outside a household microsimulation (the engine's business_rates incidence via shareholdings is the only corporate leg it holds).",
        r"corporation|bank_surcharge|surcharge|profits",
    ),
    related_reckoner_reforms=[
        "trr_corporation_tax_increase_corporation_tax_by_1_percentage_point"
    ],
)
o(
    "boe_apf_indemnity_or_reserves_remuneration_reform",
    "Renegotiate the Bank of England APF indemnity / QE loss-sharing; reserves levy or stop active QT",
    "monetary_fiscal",
    "not_expressible",
    ["nef", "ippr"],
    "NEF (Oct 2025); IPPR 'Fairness first'",
    **scope_gap(
        "Central-bank balance-sheet arithmetic; no household incidence.",
        r"boe|bank_of_england|reserves|apf|quantitative",
        link=MACRO,
    ),
)
o(
    "oil_and_gas_windfall_measures",
    "Oil and gas windfall measures",
    "corporation_tax",
    "not_expressible",
    ["fabian_society"],
    "Fabian Society pre-Budget proposals (Oct 2025)",
    **scope_gap(
        "Producer-side energy profits levy.", r"oil|gas_profit|energy_profits|windfall"
    ),
)

# NICs base extensions and partnerships
o(
    "nics_on_partnership_income",
    "Employer-NICs equivalent on partnership profits (13.04% above a GBP 5,000 exempt amount; 'membership NI' for LLPs)",
    "national_insurance",
    "not_expressible",
    ["centax", "resolution_foundation", "demos", "ippr"],
    "CenTax 'Partnership NICs' (Oct/Nov 2025: static GBP 2.4bn, post-behavioural GBP 1.9bn); RF 'Call of duties'; Demos proposal 2; IPPR 'Fairness first'",
    **gap(
        "Partnership and LLP profits are not identified within self_employment_income on the bundle, and Class 4 NICs (the nearest lever, ni_class_4 at 6% above the LPL) applies to all self-employed; a charge on partners only cannot be targeted.",
        r"partner|llp|self_employment_income|class_4",
        upstream="partnership",
        nearest={
            "variable": "ni_class_4",
            "entity": "person",
            "why_not": "Charges all self-employment profits; partnership profits are a subset the data does not mark, so applying an employer-equivalent rate to ni_class_4's base scores the wrong population.",
        },
    ),
)
o(
    "nics_on_rental_income",
    "NICs on landlords' rental income (8% above GBP 50,270 with a mortgage-interest / investment allowance; RF 'special rates on rental income'; Fabians 28/42/47% rental rates)",
    "national_insurance",
    "partial",
    ["resolution_foundation", "ippr", "demos", "fabian_society"],
    "RF 'Call of duties' Box 2; IPPR 'Fairness first'; Demos proposal 1; Fabian Society",
    pe_reform_delta=None,
    missing="property_income and the separate property-income rate schedule exist at the pin; an NI-type charge on rental income is a new base with no parameter (NI base extension switch). The Fabians' variant (rental rates 28/42/47) IS expressible via gov.hmrc.income_tax.rates.property.*.",
    policyengine_uk_development_item=True,
    upstream_item=UPSTREAM["ni_base"],
    action_link=ISSUE,
    name_search=ns(r"property_income|rental|rates\.property|ni_base"),
    head_variables=["income_tax", "ni_class_4"],
)
o(
    "self_employed_nics_main_rate_6_to_8pct",
    "Self-employed NICs main rate 6% to 8%",
    "national_insurance",
    "expressible",
    ["resolution_foundation"],
    "RF 'Call of duties' Box 2",
    pe_reform_delta={"gov.hmrc.national_insurance.class_4.rates.main": 0.08},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.hmrc.national_insurance.class_4.rates.main": 0.06},
    head_variables=["ni_class_4"],
)

# energy bills
o(
    "energy_levies_whd_eco_ro_fit_cps_off_bills",
    "Move WHD, ECO, RO and FiT costs off electricity bills to general taxation and scrap Carbon Price Support (RF package and its legs)",
    "energy_bills",
    "partial",
    ["resolution_foundation", "nef"],
    "RF 'Splitting the bill' (16 Oct 2025) and 'Black holes'; NEF energy-levy incidence (LCFS/SERL/EHS)",
    pe_reform_delta=None,
    missing="Policy costs on bills are not parameters; the legs are constructions on electricity_consumption and gas_consumption (levy share x bill), the same shape as the announced RO measure.",
    action_link=ISSUE,
    name_search=ns(
        r"electricity_consumption|gas_consumption|energy_bills|levy|renewables"
    ),
    head_variables=["domestic_energy_consumption", "energy_bills_rebate"],
)

# child poverty package options
tcl = "IFS 'Options for reforming the two-child limit' (23 Oct 2025); RF 'No half measures' (30 Oct 2025); JRF 'Two policies' (30 Sep 2025); IPPR; CPAG Budget submission (UKMOD B1.13, 17 Oct 2025); Policy in Practice (LA UC admin data); FAI (Scotland); WBG (UKMOD B2025.08)"
o(
    "scrap_two_child_limit",
    "Scrap the two-child limit entirely (pre-Budget scoring)",
    "universal_credit",
    "expressible",
    [
        "ifs",
        "resolution_foundation",
        "jrf",
        "ippr",
        "cpag",
        "policy_in_practice",
        "fraser_of_allander",
        "wbg",
    ],
    tcl,
    construction="same_lever_as_ab2025__uc_child_element_remove_two_child_limit",
    pe_reform_delta={
        "gov.dwp.universal_credit.elements.child.limit.child_count": None,
        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": None,
    },
    uncapped_sentinel="inf (limit removed), recorded as null",
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.dwp.universal_credit.elements.child.limit.child_count": None,
        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": None,
    },
    baseline_world="pre_ab2025",
    head_variables=["universal_credit", "child_tax_credit"],
    note="Pre-Budget scorings of the measure later announced. Each producer's baseline world (IFS full roll-out, RF/JRF/CPAG/IPPR end-of-parliament worlds) is carried per row (#13); they are the same lever on different worlds, not different measures.",
)
o(
    "three_child_limit",
    "Replace the two-child limit with a three-child limit",
    "universal_credit",
    "expressible",
    ["ifs", "resolution_foundation", "policy_in_practice"],
    tcl,
    pe_reform_delta={
        "gov.dwp.universal_credit.elements.child.limit.child_count": 3,
        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": 3,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.dwp.universal_credit.elements.child.limit.child_count": None,
        "gov.dwp.tax_credits.child_tax_credit.limit.child_count": None,
    },
    uncapped_sentinel="inf at the pin (limit removed from 2026), recorded as null; the option is scored on the pre_ab2025 world",
    baseline_world="pre_ab2025",
    head_variables=["universal_credit", "child_tax_credit"],
)
o(
    "two_child_limit_partial_child_element_for_third_plus_children",
    "Reintroduce a child element for third and subsequent children at 50% (IFS) or two-thirds (RF) of the standard rate",
    "universal_credit",
    "partial",
    ["ifs", "resolution_foundation"],
    tcl,
    pe_reform_delta=None,
    missing="child.limit.child_count is a count, not a rate schedule; a reduced element for children beyond the second needs a per-child-rank amount the element formula does not have.",
    action_link=ISSUE,
    name_search=ns(r"elements\.child|child_count|child_element"),
    head_variables=["universal_credit"],
)
o(
    "two_child_limit_exempt_working_families",
    "Exempt families with at least one parent in paid work (IFS; RF 16 hours at NLW variant)",
    "universal_credit",
    "partial",
    ["ifs", "resolution_foundation"],
    tcl,
    pe_reform_delta=None,
    missing="An exemption condition on the limit (work status, hours) is a formula construction; the limit parameter has no eligibility conditions.",
    action_link=ISSUE,
    name_search=ns(r"child_count|limit|in_work|hours_worked"),
    head_variables=["universal_credit"],
)
o(
    "two_child_limit_exempt_children_under_5_or_under_1",
    "Exempt children under 5 (or under 1) from the two-child limit",
    "universal_credit",
    "partial",
    ["ifs"],
    tcl,
    pe_reform_delta=None,
    missing="An age-based exemption from the limit is a formula construction; the limit parameter has no age condition (the start_year born-after rule is the only conditional).",
    action_link=ISSUE,
    name_search=ns(r"child_count|limit\.start_year|age_limit"),
    head_variables=["universal_credit"],
)
o(
    "remove_the_benefit_cap",
    "Remove the benefit cap",
    "benefit_cap",
    "expressible",
    ["cpag", "ippr", "wbg", "resolution_foundation"],
    "CPAG (UKMOD B1.13); IPPR 'Fairness first'; WBG (UKMOD B2025.08); RF 'No half measures'",
    pe_reform_delta={
        "gov.dwp.benefit_cap.single.outside_london": 10000000,
        "gov.dwp.benefit_cap.single.in_london": 10000000,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.dwp.benefit_cap.single.outside_london": 14753,
        "gov.dwp.benefit_cap.single.in_london": 16967,
    },
    head_variables=["benefit_cap_reduction", "universal_credit"],
    note="Removal expressed as an unreachable cap; the couple/family cap nodes are set alongside at compute (all gov.dwp.benefit_cap.* leaves).",
)
o(
    "raise_the_benefit_cap_to_living_wage_equivalent",
    "Raise the benefit cap to a living-wage equivalent (GBP 29,000 London, GBP 26,000 outside)",
    "benefit_cap",
    "expressible",
    ["policy_in_practice"],
    "Policy in Practice (LA UC administrative data, 8 councils)",
    pe_reform_delta={
        "gov.dwp.benefit_cap.single.outside_london": 26000,
        "gov.dwp.benefit_cap.single.in_london": 29000,
    },
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.dwp.benefit_cap.single.outside_london": 14753,
        "gov.dwp.benefit_cap.single.in_london": 16967,
    },
    head_variables=["benefit_cap_reduction"],
    note="Policy in Practice's figures are administrative-data shares of capped households, not a microsimulation; the cap interaction is what PE can express.",
)
o(
    "relink_lha_to_30th_percentile_of_local_rents",
    "Relink Local Housing Allowance to the 30th percentile of local rents",
    "housing_benefit",
    "expressible",
    ["resolution_foundation", "wbg"],
    "RF 'No half measures'; WBG",
    pe_reform_delta={"gov.dwp.LHA.freeze": False},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.dwp.LHA.freeze": True},
    head_variables=["LHA_cap", "universal_credit", "housing_benefit"],
    note="gov.dwp.LHA.freeze = True and LHA.percentile = 0.3 at the pin; unfreezing relinks to the 30th percentile of the engine's BRMA rents.",
)
o(
    "uc_protected_minimum_floor_deductions_capped_at_15pct",
    "Protected minimum floor in UC: deductions capped at 15% of the standard allowance (JRF, Trussell/WPI)",
    "universal_credit",
    "not_expressible",
    ["jrf", "trussell_wpi"],
    "JRF 'Two policies' (30 Sep 2025); Trussell / WPI Economics severe-hardship projections",
    **gap(
        "UC deductions (advances, debt repayments, third-party deductions) are not modelled at the pin: no deductions parameter and no deductions variable; the FRR deductions family in this repo is an external-scores lane, not an engine capability.",
        r"deduction|advance|third_party|debt|floor",
        upstream="uc_deductions",
    ),
)
o(
    "fsm_extension_to_all_uc_families_england",
    "Extend free school meals to all Universal Credit families in England (Spending Review 2025; component of the RF/JRF baseline worlds)",
    "in_kind",
    "not_expressible",
    ["resolution_foundation", "jrf"],
    "RF 'No half measures' baseline; JRF projections",
    **scope_gap(
        "free_school_meals is an INPUT variable with no formula at the pin, and the benefit is in kind, outside the HBAI income concept the poverty claims use; it is a world descriptor, not a scored transfer.",
        r"free_school|school_meal|fsm",
    ),
)

# keys the harvest asked for (JRF, CPAG, FAI, Trussell rows that fit no measure above)
o(
    "nics_on_investment_income",
    "National Insurance on investment income (dividends, interest, rental and pension income)",
    "national_insurance",
    "partial",
    ["jrf", "ifs", "resolution_foundation"],
    "JRF 'Put cost of living at heart of Budget' (19 Nov 2025) tax options; IFS Green Budget; RF 'Call of duties' Box 2",
    pe_reform_delta=None,
    missing="dividend_income, savings_interest_income, property_income and private_pension_income exist at the pin; an NI-type charge on them is a new base with no parameter (NI base extension switch, the same gap as ab2026__ni_extended_to_investment_property_pension_income).",
    policyengine_uk_development_item=True,
    upstream_item=UPSTREAM["ni_base"],
    action_link=ISSUE,
    name_search=ns(
        r"dividend_income|savings_interest_income|property_income|private_pension_income|ni_base|national_insurance\.class_1"
    ),
    head_variables=["ni_class_1_employee", "ni_class_4"],
)
o(
    "scottish_child_payment_increase",
    "Increase the Scottish Child Payment (to GBP 35 / GBP 37.50 / GBP 40 a week)",
    "scottish_child_payment",
    "expressible",
    ["cpag", "fraser_of_allander"],
    "CPAG Scotland release (26 Nov 2025) and Budget submission; Fraser of Allander pre-Budget Scotland analysis",
    pe_reform_delta={"gov.social_security_scotland.scottish_child_payment.amount": 40},
    delta_kind="absolute_value",
    engine_baseline_2026={
        "gov.social_security_scotland.scottish_child_payment.amount": 28.2
    },
    head_variables=["scottish_child_payment"],
    note="Three variants (35 / 37.50 / 40 a week) on one lever; each staged claim names its own in reform_hint. Scotland-only (geography Scotland); take-up parameters gov.social_security_scotland.scottish_child_payment.takeup_rate.* are the assumptions axis.",
)
o(
    "lha_freeze_maintained",
    "Local Housing Allowance rates kept frozen (the counterfactual to relinking; costs of the continued freeze)",
    "housing_benefit",
    "expressible",
    ["trussell_wpi", "resolution_foundation"],
    "Trussell / WPI Economics (26 Nov and 11 Dec 2025); RF 'No half measures' relink option is the reverse of this world",
    pe_reform_delta={"gov.dwp.LHA.freeze": True},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.dwp.LHA.freeze": True},
    already_in_baseline=True,
    head_variables=["LHA_cap", "housing_benefit", "universal_credit"],
    note="The freeze IS the certified baseline (gov.dwp.LHA.freeze = True throughout); claims about its cost are scored as the difference from the relinked world (ab2025_option__relink_lha_to_30th_percentile_of_local_rents), i.e. the same pair of worlds read from the other side.",
)

# macro-fiscal scenarios
o(
    "niesr_30bn_tax_rise_scenarios",
    "Raise GBP 30bn net by 2029-30 via income tax (+1pp average effective rate), VAT (+3pp) or corporation tax (+4.5pp); GBP 50bn variants",
    "package",
    "partial",
    ["niesr"],
    "NIESR Autumn 2025 UK Economic Outlook (Boxes C/D)",
    pe_reform_delta=None,
    missing="The income tax and VAT legs are expressible as rate levers (income_tax rates, vat rates) calibrated to the stated yield; the corporation tax leg is out of scope; NiGEM's macro feedback is the #55 lane.",
    action_link=MACRO,
    name_search=ns(r"income_tax\.rates\.uk|vat\.standard_rate|corporation"),
    head_variables=["income_tax", "vat"],
)
o(
    "triple_lock_replaced_with_double_lock",
    "Replace the State Pension triple lock with a double lock",
    "state_pension",
    "expressible",
    ["smf"],
    "Social Market Foundation pre-Budget options",
    pe_reform_delta={"gov.dwp.state_pension.triple_lock.minimum_rate": 0.0},
    delta_kind="absolute_value",
    engine_baseline_2026={"gov.dwp.state_pension.triple_lock.minimum_rate": 0.025},
    head_variables=["state_pension"],
    note="Double lock = drop the 2.5% floor (triple_lock.include_earnings / include_inflation stay True). Yield accrues over the forecast as the uprating path diverges.",
)
o(
    "hold_total_spending_growth_to_inflation",
    "Hold total spending growth to inflation until 2029-30",
    "spending",
    "not_expressible",
    ["iea"],
    "Institute of Economic Affairs pre-Budget note",
    **scope_gap(
        "Aggregate departmental spending path; no household incidence.",
        r"spending|rdel|departmental",
        link=MACRO,
    ),
)
o(
    "policy_exchange_beyond_our_means_savings_menu",
    "'Beyond Our Means' savings menu (pensions, uprating, LHA items)",
    "spending",
    "partial",
    ["policy_exchange"],
    "Policy Exchange 'Beyond Our Means' (2025) Table 1 savings menu; the PDF was CAPTCHA-gated at the 24 Sep inventory pass and readable at the harvest fetch, so the 84 rows are staged from the primary (sources/harvest-uk-ab2025-2026-09-24/uk_thinktank_misc)",
    pe_reform_delta=None,
    missing="A menu of savings items, not one measure: the pensions-uprating and LHA items are expressible levers (state_pension triple_lock.*, gov.dwp.LHA.freeze), the departmental and administrative items are out of scope; each staged row carries its own item in reform_hint and the ingest keys the expressible ones to their own registry measures where one exists.",
    action_link=ISSUE,
    name_search=ns(r"triple_lock|LHA|uprating"),
)
o(
    "housing_first_for_rough_sleepers",
    "Housing First for all rough sleepers in England",
    "spending",
    "not_expressible",
    ["smf"],
    "Social Market Foundation",
    **scope_gap(
        "Homelessness services spending; rough sleepers are not a household-survey population.",
        r"housing_first|rough_sleep|homeless",
    ),
)

# ---------------------------------------------------------------------------
# Registry document
# ---------------------------------------------------------------------------
triage = {}
for m in measures:
    triage[m["computability"]] = triage.get(m["computability"], 0) + 1
triage["already_in_baseline"] = sum(1 for m in measures if m.get("already_in_baseline"))
triage["out_of_model_scope"] = sum(1 for m in measures if m.get("out_of_model_scope"))
triage["policyengine_uk_development_item"] = sum(
    1 for m in measures if m.get("policyengine_uk_development_item")
)
triage["announced"] = sum(1 for m in measures if m["reported_status"] == "announced")
triage["options"] = sum(
    1 for m in measures if m["reported_status"] == "option_costed_by_others"
)

keys = [m["measure_key"] for m in measures]
assert len(keys) == len(set(keys)), "duplicate keys"

reg = {
    "schema_version": 1,
    "fiscal_event": "autumn_budget_2025",
    "event_date": "2025-11-26",
    "chancellor": "Rachel Reeves",
    "administration": "Starmer government",
    "registry_rule": (
        "One entry per measure ANNOUNCED at Autumn Budget 2025 (every HM Treasury Table 4.1 line, incl. the lines a household "
        "model cannot touch) and per OPTION that a producer costed for that Budget. It is the port's key space (#136): every "
        "staged claim from every producer carries conditions.measure_key from this file, so retrieval works by measure across "
        "producers, and every measure carries a computability verdict against the certified engine, so an external row on a "
        "measure the engine cannot express is compared to nothing, honestly, with somewhere to go. It stages NO value claims; "
        "values live in the harvest under their producers (sources/harvest-uk-ab2025-2026-09-24/)."
    ),
    "measure_key_rule": (
        "ab2025__<slug> for announced measures (Table 4.1 lines and the packages), ab2025_option__<slug> for options costed by "
        "others. obr_pmd_measure_key carries the autumn_budget_2025__<slug> spelling used by data/uk/obr_divergence_axes.json, "
        "tests/fixtures/obr_costings_comparison_20260817.csv and PR #56, so those join without renames."
    ),
    "verification_note": (
        "Every pe_reform_delta and pe_baseline_modifier path was RESOLVED against an installed policyengine-uk 2.89.2 on 2026-09-24 "
        "and engine_baseline_2026 records what that engine returns for 2026-06-01. Every not_expressible verdict carries a "
        "name_search COMPUTED over the pinned engine's full parameter tree and variable list (869), never typed. The tree is counted as the search walks it: 2,246 leaves = 1,530 Parameter values + 716 bracket thresholds, rates and amounts across 70 scales; the 730 ParameterNode containers are searched by path but not counted, so a walk that counts every node gives 2,330. "
        "the AB2026 registry's v1 published two false gaps from guessed paths, and #106 nearly published a false bus gap from a "
        "parameter-only search. Year-dependent facts recorded at the pin: income tax thresholds frozen through 2030-31 and the NI "
        "thresholds NOT (primary threshold/UEL uprate from April 2028, class 4 limits from April 2027); the halved UC health "
        "element applies to every claimant (no claim history); fuel duty's staggered 2026 path is collapsed to one 2027 step."
    ),
    "engine_pin": {
        "policyengine_uk": PIN,
        "resolved_on": "2026-09-24",
        "pin_meaning": (
            "The pin follows the certified populace-uk bundle, which DECLARES policyengine-uk ==2.89.2: computability is a "
            "statement about the world the scorecard computes in, not about whatever is installed (#126, #101). Later engines "
            "(2.100.x on PyPI) may close gaps recorded here; that is re-verified when the certified bundle moves."
        ),
        "certified_bundle": {
            "repo_id": BUNDLE["repo_id"],
            "revision": BUNDLE["revision"],
            "compatible_model_packages": BUNDLE["compatible_model_packages"],
            "read_on": "2026-09-24",
        },
    },
    "computability": {
        "expressible": "every leg is a resolvable parameter in the certified engine (a reversal construction where the measure is already in the baseline)",
        "partial": "some legs resolve; the missing ones are named in `missing` and a construction is stated where one exists",
        "not_expressible": "the engine has no representation; `why` names the gap, `name_search` proves it, `action_link` says where it goes",
    },
    "construction_vocabulary": {
        "reversal_on_certified_world": "the measure is IN the certified baseline; PE executes pe_baseline_modifier (the pre-Budget world) as the baseline and current law as the reform, so measure delta = current law minus pre-Budget world (#56 convention)",
        "package_of_registry_measures": "a composition of registry measures; a PE number is the sum of the expressible legs, stated as constructed with the omitted legs listed",
    },
    "action_link_rule": (
        "Every not_expressible measure carries an action_link. policyengine_uk_development_item gaps link to the upstream "
        "policyengine-uk issue once filed (upstream_item names it); until then they link to #136, which lists them. "
        "out_of_model_scope gaps link to #136 (household-model scope) or to the lane that owns the quantity (#55 macro)."
    ),
    "provenance_rule_note": "Announced-measure titles are verbatim from Table 4.1 as staged at sources/harvest-uk-2026-08-02/uk_hmt (reform_hint); source_note carries the exchequer impacts read from the same rows so a reader can check a measure's size without opening the harvest.",
    "triage": triage,
    "measures": measures,
    "reverified_at": "2026-09-24",
}


def main(argv=None):
    text = json.dumps(reg, indent=1, ensure_ascii=False) + "\n"
    if "--check" in (argv or []):
        current = OUT.read_text() if OUT.exists() else ""
        if current != text:
            raise SystemExit(f"{OUT} differs from what this script generates")
        print(f"registry reproduces byte for byte: {len(measures)} measures")
        return 0
    OUT.write_text(text)
    print("wrote", OUT, len(measures), "measures", triage)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
