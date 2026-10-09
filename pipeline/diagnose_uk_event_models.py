"""Small, pinned engine reproducers for event replay investigation candidates.

These record engine observations, not a claim that their effects explain a
specified fraction of a national OBR difference. No issue is filed. The
synthetic Carer's Allowance calculation uses two people rather than loading
or simulating the certified national population.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import inspect
import json
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


def _source(package_root: Path, relative: str) -> dict:
    payload = (package_root / relative).read_bytes()
    return {
        "engine_file": relative,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "source": payload.decode(),
    }


def investigate(case: str | None = None) -> list[dict]:
    for key in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "TRANSFORMERS_OFFLINE"):
        os.environ[key] = "1"
    version = importlib.metadata.version("policyengine-uk")
    if version != "2.89.2":
        raise RuntimeError(f"requires policyengine-uk 2.89.2; found {version}")
    import policyengine_uk
    from policyengine_uk import CountryTaxBenefitSystem, Simulation

    package_root = Path(policyengine_uk.__file__).parent
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
    for result in results:
        result["engine_version"] = version
        absent = set(result["variables"]) - set(system.variables)
        if absent:
            raise RuntimeError(f"diagnostic names unknown engine variables: {absent}")
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
    args = parser.parse_args(argv)
    results = (
        json.loads(args.from_json.read_text())
        if args.from_json
        else investigate(args.case)
    )
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
        lines = [
            "# Measured UK replay model investigation candidates",
            "",
            (
                "These small reproductions inspect policyengine-uk 2.89.2. They identify "
                "specific encoding or parameter concerns, independently of the national "
                "OBR differences. Their national effect is unsized; no issue has been filed. "
                "Fewer than ten observations are reported because the lane does not invent "
                "mechanisms to fill a requested list."
            ),
            "",
        ]
        for result in results:
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
                    "are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`."
                ),
                "",
                "```bash",
                ".venv-replay/bin/python pipeline/diagnose_uk_event_models.py "
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
