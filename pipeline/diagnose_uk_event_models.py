"""Small, pinned engine reproducers for event replay investigation candidates.

These record engine observations, not a claim that their effects explain a
specified fraction of a national OBR difference. No issue is filed. The
synthetic checks use one or two people rather than loading or simulating the
certified national population, and release each world before the next.

Each candidate was established on one engine. ``--reverify`` reruns every
case on the installed engine (``--expect-engine`` names it exactly) and
records, per case, whether the observation still shows the defect
(``persists``), shows it gone (``resolved``) or cannot decide
(``inconclusive``). The predicates read only the case's own observation.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import inspect
import json
import math
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def resolve(system, path: str, date: str):
    node = system.parameters
    for part in path.split("."):
        match = re.fullmatch(r"(.+)\[(\d+)\]", part)
        node = (
            getattr(node, match.group(1)).brackets[int(match.group(2))]
            if match
            else getattr(node, part)
        )
    value = node(date)
    return value.item() if hasattr(value, "item") else value


LEGACY_ENGINE = "2.89.2"
STATUSES = ("persists", "resolved", "inconclusive")


def _source(package_root: Path, relative: str, *, tolerant: bool = False) -> dict:
    path = package_root / relative
    if tolerant and not path.is_file():
        # A moved or deleted file on another engine is a fact to record, not a
        # resolution of the defect.
        return {"engine_file": relative, "missing": True}
    payload = path.read_bytes()
    return {
        "engine_file": relative,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "source": payload.decode(),
    }


def _with_income_behind_taxed_income(
    package_root: Path, evidence_path: str, people: dict
) -> dict:
    """A case's people, with income where its formula ignores the override.

    An engine charging above reduced net income no longer reads taxed_income,
    so a person with only that override has no income. £42,570 less the £12,570
    personal allowance leaves the override's £30,000. Engines reading the
    override keep the case they recorded.
    """
    source = _source(package_root, evidence_path, tolerant=True).get("source", "")
    if "taxed_income" in source:
        return people
    return {
        name: {**inputs, "employment_income": {"2024": 42570}}
        if "taxed_income" in inputs
        else inputs
        for name, inputs in people.items()
    }


def _additional_model_checks(
    package_root: Path, simulation_type, case: str | None, *, tolerant: bool = False
):
    """Run each small diagnostic sequentially, retaining no live prior world."""
    specifications = [
        (
            "employer_nics_state_pension_age_exemption",
            2026,
            {
                name: {
                    "age": {"2026": age},
                    "employment_income": {"2026": 50000},
                    "ni_class_1_income": {"2026": 50000},
                }
                for name, age in (("working_age", 45), ("pension_age", 70))
            },
            ["ni_liable", "ni_class_1_employer", "ni_class_1_employee"],
            "variables/gov/hmrc/national_insurance/class_1/ni_class_1_employer.py",
            ["variables/gov/hmrc/national_insurance/class_1/ni_liable.py"],
            "https://www.gov.uk/employee-reaches-state-pension-age",
            "Employers continue paying National Insurance after employees reach State Pension age.",
            "The employer formula uses the same ni_liable age mask as employee contributions. For otherwise identical £50,000 earnings, employer NICs falls to zero at age 70. HMRC states employer contributions continue after State Pension age. This is an employer-liability encoding concern; its national contribution to the NICs replay difference remains unsized.",
            ["autumn_budget_2024"],
        ),
        (
            "pension_taper_omits_employer_contributions",
            2024,
            {
                "worker": {
                    "age": {"2024": 45},
                    "employment_income": {"2024": 240000},
                    "employer_pension_contributions": {"2024": 50000},
                    "personal_pension_contributions": {"2024": 0},
                }
            },
            ["adjusted_net_income", "pension_annual_allowance"],
            "variables/gov/hmrc/income_tax/allowances/pension_annual_allowance.py",
            [
                "variables/gov/hmrc/income_tax/adjusted_net_income.py",
                "parameters/gov/hmrc/income_tax/adjusted_net_income_components.yaml",
                "parameters/gov/hmrc/income_tax/allowances/annual_allowance/taper.yaml",
                "parameters/gov/hmrc/income_tax/allowances/annual_allowance/default.yaml",
            ],
            "https://www.gov.uk/guidance/pension-schemes-work-out-your-tapered-annual-allowance",
            "Threshold income must exceed £200,000, and adjusted income adds employer pension contributions; the taper starts above £260,000.",
            "The pension taper uses adjusted_net_income, which excludes employer pension contributions, and omits the separate threshold-income gate. With £240,000 salary and £50,000 employer contributions it returns the full £60,000 allowance. HMRC's adjusted-income rule gives £290,000 and a £45,000 allowance for this controlled case. The national contribution to pension or Income Tax costing differences remains unsized.",
            ["spring_budget_2023", "autumn_budget_2024"],
        ),
        (
            "annual_allowance_charge_single_marginal_rate",
            2024,
            {
                "worker": {
                    "age": {"2024": 45},
                    "taxed_income": {"2024": 30000},
                    "pension_contributions_for_annual_allowance": {"2024": 80000},
                    "pension_annual_allowance": {"2024": 60000},
                }
            },
            ["personal_pension_contributions_tax"],
            "variables/gov/hmrc/pensions/private_pension_contributions_tax.py",
            ["parameters/gov/hmrc/income_tax/rates/uk.yaml"],
            "https://www.gov.uk/hmrc-internal-manuals/pensions-tax-manual/ptm056110",
            "The annual-allowance charge uses the rates that apply if the excess is added to taxable income, including bands crossed by that excess.",
            "The annual-allowance charge applies one marginal rate at taxed_income to the entire excess. Controlled intermediate inputs of £30,000 taxed income and £20,000 excess produce £4,000. HMRC's band-crossing rule gives £6,460 (£7,700 at 20% and £12,300 at 40%). Intermediate overrides isolate this formula rather than claim a complete household contribution history. The national contribution remains unsized.",
            ["spring_budget_2023", "autumn_budget_2024"],
        ),
    ]
    results = []
    for (
        identifier,
        year,
        people,
        variables,
        evidence_path,
        supporting_paths,
        primary_url,
        primary_rule,
        interpretation,
        events,
    ) in specifications:
        if case is not None and case != identifier:
            continue
        people = _with_income_behind_taxed_income(package_root, evidence_path, people)
        situation = {
            "people": people,
            "benunits": {name: {"members": [name]} for name in people},
            "households": {
                name: {"members": [name], "region": {str(year): "LONDON"}}
                for name in people
            },
        }
        simulation = simulation_type(situation=situation)
        try:
            observation = {}
            for name in variables:
                try:
                    observation[name] = simulation.calculate(name, year).tolist()
                except Exception:  # noqa: BLE001 - recorded, decided inconclusive
                    if not tolerant:
                        raise
                    observation[name] = None
        finally:
            del simulation
            gc.collect()
        results.append(
            {
                "id": identifier,
                "class": "pe_gap",
                "events": events,
                "variables": variables,
                "observation": observation,
                "situation": situation,
                "year": year,
                "evidence": _source(package_root, evidence_path, tolerant=tolerant),
                "supporting_evidence": [
                    _source(package_root, path, tolerant=tolerant)
                    for path in supporting_paths
                ],
                "primary_source": {
                    "url": primary_url,
                    "checked_date": "2026-10-09",
                    "rule": primary_rule,
                },
                "interpretation": interpretation,
                "national_effect": "unsized",
                "reproducer": f"--case {identifier}",
            }
        )
    return results


def investigate(
    case: str | None = None,
    *,
    expect_engine: str = LEGACY_ENGINE,
    tolerant: bool = False,
) -> list[dict]:
    """Run the cases on the installed engine, which must be ``expect_engine``.

    ``tolerant`` (re-verification on another engine) records a missing source
    file, parameter path or variable instead of raising; the predicates then
    report ``inconclusive``. The default reproduces the established run.
    """
    for key in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "TRANSFORMERS_OFFLINE"):
        os.environ[key] = "1"
    version = importlib.metadata.version("policyengine-uk")
    if version != expect_engine:
        raise RuntimeError(f"requires policyengine-uk {expect_engine}; found {version}")
    import policyengine_uk
    from policyengine_uk import CountryTaxBenefitSystem, Simulation

    package_root = Path(policyengine_uk.__file__).parent
    system = CountryTaxBenefitSystem()
    results = []

    def source(relative):
        return _source(package_root, relative, tolerant=tolerant)

    def value(path, date):
        try:
            return resolve(system, path, date)
        except (AttributeError, IndexError, KeyError):
            if not tolerant:
                raise
            return None

    def calculated(simulation, name, year):
        try:
            return simulation.calculate(name, year).tolist()
        except Exception:  # noqa: BLE001 - recorded, decided inconclusive
            if not tolerant:
                raise
            return None

    def formula_source(name, period):
        try:
            return inspect.getsource(system.variables[name].get_formula(period))
        except (KeyError, TypeError, OSError):
            if not tolerant:
                raise
            return None

    ca_source = source("variables/gov/dwp/carers_allowance.py")
    # The two synthetic people differ only in earnings; both provide 35 hours
    # of care. Separate households avoid interactions in the simple formula.
    allowance = None
    if case in (None, "carers_allowance_earnings_test_absent"):
        sim = Simulation(
            situation={
                "people": {
                    "low": {
                        "age": {"2025": 40},
                        "care_hours": {"2025": 35},
                        "employment_income": {"2025": 0},
                        "carers_allowance_reported": {"2025": 0},
                    },
                    "high": {
                        "age": {"2025": 40},
                        "care_hours": {"2025": 35},
                        "employment_income": {"2025": 100000},
                        "carers_allowance_reported": {"2025": 0},
                    },
                },
                "benunits": {
                    "low": {"members": ["low"]},
                    "high": {"members": ["high"]},
                },
                "households": {
                    "low": {"members": ["low"], "region": {"2025": "LONDON"}},
                    "high": {"members": ["high"], "region": {"2025": "LONDON"}},
                },
            }
        )
        try:
            allowance = sim.calculate("carers_allowance", 2025).tolist()
        except Exception:  # noqa: BLE001 - recorded, decided inconclusive
            if not tolerant:
                raise
        del sim
        gc.collect()
    results.append(
        {
            "id": "carers_allowance_earnings_test_absent",
            "class": "pe_gap",
            "events": ["autumn_budget_2024"],
            "variables": ["carers_allowance"],
            "observation": {
                "annual_earnings_gbp": [0, 100000],
                "care_hours_weekly": [35, 35],
                "annual_carers_allowance_gbp": allowance,
                "earnings_limit_parameter_names": list(
                    system.parameters.gov.dwp.carers_allowance.children
                )
                if not tolerant
                else sorted(
                    getattr(
                        getattr(system.parameters.gov.dwp, "carers_allowance", None),
                        "children",
                        {},
                    )
                ),
            },
            "evidence": ca_source,
            "interpretation": "The formula uses care hours or reported receipt and no earnings test. The AB2024 earnings-limit increase cannot be represented by this formula. This is an encoding gap, not a sized explanation of the national costing.",
            "reproducer": "--case carers_allowance_earnings_test_absent",
        }
    )

    cgt = {
        date: {
            name: value(f"gov.hmrc.cgt.{name}_rate", date)
            for name in ("basic", "higher", "additional")
        }
        for date in ("2024-10-29", "2024-10-30", "2025-04-06")
    }
    results.append(
        {
            "id": "cgt_main_rate_commencement",
            "class": "pe_gap",
            "events": ["autumn_budget_2024"],
            "variables": ["capital_gains_tax"],
            "observation": cgt,
            "evidence": source("parameters/gov/hmrc/cgt/basic_rate.yaml"),
            "interpretation": "The harvested AB2024 title specifies 30 October 2024, while the raw main-rate schedule starts 6 April 2025. CountryTaxBenefitSystem annualizes government policy from the 30 April snapshot. The first higher processed year, 2025, is inferred from that conversion rule and the recorded April 2025 values. This records a missing part-year 2024 commencement, not an additional delay to 2026. The parameter description also warns that it is under active development. The national timing contribution remains unsized.",
            "reproducer": "--case cgt_main_rate_commencement",
        }
    )

    sdlt_path = "gov.hmrc.stamp_duty.residential.purchase.additional.rate"
    sdlt = {
        date: [value(f"{sdlt_path}[{i}].rate", date) for i in range(5)]
        for date in ("2024-10-30", "2024-10-31", "2025-04-06", "2026-06-01")
    }
    results.append(
        {
            "id": "sdlt_additional_home_hike_absent",
            "class": "pe_gap",
            "events": ["autumn_budget_2024"],
            "variables": [
                "sdlt_on_residential_property_transactions",
                "stamp_duty_land_tax",
            ],
            "observation": sdlt,
            "evidence": source(
                "parameters/gov/hmrc/stamp_duty/residential/purchase/additional/rate.yaml",
            ),
            "interpretation": "The source title raises HRAD from 3% to 5% on 31 October 2024. The pinned additional-home scale still has rates 3/5/8/13/15% at these dates. A forward +2pp construction models this missing announced change; it is not a reversal already present in certified law.",
            "reproducer": "--case sdlt_additional_home_hike_absent",
        }
    )

    results.append(
        {
            "id": "private_school_vat_current_law_lever_zero",
            "class": "pe_gap",
            "events": ["autumn_budget_2024"],
            "variables": ["private_school_vat"],
            "observation": {
                date: value("gov.contrib.labour.private_school_vat", date)
                for date in ("2025-01-01", "2025-06-01", "2026-06-01")
            },
            "evidence": source("parameters/gov/contrib/labour/private_school_vat.yaml"),
            "interpretation": "The harvested AB2024 title applies 20% VAT to private-school education and boarding from January 2025. The pinned private-school VAT lever remains zero. The replay therefore executes a forward 20% construction; its imputed fees, attendance and omitted input-VAT recovery remain separate unsized scope limitations.",
            "reproducer": "--case private_school_vat_current_law_lever_zero",
        }
    )

    dividends = {
        date: {
            "uk_higher_threshold": value(
                "gov.hmrc.income_tax.rates.uk[1].threshold", date
            ),
            "dividend_higher_threshold": value(
                "gov.hmrc.income_tax.rates.dividends[1].threshold", date
            ),
            "uk_additional_threshold": value(
                "gov.hmrc.income_tax.rates.uk[2].threshold", date
            ),
            "dividend_additional_threshold": value(
                "gov.hmrc.income_tax.rates.dividends[2].threshold", date
            ),
        }
        for date in ("2024-06-01", "2025-06-01", "2026-06-01")
    }
    results.append(
        {
            "id": "dividend_band_threshold_lag",
            "class": "pe_gap",
            "events": [
                "autumn_statement_2023",
                "spring_budget_2024",
                "spring_budget_2023",
            ],
            "variables": ["dividend_income_tax", "income_tax"],
            "observation": dividends,
            "evidence": source("parameters/gov/hmrc/income_tax/rates/dividends.yaml"),
            "existing_issue": "https://github.com/PolicyEngine/policyengine-uk/issues/1822",
            "interpretation": "The existing mode-2 registry records the dividend thresholds lagging the main bands until April 2026. Their effect on a specific NICs costing's Income Tax interaction is unsized, so the national gap remains open.",
            "reproducer": "--case dividend_band_threshold_lag",
        }
    )

    class4 = {
        date: {
            name: value(f"gov.hmrc.national_insurance.class_4.thresholds.{name}", date)
            for name in ("lower_profits_limit", "upper_profits_limit")
        }
        for date in ("2026-06-01", "2027-06-01", "2028-06-01")
    }
    results.append(
        {
            "id": "class4_threshold_indexation_from_2027",
            "class": "pe_gap",
            "events": ["autumn_statement_2023", "spring_budget_2024"],
            "variables": ["ni_class_4"],
            "observation": class4,
            "evidence": source(
                "parameters/gov/hmrc/national_insurance/class_4/thresholds/lower_profits_limit.yaml",
            ),
            "interpretation": "The existing AB2025 baseline integrity assessment states the prior-law Class 4 freeze runs to April 2028 while the pin resumes uprating in April 2027. This changes the marginal tax base in 2027; no fraction of a replay gap is attributed without a paired run.",
            "assessment": "data/uk/ab2025_measures.json: personal_tax_thresholds_freeze_to_2031.baseline_integrity_note",
            "primary_source": {
                "url": "https://www.gov.uk/government/publications/autumn-statement-2022-documents/autumn-statement-2022-html",
                "title": "Autumn Statement 2022 tax section",
                "checked_date": "2026-10-09",
                "rule": "The Class 4 Lower Profits Limit of £12,570 and Upper Profits Limit of £50,270 were frozen until April 2028.",
            },
            "national_effect": "unsized",
            "reproducer": "--case class4_threshold_indexation_from_2027",
        }
    )

    uc_source = source("scenarios/uc_reform.py")
    uc_sim = None
    if case in (None, "uc_lcwra_protection_stops_at_2030"):
        uc_sim = Simulation(
            situation={
                "people": {
                    "carer": {
                        "age": {"2025": 40, "2029": 44, "2030": 45},
                        "uc_limited_capability_for_WRA": {
                            "2025": True,
                            "2029": True,
                            "2030": True,
                        },
                    }
                },
                "benunits": {"unit": {"members": ["carer"]}},
                "households": {
                    "household": {
                        "members": ["carer"],
                        "region": {
                            "2025": "LONDON",
                            "2029": "LONDON",
                            "2030": "LONDON",
                        },
                    }
                },
            }
        )
    results.append(
        {
            "id": "uc_lcwra_protection_stops_at_2030",
            "class": "investigation",
            "events": ["spring_statement_2025"],
            "variables": ["uc_LCWRA_element"],
            "observation": {
                "monthly_disabled_element": {
                    date: value(
                        "gov.dwp.universal_credit.elements.disabled.amount",
                        date,
                    )
                    for date in ("2025-06-01", "2026-06-01", "2030-06-01")
                },
                "annual_synthetic_lcwra_element": {
                    str(year): calculated(uc_sim, "uc_LCWRA_element", year)
                    if uc_sim is not None
                    else None
                    for year in (2029, 2030)
                },
                "formula_source": formula_source("uc_LCWRA_element", "2026"),
            },
            "evidence": uc_source,
            "interpretation": "The default Simulation constructor executes a deterministic UC modifier. It protects seeded existing claimants for 2026–2029, so inspecting uc_LCWRA_element alone would incorrectly claim all claimants are halved. The modifier loops over range(2026,2030), leaving CY2030 outside that protection override. The synthetic observation isolates the cutoff; continued-protection policy scope requires review before calling it an encoding defect.",
            "reproducer": "--case uc_lcwra_protection_stops_at_2030",
        }
    )
    if uc_sim is not None:
        del uc_sim
        gc.collect()
    results.extend(
        _additional_model_checks(package_root, Simulation, case, tolerant=tolerant)
    )
    for result in results:
        result["engine_version"] = version
        absent = set(result["variables"]) - set(system.variables)
        if absent:
            if not tolerant:
                raise RuntimeError(
                    f"diagnostic names unknown engine variables: {absent}"
                )
            result["absent_variables"] = sorted(absent)
    return results


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _close(value, target, tolerance=0.5) -> bool:
    return _number(value) and abs(value - target) <= tolerance


def _carers_allowance(o):
    awards = o.get("annual_carers_allowance_gbp")
    if not isinstance(awards, list) or len(awards) != 2:
        return "inconclusive"
    low, high = awards
    if not all(_number(v) for v in (low, high)):
        return "inconclusive"
    if low > 0 and low == high:
        return "persists"  # £100,000 of earnings leaves the award unchanged
    if low > 0 and high == 0:
        return "resolved"
    return "inconclusive"


def _cgt_commencement(o):
    # The processed CY2024 observation carries fiscal-year weights on 2.125.1:
    # policyengine_uk/utils/parameters.py:28-54,108-118 and
    # parameters/gov/hmrc/cgt/{basic,higher,additional}_rate.yaml:8-14.
    # The 2.89.2 converter instead samples 30 April (utils/parameters.py:26-47).
    before, after = o.get("2024-10-30", {}), o.get("2025-04-06", {})
    names = ("basic", "higher", "additional")
    old, new = (0.10, 0.20, 0.20), (0.18, 0.24, 0.24)
    current, later = [before.get(n) for n in names], [after.get(n) for n in names]
    if not all(_number(v) for v in current + later):
        return "inconclusive"
    if not all(_close(v, target, 1e-9) for v, target in zip(later, new)):
        return "inconclusive"
    if all(_close(v, target, 1e-9) for v, target in zip(current, old)):
        return "persists"
    blended = [a * 207 / 365 + b * 158 / 365 for a, b in zip(old, new)]
    if all(_close(v, target, 1e-9) for v, target in zip(current, blended)):
        return "resolved"
    return "inconclusive"


def _sdlt_surcharge(o):
    rates = o.get("2025-04-06")
    if rates == [0.03, 0.05, 0.08, 0.13, 0.15]:
        return "persists"
    if rates == [0.05, 0.07, 0.10, 0.15, 0.17]:
        return "resolved"
    return "inconclusive"


def _private_school_vat(o):
    values = [o.get(d) for d in ("2025-01-01", "2025-06-01", "2026-06-01")]
    if any(not _number(v) for v in values):
        return "inconclusive"
    if all(v == 0 for v in values):
        return "persists"
    if _close(values[1], 0.2, 1e-9) and _close(values[2], 0.2, 1e-9):
        return "resolved"
    return "inconclusive"


def _dividend_lag(o):
    pairs = []
    for date in ("2024-06-01", "2025-06-01"):
        row = o.get(date) or {}
        pairs += [
            (row.get("uk_higher_threshold"), row.get("dividend_higher_threshold")),
            (
                row.get("uk_additional_threshold"),
                row.get("dividend_additional_threshold"),
            ),
        ]
    if any(not _number(v) for pair in pairs for v in pair):
        return "inconclusive"
    return "persists" if any(a != b for a, b in pairs) else "resolved"


def _class4_indexation(o):
    # Prior law froze the Class 4 limits until April 2028; the defect is
    # uprating that resumes in April 2027.
    now, next_year = o.get("2026-06-01") or {}, o.get("2027-06-01") or {}
    values = [
        d.get(k)
        for d in (now, next_year)
        for k in ("lower_profits_limit", "upper_profits_limit")
    ]
    if any(not _number(v) for v in values):
        return "inconclusive"
    if values[2] > values[0] or values[3] > values[1]:
        return "persists"
    if values[2] == values[0] and values[3] == values[1]:
        return "resolved"
    return "inconclusive"


def _lcwra_cutoff(o):
    element = o.get("annual_synthetic_lcwra_element") or {}
    first, second = element.get("2029"), element.get("2030")
    if any(not isinstance(v, list) or len(v) != 1 for v in (first, second)):
        return "inconclusive"
    if not all(_number(v) for v in first + second):
        return "inconclusive"
    if second[0] < 0.75 * first[0]:
        return "persists"  # the protected award falls away in 2030
    if second[0] >= first[0]:
        return "resolved"
    return "inconclusive"


def _employer_nics_spa(o):
    employer = o.get("ni_class_1_employer") or []
    if len(employer) != 2 or not all(_number(v) for v in employer):
        return "inconclusive"
    working_age, pension_age = employer
    if working_age > 0 and pension_age == 0:
        return "persists"
    if working_age > 0 and _close(pension_age, working_age, 1.0):
        return "resolved"
    return "inconclusive"


def _pension_taper(o):
    allowances = o.get("pension_annual_allowance")
    if not isinstance(allowances, list) or len(allowances) != 1:
        return "inconclusive"
    allowance = allowances[0]
    if _close(allowance, 60_000):
        return "persists"  # HMRC's adjusted-income rule gives £45,000 here
    if _close(allowance, 45_000):
        return "resolved"
    return "inconclusive"


def _annual_allowance_charge(o):
    charges = o.get("personal_pension_contributions_tax")
    if not isinstance(charges, list) or len(charges) != 1:
        return "inconclusive"
    charge = charges[0]
    if _close(charge, 4_000):
        return "persists"  # the band-crossing rule gives £6,460
    if _close(charge, 6_460):
        return "resolved"
    return "inconclusive"


DEFECT_PREDICATES = {
    "carers_allowance_earnings_test_absent": _carers_allowance,
    "cgt_main_rate_commencement": _cgt_commencement,
    "sdlt_additional_home_hike_absent": _sdlt_surcharge,
    "private_school_vat_current_law_lever_zero": _private_school_vat,
    "dividend_band_threshold_lag": _dividend_lag,
    "class4_threshold_indexation_from_2027": _class4_indexation,
    "uc_lcwra_protection_stops_at_2030": _lcwra_cutoff,
    "employer_nics_state_pension_age_exemption": _employer_nics_spa,
    "pension_taper_omits_employer_contributions": _pension_taper,
    "annual_allowance_charge_single_marginal_rate": _annual_allowance_charge,
}


# What a JSON value of the wrong shape can raise inside a predicate: a wrong
# type (TypeError, AttributeError), a short or long unpack (ValueError), an
# index or slice into the wrong container (LookupError), or an integer beyond
# float range meeting float arithmetic (ArithmeticError).
MALFORMED = (TypeError, ValueError, AttributeError, LookupError, ArithmeticError)


def _has_nonfinite(value) -> bool:
    """Reject non-finite values anywhere in a JSON-shaped observation."""
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, float) and not math.isfinite(item):
            return True
        if isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return False


def defect_status(result: dict) -> str:
    """persists | resolved | inconclusive, from the case's own observation.

    A missing engine file or variable is inconclusive: code that moved is not
    evidence that the behaviour changed. Total over JSON records: a record or
    observation of the wrong shape (a list where a dict was expected, an
    integer too large for a float) is inconclusive, never an exception."""
    try:
        predicate = DEFECT_PREDICATES.get(result.get("id"))
        if predicate is None or result.get("absent_variables"):
            return "inconclusive"
        if "evidence" in result and not isinstance(result["evidence"], dict):
            return "inconclusive"
        if "supporting_evidence" in result and (
            not isinstance(result["supporting_evidence"], list)
            or any(not isinstance(item, dict) for item in result["supporting_evidence"])
        ):
            return "inconclusive"
        if "absent_variables" in result and not isinstance(
            result["absent_variables"], list
        ):
            return "inconclusive"
        evidence = [
            result.get("evidence") or {},
            *(result.get("supporting_evidence") or []),
        ]
        if any(item.get("missing") for item in evidence):
            return "inconclusive"
        observation = result.get("observation")
        if not isinstance(observation, dict) or _has_nonfinite(observation):
            return "inconclusive"
        status = predicate(observation)
    except MALFORMED:
        return "inconclusive"
    return status if status in STATUSES else "inconclusive"


def reverify(prior: list[dict], *, expect_engine: str) -> list[dict]:
    """Rerun every case on the installed engine and record each status."""
    if any("established" in record for record in prior):
        raise ValueError(
            "re-verify from the established diagnostics "
            "(results/uk/events/MODEL_DIAGNOSTICS.json), not a re-verified file"
        )
    established = {record["id"]: record for record in prior}
    results = investigate(None, expect_engine=expect_engine, tolerant=True)
    if {r["id"] for r in results} != set(established):
        raise RuntimeError(
            "re-verification case set differs from the prior diagnostics"
        )
    for result in results:
        prior_record = established[result["id"]]
        historical_fields = (
            "interpretation",
            "primary_source",
            "assessment",
            "existing_issue",
            "observation_provenance",
            "national_effect",
        )
        result["established"] = {
            "engine_version": prior_record["engine_version"],
            **{k: prior_record[k] for k in historical_fields if k in prior_record},
        }
        for field in historical_fields:
            result.pop(field, None)
        result["established_on"] = [prior_record["engine_version"]]
        result["reverified_on"] = result["engine_version"]
        result["status"] = defect_status(result)
        result["status_on_established_observation"] = defect_status(prior_record)
        description = {
            "persists": "the measured observation matches the predicate's persistence signature",
            "resolved": "the measured observation matches the predicate's resolution signature",
            "inconclusive": "the predicate cannot determine a status from the measured evidence",
        }[result["status"]]
        result["engine_observation"] = (
            f"On policyengine-uk {result['engine_version']}, {description}."
        )
        result["reproducer"] = (
            "--reverify results/uk/events/MODEL_DIAGNOSTICS.json "
            f"--expect-engine {expect_engine} --case {result['id']}"
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case")
    parser.add_argument(
        "--from-json",
        type=Path,
        help="Render already measured diagnostics without importing the engine",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--expect-engine",
        default=LEGACY_ENGINE,
        help="the exact policyengine-uk version that must be installed",
    )
    parser.add_argument(
        "--reverify",
        type=Path,
        help="prior MODEL_DIAGNOSTICS.json whose cases to rerun on this engine",
    )
    args = parser.parse_args(argv)
    if args.expect_engine != LEGACY_ENGINE and not (args.reverify or args.from_json):
        # Each case's interpretation describes what was observed on the
        # legacy engine; on another engine only --reverify scopes it under
        # `established` and reports a status (review of 463fc8d).
        parser.error(
            f"on policyengine-uk {args.expect_engine}, use --reverify "
            "<established MODEL_DIAGNOSTICS.json>"
        )
    if args.reverify:
        results = reverify(
            json.loads(args.reverify.read_text()), expect_engine=args.expect_engine
        )
    elif args.from_json:
        results = json.loads(args.from_json.read_text())
    else:
        results = investigate(args.case, expect_engine=args.expect_engine)
    if args.case:
        results = [r for r in results if r["id"] == args.case]
        if not results:
            parser.error("unknown diagnostic case")
    payload = json.dumps(results, indent=1, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end="")
    if args.report:
        versions = {r["engine_version"] for r in results}
        if len(versions) != 1:
            parser.error("a report requires observations from exactly one engine")
        engine_version = versions.pop()
        reverified = any("status" in r or "established" in r for r in results)
        variant = reverified or engine_version != LEGACY_ENGINE
        lines = [
            "# Measured UK replay model investigation candidates",
            "",
            (
                f"These small reproductions inspect policyengine-uk {engine_version}. "
                "Each status comes from the case's measured observation on this engine. "
                "Established diagnoses are labelled with their original engine. "
                "Their national effect is unsized."
            )
            if variant
            else (
                "These small reproductions inspect policyengine-uk 2.89.2. They identify "
                "specific encoding or parameter concerns, independently of the national "
                "OBR differences. Their national effect is unsized; no issue has been filed. "
                "These are model investigation candidates, not ten sized explanations "
                "of national differences."
            ),
            "",
        ]
        if not variant:
            lines += [
                (
                    "An [integrated execution receipt](../../results/uk/events/MODEL_DIAGNOSTICS_VERIFICATION.json) "
                    "binds the [preserved fresh output](../../results/uk/events/diagnostics/integrated_run_20261009.json) "
                    "to these observations. The Class 4 primary citation was added afterward; "
                    "the receipt distinguishes that metadata addition from engine results."
                ),
                "",
            ]
        for result in results:
            historical = result.get("established", {})
            primary = (
                historical.get("primary_source")
                if variant
                else result.get("primary_source")
            )
            evidence = result["evidence"]
            evidence_line = f"Evidence: `{evidence['engine_file']}`; " + (
                "file missing on this engine."
                if evidence.get("missing")
                else f"source SHA-256 `{evidence.get('sha256', 'not recorded')}`."
            )
            if not variant:
                evidence_line += (
                    " Full source and measured observations "
                    "are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`."
                )
            lines += [
                f"## {result['id']}",
                "",
                f"Class: `{result['class']}`. Variables: "
                + ", ".join(f"`{v}`" for v in result["variables"])
                + ".",
                "",
                result.get(
                    "engine_observation", "This observation has not been re-verified."
                )
                if variant
                else result["interpretation"],
                "",
                evidence_line,
                "",
                *(
                    [
                        f"Established on policyengine-uk {historical['engine_version']}: "
                        + historical["interpretation"],
                        "",
                    ]
                    if historical.get("interpretation")
                    else []
                ),
                *(
                    [
                        (
                            f"Primary rule (checked {primary['checked_date']}): "
                            f"{primary['rule']} "
                            f"[{primary.get('title', 'HMRC guidance')}]({primary['url']})."
                        ),
                        "",
                    ]
                    if primary
                    else []
                ),
                "```bash",
                "PYTHONPATH=. "
                + (".venv-candidate" if variant else ".venv-replay")
                + "/bin/python pipeline/diagnose_uk_event_models.py "
                + (
                    "--reverify results/uk/events/MODEL_DIAGNOSTICS.json "
                    f"--expect-engine {engine_version} --case {result['id']}"
                    if variant
                    else result["reproducer"]
                ),
                "```",
                "",
                "Observed:",
                "",
                "```json",
                json.dumps(result["observation"], indent=1, sort_keys=True),
                "```",
                "",
            ]
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
