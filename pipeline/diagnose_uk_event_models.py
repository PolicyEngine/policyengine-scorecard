"""Small, pinned engine reproducers for event replay investigation candidates.

These record engine observations, not a claim that their effects explain a
specified fraction of a national OBR difference. No issue is filed. The
synthetic checks use one or two people rather than loading or simulating the
certified national population, and release each world before the next.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import inspect
import json
import os
import re
from pathlib import Path

from pipeline.uk_bundle import (
    DEFAULT_BUNDLE,
    bundle_identity,
    validate_bundle_identity,
    validate_bundle_path,
)

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


def _source(package_root: Path, relative: str) -> dict:
    payload = (package_root / relative).read_bytes()
    return {
        "engine_file": relative,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "source": payload.decode(),
    }


def _additional_model_checks(package_root: Path, simulation_type, case: str | None):
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
            observation = {
                name: simulation.calculate(name, year).tolist() for name in variables
            }
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
                "evidence": _source(package_root, evidence_path),
                "supporting_evidence": [
                    _source(package_root, path) for path in supporting_paths
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


PAIRED_CASES = (
    "annual_allowance_relief_and_charge_pe_uk_2237",
    "sdlt_additional_purchase_stock_pe_uk_2238",
    "uc_standard_allowance_2027_2030_pe_uk_2239",
    "hicbc_opt_out",
    "nics_threshold_freeze_end_date",
)


def current_bundle_observation(result, identity):
    """Keep earlier diagnoses as references, not assertions about a later pin."""
    if identity["bundle_key"] == DEFAULT_BUNDLE:
        return result
    result.update(identity)
    result["legacy_reference"] = {
        "bundle_key": DEFAULT_BUNDLE,
        "engine_version": "2.89.2",
        "class": result["class"],
        "interpretation": result["interpretation"],
        "evidence": "results/uk/events/MODEL_DIAGNOSTICS.json",
    }
    result["class"] = "bundle_observation"
    result["interpretation"] = (
        "Current parameters, formula source and synthetic observations are recorded "
        "for the selected certified bundle. The legacy_reference retains the "
        "2.89.2 diagnosis for comparison; interpretation at this pin requires "
        "review of the current observations and source. National contributions "
        "remain unsized."
    )
    return result


def _paired_checks(package_root, simulation_type, case):
    """Issue-body reproducers, identical controlled inputs at both bundle pins."""
    if case not in PAIRED_CASES:
        return []
    year = 2025 if case in (PAIRED_CASES[1], PAIRED_CASES[3]) else 2024
    people = {}
    units = {}
    households = {}
    if case == PAIRED_CASES[0]:
        for amount in (60000, 80000):
            name = f"contributions_{amount}"
            people[name] = {
                "age": {str(year): 45},
                "employment_income": {str(year): 150000},
                "personal_pension_contributions": {str(year): amount},
            }
            units[name] = {"members": [name]}
            households[name] = {"members": [name], "region": {str(year): "LONDON"}}
        variables = [
            "pension_contributions_relief",
            "personal_pension_contributions_tax",
            "income_tax",
        ]
        evidence = "variables/gov/hmrc/pensions/pension_contributions_relief.py"
        issue = 2237
        years = [year]
    elif case == PAIRED_CASES[1]:
        for purchased in (False, True):
            name = f"purchase_{str(purchased).lower()}"
            people[name] = {
                "age": {str(year): 45},
                "employment_income": {str(year): 80000},
            }
            units[name] = {"members": [name]}
            households[name] = {
                "members": [name],
                "region": {str(year): "LONDON"},
                "main_residence_value": {str(year): 600000},
                "other_residential_property_value": {str(year): 2000000},
                "property_purchased": {str(year): purchased},
            }
        variables = ["additional_residential_property_purchased", "stamp_duty_land_tax"]
        evidence = "variables/household/consumption/additional_residential_property_purchased.py"
        issue = 2238
        years = [year]
    elif case == PAIRED_CASES[2]:
        years = list(range(2025, 2031))
        people["claimant"] = {"age": {str(y): 30 for y in years}}
        units["unit"] = {"members": ["claimant"]}
        households["household"] = {
            "members": ["claimant"],
            "region": {str(y): "LONDON" for y in years},
        }
        variables = ["uc_standard_allowance"]
        evidence = "variables/gov/dwp/universal_credit/standard_allowance/uc_standard_allowance.py"
        issue = 2239
    elif case == PAIRED_CASES[3]:
        years = [year]
        for opted in (False, True):
            name = f"opt_out_{str(opted).lower()}"
            adult, child = name + "_adult", name + "_child"
            people[adult] = {
                "age": {str(year): 45},
                "employment_income": {str(year): 100000},
            }
            people[child] = {"age": {str(year): 8}}
            units[name] = {
                "members": [adult, child],
                "child_benefit_opts_out": {str(year): opted},
                "would_claim_child_benefit": {str(year): True},
            }
            households[name] = {
                "members": [adult, child],
                "region": {str(year): "LONDON"},
            }
        variables = ["child_benefit", "CB_HITC", "child_benefit_less_tax_charge"]
        evidence = "variables/gov/hmrc/child_benefit.py"
        issue = None
    else:
        years = list(range(2026, 2031))
        people["worker"] = {
            "age": {str(y): 45 for y in years},
            "self_employment_income": {str(y): 30000 for y in years},
        }
        units["unit"] = {"members": ["worker"]}
        households["household"] = {
            "members": ["worker"],
            "region": {str(y): "LONDON" for y in years},
        }
        variables = ["ni_class_4"]
        evidence = "parameters/gov/hmrc/national_insurance/class_4/thresholds/lower_profits_limit.yaml"
        issue = None
    situation = {"people": people, "benunits": units, "households": households}
    simulation = simulation_type(situation=situation)
    try:
        observation = {
            str(y): {v: simulation.calculate(v, y).tolist() for v in variables}
            for y in years
        }
        if case == PAIRED_CASES[4]:
            for y in years:
                observation[str(y)]["class4_thresholds"] = {
                    name: resolve(
                        simulation.tax_benefit_system,
                        f"gov.hmrc.national_insurance.class_4.thresholds.{name}",
                        f"{y}-01-01",
                    )
                    for name in ("lower_profits_limit", "upper_profits_limit")
                }
    finally:
        del simulation
        gc.collect()
    return [
        {
            "id": case,
            "class": "paired_dev_observation",
            "variables": variables,
            "situation": situation,
            "years": years,
            "observation": observation,
            "evidence": _source(package_root, evidence),
            "existing_issue": f"https://github.com/PolicyEngine/policyengine-uk/issues/{issue}"
            if issue
            else None,
            "assessment": "docs/uk_replay/MODEL_INVESTIGATIONS.md: class4_threshold_indexation_from_2027"
            if case == PAIRED_CASES[4]
            else None,
            "interpretation": "Controlled synthetic observations for descriptive engine comparison. Compare the same inputs at each certified pin; this run does not size or attribute a national difference.",
            "national_effect": "unsized",
            "reproducer": f"--case {case}",
        }
    ]


def investigate(case: str | None = None, bundle=DEFAULT_BUNDLE) -> list[dict]:
    for key in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "TRANSFORMERS_OFFLINE"):
        os.environ[key] = "1"
    version = importlib.metadata.version("policyengine-uk")
    identity = bundle_identity(bundle)
    for package, expected in identity["engine_versions"].items():
        if importlib.metadata.version(package) != expected:
            raise RuntimeError(f"selected bundle requires {package} {expected}")
    import policyengine_uk
    from policyengine_uk import CountryTaxBenefitSystem, Simulation

    package_root = Path(policyengine_uk.__file__).parent
    if case in PAIRED_CASES:
        results = _paired_checks(package_root, Simulation, case)
        for result in results:
            result["engine_version"] = version
            if bundle != DEFAULT_BUNDLE:
                result.update(identity)
        return results
    system = CountryTaxBenefitSystem()
    results = []

    ca_source = _source(package_root, "variables/gov/dwp/carers_allowance.py")
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
        allowance = sim.calculate("carers_allowance", 2025).tolist()
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
                ),
            },
            "evidence": ca_source,
            "interpretation": "The formula uses care hours or reported receipt and no earnings test. The AB2024 earnings-limit increase cannot be represented by this formula. This is an encoding gap, not a sized explanation of the national costing.",
            "reproducer": "--case carers_allowance_earnings_test_absent",
        }
    )

    cgt = {
        date: {
            name: resolve(system, f"gov.hmrc.cgt.{name}_rate", date)
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
            "evidence": _source(
                package_root, "parameters/gov/hmrc/cgt/basic_rate.yaml"
            ),
            "interpretation": "The harvested AB2024 title specifies 30 October 2024, while the raw main-rate schedule starts 6 April 2025. CountryTaxBenefitSystem annualizes government policy from the 30 April snapshot. The first higher processed year, 2025, is inferred from that conversion rule and the recorded April 2025 values. This records a missing part-year 2024 commencement, not an additional delay to 2026. The parameter description also warns that it is under active development. The national timing contribution remains unsized.",
            "reproducer": "--case cgt_main_rate_commencement",
        }
    )

    sdlt_path = "gov.hmrc.stamp_duty.residential.purchase.additional.rate"
    sdlt = {
        date: [resolve(system, f"{sdlt_path}[{i}].rate", date) for i in range(5)]
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
            "evidence": _source(
                package_root,
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
                date: resolve(system, "gov.contrib.labour.private_school_vat", date)
                for date in ("2025-01-01", "2025-06-01", "2026-06-01")
            },
            "evidence": _source(
                package_root, "parameters/gov/contrib/labour/private_school_vat.yaml"
            ),
            "interpretation": "The harvested AB2024 title applies 20% VAT to private-school education and boarding from January 2025. The pinned private-school VAT lever remains zero. The replay therefore executes a forward 20% construction; its imputed fees, attendance and omitted input-VAT recovery remain separate unsized scope limitations.",
            "reproducer": "--case private_school_vat_current_law_lever_zero",
        }
    )

    dividends = {
        date: {
            "uk_higher_threshold": resolve(
                system, "gov.hmrc.income_tax.rates.uk[1].threshold", date
            ),
            "dividend_higher_threshold": resolve(
                system, "gov.hmrc.income_tax.rates.dividends[1].threshold", date
            ),
            "uk_additional_threshold": resolve(
                system, "gov.hmrc.income_tax.rates.uk[2].threshold", date
            ),
            "dividend_additional_threshold": resolve(
                system, "gov.hmrc.income_tax.rates.dividends[2].threshold", date
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
            "evidence": _source(
                package_root, "parameters/gov/hmrc/income_tax/rates/dividends.yaml"
            ),
            "existing_issue": "https://github.com/PolicyEngine/policyengine-uk/issues/1822",
            "interpretation": "The existing mode-2 registry records the dividend thresholds lagging the main bands until April 2026. Their effect on a specific NICs costing's Income Tax interaction is unsized, so the national gap remains open.",
            "reproducer": "--case dividend_band_threshold_lag",
        }
    )

    class4 = {
        date: {
            name: resolve(
                system, f"gov.hmrc.national_insurance.class_4.thresholds.{name}", date
            )
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
            "evidence": _source(
                package_root,
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

    uc_source = _source(package_root, "scenarios/uc_reform.py")
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
                    date: resolve(
                        system,
                        "gov.dwp.universal_credit.elements.disabled.amount",
                        date,
                    )
                    for date in ("2025-06-01", "2026-06-01", "2030-06-01")
                },
                "annual_synthetic_lcwra_element": {
                    str(year): uc_sim.calculate("uc_LCWRA_element", year).tolist()
                    if uc_sim is not None
                    else None
                    for year in (2029, 2030)
                },
                "formula_source": inspect.getsource(
                    system.variables["uc_LCWRA_element"].get_formula("2026")
                ),
            },
            "evidence": uc_source,
            "interpretation": "The default Simulation constructor executes a deterministic UC modifier. It protects seeded existing claimants for 2026–2029, so inspecting uc_LCWRA_element alone would incorrectly claim all claimants are halved. The modifier loops over range(2026,2030), leaving CY2030 outside that protection override. The synthetic observation isolates the cutoff; continued-protection policy scope requires review before calling it an encoding defect.",
            "reproducer": "--case uc_lcwra_protection_stops_at_2030",
        }
    )
    if uc_sim is not None:
        del uc_sim
        gc.collect()
    results.extend(_additional_model_checks(package_root, Simulation, case))
    for result in results:
        result["engine_version"] = version
        if bundle != DEFAULT_BUNDLE:
            current_bundle_observation(result, identity)
        absent = set(result["variables"]) - set(system.variables)
        if absent:
            raise RuntimeError(f"diagnostic names unknown engine variables: {absent}")
    return results


DEFAULT_REPORT = Path("docs/uk_replay/MODEL_INVESTIGATIONS.md")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case")
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--from-json",
        type=Path,
        help="Render already measured diagnostics without importing the engine",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    # Check both destinations before any engine work or write.
    for destination in (args.output, args.report):
        if destination is not None:
            validate_bundle_path(destination, args.bundle, kind="results")
    if (
        args.report is not None
        and args.bundle != DEFAULT_BUNDLE
        and args.report.resolve() == (ROOT / DEFAULT_REPORT).resolve()
    ):
        parser.error("the default bundle's investigation report is not writable here")
    results = (
        json.loads(args.from_json.read_text())
        if args.from_json
        else investigate(args.case, args.bundle)
    )
    if args.from_json:
        for result in results:
            validate_bundle_identity(result, args.bundle)
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
        model_version = bundle_identity(args.bundle)["engine_versions"][
            "policyengine-uk"
        ]
        lines = [
            "# Measured UK replay model investigation candidates",
            "",
            (
                f"These small reproductions inspect policyengine-uk {model_version}. They identify "
                "specific encoding or parameter concerns, independently of the national "
                "OBR differences. Their national effect is unsized; no issue has been filed. "
                "These are model investigation candidates, not ten sized explanations "
                "of national differences."
            ),
            "",
            *(
                [
                    (
                        "An [integrated execution receipt](../../results/uk/events/MODEL_DIAGNOSTICS_VERIFICATION.json) "
                        "binds the [preserved fresh output](../../results/uk/events/diagnostics/integrated_run_20261009.json) "
                        "to these observations. The Class 4 primary citation was added afterward; "
                        "the receipt distinguishes that metadata addition from engine results."
                    ),
                    "",
                ]
                if args.bundle == DEFAULT_BUNDLE
                else []
            ),
        ]
        for result in results:
            primary = result.get("primary_source")
            lines += [
                f"## {result['id']}",
                "",
                f"Class: `{result['class']}`. Variables: "
                + ", ".join(f"`{v}`" for v in result["variables"])
                + ".",
                "",
                result["interpretation"],
                "",
                (
                    f"Evidence: `{result['evidence']['engine_file']}`; source SHA-256 "
                    f"`{result['evidence']['sha256']}`. Full source and measured observations "
                    + (
                        "are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`."
                        if args.bundle == DEFAULT_BUNDLE
                        else f"are retained in `{args.from_json or args.output or 'the saved bundle diagnostic output'}`."
                    )
                ),
                "",
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
                (
                    "PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py "
                    if args.bundle == DEFAULT_BUNDLE
                    else f"PYTHONPATH=. <bundle_python> -m pipeline.diagnose_uk_event_models --bundle {args.bundle} "
                )
                + result["reproducer"],
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
