"""The two Growth Plan SDLT constructions on synthetic households: additional
dwellings at £200,000 and £1,000,000 (either side of the £250,000 band), and a
lease whose rent takes cumulative rent from £150,000 to £200,000. Reforms are
read from the committed AS2022 spec:

    python -I sdlt_growth_plan_check.py data/uk/experiments/autumn_statement_2022.json
"""

import importlib.metadata
import json
import sys

from policyengine_uk import Simulation

spec = json.load(open(sys.argv[1]))
reforms = {e["experiment_id"]: e["reform"] for e in spec["experiments"]}
PRICES = (200_000, 1_000_000)


def situation(year):
    households = {
        f"h{i}": {
            "members": [f"p{i}"],
            "additional_residential_property_purchased": {year: price},
            "cumulative_residential_rent": {year: 150_000},
            "rent": {year: 50_000},
        }
        for i, price in enumerate(PRICES)
    }
    return {
        "people": {f"p{i}": {"age": {year: 45}} for i in range(len(PRICES))},
        "benunits": {f"b{i}": {"members": [f"p{i}"]} for i in range(len(PRICES))},
        "households": households,
    }


print("policyengine-uk", importlib.metadata.version("policyengine-uk"))
for eid, year in (
    ("as2022_sdlt_nil_rate_bands_2024", 2024),
    ("as2022_sdlt_end_growth_plan_relief", 2025),
):
    for label, reform in (("modern", None), ("counterfactual", reforms[eid])):
        sim = Simulation(situation=situation(year), reform=reform)
        purchase = sim.calculate("sdlt_on_residential_property_transactions", year)
        rent = sim.calculate("sdlt_on_residential_property_rent", year)
        cells = ", ".join(
            f"£{price:,} dwelling {float(p):,.0f}" for price, p in zip(PRICES, purchase)
        )
        print(f"{eid} {year} {label:14} {cells}; lease {float(rent[0]):,.0f}")
