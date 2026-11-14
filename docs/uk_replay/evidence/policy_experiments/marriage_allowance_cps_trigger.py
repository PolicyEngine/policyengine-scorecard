"""Minimal reproduction: setting the statutory Marriage Allowance rate to 0
switches on the CPS expanded Marriage Allowance reform.

Two synthetic married couples, 2025:
  A: basic-rate earner (£30,000) + partner with no income (eligible today)
  B: higher-rate earner (£60,000) + partner with no income (ineligible today)

Expected with gov.hmrc.income_tax.allowances.marriage_allowance.max = 0:
the allowance is 0 for both couples, so A's tax rises and B's is unchanged.
"""

import importlib.metadata

from policyengine_uk import Simulation

YEAR = 2025


def couple(earnings: float) -> dict:
    return {
        "people": {
            "earner": {"age": {YEAR: 40}, "employment_income": {YEAR: earnings}},
            "partner": {"age": {YEAR: 40}, "employment_income": {YEAR: 0}},
        },
        "benunits": {"b": {"members": ["earner", "partner"]}},
        "households": {"h": {"members": ["earner", "partner"]}},
    }


def run(earnings: float, reform: dict | None) -> dict:
    situation = couple(earnings)
    for person in situation["people"].values():
        person["marital_status"] = {YEAR: "MARRIED"}
        person["would_claim_marriage_allowance"] = {YEAR: True}
    sim = Simulation(situation=situation, reform=reform)
    return {
        "marriage_allowance": [float(x) for x in sim.calculate("marriage_allowance", YEAR)],
        "income_tax": [float(x) for x in sim.calculate("income_tax", YEAR)],
        "max": float(sim.tax_benefit_system.parameters.gov.hmrc.income_tax.allowances.marriage_allowance.max(f"{YEAR}-01-01")),
    }


ZERO = {"gov.hmrc.income_tax.allowances.marriage_allowance.max": {f"{YEAR}-01-01.{YEAR}-12-31": 0.0}}
print("policyengine-uk", importlib.metadata.version("policyengine-uk"))
for label, earnings in (("A basic-rate earner", 30_000), ("B higher-rate earner", 60_000)):
    base = run(earnings, None)
    zero = run(earnings, ZERO)
    print(f"{label}: current law {base}")
    print(f"{' ' * len(label)}  max = 0    {zero}")
    print(f"{' ' * len(label)}  couple's income tax change: {sum(zero['income_tax']) - sum(base['income_tax']):+.2f}")
