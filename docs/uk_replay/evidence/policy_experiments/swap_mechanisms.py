"""Synthetic households behind two model-swap changes (pe-uk 2.132.6 against
2.143.0): the personal savings allowance and the high-income child benefit
charge. Prints each quantity on the installed policyengine-uk."""

import importlib.metadata

from policyengine_uk import Simulation

YEAR = 2025
NO_PSA = {
    "gov.hmrc.income_tax.allowances.personal_savings_allowance.basic": {
        "2025-01-01.2025-12-31": 0.0
    },
    "gov.hmrc.income_tax.allowances.personal_savings_allowance.higher": {
        "2025-01-01.2025-12-31": 0.0
    },
}


def saver():
    # £20,000 of earnings and £3,000 of interest: taxable non-savings income
    # of £7,430, which under ITA 2007 s. 12 removes the whole £5,000
    # starting-rate band.
    return {
        "people": {
            "p": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: 20_000},
                "savings_interest_income": {YEAR: 3_000},
            }
        },
        "benunits": {"b": {"members": ["p"]}},
        "households": {"h": {"members": ["p"]}},
    }


def parent():
    # £62,000 of earnings, £4,000 of employee pension contributions, one
    # child: adjusted net income falls with the relieved contributions.
    return {
        "people": {
            "p": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: 62_000},
                "employee_pension_contributions": {YEAR: 4_000},
            },
            "c": {"age": {YEAR: 5}},
        },
        "benunits": {
            "b": {"members": ["p", "c"], "would_claim_child_benefit": {YEAR: True}}
        },
        "households": {"h": {"members": ["p", "c"]}},
    }


print("policyengine-uk", importlib.metadata.version("policyengine-uk"))
for reform, label in ((None, "current law"), (NO_PSA, "no savings allowance")):
    sim = Simulation(situation=saver(), reform=reform)
    print(
        "saver", label,
        "starting-rate income", float(sim.calculate("savings_starter_rate_income", YEAR)[0]),
        "income tax", round(float(sim.calculate("income_tax", YEAR)[0]), 2),
    )
sim = Simulation(situation=parent())
print(
    "parent adjusted net income", round(float(sim.calculate("adjusted_net_income", YEAR)[0]), 2),
    "child benefit charge", round(float(sim.calculate("CB_HITC", YEAR)[0]), 2),
)
