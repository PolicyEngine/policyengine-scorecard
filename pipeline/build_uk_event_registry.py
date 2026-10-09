"""Build an accounted OBR fiscal-event registry against the certified UK pin.

The source is the checked-in, byte-identical copy of the user's harvested PMD.
Every source row, including zero cells and heads outside household scope, has
one stable identity and exactly one classification. £ accounting uses Decimal
on the harvested GBP values, avoiding a floating-point cancellation identity.

    PYTHONPATH=. .venv-replay/bin/python pipeline/build_uk_event_registry.py --event autumn_budget_2024
    PYTHONPATH=. .venv-replay/bin/python pipeline/build_uk_event_registry.py --event autumn_budget_2024 --check
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from pathlib import Path

try:
    from pipeline.uk_engine_registry import engine_dumps
except ModuleNotFoundError:
    from uk_engine_registry import engine_dumps

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz"
SOURCE_MANIFEST = ROOT / "sources/uk_replay/source.json"
CERTIFIED = ROOT / "data/uk/certified_bundle.json"
EVENTS = {
    "autumn_budget_2024": "Autumn Budget 2024",
    "autumn_statement_2023": "Autumn Statement 2023",
    "spring_budget_2024": "Spring Budget 2024",
    "spring_statement_2025": "Spring Statement 2025",
    "spring_budget_2023": "Spring Budget 2023",
}
CLASSES = ("expressible", "partial", "not_expressible", "out_of_household_scope")
AXES = [
    "population_vintage",
    "baseline_vintage",
    "behavioural_adjustment",
    "cy_proxies_fy",
    "head_scope",
]
NIC_VARIABLES = [
    "ni_class_1_employee",
    "ni_class_1_employer",
    "ni_class_2",
    "ni_class_4",
]
NON_HOUSEHOLD_HEADS = {
    "Corporation tax (onshore)",
    "Bank levy",
    "Bank surcharge",
    "Business rates",
    "North sea taxes",
    "Energy profits levy",
    "Electricity generators levy",
    "Climate change levy",
    "Aggregates levy",
    "Landfill tax",
    "Customs duty",
    "CBAM",
    "Company and other credits",
    "Betting",
    "Penalties",
    "Gambling levy",
    "PSCE in RDEL",
    "PSGI in CDEL",
    "Scottish BGA (current)",
    "Scottish BGA (capital)",
    "Welsh BGA (current)",
    "Welsh BGA (capital)",
    "VAT refunds",
    "Locally-financed current expenditure",
    "Locally-financed capital expenditure",
    "Other departmental expenditure (current)",
    "Other departmental expenditure (capital)",
    "Interest and dividend receipts",
    "Student loans",
    "Net public service pension payments",
}


def canonical_bytes(value):
    return (
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode()


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def source_rows(event_slug):
    """Read pinned PMD with source position retained, refusing changed digests."""
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    compressed = SOURCE.read_bytes()
    if hashlib.sha256(compressed).hexdigest() != manifest["claims_gzip_sha256"]:
        raise ValueError("replay source compressed digest changed")
    raw = gzip.decompress(compressed)
    if hashlib.sha256(raw).hexdigest() != manifest["claims_uncompressed_sha256"]:
        raise ValueError("replay source uncompressed digest changed")
    out = []
    labels = set()
    for number, line in enumerate(raw.decode().splitlines(), 1):
        row = json.loads(line)
        event_name = row.get("conditions", {}).get("fiscal_event", "")
        if slugify(event_name) != event_slug:
            continue
        labels.add(event_name)
        c = row["conditions"]
        if c.get("sign_convention") != "positive_gain_to_exchequer":
            raise ValueError(f"source row {number}: unrecognised sign convention")
        metric = row.get("metric") or row.get("proposed_metric")
        if metric not in {"revenue_change", "exchequer_impact"}:
            raise ValueError(f"source row {number}: unrecognised metric {metric!r}")
        head_kind = "tax" if metric == "revenue_change" else "spending"
        row_hash = hashlib.sha256(line.encode()).hexdigest()
        out.append(
            {
                "source_row_id": f"obr_pmd_nov2025:{number}:{row_hash[:16]}",
                "source_row_number": number,
                "source_row_sha256": row_hash,
                "title": row["reform_hint"].strip(),
                "metric": metric,
                "fy": c["fy"],
                "tax_head": c.get("tax_head") or c.get("spending_head"),
                "head_kind": head_kind,
                "value_gbp": row["value"],
                "value_gbp_decimal": str(Decimal(str(row["value"]))),
                "source_table": row["source_table"],
                "source_column": row["source_column"],
                "sign_convention": "positive_gain_to_exchequer",
            }
        )
        if event_slug not in EVENTS:
            out[-1]["fiscal_event"] = event_name
    if not out:
        raise ValueError(f"event {event_slug} has no source rows")
    if len(labels) != 1:
        raise ValueError(
            f"event slug {event_slug!r} ambiguously identifies {sorted(labels)}"
        )
    return out


def _sum(rows, absolute=False):
    values = [Decimal(r["value_gbp_decimal"]) for r in rows]
    if not values:
        return "0"
    # Precision is sized from the cells, so row reordering cannot round away
    # small fractional GBP values beside a large departmental spending cell.
    places = min(v.as_tuple().exponent for v in values)
    width = max(v.adjusted() + 1 for v in values) - places + len(str(len(values))) + 2
    with localcontext() as context:
        context.prec = max(80, width)
        return str(sum((abs(v) if absolute else v for v in values), Decimal(0)))


def accounting(rows, measures):
    """Independent input/output accounts; also verifies uniqueness and identity."""
    classified = [r for m in measures for r in m["source_rows"]]
    incoming = Counter(r["source_row_id"] for r in rows)
    outgoing = Counter(r["source_row_id"] for r in classified)
    if any(n != 1 for n in incoming.values()) or incoming != outgoing:
        raise ValueError(
            "accounting: every incoming source row must appear exactly once"
        )
    for r in classified:
        if r.get("classification") not in CLASSES:
            raise ValueError(f"accounting: invalid class on {r['source_row_id']}")
    original = {r["source_row_id"]: r for r in rows}
    for r in classified:
        for field in ("value_gbp_decimal", "value_gbp", "fy", "tax_head", "metric"):
            if r[field] != original[r["source_row_id"]][field]:
                raise ValueError(
                    f"accounting: source {field} changed on {r['source_row_id']}"
                )
    by_class = {}
    for cls in CLASSES:
        rs = [r for r in classified if r["classification"] == cls]
        by_class[cls] = {
            "rows": len(rs),
            "net_gbp_decimal": _sum(rs),
            "absolute_gbp_decimal": _sum(rs, True),
            "measures": sum(m["classification"] == cls for m in measures),
        }
    fiscal_years = sorted({r["fy"] for r in rows})
    by_fy = {}
    for fy in fiscal_years:
        inp = [r for r in rows if r["fy"] == fy]
        out = [r for r in classified if r["fy"] == fy]
        assert (
            len(inp) == len(out)
            and _sum(inp) == _sum(out)
            and _sum(inp, True) == _sum(out, True)
        )
        by_fy[fy] = {
            "rows_in": len(inp),
            "rows_classified": len(out),
            "net_gbp_in_decimal": _sum(inp),
            "net_gbp_classified_decimal": _sum(out),
            "absolute_gbp_in_decimal": _sum(inp, True),
            "absolute_gbp_classified_decimal": _sum(out, True),
        }
    return {
        "identity": "rows_in = rows_classified; net GBP in = net GBP classified; absolute GBP in = absolute GBP classified (also within each FY)",
        "sign_convention": "positive means a gain to the Exchequer",
        "amount_basis": "All harvested GBP cells across all source heads and costing years, including zeros; this is not a one-year Budget total.",
        "rows_in": len(rows),
        "rows_classified": len(classified),
        "net_gbp_in_decimal": _sum(rows),
        "net_gbp_classified_decimal": _sum(classified),
        "absolute_gbp_in_decimal": _sum(rows, True),
        "absolute_gbp_classified_decimal": _sum(classified, True),
        "by_class": by_class,
        "by_fy": by_fy,
    }


def validate_registry(document):
    """Verify a checked-in event account against its independently pinned source."""
    event_slug = document["event_slug"]
    actual = accounting(source_rows(event_slug), document["measures"])
    if actual != document["accounting"]:
        raise ValueError(
            "accounting: registry commitment differs from classified source cells"
        )
    return actual


def _construct(key, program, spec, heads, *, partial=None, note="", start=2024):
    return {
        "key": key,
        "program": program,
        "classification": "partial" if partial else "expressible",
        "construction": "reversal_on_certified_world",
        "pe_baseline_modifier": spec,
        "heads": heads,
        "missing_legs": partial or [],
        "note": note,
        "commences_fy": f"{start}-{str(start + 1)[-2:]}",
    }


def _head(name, variables, channel="tax"):
    return {"obr_head": name, "pe_variables": variables, "channel": channel}


def authored_construction(event_slug, title, resolve):
    """Announcement levers, applied as marginal reversals on the certified world.

    Later policy already in that world is retained. This is an explicit
    construction and is never labelled the OBR's announcement baseline.
    """
    rate1 = "gov.hmrc.national_insurance.class_1.rates.employee.main"
    rate4 = "gov.hmrc.national_insurance.class_4.rates.main"
    tax_nic_heads = [
        _head("Income tax", ["income_tax"]),
        _head("NICs", NIC_VARIABLES),
        _head("Welfare inside cap", ["universal_credit"], "spending"),
    ]
    common_missing = [
        "Static Universal Credit represents only part of the Welfare inside cap head; behavioural earnings, company-tax and departmental channels are absent."
    ]
    if (
        event_slug in {"autumn_statement_2023", "spring_budget_2024"}
        and "main rate of Class 1 employee NICs" in title
    ):
        return _construct(
            "class_1_employee_nics_main_rate_cut_2p"
            if event_slug == "autumn_statement_2023"
            else "class_1_employee_nics_main_rate_cut_2pp",
            "national_insurance",
            {rate1: {"2024-01-01": 0.10}},
            tax_nic_heads,
            partial=common_missing,
            start=2023 if event_slug == "autumn_statement_2023" else 2024,
            note=(
                "The pinned engine samples government parameters on 30 April and applies that fiscal policy value to the whole nominal year. Its processed employee NICs main rate is 8% throughout 2024, so the 2pp marginal AS2023 reversal is 10% throughout 2024, retaining the later SB2024 cut. Although the liability variable is monthly, raw January-March rates do not survive parameter preprocessing. Nominal 2023 is unchanged, so the original January-March FY2023-24 costing leg is omitted by this annual fiscal policy snapshot and remains a named period/construction divergence."
                if event_slug == "autumn_statement_2023"
                else "The 2pp marginal reversal on the certified 8% world is 10%. For AS2023, CY2023 has zero because commencement was January 2024; CY-proxies-FY explicitly misses the January-March FY2023-24 leg. Later SB2024 cuts are retained in the certified world."
            ),
        )
    if (
        event_slug in {"autumn_statement_2023", "spring_budget_2024"}
        and "main rate of Class 4 self-employed NICs" in title
    ):
        prior = 0.07 if event_slug == "autumn_statement_2023" else 0.08
        return _construct(
            "class_4_self_employed_nics_main_rate_cut_1p"
            if event_slug == "autumn_statement_2023"
            else "class_4_self_employed_nics_main_rate_cut_2pp",
            "national_insurance",
            {rate4: {"2024-01-01": prior}},
            tax_nic_heads,
            partial=common_missing,
            note="Reverse the announced 1pp/2pp marginal cut on the certified 6% Class 4 world, retaining later policy changes.",
        )
    if event_slug == "spring_budget_2024" and title.startswith(
        "High Income Child Benefit Charge: increase"
    ):
        return _construct(
            "hicbc_threshold_and_taper",
            "child_benefit",
            {
                "gov.hmrc.income_tax.charges.CB_HITC.phase_out_start": {
                    "2024-01-01": 50000
                },
                "gov.hmrc.income_tax.charges.CB_HITC.phase_out_end": {
                    "2024-01-01": 60000
                },
            },
            [
                _head("Income tax", ["income_tax"]),
                _head("Welfare inside cap", ["child_benefit"], "spending"),
            ],
            partial=[
                "Child Benefit take-up is fixed; OBR's additional claims response is absent."
            ],
            note="Restore the pre-announcement £50,000-£60,000 tax-charge taper; child_benefit mapping is provisional and does not assert the OBR welfare head's programme identity.",
        )
    if event_slug == "autumn_budget_2024" and title.startswith(
        "Employer National Insurance contributions: Increase rate"
    ):
        return _construct(
            "employer_nics_package",
            "national_insurance",
            {
                "gov.hmrc.national_insurance.class_1.rates.employer": {
                    "2025-01-01": 0.138
                },
                "gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold": {
                    "2025-01-01": 175
                },
            },
            [_head("Income tax", ["income_tax"]), _head("NICs", NIC_VARIABLES)],
            start=2025,
            partial=[
                "Employment Allowance increase to £10,500 and removal of the £100,000 eligibility test: no firm entity or Employment Allowance formula."
            ],
            note="Rate and weekly secondary-threshold reversal reuses the mode-2 construction. £175/week = £9,100/year; the current model's £96/week = £4,992/year. Employer-NI employee_incidence=1 at the pin changes wages holding employer cost fixed; indirect tax heads consequently move. This differs from the OBR's direct costing scope.",
        )
    if event_slug == "autumn_budget_2024" and title.startswith(
        "Capital Gains Tax: Increase the main rates"
    ):
        return _construct(
            "capital_gains_main_rates_and_reliefs",
            "capital_gains_tax",
            {
                "gov.hmrc.cgt.basic_rate": {"2024-10-30": 0.10},
                "gov.hmrc.cgt.higher_rate": {"2024-10-30": 0.20},
                "gov.hmrc.cgt.additional_rate": {"2024-10-30": 0.20},
            },
            [_head("Capital gains tax", ["capital_gains_tax"])],
            partial=[
                "Business Asset Disposal Relief and Investors' Relief rates/qualifying gains are not separately represented.",
                "The pinned main-rate parameters start on 2025-04-06, although the announcement starts on 2024-10-30; annual formulas sample the period start. No onset repair is applied.",
                "CGT aggregates do not distinguish residential, BADR, IR or other gain types; the engine parameter descriptions mark CGT as under active development.",
            ],
            note="A literal pre-announcement main-rate reversal, not a repair of the certified world's delayed rate onset or gains composition. Receipt timing and realisations responses remain divergence axes.",
        )
    if event_slug == "autumn_budget_2024" and title.startswith(
        "Stamp Duty Land Tax (SDLT): Increase the Higher Rate"
    ):
        prefix = "gov.hmrc.stamp_duty.residential.purchase.additional.rate"
        spec = {
            f"{prefix}[{i}].rate": {"2024-10-31": rate}
            for i, rate in enumerate((0.05, 0.07, 0.10, 0.15, 0.17))
        }
        return {
            "key": "sdlt_additional_dwelling_surcharge_2pp",
            "program": "stamp_duty_land_tax",
            "classification": "partial",
            "construction": "forward_delta_on_certified_world",
            "pe_reform_delta": spec,
            "heads": [_head("Stamp duty", ["stamp_duty_land_tax"])],
            "missing_legs": [
                "Corporate purchasers, housing transactions response, and OBR CGT/IHT interactions are outside this household SDLT rate leg.",
                "The certified population must contain additional-home purchase values; absence yields an inert leg rather than an inferred national tax base.",
            ],
            "commences_fy": "2024-25",
            "note": "The pin still has the 3% surcharge scale, so the announcement is a forward 2pp increase to every marginal bracket. The date-keyed onset makes CY2024 inert under annual period-start sampling. Main-home rates and thresholds are retained.",
        }
    if event_slug == "autumn_budget_2024" and title.startswith(
        "Winter Fuel Payments: Target payments"
    ):
        return _construct(
            "winter_fuel_means_test",
            "winter_fuel_payment",
            {
                "gov.dwp.winter_fuel_payment.eligibility.require_benefits": {
                    "2024-01-01": False
                },
            },
            [_head("Welfare inside cap", ["winter_fuel_allowance"], "spending")],
            partial=[
                "The engine excludes Scotland; its qualifying-benefit list omits Universal Credit.",
                "The certified 2025+ world includes the later £35,000 England/Wales income passport. Retaining that policy gives the remaining certified-world marginal savings, rather than the original 2024 announcement baseline.",
            ],
            note="Restore universal age-based eligibility by require_benefits=False. The executed reform world retains all later policy. Source Scottish block-grant rows are separately outside household scope.",
        )
    if event_slug == "autumn_budget_2024" and title.startswith(
        "VAT: Applying the standard rate (20%) to education"
    ):
        return {
            "key": "private_school_vat_20pct",
            "program": "value_added_tax",
            "classification": "partial",
            "construction": "forward_delta_on_certified_world",
            "pe_reform_delta": {
                "gov.contrib.labour.private_school_vat": {"2025-01-01": 0.20}
            },
            "heads": [_head("VAT", ["private_school_vat"])],
            "commences_fy": "2024-25",
            "missing_legs": [
                "The engine uses imputed school attendance and average fees, not observed establishment-level education/boarding supplies.",
                "Input-VAT recovery, state-school spending response and attendance/fee behaviour are absent from this gross private-school VAT leg.",
            ],
            "note": "The certified private-school VAT lever remains zero, so set it to 20% from January2025. The formula multiplies imputed attending children by private_school_fees, rate and private_school_vat_basis. VAT refunds source rows remain outside household scope.",
        }
    if event_slug == "spring_budget_2023" and title.startswith(
        "Annual Allowance (AA): increase"
    ):
        prefix = "gov.hmrc.income_tax.allowances.annual_allowance"
        return _construct(
            "pension_annual_allowance_package",
            "income_tax",
            {
                f"{prefix}.default": {"2023-04-06": 40000},
                f"{prefix}.minimum": {"2023-04-06": 4000},
                f"{prefix}.taper": {"2023-04-06": 240000},
            },
            [_head("Income tax", ["income_tax"]), _head("NICs", NIC_VARIABLES)],
            start=2023,
            partial=[
                "Aggregation of Pension Input Amounts across open/closed public-service schemes needs scheme membership and defined-benefit input amounts; these are not separately observed.",
                "Carry-forward and announcement-specific retirement/earnings responses are absent from this annual static relief leg.",
            ],
            note="Restore £40,000 default, £4,000 tapered minimum and £240,000 adjusted-income taper. These three old/new values are encoded at the pin; the separate MPAA measure is not treated as the minimum tapered annual allowance.",
        )
    if event_slug == "spring_statement_2025" and title.startswith(
        "Universal Credit Standard Allowance:"
    ):
        index_path = "gov.benefit_uprating_cpi"
        prefix = "gov.dwp.universal_credit.standard_allowance.amount"
        old = {
            t: resolve(f"{prefix}.{t}", "2025-04-06")
            for t in ("SINGLE_YOUNG", "SINGLE_OLD", "COUPLE_YOUNG", "COUPLE_OLD")
        }
        base_index = resolve(index_path, "2025-04-06")
        spec = {
            f"{prefix}.{t}": {
                str(y): round(v * resolve(index_path, f"{y}-04-06") / base_index, 2)
                for y in range(2026, 2030)
            }
            for t, v in old.items()
        }
        m = _construct(
            "uc_standard_allowance_above_inflation",
            "universal_credit",
            spec,
            [
                _head("Welfare inside cap", ["universal_credit"], "spending"),
                _head("Welfare outside cap", [], "spending"),
            ],
            start=2026,
            partial=[
                "Existing/new-claimant health-element protections interact with the allowance change; this leg holds the certified health world fixed.",
                "OBR Welfare outside cap is not separately identified by the annual UC liability; it has no invented mapping.",
            ],
            note="Counterfactual is the four 2025-26 monthly allowances uprated by the certified benefit-CPI index each April, without the additional announced uplift. This is an explicit later-vintage indexed baseline, not the March2025 forecast path.",
        )
        m["heads"] = [h for h in m["heads"] if h["pe_variables"]]
        m["counterfactual_derivation"] = {
            "formula": "round(monthly_amount_2025_26 * benefit_CPI_April_year / benefit_CPI_April_2025, 2)",
            "amounts_2025_26": old,
            "index_parameter": index_path,
        }
        return m
    if event_slug == "spring_statement_2025" and title.startswith(
        "Universal Credit Health Element:"
    ):
        path = "gov.dwp.universal_credit.rebalancing.new_claimant_health_element"
        index_path = "gov.benefit_uprating_cpi"
        old = resolve("gov.dwp.universal_credit.elements.disabled.amount", "2025-04-06")
        base_index = resolve(index_path, "2025-04-06")
        spec = {
            path: {
                str(y): round(old * resolve(index_path, f"{y}-04-06") / base_index, 2)
                for y in range(2026, 2030)
            }
        }
        m = _construct(
            "uc_health_element_freeze_and_new_claimant_cut",
            "universal_credit",
            spec,
            [_head("Welfare inside cap", ["universal_credit"], "spending")],
            start=2026,
            partial=[
                "The default simulation modifier assigns new-claimant cohorts using seeded synthetic shares (11%, 13%, 16%, 22% in 2026-29), not observed claim-start history or the March2025 OBR forecast cohorts.",
                "The original existing-claimant rate freeze is not reversed: later legislated combined-award protections remain in the certified world.",
                "Later legislated protections and rate paths differ from the original March2025 announcement.",
            ],
            note="Restore new_claimant_health_element to the 2025-26 monthly amount uprated by the certified benefit-CPI path. The default uc_reform.py simulation modifier applies that amount to its seeded new-claimant cohort; existing-claimant protections remain. Reversing disabled.amount alone would be overridden by this modifier and would not isolate the measure.",
        )
        m["counterfactual_derivation"] = {
            "formula": "round(monthly_health_amount_2025_26 * benefit_CPI_April_year / benefit_CPI_April_2025, 2)",
            "amount_2025_26": old,
            "index_parameter": index_path,
        }
        return m
    return None


def gap_reason(title, rows):
    low = title.lower()
    if re.match(
        r"business rates|capital allowances|r&d|research and development|energy profits levy|electricity generator levy|creative reliefs|cultural reliefs|audio.visual|orchestra|visual effects|gaming duty|carbon border|carbon price|climate change|re.insurance|implement the oecd",
        low,
    ):
        return (
            "out_of_household_scope",
            "Business/sector tax, firm allowance or credit; household income-tax spillovers in the PMD do not make the underlying business measure a household reform.",
            "business_tax",
            r"corporation|business|research|firm",
        )
    if all(r["tax_head"] in NON_HOUSEHOLD_HEADS for r in rows):
        return (
            "out_of_household_scope",
            "Business, departmental, local-authority, financing or block-grant accounts; no household tax/benefit counterpart for these source heads.",
            "scope",
            r"firm|corporation|department|block_grant",
        )
    rules = [
        (
            r"inheritance|estate",
            "No estates, bequests, death events or agricultural/business-property inheritance-tax relief model on the certified household population.",
            "inheritance_tax",
            r"inheritance|estate|bequest|death",
        ),
        (
            r"non.dom|domicil|foreign income|repatriation",
            "No residence-history, foreign-income regime or repatriation/base-cost history needed by the announcement package.",
            "income_tax",
            r"domicil|residen|foreign|repatri",
        ),
        (
            r"fraud|error|compliance|debt management|tax collection|tax receipts|tax practitioners|non.compliance|avoidance|reporting|making tax digital|unpaid tax|penalt|payroll software",
            "Administrative collection, compliance, reporting or debt intervention; liability rules do not identify recovered debts, extra staff productivity or compliance behaviour.",
            "administration",
            r"compliance|fraud|debt|error|penalt|report",
        ),
        (
            r"carried interest|limited liability|liquidation|partnership|close companies",
            "No carried-interest/partnership/liquidation identity and transaction history for this targeted tax-base change.",
            "capital_gains_tax",
            r"carried_interest|partnership|liquidat|llp",
        ),
        (
            r"isa|savings accounts|child trust|help to save",
            "No ISA subscriptions, product holdings or Help to Save savings/bonus history on the certified population.",
            "savings",
            r"isa|subscription|help_to_save|child_trust",
        ),
        (
            r"lifetime allowance",
            "The pinned annual pension-contributions relief model has no lifetime pension-pot allowance or lifetime-allowance charge variable/parameter; accumulated pension-pot and crystallisation events are needed.",
            "income_tax",
            r"lifetime|lta|crystallis|pension_pot",
        ),
        (
            r"money purchase annual allowance|mpaa",
            "The tapered minimum annual allowance is not the Money Purchase Annual Allowance. The pinned relief model has no flexibly-accessed pension history or MPAA switch; substituting annual_allowance.minimum would apply the wrong rule.",
            "income_tax",
            r"money_purchase|mpaa|flexibl|annual_allowance",
        ),
        (
            r"company car|van benefit|car ownership|vehicle|air passenger|private jets",
            "Targeted transport tax needs vehicle emissions/ownership, company-car benefit attributes or passenger journeys absent from the certified household inputs.",
            "transport",
            r"vehicle|company_car|van_benefit|air_passenger",
        ),
        (
            r"surplus earnings|transitional|migration|severe disability|minimum income floor|assessment|descriptor|reassessment|award review|capacity for processing|take.up|conditionality|sanctions|administrative earnings",
            "Requires claim history, previous awards, assessment descriptors, administrative process or an announcement-specific caseload response; a current annual liability parameter alone cannot replay it.",
            "welfare",
            r"surplus|transitional|claim_history|descriptor|assessment|deduction",
        ),
        (
            r"carer.s allowance",
            "The pinned carers_allowance formula tests care hours or reported receipt, then pays the flat rate. It has no earnings-limit test; the announced £151-to-£196 weekly earnings limit cannot be expressed by changing its rate or care-hours parameter.",
            "carers_allowance",
            r"carers_allowance|carer_support_payment|earnings_limit",
        ),
        (
            r"winter fuel",
            "Historical means-tested Winter Fuel eligibility interacts with the later £35,000 recovery regime; requires an explicitly reconstructed eligibility world and Scottish scope before executable classification.",
            "winter_fuel_payment",
            r"winter_fuel|winter_fuel_allowance|pension_credit",
        ),
        (
            r"fuel duty",
            "Fuel-duty current-law path is collapsed by later freezes. A single-event reversal needs an announcement-consistent counterfactual uprating path, which is not guessed from the later certified path.",
            "fuel_duty",
            r"fuel_duty|petrol|diesel",
        ),
        (
            r"alcohol|tobacco|vaping|soft drinks|vat|carbon|levy|tariff",
            "This targeted indirect-tax measure requires product/sector-specific tax-base inputs, rate histories or business/supply-side scope not established by a generic household consumption liability.",
            "indirect_tax",
            r"alcohol|tobacco|vaping|vat|levy",
        ),
        (
            r"childcare|housing allowance|pensions|allowance|savings|national insurance|nic",
            "The relevant liability exists, but this announcement's counterfactual path or targeted eligibility has not been established on the certified population; no guessed parameter or baseline.",
            "tax_benefit",
            r"childcare|lha|pension|allowance|national_insurance",
        ),
    ]
    for pattern, why, program, search in rules:
        if re.search(pattern, low):
            return "not_expressible", why, program, search
    return (
        "not_expressible",
        "The announcement needs a targeted tax-base, entitlement, transaction or programme mechanism not established as an executable reform on the certified household population.",
        "other",
        r"transaction|eligibility|reform",
    )


def build_registry(event_slug, engine_parameters, engine_variables, resolve):
    rows = source_rows(event_slug)
    event_name = EVENTS.get(event_slug) or rows[0]["fiscal_event"]
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["title"]].append(row)
    years = sorted({int(r["fy"][:4]) for r in rows if 2023 <= int(r["fy"][:4]) <= 2030})
    measures = []
    for title, rs in grouped.items():
        authored = authored_construction(event_slug, title, resolve)
        if authored:
            m = dict(authored)
            key = m.pop("key")
            classification = m["classification"]
            search = "|".join(
                re.escape(p)
                for p in (
                    m.get("pe_baseline_modifier") or m.get("pe_reform_delta") or {}
                )
            )
            m["pe_gap"] = "; ".join(m["missing_legs"]) or None
        else:
            classification, reason, program, search = gap_reason(title, rs)
            key = slugify(title)[:110]
            # Digest prevents collisions when similarly titled measures truncate.
            key += "_" + hashlib.sha256(title.encode()).hexdigest()[:8]
            m = {
                "program": program,
                "classification": classification,
                "heads": [],
                "construction": None,
                "pe_reform_delta": None,
                "pe_gap": reason,
                "missing_legs": [reason],
                "note": reason,
            }
            m["gap_kind"] = (
                "construction_pending"
                if any(
                    phrase in reason
                    for phrase in (
                        "not been established",
                        "not established",
                        "requires an explicitly",
                        "not guessed",
                    )
                )
                else "out_of_household_scope"
                if classification == "out_of_household_scope"
                else "model_or_data_gap"
            )
        rx = re.compile(search, re.IGNORECASE)
        ph = [
            p
            for p in engine_parameters
            if rx.search(p) and not p.startswith("baseline.")
        ]
        vh = [v for v in engine_variables if rx.search(v)]
        m.update(
            {
                "measure_key": f"{event_slug}__{key}",
                "title": title,
                "reported_status": "announced",
                "fiscal_event": event_name,
                "computability": classification,
                "measure_type": m["program"],
                "source_rows": [],
                "divergence_axes": AXES,
                "name_search": {
                    "pattern": search,
                    "parameter_matches": ph,
                    "variable_matches": vh,
                    "engine_version": "2.89.2",
                    "searched": ["full_parameter_tree", "full_variable_list"],
                },
            }
        )
        mapped = {h["obr_head"] for h in m["heads"]}
        m["unmapped_obr_heads"] = sorted({r["tax_head"] for r in rs} - mapped)
        for row in rs:
            r = dict(row)
            if (
                classification == "out_of_household_scope"
                or r["tax_head"] in NON_HOUSEHOLD_HEADS
            ):
                r["classification"] = "out_of_household_scope"
                r["classification_reason"] = (
                    "Source head is outside household tax-benefit scope; retained for event accounting."
                )
            elif classification == "expressible" and r["tax_head"] not in mapped:
                r["classification"] = "partial"
                r["classification_reason"] = (
                    "Measure's parameter leg is expressible; this source head has no validated counterpart mapping."
                )
            else:
                r["classification"] = classification
                r["classification_reason"] = (
                    m["pe_gap"]
                    or "Validated parameter reversal and named head mapping."
                )
            m["source_rows"].append(r)
        m["head_variables"] = list(
            dict.fromkeys(v for h in m["heads"] for v in h["pe_variables"])
        )
        spec = m.get("pe_baseline_modifier") or m.get("pe_reform_delta") or {}
        if spec:
            m["engine_baseline_by_year"] = {
                str(y): {path: resolve(path, f"{y}-06-01") for path in spec}
                for y in years
            }
            for path in spec:
                if path not in engine_parameters:
                    raise ValueError(
                        f"{m['measure_key']}: missing pinned parameter {path}"
                    )
            for name in m["head_variables"]:
                if name not in engine_variables:
                    raise ValueError(
                        f"{m['measure_key']}: missing pinned variable {name}"
                    )
        measures.append(m)
    keys = [m["measure_key"] for m in measures]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate measure key")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    bundle = json.loads(CERTIFIED.read_text())
    return {
        "schema_version": 1,
        "event_slug": event_slug,
        "event_name": event_name,
        "classification_note": "not_expressible means no established executable construction in this replay. gap_kind distinguishes evidenced model/data gaps from construction_pending decisions; pending constructions do not claim the underlying liability model is absent.",
        "calendar_years": years,
        "years_note": (
            "Calendar year starting the OBR fiscal year is the proxy. FY before 2023-24 stays accounted but is not simulated. Detailed pinned-engine/data support is recorded in docs/uk_replay/YEARS.md."
            if event_slug in EVENTS
            else "Calendar year starting the OBR fiscal year is the proxy. FY before 2023-24 or starting after 2030 stays accounted but is not simulated. Detailed pinned-engine/data support is recorded in docs/uk_replay/YEARS.md."
        ),
        "bundle": bundle,
        "source": manifest,
        "orientation": "positive means gain to the Exchequer; reversal effect = -(literal reversal - certified baseline)",
        "accounting": accounting(rows, measures),
        "measures": measures,
    }


def engine_resolver(system=None):
    from policyengine_uk import CountryTaxBenefitSystem

    if system is None:
        system = CountryTaxBenefitSystem()

    def resolve(path, date):
        node = system.parameters
        for part in path.split("."):
            match = re.fullmatch(r"(.+)\[(\d+)\]", part)
            node = (
                getattr(node, match.group(1)).brackets[int(match.group(2))]
                if match
                else getattr(node, part)
            )
        value = node(date)
        if hasattr(value, "item"):
            value = value.item()
        return value

    return resolve


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--event",
        required=True,
        help="Slug of any fiscal event in the pinned source; 'all' builds the five pilot events.",
    )
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", args.event):
        p.error("--event must be a lowercase fiscal-event slug")
    for name in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "TRANSFORMERS_OFFLINE"):
        os.environ[name] = "1"
    from policyengine_uk import CountryTaxBenefitSystem

    system = CountryTaxBenefitSystem()
    params, variables = engine_dumps(system=system)
    resolve = engine_resolver(system)
    for event_slug in EVENTS if args.event == "all" else [args.event]:
        registry = build_registry(event_slug, params, variables, resolve)
        output = ROOT / "data/uk/events" / f"{event_slug}_measures.json"
        content = canonical_bytes(registry)
        if args.check:
            if not output.exists() or output.read_bytes() != content:
                raise SystemExit(f"registry differs: {output}")
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
        print(
            json.dumps(
                {
                    "event": event_slug,
                    "measures": len(registry["measures"]),
                    "rows": registry["accounting"]["rows_in"],
                    "classes": registry["accounting"]["by_class"],
                }
            )
        )


if __name__ == "__main__":
    main()
