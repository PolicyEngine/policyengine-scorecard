"""Preserve the small source audit used by HISTORICAL_RULES.md.

Run with the existing audit venv; this reads source/YAML only, never imports
the country model or runs a simulation. Arguments are the installed package
directory and the shallow rulespec-uk checkout. Output is a durable JSON
evidence file next to the deliverables, independent of temporary checkouts.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml


UK_FILES = """
tax_benefit_system.py
programs.yaml
utils/parameters.py
variables/input/employment_income.py
variables/gov/simulation/labour_supply_response/income_elasticity_lsr.py
variables/gov/hmrc/income_tax/allowances/married_couples_allowance.py
variables/gov/hmrc/income_tax/bracketized_liability/tax_band.py
variables/gov/hmrc/income_tax/liability/dividend_income_tax.py
variables/gov/hmrc/income_tax/bases/taxed_dividend_income.py
variables/gov/hmrc/income_tax/earned_income_tax.py
variables/gov/hmrc/regional/pays_scottish_income_tax.py
variables/gov/hmrc/national_insurance/class_3/ni_class_3.py
variables/gov/hmrc/national_insurance/class_2/ni_class_2.py
variables/gov/hmrc/national_insurance/class_1/ni_class_1_employee.py
variables/gov/hmrc/national_insurance/class_1/ni_class_1_employer.py
variables/gov/hmrc/national_insurance/class_1/ni_liable.py
variables/gov/hmrc/national_insurance/class_4/ni_class_4.py
variables/gov/dwp/is_WTC_eligible.py
variables/gov/dwp/is_CTC_eligible.py
variables/gov/dwp/working_tax_credit.py
variables/gov/dwp/child_tax_credit.py
variables/gov/dwp/tax_credits_applicable_income.py
variables/gov/dwp/jsa_contrib.py
variables/gov/dwp/jsa_income.py
variables/gov/dwp/esa_contrib.py
variables/gov/dwp/esa_income.py
variables/gov/dwp/income_support_entitlement.py
variables/gov/dwp/income_support_applicable_amount.py
variables/gov/dwp/housing_benefit/housing_benefit_eligible.py
variables/gov/dwp/housing_benefit/entitlement/housing_benefit_entitlement.py
variables/gov/dwp/universal_credit/would_claim_uc.py
variables/gov/dwp/universal_credit/is_uc_eligible.py
variables/gov/dwp/universal_credit/housing_costs_element/uc_housing_costs_element.py
variables/gov/dwp/basic_state_pension.py
variables/gov/dwp/additional_state_pension.py
variables/gov/dwp/new_state_pension.py
variables/gov/dwp/state_pension_type.py
variables/gov/dwp/state_pension_reported.py
variables/gov/dwp/state_pension_age.py
utils/state_pension_age.py
variables/gov/dwp/pip/pip_dl.py
variables/gov/dwp/dla/dla_sc.py
variables/gov/dwp/attendance_allowance.py
variables/gov/dwp/carers_allowance_pre_overlap.py
variables/gov/dwp/council_tax_benefit.py
variables/input/consumption/property/council_tax.py
variables/gov/hmrc/sdlt_on_residential_property_transactions.py
variables/gov/hmrc/sdlt_liable.py
variables/gov/revenue_scotland/lbtt_liable.py
variables/gov/wra/ltt_liable.py
variables/gov/hmrc/vat.py
variables/gov/hmrc/fuel_duty/fuel_duty.py
variables/gov/hmrc/tobacco_duty/tobacco_duty.py
variables/gov/hmrc/alcohol_duty/beer_duty.py
variables/gov/dft/vehicle_excise_duty/car_vehicle_excise_duty.py
parameters/gov/simulation/labour_supply_responses/income_elasticity.yaml
parameters/gov/hmrc/income_tax/allowances/personal_allowance/amount.yaml
parameters/gov/hmrc/income_tax/allowances/personal_allowance/maximum_ANI.yaml
parameters/gov/hmrc/income_tax/allowances/personal_savings_allowance/basic.yaml
parameters/gov/hmrc/income_tax/allowances/dividend_allowance.yaml
parameters/gov/hmrc/income_tax/allowances/marriage_allowance/max.yaml
parameters/gov/hmrc/income_tax/rates/uk.yaml
parameters/gov/hmrc/income_tax/rates/scotland/rates.yaml
parameters/gov/hmrc/income_tax/rates/dividends.yaml
parameters/gov/hmrc/income_tax/rates/savings_starter_rate/allowance.yaml
parameters/gov/hmrc/national_insurance/class_1/rates/employee/main.yaml
parameters/gov/hmrc/national_insurance/class_1/rates/employee/additional.yaml
parameters/gov/hmrc/national_insurance/class_1/rates/employer.yaml
parameters/gov/hmrc/national_insurance/class_1/thresholds/primary_threshold.yaml
parameters/gov/hmrc/national_insurance/class_2/flat_rate.yaml
parameters/gov/hmrc/national_insurance/class_4/rates/main.yaml
parameters/gov/hmrc/national_insurance/class_4/rates/additional.yaml
parameters/gov/dwp/tax_credits/working_tax_credit/elements/basic.yaml
parameters/gov/dwp/tax_credits/working_tax_credit/min_hours/couple_with_children.yaml
parameters/gov/dwp/tax_credits/child_tax_credit/elements/child_element.yaml
parameters/gov/dwp/tax_credits/means_test/income_threshold.yaml
parameters/gov/dwp/JSA/income/amount_over_25.yaml
parameters/gov/dwp/ESA/income/amount_over_25.yaml
parameters/gov/dwp/income_support/amounts/amount_16_24.yaml
parameters/gov/dwp/income_support/eligibility/lone_parent_youngest_child_age_limit.yaml
parameters/gov/dwp/universal_credit/standard_allowance/amount.yaml
parameters/gov/dwp/universal_credit/means_test/work_allowance.yaml
parameters/gov/dwp/universal_credit/rollout_rate.yaml
parameters/gov/hmrc/child_benefit/amount/eldest.yaml
parameters/gov/hmrc/income_tax/charges/CB_HITC/phase_out_start.yaml
parameters/gov/dwp/state_pension/basic_state_pension/amount.yaml
parameters/gov/dwp/state_pension/new_state_pension/active.yaml
parameters/gov/dwp/state_pension/age/age_by_birth_date.yaml
parameters/gov/dwp/state_pension/age/day_by_birth_date.yaml
parameters/gov/dwp/state_pension/age/male/age.yaml
parameters/gov/dwp/state_pension/age/male/born_before.yaml
parameters/gov/dwp/pension_credit/guarantee_credit/minimum_guarantee.yaml
parameters/gov/dwp/pension_credit/savings_credit/threshold.yaml
parameters/gov/dwp/benefit_cap.yaml
parameters/gov/dwp/housing_benefit/means_test/withdrawal_rate.yaml
parameters/gov/dwp/LHA/maximum/A.yaml
parameters/gov/local_authorities/england/council_tax_reduction/pensioners/means_test/withdrawal_rate.yaml
parameters/gov/local_authorities/scotland/council_tax_reduction/means_test/withdrawal_rate.yaml
parameters/gov/local_authorities/wales/council_tax_reduction/means_test/withdrawal_rate.yaml
parameters/gov/hmrc/vat/standard_rate.yaml
parameters/gov/hmrc/fuel_duty/petrol_and_diesel.yaml
parameters/gov/hmrc/cgt/basic_rate.yaml
parameters/gov/hmrc/cgt/higher_rate.yaml
parameters/gov/hmrc/cgt/annual_exempt_amount.yaml
parameters/gov/hmrc/stamp_duty/residential/purchase/main/subsequent.yaml
parameters/gov/hmrc/stamp_duty/residential/purchase/main/first/max.yaml
parameters/gov/hmrc/stamp_duty/residential/purchase/additional/min.yaml
parameters/gov/revenue_scotland/lbtt/residential/rate.yaml
parameters/gov/wra/land_transaction_tax/residential/primary.yaml
""".split()

RS_FILES = """
README.md
uk/statutes/ukpga/2007/3/35.yaml
uk/statutes/ukpga/2007/3/8.yaml
uk/statutes/ukpga/2007/3/55B.yaml
uk/statutes/ukpga/1992/4/8.yaml
uk/statutes/ukpga/1992/4/15.yaml
uk/statutes/ukpga/1992/4/13.yaml
uk/regulations/uksi/2013/376/80A.yaml
uk/regulations/uksi/2013/376/24A.yaml
uk/regulations/uksi/2002/2005/schedule/2.yaml
uk/regulations/uksi/2002/2007/7.yaml
uk/regulations/uksi/2024/247/3.yaml
uk/regulations/uksi/1987/1967/53.yaml
uk/regulations/uksi/1996/207/116.yaml
uk/regulations/uksi/2008/794/118.yaml
uk/policies/esa_income_related_applicable_amount_pipeline.yaml
uk/policies/govuk/state-pension.yaml
uk/policies/universal_credit_composed_award_pipeline.yaml
uk/statutes/asp/2013/11/24.yaml
uk/statutes/anaw/2017/1/24.yaml
""".split()


def source(root: Path, paths: list[str]):
    missing = [rel for rel in paths if not (root / rel).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing sources under {root}: {missing}")
    out = {}
    for rel in paths:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
        out[rel] = {"sha256": hashlib.sha256(raw).hexdigest(), "text": raw.decode()}
    return out


def searches(root: Path, patterns: dict[str, str], subdirs: list[str]):
    globs = ["--glob", "*.py", "--glob", "*.yaml", "--glob", "!*.test.yaml"]
    file_list = subprocess.check_output(["rg", "--files", *globs, *subdirs],
                                        cwd=root, text=True).splitlines()
    matches = {label: {"pattern": expression, "hits": []}
               for label, expression in patterns.items()}
    compiled = {label: re.compile(expression, re.I)
                for label, expression in patterns.items()}
    expressions = [item for pattern in patterns.values() for item in ["-e", pattern]]
    result = subprocess.run(["rg", "--json", "--ignore-case", *globs,
                             *expressions, *subdirs], cwd=root, text=True,
                            capture_output=True, check=False)
    if result.returncode not in {0, 1}:
        raise RuntimeError(result.stderr)
    for row in result.stdout.splitlines():
        record = json.loads(row)
        if record["type"] != "match":
            continue
        data = record["data"]
        line = data["lines"]["text"].rstrip("\n")
        for label, expression in compiled.items():
            if expression.search(line):
                matches[label]["hits"].append({"file": data["path"]["text"],
                                              "line": data["line_number"], "text": line})
    return {"scanned_files": len(file_list), "roots": subdirs, "queries": matches}


def main():
    uk, rs = map(Path, sys.argv[1:3])
    # All national fiscal modules, excluding companion test/ProgramSpec files.
    rules = []
    for path in sorted((rs / "uk").rglob("*.yaml")):
        if path.name.endswith(".test.yaml"):
            continue
        data = yaml.load(path.read_text(), Loader=yaml.CSafeLoader) or {}
        if data.get("format") != "rulespec/v1":
            continue
        for rule in data.get("rules", []):
            versions = rule.get("versions", [])
            rules.append({"file": str(path.relative_to(rs)), "name": rule["name"],
                          "kind": rule.get("kind"), "versions": versions})
    print(f"Read {len(rules)} national RuleSpec rules", flush=True)
    uk_patterns = {
        "inheritance_tax": r"inheritance|nil.rate.band|\biht\b",
        "contracted_out_nics": r"contracted[ _-]?out",
        "employment_allowance": r"employment[ _-]allowance",
        "apd_and_ipt": r"air[ _-]passenger|insurance[ _-]premium",
        "age_related_allowances": r"age[ _-]related|age[ _-]allowance",
        "social_sector_size_criteria": r"under.occup|bedroom.tax|\bB13\b|spare.room",
        "council_tax_freeze_grants": r"council.tax.freeze|freeze.grant",
    }
    uk_sources = source(uk, UK_FILES)
    rs_sources = source(rs, RS_FILES)
    print(f"Preserved {len(uk_sources)} UK source files and {len(rs_sources)} RuleSpec files", flush=True)
    out = {
        "audit_date": "2026-10-09",
        "method": "Read raw YAML/source only. No model import or simulation.",
        "policyengine_uk_version": importlib.metadata.version("policyengine-uk"),
        "policyengine_core_version": importlib.metadata.version("policyengine-core"),
        "rulespec_uk_commit": subprocess.check_output(["git", "-C", str(rs), "rev-parse", "HEAD"], text=True).strip(),
        "uk_sources": uk_sources,
        "uk_absence_searches": searches(uk, uk_patterns, ["parameters", "variables"]),
        "uc_rollout_formula_search": searches(uk, {"rollout_rate": r"rollout_rate"}, ["variables"]),
        "rulespec_sources": rs_sources,
        "rulespec_national_rules": rules,
        "rulespec_absence_searches": searches(rs, {"additional_state_pension": r"additional.state.pension|\bSERPS\b|\bS2P\b"}, ["uk"]),
        "absence_search_interpretation": {
            "employment_allowance": "One metadata reference-title hit; no implementing parameter/variable machinery found.",
            "age_related_allowances": "All 33 hits inspected: Marriage Allowance/mileage substrings or SDA age-related addition comments. None implements income-tax age-related personal allowances.",
        },
    }
    dest = Path(__file__).resolve().parent.parent / "evidence" / "historical_rules_sources.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, default=str, sort_keys=True) + "\n")
    print(f"Wrote {dest}: {len(out['uk_sources'])} UK files, {len(rules)} national RuleSpec rules")


if __name__ == "__main__":
    main()
