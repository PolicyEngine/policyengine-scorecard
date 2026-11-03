"""Stage HM Treasury, Budget 2026: Policy Costings (PU 3699) for the AB2026 harvest (#230).

Family uk_hmt_costings, source hm_treasury. The rows are data in this file:
COSTINGS holds the 96 costing notes (pp.12-109) with their single Exchequer
impact table, and TEXT_CLAIMS holds the estimates printed in the notes' text
(tax bases, behavioural parameters, eligible counts, the tax gap behind one
tax base, and PSND, PSNFL and financial-transaction impacts). README rules 8
and 9: design numbers are not rows, and a part of one Table 6.1 line carries
that line's key with conditions.row_type measure_component.
Running the script rewrites claims_staged.jsonl.gz byte for byte:

    python3 stage.py

`python3 stage.py --verify PATH/TO/AB26_Policy_Costing.pdf` writes nothing. It
checks that the gzip on disk equals a fresh build, that the PDF has the pinned
sha256, and, for every row, that the page its locator cites prints it (needs
pdftotext). Table rows: the heading, the years, the six values in order, the
row's value in its year's column, the row label and any footnote. Text rows:
the quote verbatim, value_raw inside it, and value equal to value_raw's number
at the scale and sign the normalization names. Every keyed row: the
measure's title on the note's first page.
"""

import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "claims_staged.jsonl.gz"

PUBLICATION = {
    "title": "Budget 2026: Policy Costings (PU 3699)",
    "url": "https://assets.publishing.service.gov.uk/media/6ae1883fe4367e5c8b0467df/AB26_Policy_Costing.pdf",
    "date": "2026-10-28",
    "publisher": "HM Treasury",
    "primary_sha256": "f716efada8a4d0726ce12b0f97d3f0dac671c31b2d005ecf300a48ff309638bf",
    "access": "direct",
}
FYS = ["2026-27", "2027-28", "2028-29", "2029-30", "2030-31", "2031-32"]
SIGN = (
    "positive = yield to the Exchequer (reduces borrowing); negative = cost to the "
    "Exchequer (no legend printed in the document; convention observed from the costings "
    "themselves: p.38 says its figures 'represent net income from developer fees' and prints "
    "+50m to +95m from 2027-28 after -15m in 2026-27, the Bank Surcharge rise prints +, the VAT "
    "cut on domestic electricity prints -, and Table 6.1 prints the same values with the same signs)"
)
NORMALIZATION = "GBP m as printed (sign and trailing 'm' verbatim) x 1e6 -> GBP"
NATIONAL_ACCOUNTS = "All costings are presented on a National Accounts basis (p.10)"
COMMON = {
    "source": "hm_treasury",
    "source_model": "hmt_costing_obr_certified",
    "baseline_policy": None,
    "proposed_baseline": None,
    "status": "ok",
}

COSTINGS = [{'page': 12,
  'pages': [12],
  'table_page': 12,
  'title': 'Support for Energy Bills: Cut VAT on domestic electricity from 5% to 0% from 1 October 2026 to 1 '
           'July 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of expenditure on domestic electricity supplies eligible for the reduced '
           'rate of VAT, including qualifying household, charity, residential care and a small amount of '
           'business consumption. The tax base is estimated using ONS consumer expenditure data.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in nominal '
           'consumer expenditure on electricity.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby lower electricity prices encourage '
              'some consumers to shift some of their consumption from gas and other fuels towards '
              'electricity.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-755m', '-305m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '2',
  'measure_key': 'ab2026__electricity_vat_zero_rate_to_july_2027',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 13,
  'pages': [13],
  'table_page': 13,
  'title': 'Fuel Duty: Extend the temporary 5p-per-litre duty cut and defer the planned Retail Prices Index '
           '(RPI) increase to 1 July 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of every litre of taxable fuel that is made available for use in the UK. '
           'Projected volumes are taken from the fuel duty forecasting model.',
           'The tax base is grown over the forecast horizon using the OBR’s economy forecast determinants '
           'for Gross Domestic Product and real consumer expenditure.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby consumers may change their '
              'consumption in response to changes in pump prices.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-575m', '-780m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '3',
  'measure_key': 'ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 14,
  'pages': [14],
  'table_page': 14,
  'title': 'Mileage Rates: Increase the tax-free and tax-deductible car and van rates to 55p for the first '
           '10,000 business miles from 6 April 2026 and the higher mileage rate to 35p from 6 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of employees, sole traders and partnerships that use cars or vans for '
           'business purposes and incur allowable business motoring expenses including those subject to the '
           'AMAP regime, Relative Motoring Expenditure, or those who receive Mileage Allowance Relief.',
           'The tax base is estimated using survey evidence on the self-employed population and their use of '
           'business vehicles, HMRC administrative data and National Transport Survey data to estimate size '
           'of population, average mileage, and reimbursement rate.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in '
           'employment, the self-employed population, self-employed income and the Consumer Price Index '
           '(CPI).'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for behavioural responses from both employees and the self-employed '
              'claiming mileage relief. This includes greater awareness of the regime from employees and the '
              'self-employed leading to increased claims for Mileage Allowance relief. The behavioural '
              'adjustment also accounts for some employers increasing reimbursement rates, whereas some '
              'employers may choose not to increase employee reimbursement, widening the gap between the '
              'amount reimbursed and the approved mileage rate, and therefore increasing the value of '
              'Mileage Allowance Relief claims.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-30m', '-200m', '-220m', '-225m', '-235m', '-245m'],
  'table_61_line': '5',
  'measure_key': 'ab2026__mileage_allowance_payments_55p',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 15,
  'pages': [15],
  'table_page': 15,
  'title': 'Parental Pay: Establish a Parental Allowance for fathers, partners and adopters in Great Britain '
           'from April 2029',
  'base_heading': 'The cost base',
  'base': ['The cost base consists of self-employed fathers, partners and adopters, and parents who are '
           'recently employed, recently unemployed or who may have a broken or irregular pattern of '
           'employment. There are an estimated 166,000 fathers and partners and around 750 self-employed '
           'adopters who fall into these categories.'],
  'costing': ['The costing assumes an 89% take-up rate. The costing uses OBR forecast determinants for '
              'employment growth and projected births to scale the eligible population and CPI assumptions '
              'to uprate the statutory weekly rate.'],
  'uncertainty': ['The main uncertainties relate to take-up (including awareness and application-completion '
                  'risk), claimant work absence, interaction with existing provision, and delivery costs '
                  'including verification, fraud and error, and NICs records/work-history checks.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '-70m', '-70m', '-70m'],
  'table_61_line': '6',
  'measure_key': 'ab2026__parental_allowance_fathers_partners_adopters',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'Great Britain',
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 16,
  'pages': [16],
  'table_page': 16,
  'title': 'Carer’s Allowance: Introduce a taper on earnings above the Weekly Earning Limit within 2030-31',
  'base_heading': 'The cost base',
  'base': ['The cost base is DWP’s forecast for caseload and expenditure on Carer’s Allowance and Universal '
           'Credit, as well as OBR projections for increases in the National Living Wage.'],
  'costing': ['The costing is calculated by estimating the additional Carer’s Allowance expenditure from '
              'paying tapered awards on earnings above the Weekly Earnings Limit versus the current '
              'non-payment of the benefit. It also factors in interactions with Universal Credit awards.',
              'The costing accounts for a behavioural response whereby some Carer’s Allowance claimants '
              'increase their earnings or enter work which results in a reduction in Carer’s Allowance and '
              'Universal Credit expenditure. It also accounts for the take-up of tapered Carer’s Allowance '
              'awards amongst newly eligible individuals who currently earn above the Weekly Earnings Limit.',
              'See the Data Sources supporting document for Budget 2026 for information on the methodology '
              'on estimated beneficiaries of this measure.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response in '
                  'relation to labour supply by carers. Additionally, the take-up of tapered awards amongst '
                  'newly eligible individuals is uncertain.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+0m', '-40m', '-80m'],
  'table_61_line': '7',
  'measure_key': 'ab2026__carers_allowance_earnings_taper',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 17,
  'pages': [17],
  'table_page': 17,
  'title': 'Universal Credit: Extend the £2,500 surplus earnings threshold for one year from 1 April 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base comes from the OBR’s Universal Credit benefit expenditure forecast, the Family '
           'Resources Survey and the OBR’s forecast of economic determinants.'],
  'costing': ['The costing is produced by comparing the cost base described above to a pre-measure forecast '
              'baseline. No behavioural effects have been taken into account as these are judged to be '
              'negligible.'],
  'uncertainty': ['The main uncertainties in this costing relate to the earning patterns of claimants and '
                  'the number of claimants who may have more pay days than usual during an assessment '
                  'period.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-140m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '8',
  'measure_key': 'ab2026__uc_surplus_earnings_threshold_2500_extended',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'No behavioural effects have been taken into account as these are judged "
                            "to be negligible.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 18,
  'pages': [18],
  'table_page': 18,
  'title': 'Tariff Suspension Packages: Suspend tariffs on 135 food products from 21 June 2026 until 31 '
           'December 2028; 101 food products and kerosene for heating oil from 26 November 2026 until 31 '
           'December 2028; and fertiliser from 26 November 2026 until 31 December 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base is the expected Customs Duty revenue from the relevant commodity codes impacted, '
           'had the measure not been implemented. The tax base has been projected across the forecast using '
           'the OBR’s forecasts for non-oil goods imports.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above. A behavioural adjustment is made to account for the proportion of '
              'traders expected to utilise the tariff suspensions.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-50m', '-75m', '-55m', '+0m', '+0m', '+0m'],
  'table_61_line': '10',
  'measure_key': 'ab2026__food_and_heating_oil_tariff_suspensions',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 19,
  'pages': [19],
  'table_page': 19,
  'title': 'Cash ISAs: Maintain the cash ISA limit at £20,000 from 6 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of interest on savings held by under-65s who would otherwise save more '
           'than £12,000 per year into Cash ISAs. The tax base is estimated using HMRC administrative data.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for returns on savings '
           'deposits.'],
  'costing': ['The costing has no static impact on taxpayer liabilities.',
              'The costing accounts for a behavioural response whereby individuals utilise cash ISAs up to '
              'the £20k limit.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-5m', '-20m', '-35m', '-50m', '-70m'],
  'table_61_line': '11',
  'measure_key': 'ab2026__cash_isa_limit_held_at_20000',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': "none: 'The costing has no static impact on taxpayer liabilities.'",
  'mapping_note': ''},
 {'page': 20,
  'pages': [20],
  'table_page': 20,
  'title': 'Business Rates: Increase business rates relief for pubs, social clubs and live music venues by '
           '20ppts to 35% from 1 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base for the relief consists of the estimated rateable value of all pubs, social clubs '
           'and live music venues, multiplied by the relevant multiplier for relevant years.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above. The static cost is adjusted to reflect that business rates are '
              'deductible for Corporation Tax for companies and Income Tax for the self-employed, and that '
              'business rates are devolved to Scotland, Wales, and Northern Ireland.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base, the impacts of '
                  'appeals against property valuations on rateable values, and the impact of behavioural '
                  'responses.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+5m', '-160m', '-115m', '-5m', '-5m', '-5m'],
  'table_61_line': '12',
  'measure_key': 'ab2026__business_rates_pubs_relief_35pc',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 21,
  'pages': [21],
  'table_page': 21,
  'title': 'Business Rates: Increase valuation thresholds for Small Business Rate Relief for retail, '
           'hospitality and leisure (RHL) properties from £12,000 to £18,000 for 100% relief and from '
           '£15,000 to £21,000 for tapered relief from 1 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base for the relief consists of the estimated rateable value of qualifying properties '
           'within the thresholds, multiplied by the relevant multiplier for relevant years and factoring in '
           'the taper.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above. The static cost is adjusted to reflect that business rates are '
              'deductible for Corporation Tax for companies and Income Tax for the self-employed, and that '
              'business rates are devolved to Scotland, Wales, and Northern Ireland.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base, the impacts of '
                  'appeals against property valuations on rateable values, and the impact of behavioural '
                  'responses.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+5m', '-315m', '-320m', '+0m', '-5m', '-5m'],
  'table_61_line': '13',
  'measure_key': 'ab2026__business_rates_sbrr_rhl_thresholds_raised',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 22,
  'pages': [22],
  'table_page': 22,
  'title': 'Business Rates: Introduce a transitional support package, including a two-year real terms bills '
           'freeze for RHL businesses and a one-year extension of the 2023 Supporting Small Business '
           'support, part funded by extending the Transitional Relief Supplement for two years from 1 April '
           '2027',
  'base_heading': 'The tax base',
  'base': ['The tax base for the reliefs consists of the estimated rateable value of qualifying properties, '
           'multiplied by the relevant multiplier for relevant years.',
           'The tax base for the Transitional Relief Supplement is the rateable value of all eligible '
           'non-domestic properties, with a 1p supplement applied to the relevant multiplier.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above. The static cost is adjusted to reflect that business rates are '
              'deductible for Corporation Tax for companies and Income Tax for the self-employed, and that '
              'business rates are devolved to Scotland, Wales, and Northern Ireland.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base, the impacts of '
                  'appeals against property valuations on rateable values, and the impact of behavioural '
                  'responses.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-10m', '-230m', '+0m', '+0m', '+0m'],
  'table_61_line': '14',
  'measure_key': 'ab2026__business_rates_rhl_transitional_support',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 23,
  'pages': [23],
  'table_page': 23,
  'title': 'Trading Allowance: Increase the Income Tax Trading Allowance to £3,000 from £1,000 from 6 April '
           '2027',
  'base_heading': 'The tax base',
  'base': ['The tax base comprises sole traders and people with miscellaneous income whose allowable '
           'expenses are £3,000 or less and for whom claiming the trading allowance is more beneficial than '
           'claiming actual business expenses.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The static costing captures taxpayers with income over £1,000 who already claim the maximum '
              'allowance. The costing also accounts for behavioural responses from taxpayers who currently '
              'claim expenses and allowances less than £3,000 for whom it will be advantageous both in cash '
              'and administrative terms to switch to the allowance.'],
  'uncertainty': ['The main uncertainty in this costing relates to behavioural effects. In particular, there '
                  'is uncertainty around the proportion of eligible taxpayers currently claiming actual '
                  'business expenses who will switch to claiming the trading allowance following the '
                  'increase from £1,000 to £3,000.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '-225m', '-165m', '-175m', '-180m'],
  'table_61_line': '15',
  'measure_key': 'ab2026__trading_allowance_3000',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 24,
  'pages': [24],
  'table_page': 24,
  'title': 'Business Tariff Suspensions: Suspend tariffs on 72 products from 5 August 2026 and extend '
           'suspensions for 361 products in 2027-28',
  'base_heading': 'The tax base',
  'base': ['The tax base is the expected Customs Duty revenue from the relevant commodity codes had the '
           'measure not been implemented. The tax base has been projected across the forecast using the '
           'OBR’s forecasts for non-oil goods imports.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above. A behavioural adjustment is made to account for the proportion of '
              'traders expected to use the tariff suspensions, and the incentive for traders to forestall by '
              'bringing forward imports to avoid paying duty once the suspensions end.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-65m', '-215m', '-155m', '+0m', '+0m', '+0m'],
  'table_61_line': '16',
  'measure_key': 'ab2026__business_tariff_suspensions',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 25,
  'pages': [25],
  'table_page': 25,
  'title': 'Climate Change Levy: Freeze electricity & liquefied petroleum gas main rates, and uprate gas and '
           'solid fuels main rates by RPI from 1 April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of supplies of electricity and LPG used as fuel that are subject to CCL. '
           'The tax base is estimated using energy consumption outturn data and energy and emissions '
           'projections from the Department for Energy Security and Net Zero.',
           'The tax base is grown over the forecast horizon using the OBR’s forecasts for gross domestic '
           'product (GDP).'],
  'costing': ['The costing is estimated by applying the post-measure tax rates to the tax base described '
              'above and comparing this with the baseline, in which CCL rates are uprated in line with RPI.',
              'The costing accounts for a behavioural response whereby taxpayers increase their consumption '
              'of electricity in response to the lower post-tax price. Any behavioural response for LPG is '
              'assumed to be negligible.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '-25m', '-25m', '-25m', '-25m'],
  'table_61_line': '17',
  'measure_key': 'ab2026__climate_change_levy_rates_2028',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 26,
  'pages': [26],
  'table_page': 26,
  'title': 'Red Diesel: Reduce duty rates by 3.7p-per-litre from 15 June 2026 to 1 July 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of all litres of gas oil (red diesel) eligible for the rebated red diesel '
           'duty rate. It is estimated using forecast red diesel clearance volumes from the fuel duty '
           'forecasting model.',
           'The tax base is grown over the forecast horizon using the OBR’s economic forecast for real '
           'consumer spending and gross domestic product.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby some consumers increase their '
              'consumption of red diesel in response to the lower fuel prices.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-60m', '-30m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '18',
  'measure_key': 'ab2026__red_diesel_duty_cut',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 27,
  'pages': [27],
  'table_page': 27,
  'title': 'Alcohol Duty: Increase the generosity of Small Producer Relief from 1 February 2027',
  'base_heading': 'The tax base',
  'base': ['Alcohol duty is payable on alcoholic products when they are released for consumption onto the UK '
           'market, referred to as alcohol clearances. The tax base for this measure is the forecast of '
           'alcohol clearances paying SPR rates, derived from the OBR’s alcohol duty forecast.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for behavioural responses whereby the demand for alcoholic products is '
              'adjusted in response to the duty rate change.',
              'The costing is also adjusted to account for forestalling of alcoholic products, whereby '
              'producers/importers bring forward or delay clearances in anticipation of new duty rates.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-10m', '-10m', '-10m', '-10m', '-10m'],
  'table_61_line': '19',
  'measure_key': 'ab2026__alcohol_duty_small_producer_relief',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 28,
  'pages': [28],
  'table_page': 28,
  'title': 'Business Rates Retention: Devolve a share of business rates income and growth to Mayoral '
           'Strategic Authorities from April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base is the business rates forecast and the expected foregone grant allocation to '
           'Mayoral Strategic Authorities (MSAs) benefiting from additional business rates retention.'],
  'costing': ['Giving Mayors a share of business rates will mean that MSAs retain more business rates and '
              'increase spending financed by locally generated revenues. This is offset by a reduction in '
              'central government grant to those MSAs, and therefore a reduction in spending financed by '
              'grant income. MSAs will gain from any income retained above their business rates baseline due '
              'to growth in their business rates base, which is reflected in the estimated exchequer impact.',
              'It is assumed that 25% of the additional income above the baseline is placed into MSAs’ '
              'reserves.'],
  'uncertainty': ['The main uncertainties in this costing relate to the forecast growth of the business '
                  'rates base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-10m', '-45m', '-75m', '-110m', '-140m'],
  'table_61_line': '21',
  'measure_key': 'ab2026__business_rates_retention_mayoral_authorities',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 29,
  'pages': [29],
  'table_page': 29,
  'title': "Founders' Relief: Introduce a new CGT relief for qualifying founders of high-growth, innovative "
           'companies from 6 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of gains on qualifying share disposals by eligible individuals who are '
           'founders or early investors in high-growth, innovative companies. It is estimated using HMRC '
           'administrative data and external data from Moody’s financial accounting made easy (FAME) '
           'database and Companies House.',
           'The tax base is grown over the forecast horizon using OBR’s forecast for growth in equity '
           'prices.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby some near-qualifying companies '
              'restructure so that individuals become eligible for the relief, while the lower CGT rate also '
              'encourages additional or earlier disposals and some shifting of income into capital gains.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-260m', '-180m', '-260m', '-285m', '-300m'],
  'table_61_line': '26',
  'measure_key': 'ab2026__founders_relief_cgt',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 30,
  'pages': [30],
  'table_page': 30,
  'title': 'R&D Tax Reliefs: Remove the Claim Notification Form from 1 April 2027 and simplify the '
           'Additional Information Form from Autumn 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base for the claim notification removal is qualifying R&D expenditure of companies who '
           'have not claimed R&D tax relief in the past 3 years, including first-time claimants. The tax '
           'base for the AIF changes is all qualifying R&D expenditure on which companies can claim R&D tax '
           'relief.',
           'The tax base is estimated using information on R&D tax relief claims in corporation tax returns '
           'and grown over the forecast horizon using the OBR’s forecast growth in investment.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The main behavioural response included in the costing is increased claims by first-time R&D '
              'claimants.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-45m', '-60m', '-65m', '-65m', '-70m'],
  'table_61_line': '27',
  'measure_key': 'ab2026__rd_relief_claim_notification_form_removed',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 31,
  'pages': [31, 32],
  'table_page': 32,
  'title': 'Enterprise Management Incentives 2 (EMI2): Increase the individual option limit to £120,000, '
           'extending the exercise period to 15 years and remove interaction with EMI option limit from 6 '
           'April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the value of share options granted under the EMI2 and EMI schemes and '
           'non-tax advantaged schemes, to employees. The tax base is estimated using HMRC administrative '
           'data on share option grants and exercises.',
           "The tax base is grown over the forecast horizon using the OBR's forecast for equity prices and "
           'with the historical growth rate seen in the Business Population Estimates.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby employers grant additional share '
              'options to employees because of the higher limits and other improvements affecting EMI, EMI2 '
              'and non-tax advantaged schemes. The costing accounts for additional EMI2 grants due to '
              'increased awareness of the EMI2 scheme, and additional grants due to the higher limits and '
              'the removal of the EMI/EMI2 interaction.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-25m', '-35m', '-45m', '-145m', '-140m'],
  'table_61_line': '28',
  'measure_key': 'ab2026__emi2_option_limit_120000',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 33,
  'pages': [33],
  'table_page': 33,
  'title': 'British Business Bank: Bring forward activity from 2027-2031 into the current financial year to '
           'take advantage of market opportunities in the innovation economy',
  'base_heading': 'The cost base',
  'base': ['The cost base consists of the difference between the drawdown, distributions and valuation '
           'profiles of the accelerated commitments and the commitments forgone in later years.'],
  'costing': ['The costing compares the forecast cash flows and asset values under the accelerated '
              'investment profile with those under the pre-measure profile. Although £1 billion is committed '
              'in 2026-27, the funds draw this capital over time, while the reductions in later commitments '
              'lower future drawdowns and distributions.',
              'The programme is expected to be a net cost to both public sector net debt (PSND) (approx. '
              '£386m) and public sector net financial liabilities (PSNFL) (approx. £375m) over the period to '
              '2031-32. The portfolio is expected to appreciate in value over its lifetime beyond this '
              'period, and so will ultimately become net-income generating for the Exchequer. The costs of '
              'this acceleration are initial capital investment, and subsequent returns in later years. Both '
              'of these are captured within PSND impacts, and PSNFL for valuation changes of the portfolio '
              'over its lifetime.'],
  'uncertainty': ['The main uncertainties relate to the timing of investment commitments, drawdowns and '
                  'distributions, and changes in the value of the underlying investments.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '29',
  'measure_key': 'ab2026__british_business_bank_backing_innovation',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'British Business Bank: Bring forward activity from 2027-2031 into the current financial year '
               'to take advantage of market opportunities in the innovation economy',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.33-34) for Table 6.1 line 29 'Backing Innovation: Bring "
                  'forward £1bn investment and increase financial capacity by £2bn for the British Business '
                  "Bank to support additional investment in the UK (resource impacts of increased lending)', "
                  "whose title names both. The line's figure covers both, so this row carries the line's key "
                  "as a measure_component (README rule 9); components are never summed with the line's "
                  'total.'},
 {'page': 34,
  'pages': [34],
  'table_page': 34,
  'title': 'British Business Bank: Increase the British Business Bank’s total financial capacity to deliver '
           'additional investment into UK businesses',
  'base_heading': 'The cost base',
  'base': ['The cost base consists of the additional investments, loans and guarantees expected to be '
           'entered into using the recapitalisation. It includes:',
           '• £1,405 million for commercial equity commitments;',
           '• £165 million of lending through Community Development Finance Institutions;',
           '• £450 million to support direct venture debt.'],
  'costing': ['The costing applies the relevant cash-flow profiles to each product.',
              'The expected figures outlined in the table below are those which impact public sector net '
              'borrowing (PSNB) – including interest and guarantee fee income to be generated by the '
              'portfolio, as well as the costs of delivery and expected losses incurred. Public sector net '
              'debt (PSND) impact includes the cost and income generated above, as well as the net capital '
              'cost and return of the investment and lending expected. Over the period until 2031-32, this '
              'is anticipated to be a cost of approximately £775m, with the portfolio expected to be profit '
              'generating for the Exchequer over its lifetime. Public sector net financial liabilities '
              '(PSNFL) also includes expected movements in the fair value of the portfolio. This is expected '
              'to add an additional cost of £68m in the period to 2031-32 as the value of the portfolio '
              'matures.'],
  'uncertainty': ['The main uncertainties are deployment, fund drawdowns and distributions, investment '
                  'valuations, income and delivery costs.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+5m', '+0m', '+5m', '+10m', '+25m'],
  'table_61_line': '29',
  'measure_key': 'ab2026__british_business_bank_backing_innovation',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'British Business Bank: Increase the British Business Bank’s total financial capacity to '
               'deliver additional investment into UK businesses',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.33-34) for Table 6.1 line 29 'Backing Innovation: Bring "
                  'forward £1bn investment and increase financial capacity by £2bn for the British Business '
                  "Bank to support additional investment in the UK (resource impacts of increased lending)', "
                  "whose title names both. The line's figure covers both, so this row carries the line's key "
                  "as a measure_component (README rule 9); components are never summed with the line's "
                  'total.'},
 {'page': 35,
  'pages': [35],
  'table_page': 35,
  'title': 'National Wealth Fund: Invest additional capital to support growth, including £2bn for the new '
           'Energy Wealth Fund',
  'base_heading': 'The cost base',
  'base': ['The cost base is estimated using NWF’s AME financial forecasting model based on assumed '
           'commitments over the next five years.'],
  'costing': ['This costing accounts for the public sector net borrowing (PSNB) impact of the NWF’s '
              'financing activity, compared to the pre-measure baseline.',
              'The increase in NWF activity also has a public sector net debt (PSND) impact, based on the '
              'NWF’s assumed drawdowns.',
              'The costing assumes no behavioural impacts.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size, phasing, and product mix of '
                  'funding commitments over the forecast period.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+35m', '+120m', '+250m', '+470m'],
  'table_61_line': '30',
  'measure_key': 'ab2026__national_wealth_fund_capital',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'The costing assumes no behavioural impacts.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 36,
  'pages': [36],
  'table_page': 36,
  'title': 'Rough Sleeping: Invest in a route off the streets across the Parliament, alongside longer-term '
           'accommodation and intensive support',
  'base_heading': 'The cost base',
  'base': ['The cost base consists of all Housing Benefit (HB) and Universal Credit (UC) expenditure in '
           'England.'],
  'costing': ['The costing is estimated on the basis of the number of expected new HB and UC claims as a '
              'result of the programme, applied to the pre-measure cost base above.',
              'The costing accounts for a behavioural response whereby a proportion of individuals supported '
              'move on to more stable housing and continue to receive support.',
              'The exchequer impact below also includes the costs of providing accommodation and support to '
              'rough sleepers.'],
  'uncertainty': ['The main uncertainties in this costing relate to the number of emergency accommodation '
                  'bedspaces and longer-term accommodation units delivered, the proportion of supported '
                  'individuals who generate a new HB or UC claim, average HB and UC awards, the '
                  'accommodation mix of the programme, and behavioural assumptions on move-on outcomes.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-175m', '-515m', '-580m', '-85m', '-90m', '-95m'],
  'table_61_line': '33',
  'measure_key': 'ab2026__rough_sleeping_investment',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 37,
  'pages': [37],
  'table_page': 37,
  'title': 'Social Housing: Introduce a zero rate of VAT for land sold to registered social housing '
           'providers (relevant housing associations) from 1 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of expenditure on land for new social housing where VAT-bearing costs are '
           'currently incurred and cannot be recovered. The tax base is estimated using housing association '
           'expenditure on new dwellings, adjusted using assumptions about the proportion relating to land '
           'acquisition costs and the proportion subject to VAT.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in average '
           'house prices.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing does not account for a behavioural response.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-15m', '-15m', '-15m', '-15m', '-15m'],
  'table_61_line': '36',
  'measure_key': 'ab2026__vat_zero_rate_land_for_social_housing',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "none: 'The costing does not account for a behavioural response.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 38,
  'pages': [38],
  'table_page': 38,
  'title': 'Your First Home: Introduce a new equity loan scheme to support around 70,000 first-time buyers '
           'from April 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base for the upfront cost of funding the loans is a fixed pot of Financial Transactions '
           'funding each year.'],
  'costing': ['Exchequer impacts below represent net income from developer fees after accounting for '
              'operational costs.',
              'The number of loans funded from the fixed pot, as well as the loan redemption behaviour, is '
              'estimated using historical data from similar schemes, adjusted to account for the different '
              'eligibility criteria under the new scheme.',
              'This is supplemented by affordability analysis for the new lower-deposit caseload that this '
              'scheme opens up access to.'],
  'uncertainty': ['The main uncertainties in this costing relate to the mix of customers, properties, '
                  'developers, and locations that will access the fixed pot of funding.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-15m', '+50m', '+95m', '+95m', '+95m', '+95m'],
  'table_61_line': '37',
  'measure_key': 'ab2026__your_first_home_equity_loan',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 39,
  'pages': [39],
  'table_page': 39,
  'title': 'First Time Buyer ISA: Introduce a new ISA for first-time buyers, replacing the Lifetime ISA for '
           'new savers from 6 April 2029',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the savings of first-time buyers expected to purchase a home valued '
           'below £450,000. It is estimated using information on Lifetime ISA holders and first-time buyer '
           'activity to project the number of individuals expected to use the new product.',
           'The tax base is grown over the forecast horizon using the OBR’s forecasts for growth in wages '
           'and salaries, equity prices and interest rates.'],
  'costing': ['The costing is estimated by modelling the changes in the amount and timing of government '
              'bonus payment and withdrawal charge rates.',
              'The costing accounts for a behavioural response whereby potential LISA holders start saving '
              'into the new product. Some individuals who would otherwise have used Lifetime ISAs for '
              'retirement saving instead switch to personal pensions.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+110m', '+110m', '+235m'],
  'table_61_line': '38',
  'measure_key': 'ab2026__first_time_buyer_isa',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 40,
  'pages': [40],
  'table_page': 40,
  'title': 'Lifetime ISA: Reduce the withdrawal charge from 25% to 20% for first-time buyers purchasing '
           'properties above the £450,000 price cap from 29 October 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of withdrawals from Lifetime ISAs where ISA holders purchase properties '
           'above the £450,000 property price cap. The tax base is estimated from the OBR’s forecast of '
           'Lifetime ISA withdrawal charges.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for UK wages and '
           'salaries, alongside forecast trends in Lifetime ISA subscribers.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby the reduced withdrawal charge '
              'encourages additional individuals to open and save into Lifetime ISAs.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-15m', '-20m', '-20m', '-25m', '-25m', '-25m'],
  'table_61_line': '39',
  'measure_key': 'ab2026__lifetime_isa_withdrawal_charge_20pc_above_cap',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 41,
  'pages': [41],
  'table_page': 41,
  'title': 'British Business Bank: Accelerate £450m of commitments to support defence-related and dual-use '
           'businesses',
  'base_heading': 'The cost base',
  'base': ['The measure is modelled as additional commitments between June 2026 and 2028-29, offset by '
           'reductions across the remainder of the Five-Year Strategic Plan period to 2030-31.'],
  'costing': ['The costing compares the forecast profile of drawdowns, distributions and income following '
              'the acceleration with the profile that would otherwise have occurred.',
              'The figures outlined in the table below are those which impact on public sector net borrowing '
              '(PSNB) – including interest and guarantee fee income to be generated by the portfolio, as '
              'well as the costs of delivery and expected losses incurred.',
              'There is also an impact on public sector net debt (PSND) which includes the cost and income '
              'generated above, as well as the net capital cost and return of the investment and lending '
              'expected. Over the period until 2031-32, this is anticipated to be a cost of approximately '
              '£32m, with the portfolio expected to be profit generating for the Exchequer over its '
              'lifetime.',
              'There is an additional impact on public sector net financial liabilities (PSNFL) due to '
              'expected movements in the fair value of the portfolio. This is to be net income generating as '
              'the value of the portfolio increases by approximately £86m (total PSNFL benefit of £54m). The '
              'value is expected to continue to rise beyond this period.'],
  'uncertainty': ['The main uncertainties relate to the timing of fund drawdowns and distributions, the '
                  'timing of debt repayment, and the future value and realised returns of the underlying '
                  'investments.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+5m', '+10m', '+20m', '+25m', '+30m'],
  'table_61_line': None,
  'measure_key': None,
  'proposed_measure_key': 'ab2026__british_business_bank_defence_commitments_accelerated',
  'row_type': 'measure',
  'component': None,
  'document_position': 'between the notes for Table 6.1 lines 39 (p.40) and 44 (p.42)',
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'not_identified_on_table_6_1',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': 'No Table 6.1 title names this measure. The document orders its costing notes by Table 6.1 '
                  "line, and this note sits between line 39's note (p.40) and line 44's (p.42), among the "
                  "national-security lines 40-43. Of those, only line 41 'Defence Investment Plan: "
                  "Reallocate capital spending to fully fund the Defence Investment Plan' has a SUBTOTAL "
                  'head (the others are DEL), but its title does not name the British Business Bank and no '
                  'figure ties the two, so this row carries a proposed key.'},
 {'page': 42,
  'pages': [42],
  'table_page': 42,
  'title': 'UK Export Finance: Increase capacity to support UK defence exports from June 2026',
  'base_heading': 'The cost base',
  'base': ['The cost base comprises the forecast value of UK Export Finance guarantees and loans issued to '
           'support defence exports.'],
  'costing': ['UKEF charges fees when it issues guarantees or loans. In addition, it receives interest on '
              'loans it issues. The costing assumes £10 billion in new guarantees are issued each year '
              'between 2027-28 and 2030-31 with fees paid upfront for each facility. Costs arising from '
              'guarantees being called are not expected over the forecast horizon.',
              'The costing is based on the assumptions noted above on the scale and timing of transactions. '
              'No behavioural responses are anticipated.'],
  'uncertainty': ['The main uncertainties in this costing relate to the timing and scale of future '
                  'guarantees and loans which may be issued using this capacity.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+200m', '+200m', '+200m', '+200m', '+0m'],
  'table_61_line': '44',
  'measure_key': 'ab2026__uk_export_finance_defence_capacity',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "none: 'No behavioural responses are anticipated.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 43,
  'pages': [43],
  'table_page': 43,
  'title': 'E-invoicing: HMRC will require VAT invoices to be issued in a specified electronic format from 1 '
           'April 2029',
  'base_heading': 'The tax base',
  'base': ["The tax base is derived from HMRC's tax gap estimates for VAT, Corporation Tax (CT) and Self "
           'Assessment (SA), split by taxpayer behaviour and business size. These are projected forward over '
           'the forecast period using internal forecasts for VAT liabilities and CT and SA receipts.'],
  'costing': ['The costing has no static impact on taxpayer liabilities.',
              'The costing accounts for a behavioural response whereby businesses adopt mandatory '
              'e-invoicing processes. This generates benefits across two revenue channels: (i) additional '
              'revenue from improved compliance, driven by improved invoice accuracy, increased reliability '
              'and auditability of business records, and greater data transparency. This can reduce '
              'incidences of error, evasion and failure to take reasonable care; and (ii) accelerated tax '
              'collection, through short-term debt prevention enabled by faster invoice processing.',
              'While e-invoicing applies to VAT transactions, improved record keeping and data quality are '
              'expected to generate compliance benefits across CT and SA through better financial reporting '
              'and greater visibility of business activity. The final Exchequer impact increases across the '
              'forecast period, as more businesses adopt e-invoicing solutions.'],
  'uncertainty': ['The main uncertainties relate to the behavioural response across different business '
                  'sizes, including their take-up rates, and the VAT spillover effects on CT and SA '
                  'estimations.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+10m', '+55m', '+140m', '+160m', '+150m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'E-invoicing: HMRC will require VAT invoices to be issued in a specified electronic format '
               'from 1 April 2029',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': "none: 'The costing has no static impact on taxpayer liabilities.'",
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 44,
  'pages': [44],
  'table_page': 44,
  'title': 'Employment expenses: Remove the £2,500 Income Tax Self Assessment expenses threshold from 6 '
           'April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of outturn employment expenses relief claimed through Self Assessment by '
           'taxpayers whose sole reason for filing is to claim relief for non-reimbursed employment '
           'expenses. Fixed deductions and flat-rate expenses are excluded from scope as they do not require '
           'evidence.',
           'The tax base is estimated using HMRC administrative data on claimant numbers and the value of '
           'expenses claimed. The tax base is grown over the forecast horizon using the OBR’s forecasts for '
           'employee number growth and consumer price inflation.'],
  'costing': ['The measure has no static impact on taxpayer liabilities. It does move expenses from Self '
              'Assessment to a P87 claim and therefore changes the timing of repayments.',
              'The costing accounts for a behavioural response where evidential requirements prior to relief '
              'being provided will help manage the risk of error and reduce unsupported employment expenses '
              'claims. As this is voluntary, some taxpayers continue to claim through Self Assessment rather '
              'than using P87 forms/digital equivalents.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural responses '
                  'including those voluntarily moving in payrolling, potential reduction in claims and a '
                  'decrease in errors.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '-85m', '+70m', '+25m', '+25m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Employment expenses: Remove the £2,500 Income Tax Self Assessment expenses threshold from 6 '
               'April 2028',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': "none: 'The measure has no static impact on taxpayer liabilities.'",
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 45,
  'pages': [45],
  'table_page': 45,
  'title': 'More Timely Payment: Require Income Tax Self Assessment taxpayers to pay more of their '
           'liabilities in-year from 2029',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of Self Assessment taxpayers who meet the existing POA criteria. This is '
           'estimated using HMRC administrative Self Assessment and PAYE data to identify taxpayers in scope '
           'and their forecast liabilities.',
           'The tax base is projected over the forecast horizon using the forecast for Self Assessment '
           'receipts.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure payment regimes to the tax '
              'base described above.',
              'The costing takes account of changes in the timing of payments and behavioural responses to '
              'the introduction of regular in-year payments.'],
  'uncertainty': ['The main uncertainties in this costing relate to taxpayer behavioural responses and the '
                  'effect of the measure on the timing and recovery of payments.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+1,355m', '+1,605m', '+1,815m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'More Timely Payment: Require Income Tax Self Assessment taxpayers to pay more of their '
               'liabilities in-year from 2029',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 46,
  'pages': [46],
  'table_page': 46,
  'title': 'VAT and PAYE: Require direct debit arrangements for VAT and PAYE return liabilities from 1 and 6 '
           'April 2029 respectively',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of PAYE and VAT return debts. This is estimated using administrative data '
           'from HMRC’s debt management system, excluding PAYE debts relating to the Construction Industry '
           'Scheme.',
           'The tax base is grown over the forecast period using the OBR’s forecast for growth in PAYE and '
           'VAT receipts.'],
  'costing': ['The costing is estimated by applying assumptions, informed by social research and other '
              'external data, about the proportion of debt that could be prevented through mandating Direct '
              'Debit.',
              'The costing accounts for a behavioural response whereby a proportion of customers who would '
              'otherwise clear their PAYE and VAT return debts shortly after the payment deadline instead '
              'pay on time through mandated Direct Debit.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+165m', '+5m', '+5m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'VAT and PAYE: Require direct debit arrangements for VAT and PAYE return liabilities from 1 '
               'and 6 April 2029 respectively',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 47,
  'pages': [47],
  'table_page': 47,
  'title': 'Real Estate: Participate in a new international agreement to automatically exchange information '
           'on real estate from 2029-30',
  'base_heading': 'The tax base',
  'base': ['The tax base for this measure consists of undeclared rental income and capital gains arising to '
           'UK taxpayers from real estate in jurisdictions signing up to the agreement. The tax base is '
           'estimated using HMRC administrative data and survey data on overseas property ownership.'],
  'costing': ['The costing accounts for a behavioural response whereby the exchange of information and the '
              'increased detection risk provide a deterrent effect that reduces the amount of non-reporting '
              'of Income Tax and Capital Gains by individuals through self-assessment. The costing also '
              'accounts for additional voluntary disclosures of previous liabilities.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+20m', '+65m', '+55m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Real Estate: Participate in a new international agreement to automatically exchange '
               'information on real estate from 2029-30',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 48,
  'pages': [48],
  'table_page': 48,
  'title': 'Debt Management: Enable HMRC to recover lower value tax debts from the bank accounts of '
           'taxpayers who can afford to pay but repeatedly fail to do so from July 2029',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of taxpayers with eligible tax debts up to £5,000 for individuals, and '
           'companies with debts up to £10,000. This is estimated using administrative data from HMRC’s debt '
           'management system.',
           'The tax base is grown over the forecast period using HMRC’s forecasts of debt stock and debt '
           'flow.'],
  'costing': ['The costing uses the tax base above and makes reductions to reflect assumptions on '
              'affordability, availability of external data, number of debts that can be processed and the '
              'planned rollout across different tax regimes.',
              'The costing accounts for a potential behavioural response, considering that some taxpayers '
              'may be more likely to settle their debts upon learning of these new powers.'],
  'uncertainty': ['The main uncertainties in this costing relate to any unexpected delays in '
                  'operationalisation and the rates of affordability.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+50m', '+255m', '+320m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Debt Management: Enable HMRC to recover lower value tax debts from the bank accounts of '
               'taxpayers who can afford to pay but repeatedly fail to do so from July 2029',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 49,
  'pages': [49],
  'table_page': 49,
  'title': "Debt Management: Invest in HMRC's debt management to collect more overdue tax debts",
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the total value of new and aged tax debt placed with third-party DCAs '
           'as a result of the additional funding provided by the measure. This is estimated using HMRC '
           'administrative data on the tax debt balance.'],
  'costing': ['The costing has been calculated by estimating the additional tax collected as a result of the '
              'increased investment which enables additional tax debts to be sent to DCAs. The modelling '
              'uses data on previous DCA debt collection rates, and the known costs of placing tax debts '
              'with these third parties.',
              'The costing accounts for a positive behavioural response whereby some taxpayers, upon '
              'learning their debts have been placed with a DCA, make payments directly to HMRC or enter '
              'into managed payment plans, resulting in recoveries beyond the initial placement period.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base, the collection '
                  'rates of older debts and future DCA commission rates and management fees.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+65m', '+120m', '+0m', '+75m', '+250m', '+575m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': "Debt Management: Invest in HMRC's debt management to collect more overdue tax debts",
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 50,
  'pages': [50],
  'table_page': 50,
  'title': "Tax Compliance: Expand investment in HMRC's compliance workforce to recruit an additional 670 "
           'officers by 2029-30',
  'base_heading': 'The tax base',
  'base': ['The tax base for this costing is the total tax gap less the additional tax revenues accounted '
           'for by previously announced Closing the Tax Gap (CTG) initiatives. The UK tax gap in 2024 to '
           '2025 is estimated to be 6.4% of total theoretical tax liabilities, or £59.2 billion in absolute '
           'terms. This is the difference between the amount of tax due to be paid to HMRC, and what is '
           'actually paid.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in nominal '
           'GDP.'],
  'costing': ['The costing model has been calculated by estimating the additional tax collected by the '
              'additional staff based on historic performance, expectations on the future tax base and '
              'expected future performance.',
              'There is no behavioural effect.'],
  'uncertainty': ['The main uncertainties in this costing relate to the ability to continue to recruit '
                  'specialists at current pace and the diminishing returns associated with hiring new staff. '
                  'A diminishing returns adjustment is applied where the marginal yield from additional '
                  'compliance staff is likely to reduce compared to the baseline.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+50m', '+205m', '+310m', '+260m', '+270m', '+415m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': "Tax Compliance: Expand investment in HMRC's compliance workforce to recruit an additional "
               '670 officers by 2029-30',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "none: 'There is no behavioural effect.'",
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 51,
  'pages': [51],
  'table_page': 51,
  'title': 'Making Tax Digital (MTD) for Income Tax Self Assessment: Introduce a 12 month penalty easement '
           'for taxpayers joining MTD for Income Tax from 6 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base is the revenue lost due to error and failure to take reasonable care by sole '
           'traders and landlords in the income tax Self Assessment population due to join MTD from April '
           '2027.',
           'The forecast profile rises in line with the growth in liabilities and take-up and is estimated '
           'using HMRC’s analysis of the tax gap.'],
  'costing': ['The costing accounts for a behavioural response whereby the lack of penalties for missed '
              'quarterly updates is expected to reduce the rate at which taxpayers join MTD, and results in '
              'less efficient use of quarterly updates during the period.',
              'The reduced rate at which taxpayers join MTD under this measure also impacts the '
              'effectiveness of the transactional risking (digital prompting) element of MTD. An estimate of '
              'this is included in the overall exchequer impact below.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-15m', '-40m', '+5m', '+0m', '+0m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Making Tax Digital (MTD) for Income Tax Self Assessment: Introduce a 12 month penalty '
               'easement for taxpayers joining MTD for Income Tax from 6 April 2027',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 52,
  'pages': [52],
  'table_page': 52,
  'title': 'Image Rights: Delay the implementation of legislation to clarify the tax treatment of image '
           'rights by one year to 6 April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of image rights payments that would be treated as employment income and '
           'therefore subject to Income Tax and National Insurance contributions rather than being paid '
           'through a personal service company and subject primarily to Corporation Tax. It is estimated '
           'using HMRC administrative and compliance data on image rights arrangements.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for average salary '
           'growth.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby some employers are expected to bring '
              'image rights payments into PAYE arrangements ahead of the legislation coming into force, '
              'resulting in tax being paid earlier than would otherwise be the case.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-5m', '-30m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '45',
  'measure_key': 'ab2026__hmrc_tax_gap_package',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Image Rights: Delay the implementation of legislation to clarify the tax treatment of image '
               'rights by one year to 6 April 2028',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 45 'HMRC: Measures to close the tax gap4', whose footnote 4 "
                  "reads 'Full costings for the measures in this package are set out in the Budget 2026 "
                  "Policy Costings document.' The document orders its costing notes by Table 6.1 line, and "
                  "this note sits between line 44's note (p.42) and line 46's (p.53), with the package's "
                  "other notes on pp.43-52. The line's figure covers the whole package, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 53,
  'pages': [53],
  'table_page': 53,
  'title': 'Online Marketplace Liability: Extend to UK businesses with a minimum annual sales threshold per '
           'platform of £90,000 from 1 October 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base is estimated using HMRC operational data covering sales on some online '
           'marketplaces, scaled to cover all online marketplaces based on market research and to exclude '
           'sales which are not in-scope.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in VAT '
           'receipts.'],
  'costing': ['The costing estimates how much VAT might not be currently paid on sales in-scope.',
              'The costing accounts for several behavioural responses where some traders may register for '
              'VAT, absorb some of the additional VAT, reduce sales, or find other ways to reduce their VAT '
              'liability.'],
  'uncertainty': ['The main uncertainties in this costing relate to the share of sales on online '
                  'marketplaces which are in-scope and the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+165m', '+320m', '+270m', '+250m', '+265m'],
  'table_61_line': '46',
  'measure_key': 'ab2026__online_marketplace_liability_uk_businesses',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 54,
  'pages': [54],
  'table_page': 54,
  'title': 'Abroad Fraud: Use data to identify benefit claimants spending longer abroad than permitted from '
           'June 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base is estimated using benefit caseloads, benefit expenditure and levels of fraud and '
           'error forecasted by the OBR and management information from operational trials within DWP.'],
  'costing': ['The costing is estimated by using the results from the operational trials to calculate future '
              'overpayments that will be prevented, whilst taking into account possible overlaps with other '
              'fraud and error activity. No behavioural effects have been taken into account as these are '
              'judged to be negligible.'],
  'uncertainty': ['The main uncertainties in this costing relate to the extent to which findings from '
                  'operational testing are replicated at scale, operational and service delivery '
                  'assumptions, and potential overlap with other fraud and error activity.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+65m', '+145m', '+55m', '+40m', '+40m'],
  'table_61_line': '47',
  'measure_key': 'ab2026__dwp_fraud_and_error_prevention',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Abroad Fraud: Use data to identify benefit claimants spending longer abroad than permitted '
               'from June 2027',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'No behavioural effects have been taken into account as these are judged "
                            "to be negligible.'",
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 47 'DWP Fraud and Error: Expand use of data and targeted "
                  "controls to prevent fraud from entering the benefits system4', whose footnote 4 reads "
                  "'Full costings for the measures in this package are set out in the Budget 2026 Policy "
                  "Costings document.' The document orders its costing notes by Table 6.1 line, and this "
                  "note sits between line 46's note (p.53) and line 48's (p.59), with the package's other "
                  "notes on pp.54-58. The line's figure covers the whole package, so this row carries the "
                  "line's key as a measure_component (README rule 9); components are never summed with the "
                  "line's total."},
 {'page': 55,
  'pages': [55],
  'table_page': 55,
  'title': 'Pension Credit: Require claimants to redeclare the amount of capital they hold from January 2028',
  'base_heading': 'The cost base',
  'base': ['The cost base is estimated using benefit caseloads, benefit expenditure and levels of fraud and '
           'error forecasted by the OBR.'],
  'costing': ['The costing is estimated by applying the above cost base to calculate future overpayments '
              'that will be prevented, taking into account the frequency with which the prompts will be sent '
              'out and any overlaps with other fraud and error activity. No behavioural effects have been '
              'taken into account as these are judged to be negligible.'],
  'uncertainty': ['The main uncertainties in this costing relate to the number of changes reported by '
                  'claimants, the value of those changes and the possible overlap with other fraud and error '
                  'activity.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-5m', '+0m', '+20m', '+40m', '+55m'],
  'table_61_line': '47',
  'measure_key': 'ab2026__dwp_fraud_and_error_prevention',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Pension Credit: Require claimants to redeclare the amount of capital they hold from January '
               '2028',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'No behavioural effects have been taken into account as these are judged "
                            "to be negligible.'",
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 47 'DWP Fraud and Error: Expand use of data and targeted "
                  "controls to prevent fraud from entering the benefits system4', whose footnote 4 reads "
                  "'Full costings for the measures in this package are set out in the Budget 2026 Policy "
                  "Costings document.' The document orders its costing notes by Table 6.1 line, and this "
                  "note sits between line 46's note (p.53) and line 48's (p.59), with the package's other "
                  "notes on pp.54-58. The line's figure covers the whole package, so this row carries the "
                  "line's key as a measure_component (README rule 9); components are never summed with the "
                  "line's total."},
 {'page': 56,
  'pages': [56],
  'table_page': 56,
  'title': 'Universal Credit: Expand specialist fraud and error checks in Jobcentres from April 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base is estimated using benefit caseloads, benefit expenditure and levels of fraud and '
           'error forecasted by the OBR and management information from operational trials from DWP.'],
  'costing': ['The costing is estimated by applying the above cost base to calculate historical overpayments '
              'that will be identified and future overpayments that will be prevented, whilst taking into '
              'account debt recoveries and overlaps with other fraud and error activity. No behavioural '
              'effects have been taken into account as these are judged to be negligible.'],
  'uncertainty': ['The main uncertainties in this costing relate to staff performance, the value of '
                  'overpayments and overlap with other fraud and error activity.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-5m', '-40m', '-25m', '+10m', '+105m', '+175m'],
  'table_61_line': '47',
  'measure_key': 'ab2026__dwp_fraud_and_error_prevention',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Universal Credit: Expand specialist fraud and error checks in Jobcentres from April 2027',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'No behavioural effects have been taken into account as these are judged "
                            "to be negligible.'",
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 47 'DWP Fraud and Error: Expand use of data and targeted "
                  "controls to prevent fraud from entering the benefits system4', whose footnote 4 reads "
                  "'Full costings for the measures in this package are set out in the Budget 2026 Policy "
                  "Costings document.' The document orders its costing notes by Table 6.1 line, and this "
                  "note sits between line 46's note (p.53) and line 48's (p.59), with the package's other "
                  "notes on pp.54-58. The line's figure covers the whole package, so this row carries the "
                  "line's key as a measure_component (README rule 9); components are never summed with the "
                  "line's total."},
 {'page': 57,
  'pages': [57],
  'table_page': 57,
  'title': 'Universal Credit: Reverse the capital verification element of previously announced upfront '
           'verification checks',
  'base_heading': 'The cost base',
  'base': ['The cost base for this measure is estimated using current and forecasted levels of fraud and '
           'error in Universal Credit, including national statistics on DWP fraud and error and the OBR’s '
           'Autumn 2026 forecast for fraud and error in Universal Credit.'],
  'costing': ['The costing is estimated by breaking down the national statistics on DWP fraud and error by '
              'cause to determine how many claimants are not declaring the right levels of capital then '
              'applying this to forecasted levels of incorrect benefit payments.'],
  'uncertainty': ['The main uncertainties in this costing relate to the level of incorrect payments due to '
                  'capital not being declared and potential overlap with other DWP initiatives to tackle '
                  'fraud and error.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-5m', '-10m', '+5m', '+15m', '-5m', '+0m'],
  'table_61_line': '47',
  'measure_key': 'ab2026__dwp_fraud_and_error_prevention',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Universal Credit: Reverse the capital verification element of previously announced upfront '
               'verification checks',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 47 'DWP Fraud and Error: Expand use of data and targeted "
                  "controls to prevent fraud from entering the benefits system4', whose footnote 4 reads "
                  "'Full costings for the measures in this package are set out in the Budget 2026 Policy "
                  "Costings document.' The document orders its costing notes by Table 6.1 line, and this "
                  "note sits between line 46's note (p.53) and line 48's (p.59), with the package's other "
                  "notes on pp.54-58. The line's figure covers the whole package, so this row carries the "
                  "line's key as a measure_component (README rule 9); components are never summed with the "
                  "line's total."},
 {'page': 58,
  'pages': [58],
  'table_page': 58,
  'title': 'Universal Credit: Restrict repeat access to New Claim Advances from April 2029',
  'base_heading': 'The cost base',
  'base': ['The cost base is estimated using benefit caseloads, benefit expenditure and levels of fraud and '
           'error forecasted by the OBR.'],
  'costing': ['The costing is estimated by forecasting the number of new claims advances that are paid to '
              'people who currently have an outstanding new claims advances debt and applying a reduction to '
              'that amount to account for exceptions. Consequential adjustments to future flows of '
              'repayments are then netted off the savings. No behavioural effects have been taken into '
              'account.',
              'The costing is accounted as a financial transaction, with an impact of +£130m estimated in '
              '2029-30 in cash terms, but the funding of the measure is accounted as public expenditure, '
              'with an impact of -£35m in 2029-30 in expenditure terms.'],
  'uncertainty': ['The main uncertainties in this costing relate to future forecasts of Universal Credit, '
                  'claimant behaviour and finalising the policy design around exemptions.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '-35m', '-35m', '-35m'],
  'table_61_line': '47',
  'measure_key': 'ab2026__dwp_fraud_and_error_prevention',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Universal Credit: Restrict repeat access to New Claim Advances from April 2029',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'No behavioural effects have been taken into account.'",
  'static_impact': None,
  'mapping_note': "Component of Table 6.1 line 47 'DWP Fraud and Error: Expand use of data and targeted "
                  "controls to prevent fraud from entering the benefits system4', whose footnote 4 reads "
                  "'Full costings for the measures in this package are set out in the Budget 2026 Policy "
                  "Costings document.' The document orders its costing notes by Table 6.1 line, and this "
                  "note sits between line 46's note (p.53) and line 48's (p.59), with the package's other "
                  "notes on pp.54-58. The line's figure covers the whole package, so this row carries the "
                  "line's key as a measure_component (README rule 9); components are never summed with the "
                  "line's total."},
 {'page': 59,
  'pages': [59],
  'table_page': 59,
  'title': 'Welfare Reform: Remove benefit entitlements from serious offenders hospitalised in Great Britain '
           'from 6 April 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base for this measure comes from the OBR’s Universal Credit benefit expenditure '
           'forecast as we anticipate that the majority of claimants affected by the change will be in '
           'receipt of Universal Credit.'],
  'costing': ['The costing is calculated by applying forecast benefit award amounts to the estimated '
              'affected caseload which has been calculated using HMPPS data for England and Wales, and NHS '
              'England data. As comparable Scottish statistics are not available, the costing includes an '
              'uplift to account for Scotland. That costing has then been reduced by the expected costs to '
              'the NHS because of the policy change. We do not anticipate any behavioural effects because of '
              'this policy change because the potential loss of benefit entitlement is unlikely to influence '
              'whether an individual commits a serious offence.'],
  'uncertainty': ['The main uncertainties in this costing relate to the number of claimants in scope, '
                  'resulting length of stay costs to the NHS and the existing benefit award amount received '
                  'by claimants in scope.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+5m', '+5m', '+5m', '+5m', '+5m'],
  'table_61_line': '48',
  'measure_key': 'ab2026__benefits_removed_hospitalised_serious_offenders',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'Great Britain',
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'We do not anticipate any behavioural effects because of this policy "
                            'change because the potential loss of benefit entitlement is unlikely to '
                            "influence whether an individual commits a serious offence.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 60,
  'pages': [60],
  'table_page': 60,
  'title': 'Distributions: Modernise the distributions framework from 6 April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of distributions and other value extracted from companies by individuals '
           'that are currently subject to Capital Gains Tax, or are not currently taxed, but which would be '
           'brought within the dividend Income Tax regime under the reforms. It is estimated using a '
           'combination of HMRC administrative data, including clearance, compliance and Self Assessment '
           'data, supplemented by expert judgement where direct data is unavailable.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in equity '
           'prices.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above. The measure largely increases the tax charged on distributions currently '
              'taxed as Capital Gains Tax and brings some currently untaxed transactions within the dividend '
              'Income Tax regime. The package also includes modernisation of targeted reliefs, to retain CGT '
              'treatment for genuine commercial exits and demergers, meaning no change in rates for these '
              'transactions.',
              'The costing accounts for a behavioural response whereby affected individuals change how they '
              'extract value from companies, including by no longer undertaking affected transactions, '
              'restructuring their affairs, or seeking alternative routes that reduce their tax '
              'liabilities.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+55m', '+800m', '+775m', '+785m'],
  'table_61_line': '49',
  'measure_key': 'ab2026__distributions_framework_modernised',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 61,
  'pages': [61],
  'table_page': 61,
  'title': 'Advance Corporation Tax (ACT): Abolish Advance Corporation Tax from 1 April 2031',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the taxable profits of companies with remaining unrelieved surplus ACT '
           'balances. The tax base is estimated using HMRC’s Corporation Tax administrative data. It is '
           'grown over the forecast horizon using the OBR’s forecast for growth in taxable company profits '
           'and information gathered during the Government’s call for evidence on ACT reform.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing does not account for a behavioural response.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+0m', '+5m', '+15m'],
  'table_61_line': '50',
  'measure_key': 'ab2026__advance_corporation_tax_abolished',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "none: 'The costing does not account for a behavioural response.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 62,
  'pages': [62],
  'table_page': 62,
  'title': 'Cross-Border Services: Restrict the reverse charge on supplies of services from overseas to '
           'VAT-registered businesses from 1 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of taxable cross-border supplies of services made by overseas businesses '
           'to non-VAT-registered UK businesses. The tax base is estimated using information on overseas '
           'suppliers’ total sales from published annual reports, adjusted to identify taxable supplies '
           'within scope.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in nominal '
           'GDP.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response including changes to the timing of purchases '
              'and overseas businesses absorbing part of the tax cost. An allowance is also made for some '
              'activity moving outside the scope of the measure due to other behavioural responses.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base, the extent to '
                  'which VAT is already charged on supplies, and behavioural responses following '
                  'implementation.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+70m', '+75m', '+75m', '+75m', '+75m'],
  'table_61_line': '51',
  'measure_key': 'ab2026__vat_reverse_charge_overseas_services_restricted',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 63,
  'pages': [63],
  'table_page': 63,
  'title': 'Pension Tax Allowance: Remove the income tax liability for pensioners with total income up to '
           'the value of the new State Pension from 6 April 2027 until 5 April 2030',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of individuals above State Pension age with an Income Tax liability who '
           'are entitled to the full or tapered Allowance based on their total income. It is estimated using '
           'HMRC’s Personal Tax Model and HMRC administrative data.',
           'The tax base and cost are grown over the forecast horizon using the OBR’s forecast for pensioner '
           'incomes, including State Pension uprating, inflation and earnings growth.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing assumes no behavioural response as an individual’s ability to manage their income '
              'to retain entitlement to the Allowance is expected to be limited.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base, and the value '
                  'of the new State Pension.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-45m', '-90m', '-150m', '+50m', '-15m'],
  'table_61_line': '52',
  'measure_key': 'ab2026__pension_tax_allowance',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "none: 'The costing assumes no behavioural response as an individual’s ability "
                            'to manage their income to retain entitlement to the Allowance is expected to be '
                            "limited.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 64,
  'pages': [64],
  'table_page': 64,
  'title': 'Pensions Tax: Remove the two-year rule for taxation of pension and lump sum death benefits from '
           '28 October 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of pension and lump sum death benefits paid following the death of '
           'individuals aged under 75 that would, in the absence of the measure, be subject to Income Tax '
           'because they are paid outside the two-year period. The tax base is estimated using the ONS’s '
           'Wealth and Asset Survey data on pension wealth and modelling assumptions about deaths, '
           'beneficiary payments and the proportion paid outside the two-year period.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for long-term GDP '
           'growth.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above. Under the pre-measure regime, affected payments are subject to Income Tax at '
              'the beneficiary’s marginal rate where paid to an individual and a flat rate of 45% where paid '
              'to a non-individual such as a trust or the deceased person’s estate; under the post-measure '
              'regime, this charge is removed.',
              'The costing does not account for any behavioural response to the policy change as these are '
              'expected to be negligible.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-5m', '-15m', '-15m', '-15m', '-15m', '-15m'],
  'table_61_line': '53',
  'measure_key': 'ab2026__pension_death_benefits_two_year_rule_removed',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "none: 'The costing does not account for any behavioural response to the policy "
                            "change as these are expected to be negligible.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 65,
  'pages': [65],
  'table_page': 65,
  'title': 'Modernising Taxation of Foreign Sovereign Investments: Introduce a new statutory regime for the '
           'direct taxation of foreign sovereigns from 1 January 2029',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of UK assets held by foreign sovereigns, sovereign wealth funds, '
           'State-operated Overseas Pension Funds (SOPFs) and certain sovereign individuals that will become '
           'subject to UK tax under the reformed sovereign immunity regime. It is estimated using HMRC '
           'administrative data combined with external information on Sovereign Wealth Fund Institute and '
           'SOPFs.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for UK property prices '
           'and property transactions.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby affected taxpayers may restructure, '
              'dispose of, or adjust their UK investment holdings in response to becoming subject to UK '
              'tax.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+110m', '+495m', '+690m', '+675m', '+655m'],
  'table_61_line': '54',
  'measure_key': 'ab2026__foreign_sovereign_investments_taxation',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 66,
  'pages': [66],
  'table_page': 66,
  'title': 'Bank Surcharge: Temporarily increase the Bank Corporation Tax Surcharge rate from 3% to 6%, to '
           'fund breathing space measures for households, for 15 months from 1 January 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base is estimated using Banking Surcharge liabilities based on HMRC receipts data. The '
           'tax base is grown over the forecast horizon using the OBR’s forecast for growth in the taxable '
           'profits of the financial sector.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby banking groups with internationally '
              'mobile profits may locate activity outside of the UK in response to the higher rate, although '
              'this impact is limited by the defined period of the measure.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+305m', '+950m', '+220m', '+0m', '+0m', '+0m'],
  'table_61_line': '55',
  'measure_key': 'ab2026__bank_surcharge_6pc_temporary',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 67,
  'pages': [67],
  'table_page': 67,
  'title': 'Machine Games Duty: Increase the rate from 20% to 25% for higher stake machines from 1 April '
           '2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the net takings from gaming machines with a maximum stake above £1 or a '
           'maximum prize above £100. The tax base is estimated using HMRC administrative data on Machine '
           'Games Duty registrations and returns and the Gambling Commission’s Industry Statistics.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for Machine Games Duty '
           'receipts.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response by gambling operators who may pass on some of '
              'the duty rise by lowering the Return to Player, leading to machine gambling demand falling '
              'and for some activity to shift towards remote gambling. An elasticity of -0.95 is used, with '
              '25% of the reduction in stakes then assumed to substitute to Remote Gaming Duty. A general '
              'attrition assumption is applied to account for further demand reductions over time.',
              'A reduction in Corporation Tax receipts is estimated as part of the costing, given affected '
              'companies’ profits may reduce due to higher Machine Games Duty rates.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+135m', '+130m', '+130m', '+130m', '+130m'],
  'table_61_line': '56',
  'measure_key': 'ab2026__machine_games_duty_higher_stake_25pc',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Machine Games Duty: Increase the rate from 20% to 25% for higher stake machines from 1 April '
               '2027',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.67-68) for Table 6.1 line 56 'Machine Games Duty: Increase "
                  'the rate from 20% to 25% for higher stake machines from 1 April 2027 and move duty '
                  "liability to the machine supplier from 1 April 2028', whose title names both. The line's "
                  "figure covers both, so this row carries the line's key as a measure_component (README "
                  "rule 9); components are never summed with the line's total."},
 {'page': 68,
  'pages': [68],
  'table_page': 68,
  'title': 'Machine Games Duty: Move duty liability to the machine supplier from 1 April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base is the Machine Games Duty liability of operators using a profit-sharing '
           'arrangement. The tax base is estimated using HMRC administrative data from Machine Games Duty '
           'returns, payments, registration information and compliance activity.',
           'The tax base is grown over the forecast horizon using the OBR’s Machine Games Duty forecast.'],
  'costing': ['The costing is calculated by estimating the additional revenue from reduced non-compliance '
              'and from earlier payment of duty through reduced late payments.',
              'The costing accounts for a behavioural response whereby some operators will adjust their '
              'behaviour and reduce their liability for Machine Games Duty.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural assumptions.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+20m', '+15m', '+15m', '+10m'],
  'table_61_line': '56',
  'measure_key': 'ab2026__machine_games_duty_higher_stake_25pc',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Machine Games Duty: Move duty liability to the machine supplier from 1 April 2028',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.67-68) for Table 6.1 line 56 'Machine Games Duty: Increase "
                  'the rate from 20% to 25% for higher stake machines from 1 April 2027 and move duty '
                  "liability to the machine supplier from 1 April 2028', whose title names both. The line's "
                  "figure covers both, so this row carries the line's key as a measure_component (README "
                  "rule 9); components are never summed with the line's total."},
 {'page': 69,
  'pages': [69],
  'table_page': 69,
  'title': 'Business Rates: Remove reliefs for vape shops and Adult Gaming Centres from 1 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base for the relief consists of the estimated rateable value of qualifying properties, '
           'multiplied by the relevant multiplier for relevant years.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above. The static cost is adjusted to reflect that business rates are '
              'deductible for Corporation Tax for companies and Income Tax for the self-employed, and that '
              'business rates are devolved to Scotland, Wales, and Northern Ireland.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size and rateable value of the tax '
                  'base, the future growth in number of eligible properties, the impacts of appeals against '
                  'property valuations on rateable values, and the impact of behavioural responses.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+10m', '+10m', '+10m', '+10m', '+10m'],
  'table_61_line': '57',
  'measure_key': 'ab2026__business_rates_vape_shops_and_agcs_reliefs_removed',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 70,
  'pages': [70, 71],
  'table_page': 70,
  'title': 'Writing-down Allowances: Reduce the main rate writing-down allowance to 12% from April 2027 and '
           'increase the main rate first-year allowance to 50% from 1 January 2027',
  'base_heading': 'The tax base',
  'base': ['For the main Writing Down Allowance rate cut, the tax base consists of capital expenditure '
           'eligible for main rate Writing Down Allowances, including both new qualifying expenditure and '
           'existing pooled expenditure from previous years. For the first-year allowance increase, the tax '
           'base consists of new expenditure eligible for main rate Writing Down Allowances apart from '
           'second-hand assets and cars. Both allowance rate changes impact Corporation Tax and Income Tax '
           'populations.',
           'The tax base is estimated using HMRC administrative data on capital allowances claims and '
           'expenditure from company tax and self-assessment returns, supplemented by other data sources '
           'such as survey data and transport statistics.',
           "The tax base is grown over the forecast horizon using the OBR's economic determinants, including "
           'forecasts for business investment growth.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby some businesses may seek to increase '
              'claims under more generous capital allowance regimes, or make non-compliant claims, in '
              'response to the reduction in the generosity of main rate Writing Down Allowances and the '
              'increase in generosity of the first-year allowance.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+125m', '+765m', '+1,040m', '+1,075m', '+1,100m', '+1,120m'],
  'table_61_line': '58',
  'measure_key': 'ab2026__writing_down_allowance_12pc_and_fya_50pc',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 72,
  'pages': [72],
  'table_page': 72,
  'title': 'Private Hire Vehicle Operators: Deem larger operators with annual fare turnover over £50 million '
           'liable for VAT on the full value of their fares from 2 January 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists mainly of fares of private hire vehicle operators outside London that '
           'would otherwise pay VAT only on their commission, with adjustments for operators potentially '
           'newly included or excluded by the £50 million threshold. It is estimated using HMRC tax data and '
           'information on operators’ turnover and an estimate of the share of fares earned outside London.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in nominal '
           'consumer expenditure.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby affected private hire vehicle '
              'operators may split their businesses to be below the turnover threshold, alongside some '
              'customers switching to operators outside the measure. The costing also makes an allowance for '
              'some drivers voluntarily registering for VAT in order to recover VAT on their purchases.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+95m', '+385m', '+395m', '+410m', '+425m'],
  'table_61_line': '59',
  'measure_key': 'ab2026__private_hire_operators_vat_full_fare',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 73,
  'pages': [73],
  'table_page': 73,
  'title': 'Business Asset Disposal Relief (BADR): Reduce the lifetime limit to £500,000 from 6 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of all CGT liable gains above the new £500,000 lifetime limit on BADR '
           'eligible assets disposed of from 6 April 2027 and over the forecast period.',
           'The tax base is grown over the forecast horizon using the OBR’s CGT forecast.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for behavioural responses whereby some taxpayers may change the timing '
              'of their disposals, switch to taxable income, or switch to other types of investment that '
              'receive CGT relief where they are eligible.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+5m', '+60m', '+180m', '+255m', '+280m', '+305m'],
  'table_61_line': '60',
  'measure_key': 'ab2026__badr_lifetime_limit_500000',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 74,
  'pages': [74],
  'table_page': 74,
  'title': 'Property Income: Increase tax rates on property income by 2ppts at the basic, higher and '
           'additional rate from 6 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of all individuals and partnerships that receive property income. It is '
           'estimated using HMRC administrative data from the 2024-25 Self Assessment returns.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in land and '
           'property income.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby some landlords may choose to '
              'incorporate their property business to avoid the increased property income taxation, though '
              'this response is expected to be limited.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+35m', '+575m', '+435m', '+445m', '+455m'],
  'table_61_line': '61',
  'measure_key': 'ab2026__property_income_rates_plus_2pp',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 75,
  'pages': [75],
  'table_page': 75,
  'title': 'Savings Income: Increase tax rates on savings income by 2ppts at the basic, higher and '
           'additional rate from 6 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of all taxable savings income held by individuals, excluding income within '
           'the Personal Allowance, Personal Savings Allowance, the Starting Rate for Savings, and ISA '
           'returns. This is estimated using HMRC’s Personal Tax Model, drawing on administrative data from '
           'the 2023 to 2024 Survey of Personal Incomes.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in savings '
           'income.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby some individuals shift their savings '
              'into tax-advantaged products such as Individual Savings Accounts (ISAs).'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+15m', '+125m', '+555m', '+520m', '+555m', '+590m'],
  'table_61_line': '62',
  'measure_key': 'ab2026__savings_income_rates_plus_2pp',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 76,
  'pages': [76],
  'table_page': 76,
  'title': 'Heavy Goods Vehicles: Reduce Vehicle Excise Duty to £1 for 12 months from 1 July 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base for this policy consists of every HGV in eligible tax classes that pays Vehicle '
           'Excise Duty between 1 July 2026 and 30 June 2027. The tax base is estimated using annual VED '
           'stock data which is provided by DVLA.',
           'The tax base is grown over the forecast horizon using projected growth in the stock of eligible '
           'heavy goods vehicles using historical annual VED stock data.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing includes an assumed timing effect associated with the temporary reduced rate.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-135m', '-50m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '65',
  'measure_key': 'ab2026__hgv_ved_1_for_12_months',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 77,
  'pages': [77],
  'table_page': 77,
  'title': 'Great British Summer Savings Scheme: Reduce VAT to 5% on family days out from 25 June to 1 '
           'September',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the VAT-exclusive value of children’s meals and tickets, and admission '
           'to family attractions within scope of the measure. It is estimated using mainly ONS statistics '
           'and HMRC VAT return data, with adjustments to reflect the specific services covered.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in nominal '
           'consumer expenditure.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for behavioural responses whereby businesses broaden the availability of '
              'eligible children’s offers and consumers shift or increase spending during the relief '
              'period.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-310m', '+0m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '66',
  'measure_key': 'ab2026__vat_5pc_family_days_out_summer_2026',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 78,
  'pages': [78],
  'table_page': 78,
  'title': 'Corporation Tax: Make the foreign permanent establishment exemption mandatory, preventing their '
           'losses from reducing UK corporation tax receipts for accounting periods beginning on or after 1 '
           'January 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the non-ring-fenced UK taxable profits of large groups that have been '
           'identified as currently set against foreign branch losses. This is estimated using Corporation '
           'Tax return data and information from company tax computations.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in non-North '
           'Sea corporate profits.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby affected groups increase the '
              'utilisation of foreign branch losses and related reliefs before the measure takes effect and, '
              'over the longer term, may make structural changes to reduce their exposure to the policy.'],
  'uncertainty': ['The main uncertainties in this costing relate to size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+120m', '+480m', '+495m', '+450m', '+460m', '+470m'],
  'table_61_line': '68',
  'measure_key': 'ab2026__foreign_permanent_establishment_exemption_mandatory',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 79,
  'pages': [79],
  'table_page': 79,
  'title': 'Electricity Generator Levy: Increase the rate from 45% to 55% until 31 March 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of exceptional revenues from in-scope electricity generation over and '
           'above the EGL’s benchmark price, after relevant exclusions, exceptional costs and the annual '
           'allowance. It is estimated using electricity generation data from Department for Energy Security '
           'and Net Zero and HMRC administrative data.',
           'The tax base is grown over the forecast horizon using the OBR’s forecasts for wholesale '
           'electricity prices and CPI inflation, alongside projected electricity generation.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a small behavioural response whereby some firms reduce their EGL '
              'liabilities through tax planning.'],
  'uncertainty': ['The main uncertainty in this costing relates to the size of the tax base, in particular '
                  'future wholesale electricity prices.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+60m', '+35m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '69',
  'measure_key': 'ab2026__electricity_generator_levy_55pc',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 80,
  'pages': [80],
  'table_page': 80,
  'title': 'Industrial Electricity: Fund the British Industrial Competitiveness Scheme starting from 1 April '
           '2027, including a backdated payment for eligible businesses',
  'base_heading': 'The cost base',
  'base': ['The cost base is total estimated energy consumption of businesses eligible for the BICS and '
           'Supercharger uplift schemes.'],
  'costing': ['The costing has been calculated by subtracting the cost of the BICS and Supercharger uplift '
              'schemes from the estimated aggregate bill saving impact of removing Carbon Price Support from '
              'April 2028 and changing the indexation mechanism for the Renewables Obligation and Feed in '
              'Tariffs schemes from the Retail Prices Index to the Consumer Price Index.',
              'The costing accounts for a behavioural response whereby businesses eligible for BICS increase '
              'their energy consumption in response to a lower unit price of electricity.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the cost base and '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-1,235m', '-65m', '-135m', '-420m', '-465m'],
  'table_61_line': '70',
  'measure_key': 'ab2026__british_industrial_competitiveness_scheme',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 81,
  'pages': [81],
  'table_page': 81,
  'title': 'Carbon Price Support (CPS): Remove the CPS rates to reduce energy bills from 1 April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of fossil fuels (coal, gas, liquefied petroleum gas, oil) used for '
           'electricity generation by major power producers and Combined Heat and Power installations '
           'producing non-qualifying electricity. It is estimated using HMRC administrative data and '
           'forecasts of fossil fuel electricity generation from the Department for Energy Security and Net '
           'Zero’s Dynamic Dispatch Model.',
           'The tax base projections are adjusted to account for the OBR’s forecasts for GDP, inflation, '
           'exchange rates, and energy prices.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby the removal of Carbon Price Support '
              'increases demand for UK Emissions Trading Scheme (ETS) permits from electricity generators, '
              'leading to a higher UK ETS price and therefore higher UK ETS revenue than would otherwise '
              'have been the case.'],
  'uncertainty': ['The main uncertainties in this costing relate to future fossil fuel electricity '
                  'generation and the size of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '-165m', '-45m', '-15m', '-10m'],
  'table_61_line': '71',
  'measure_key': 'ab2026__carbon_price_support_removed',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 82,
  'pages': [82],
  'table_page': 82,
  'title': 'Spring 2026 Youth Employment and Skills Package: Expand Youth Guarantee and apprenticeship '
           'support',
  'base_heading': 'The cost base',
  'base': ["The cost base uses data on current Universal Credit expenditure and the OBR's Universal Credit "
           'expenditure forecast for the eligible cohort of the expanded scheme only (22- to 24-year-olds).'],
  'costing': ['AME savings from the programme arise from lower welfare spending, as individuals will have a '
              'reduced UC entitlement while in employment.',
              'The costing is estimated by calculating a UC saving per job and applying this to estimated '
              'cohort volumes.',
              'The costing accounts for a behavioural response, whereby some claimants will leave subsidised '
              'employment before completing the six-month job.'],
  'uncertainty': ['The main uncertainties in this costing relate to the number of individuals eligible for a '
                  'role, the behavioural response (the length of time each young person remain in the job), '
                  'and the additionality of welfare savings.'],
  'table_label': 'Exchequer impact [AME savings only]',
  'table_row': 'Exchequer impact [AME savings only]',
  'table_notes': [],
  'values': ['+0m', '+25m', '+35m', '+0m', '+0m', '+0m'],
  'table_61_line': '72',
  'measure_key': 'ab2026__youth_guarantee_and_apprenticeships_spring_2026',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': "AME savings only ('Exchequer impact [AME savings only]'), for the Youth Guarantee expansion "
               'to 22- to 24-year-olds',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "The note's title equals Table 6.1 line 72's, 'Spring 2026 Youth Employment and Skills "
                  "Package: Expand Youth Guarantee and apprenticeship support', but its table prints the AME "
                  "savings only ('Exchequer impact [AME savings only]'), and its text costs the expansion of "
                  'the Youth Guarantee to 22- to 24-year-olds without mentioning the apprenticeship support '
                  'the line also names. Table 6.1 prints -290 in 2027-28 and -375 in 2028-29 for the line. '
                  "The figure is one fiscal head of the line, so this row carries the line's key as a "
                  "measure_component (README rule 9); components are never summed with the line's total."},
 {'page': 83,
  'pages': [83],
  'table_page': 83,
  'title': 'British Business Bank: Expand the Growth Guarantee Scheme to support £6.5 billion of additional '
           'SME lending across this Parliament',
  'base_heading': 'The cost base',
  'base': ['The cost base consists of the additional lending supported by the Growth Guarantee Scheme '
           'relative to the pre-measure forecast. The measure increases supported lending by £1.0 billion in '
           '2026-27, £1.5 billion in 2027-28 and £2.0 billion in each of 2028-29 and 2029-30.'],
  'costing': ['The costing applies the expected lifetime loss rate to each year’s additional guaranteed '
              'lending. Expected losses are recognised when guarantees are entered into, while Scheme Lender '
              'Fee income accrues over the period for which the guaranteed lending remains outstanding.',
              'The loss-rate assumptions draw on the performance and valuation of the existing Growth '
              'Guarantee Scheme portfolio, with adjustments for the introduction of ten-year facilities and '
              'the expected characteristics of future borrowers. Fee income is estimated using the expected '
              'deployment and amortisation profile of the additional lending.'],
  'uncertainty': ['The main uncertainties in this costing relate to future take-up, and default and recovery '
                  'rates, particularly given the introduction of ten-year facilities.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-105m', '-145m', '-180m', '-170m', '-160m', '-155m'],
  'table_61_line': '75',
  'measure_key': 'ab2026__growth_guarantee_scheme_expansion',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 84,
  'pages': [84],
  'table_page': 84,
  'title': 'Leeds City Fund: Establish the Leeds City Fund with 100% retention of business rates growth',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of estimated new commercial floorspace created within the zone. This is '
           'multiplied by the estimated rateable value per square metre of the new floorspace.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure local retention share '
              'to the tax base described above.',
              'Additional business rates income is assumed to facilitate borrowing against future revenue. '
              'Borrowing is estimated as £20 million of additional capital borrowing annually from 2028-29 '
              'to 2031-32, plus interest and minimum revenue provision; none is assumed without the zone.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'associated level of borrowing.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '-25m', '-25m', '-25m', '-30m'],
  'table_61_line': '76',
  'measure_key': 'ab2026__leeds_city_fund',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 85,
  'pages': [85],
  'table_page': 85,
  'title': 'UK-India Comprehensive Economic and Trade Agreement (CETA): Changes to tariffs following entry '
           'into force on 15 July 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base is the expected Customs Duty revenue from the relevant commodity codes impacted, '
           'had the measure not been implemented. The tax base has been projected across the forecast using '
           'the OBR’s forecasts for non-oil goods imports.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above.',
              'A behavioural adjustment is made to account for the incentive for traders to delay imports '
              'before the agreement takes effect, the proportion of traders that utilise the preferential '
              'tariff rates, and traders diverting their trade to benefit from the preferential tariffs.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-175m', '-260m', '-265m', '-270m', '-280m', '-295m'],
  'table_61_line': '77',
  'measure_key': 'ab2026__uk_india_ceta_and_double_contributions_convention',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'UK-India Comprehensive Economic and Trade Agreement (CETA): Changes to tariffs following '
               'entry into force on 15 July 2026',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.85-86) for Table 6.1 line 77 'UK-India: Bring into force the "
                  'Comprehensive Economic and Trade Agreement and Double Contributions Convention from 15 '
                  "July 2026', whose title names both. The line's figure covers both, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 86,
  'pages': [86],
  'table_page': 86,
  'title': 'National Insurance Contributions: Bring the UK-India Double Contributions Convention into force '
           'from 15 July 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the income of employees moving between the UK and India, which becomes '
           'liable to, or ceases to be liable to, Class 1 National Insurance contributions as a consequence '
           'of the DCC. Estimates of the population affected by the DCC have been produced using available '
           'administrative data and reasonable proxies where direct measures are not available.',
           'The tax base is grown over the forecast horizon using the OBR’s forecasts for employee growth '
           'and wage growth.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above. The relative flows of temporary workers between the UK and India and the '
              'changes in National Insurance liabilities introduced by the DCC result in an overall net '
              'reduction in receipts.',
              'The costing includes a small temporary behavioural adjustment associated with the '
              'introduction of the new detached worker arrangements.'],
  'uncertainty': ['The main uncertainties in this costing relate to the number of UK and Indian workers who '
                  'qualify for the detached worker period, both initially and over the forecast period. '
                  'There is also uncertainty around assumptions about temporary work assignment duration and '
                  'the behavioural response of affected workers.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+5m', '-25m', '-65m', '-90m', '-105m', '-105m'],
  'table_61_line': '77',
  'measure_key': 'ab2026__uk_india_ceta_and_double_contributions_convention',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'National Insurance Contributions: Bring the UK-India Double Contributions Convention into '
               'force from 15 July 2026',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.85-86) for Table 6.1 line 77 'UK-India: Bring into force the "
                  'Comprehensive Economic and Trade Agreement and Double Contributions Convention from 15 '
                  "July 2026', whose title names both. The line's figure covers both, so this row carries "
                  "the line's key as a measure_component (README rule 9); components are never summed with "
                  "the line's total."},
 {'page': 87,
  'pages': [87],
  'table_page': 87,
  'title': 'Steel Tariff: Change tariff rate and quotas on imported steel from 1 July 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base is the expected Customs Duty revenue from the relevant commodity codes impacted, '
           'had the measure not been implemented. The tax base has been projected across the forecast using '
           'the OBR’s forecasts for non-oil goods imports.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above.',
              'For the new steel measure, a behavioural adjustment is made to account for traders retiming '
              'or diverting their trade to avoid paying additional duty, and for a reduction in demand for '
              'imports due to the 50% tariff rate above the new quotas.',
              'The costing accounts for the interaction with the Carbon Border Adjustment Mechanism (CBAM), '
              'which comes into force on 1 January 2027, and includes a reduction in CBAM revenue resulting '
              'from the impact of the new steel measure on imports.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+85m', '+110m', '+120m', '+120m', '+120m', '+115m'],
  'table_61_line': '78',
  'measure_key': 'ab2026__steel_tariff_and_quotas',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 88,
  'pages': [88],
  'table_page': 88,
  'title': 'Stamp Taxes on Shares: Replace Stamp Duty and Stamp Duty Reserve Tax with the Securities '
           'Transfer Tax from late 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of transactions in securities currently subject to Stamp Duty or Stamp '
           'Duty Reserve Tax and is estimated using HMRC receipts and administrative data.',
           'The tax base is grown over the forecast horizon using the OBR’s forecasts for Stamp Taxes on '
           'Shares receipts.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing covers several technical changes that each have small or negligible impacts. The '
              'largest element of the costing is accounted for by the tax becoming self-assessed. This '
              'change may affect how taxpayers interact with the tax system with a corresponding impact on '
              'receipts.'],
  'uncertainty': ['The main uncertainties in this costing relate to the availability of data and assumptions '
                  'used to cost the self-assessment element.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-15m', '-30m', '-30m', '-30m', '-30m'],
  'table_61_line': '79',
  'measure_key': 'ab2026__securities_transfer_tax',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 89,
  'pages': [89],
  'table_page': 89,
  'title': 'Business Rates: Introduce 100% relief for eligible Electric Vehicle Charging Points (EVCPs) and '
           'electric vehicle-only forecourts for ten years from 1 April 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base is the estimated business rates liability of EVCPs, based on their estimated '
           'rateable value and applicable multiplier for relevant years.'],
  'costing': ['The static costing is estimated by applying the pre- and post-measure tax regimes to the tax '
              'base described above. The static cost is adjusted to reflect that business rates are '
              'deductible for Corporation Tax for companies and Income Tax for the self-employed, and that '
              'business rates are devolved to Scotland, Wales, and Northern Ireland.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size and rateable value of the tax '
                  'base, the future growth in number of eligible properties, the impacts of appeals against '
                  'property valuations on rateable values, and the impact of behavioural responses.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-15m', '-5m', '-10m', '-15m', '-15m'],
  'table_61_line': '80',
  'measure_key': 'ab2026__business_rates_ev_charging_relief',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 90,
  'pages': [90],
  'table_page': 90,
  'title': "Infected Blood Compensation Scheme: Implement the Inquiry's Additional Report recommendations "
           'from 24 July 2026',
  'base_heading': 'The cost base',
  'base': ['The cost base for this measure is the estimated number of people eligible to claim compensation '
           'through the Infected Blood Compensation Scheme and the amount of compensation awarded.'],
  'costing': ['The costing estimates the number of people who will receive additional compensation as a '
              'result of changes to the Scheme, referred to as the fourth set of regulations, the additional '
              'compensation they are expected to receive and the timings of compensation payments.',
              'While the fourth set of regulations widens eligibility and introduces new awards, these '
              'changes do not materially alter the behavioural assumptions underlying the scheme’s cost '
              'model.',
              'The costs presented here relate to the impact of the fourth regulations only, rather than the '
              'overall cost of the Infected Blood Compensation Scheme.'],
  'uncertainty': ['The main uncertainties in this costing relate to the number of eligible claimants in each '
                  'category, when they choose to apply and how they choose to receive compensation.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-360m', '-355m', '-265m', '-90m', '-75m', '+0m'],
  'table_61_line': '82',
  'measure_key': 'ab2026__infected_blood_compensation_additional_report',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "included (see note): the costing keeps the scheme's behavioural assumptions, "
                            "'While the fourth set of regulations widens eligibility and introduces new "
                            'awards, these changes do not materially alter the behavioural assumptions '
                            "underlying the scheme’s cost model.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 91,
  'pages': [91],
  'table_page': 91,
  'title': 'Student Loans: Cap interest rates for Plan 2 and Plan 3 student loans at 6% from 1 September '
           '2026 to 31 August 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base is primarily the Plan 2 and Plan 3 modified interest components of the Student '
           'Finance Modelling Unit forecast for English borrowers. That is, the interest charged on the loan '
           'portion of these parts of the student loan book as defined by ONS methodology. This is defined '
           'by both the capitalised interest accrued by borrowers and future repayments against their loan '
           'balances. The cost base assumes that Plan 2 and 3 interest rates for academic year 2026-27 are '
           'based on the RPI outturn figure of 4.1% for the 12 months to March 2026, published in April '
           '2026. In the absence of the measure, the maximum interest rate would have been 7.1%.'],
  'costing': ['The costing estimates the reduction in modified interest received on Plan 2 and 3 student '
              'loans as a result of the 6% interest rate cap for academic year 2026-27, using outputs from '
              'DfE’s Higher Education student loan outlay and repayment model.',
              'This costing assumes no behavioural response by borrowers.'],
  'uncertainty': ['The main uncertainty in this costing relates to the long-term assumptions of student loan '
                  'forecasts.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-230m', '-170m', '-10m', '-10m', '-5m', '-15m'],
  'table_61_line': '83',
  'measure_key': 'ab2026__student_loan_interest_cap_6pc_plan_2_and_3',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'This costing assumes no behavioural response by borrowers.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 92,
  'pages': [92],
  'table_page': 92,
  'title': 'Waste Crime: Fund Landfill Tax costs for six priority illegal waste site clearances until 31 '
           'March 2029',
  'base_heading': 'The cost base',
  'base': ['The cost base comprises the Landfill Tax liabilities associated with waste removed through '
           'funded clearances of illegal waste sites in the period 2026-27 to 2028-29. It is projected '
           'across the forecast period using the OBR’s RPI forecast to project future Landfill Tax rates.'],
  'costing': ['The costing is estimated using projected waste tonnages from eligible site clearances and '
              'forecast Landfill Tax rates. It assumes that the rebate expenditure is fully offset by '
              'additional Landfill Tax receipts. The Barnett formula has applied in the normal way to '
              'additional funding provided to Defra.'],
  'uncertainty': ['The main uncertainty is the volume of waste that will require landfill disposal. '
                  'Estimates may change following detailed site investigations and the start of excavation '
                  'activities.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-2m', '-2m', '-3m', '+0m', '+0m'],
  'table_61_line': '84',
  'measure_key': 'ab2026__waste_crime_landfill_tax_clearances',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Waste Crime: Fund Landfill Tax costs for six priority illegal waste site clearances until 31 '
               'March 2029',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.92-93) for Table 6.1 line 84 'Waste Crime: Fund Landfill Tax "
                  'costs for six priority illegal waste site clearances until 31 March 2029 and a three-year '
                  "pilot to fund Local Authorities' Landfill Tax liabilities arising from illegal waste site "
                  "clearances from 2027', whose title names both. The line's figure covers both, so this row "
                  "carries the line's key as a measure_component (README rule 9); components are never "
                  "summed with the line's total."},
 {'page': 93,
  'pages': [93],
  'table_page': 93,
  'title': "Waste Crime: Fund a three-year pilot to fund Local Authorities' Landfill Tax liabilities arising "
           'from illegal waste site clearances from 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base comprises the Landfill Tax liabilities associated with local authority-led '
           'clearances of illegal waste sites in the period 2027-28 to 2029-30. It is projected across the '
           'forecast period using the OBR’s RPI forecast to project future Landfill Tax rates.'],
  'costing': ['The costing is estimated using projected waste tonnages from eligible site clearances and '
              'forecast Landfill Tax rates. It assumes that the rebate expenditure is fully offset by '
              'additional Landfill Tax receipts. The Barnett formula has applied in the normal way to '
              'additional funding provided to local authorities.'],
  'uncertainty': ['The main uncertainties relate to the behavioural response to the rebate scheme and local '
                  'authorities’ ability to carry out clearances, including their ability to fund costs not '
                  'covered by the Landfill Tax rebate.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-2m', '-1m', '+0m', '+0m', '+0m'],
  'table_61_line': '84',
  'measure_key': 'ab2026__waste_crime_landfill_tax_clearances',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': "Waste Crime: Fund a three-year pilot to fund Local Authorities' Landfill Tax liabilities "
               'arising from illegal waste site clearances from 2027',
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': "One of two costing notes (pp.92-93) for Table 6.1 line 84 'Waste Crime: Fund Landfill Tax "
                  'costs for six priority illegal waste site clearances until 31 March 2029 and a three-year '
                  "pilot to fund Local Authorities' Landfill Tax liabilities arising from illegal waste site "
                  "clearances from 2027', whose title names both. The line's figure covers both, so this row "
                  "carries the line's key as a measure_component (README rule 9); components are never "
                  "summed with the line's total."},
 {'page': 94,
  'pages': [94],
  'table_page': 94,
  'title': 'Erasmus+: Enable UK participation in the Erasmus+ study scheme for 2027 from 1 January 2027',
  'base_heading': 'The cost base',
  'base': ['The cost base is the Student Finance Modelling Unit forecast for English undergraduate student '
           'loan outlay and repayments.'],
  'costing': ['The costing is the difference between the pre- and post-measure forecasts. Where an Erasmus+ '
              'placement year replaces an existing year of study, the standard loan entitlement is replaced '
              'by the lower year-abroad entitlement. Where it adds a year to the course, the year-abroad '
              'entitlement is additional.',
              'In 2027-28 and 2028-29 there are savings because the affected borrowers receive lower tuition '
              'fee loans and, for work placements, no maintenance loans. Future years include costs from '
              'Erasmus+ placement years that extend courses.',
              'This costing assumes no additional behavioural adjustment.'],
  'uncertainty': ['The main uncertainties in this costing relate to borrower behaviour and programme '
                  'utilisation.'],
  'table_label': 'Exchequer impact*',
  'table_row': 'Exchequer impact',
  'table_notes': ['*Note: This costing also includes delivery costs.'],
  'values': ['-15m', '+70m', '+45m', '-5m', '+0m', '-15m'],
  'table_61_line': '85',
  'measure_key': 'ab2026__further_priorities_nhs_and_vawg',
  'proposed_measure_key': None,
  'row_type': 'measure_component',
  'component': 'Erasmus+: Enable UK participation in the Erasmus+ study scheme for 2027 from 1 January 2027',
  'document_position': 'between the notes for Table 6.1 lines 84 (pp.92-93) and 86 (p.95)',
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'This costing assumes no additional behavioural adjustment.'",
  'static_impact': None,
  'mapping_note': 'No Table 6.1 title names Erasmus+. The document orders its costing notes by Table 6.1 '
                  "line, and this note sits between line 84's notes (pp.92-93) and line 86's (p.95), the "
                  "place of line 85 'Further Priorities: Fund key priorities, including pressures facing the "
                  "NHS and delivery of the Violence against Women and Girls Strategy'. That line's 2029-30 "
                  "to 2031-32 figures (-5, 0, -15) equal this note's, and Table 6.1's footnote 2 excludes "
                  'only two measures, neither of them Erasmus+. The line covers more than this costing, so '
                  "this row carries the line's key as a measure_component (README rule 9); components are "
                  "never summed with the line's total."},
 {'page': 95,
  'pages': [95],
  'table_page': 95,
  'title': 'Company Car Tax: Set the Benefit-in-Kind rates (appropriate percentages) for electric vehicles, '
           'hybrids and internal combustion engine vehicles for 2030-31',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of individuals who receive taxable company car benefits, estimated using '
           'HMRC company car administrative data including car volumes by fuel type, list prices and taxable '
           'value.',
           'The tax base is grown over the forecast horizon using a mix of the OBR’s Consumer Price Index '
           'and company car volumes projections.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response where some company car users switch to '
              'cheaper company cars due to differences in the relative tax treatment between alternative '
              'types of company cars.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base, and the size '
                  'of the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+0m', '+310m', '+345m'],
  'table_61_line': '86',
  'measure_key': 'ab2026__company_car_tax_rates_2030_31',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 96,
  'pages': [96],
  'table_page': 96,
  'title': 'Supported Housing: Introduce a licensing regime to enforce national standards for supported '
           'housing from 2027-28',
  'base_heading': 'The cost base',
  'base': ['The cost base consists of DWP forecasts of Housing Benefit expenditure in Great Britain, '
           'published in the Benefit Expenditure and Caseload Tables, which are adjusted to cover England '
           'only.'],
  'costing': ['The costing assumes the vast majority of licence fees paid by supported housing providers are '
              'ultimately recovered through eligible service charges met by Housing Benefit.'],
  'uncertainty': ['The main uncertainties in this costing relate to the costs incurred by local authorities '
                  'and the licence fees subsequently set; the proportion and timing of fees recovered by '
                  'providers through Housing Benefit; and the potential effect on the Housing Benefit '
                  'caseload where providers withdraw or do not obtain a licence.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-55m', '-70m', '-30m', '-30m', '-30m'],
  'table_61_line': '87',
  'measure_key': 'ab2026__supported_housing_licensing',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 97,
  'pages': [97],
  'table_page': 97,
  'title': 'Donated Medicines: Introduce a zero rate of VAT for the donation of medicines under qualifying '
           'circumstances from 23 June 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the value of donated medicines that are currently subject to VAT under '
           'the deemed supply rules. The tax base is estimated using internal HMRC administrative data.',
           'The tax base is grown over the forecast horizon using the Office for Budget Responsibility’s '
           'forecast growth in nominal GDP.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.'],
  'uncertainty': ['The main uncertainty in this costing relates to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-15m', '-20m', '-20m', '-25m', '-25m', '-25m'],
  'table_61_line': '88',
  'measure_key': 'ab2026__vat_zero_rate_donated_medicines',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 98,
  'pages': [98],
  'table_page': 98,
  'title': 'Temporary Staffing: Amend Group 7 of Schedule 9 to the VAT Act 1994 to restore the tax treatment '
           'of medical deputies to its previously intended position',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of spending on GMC registered locum doctors supplied through employment '
           'agencies and other organisations. It is estimated using market research on healthcare sector '
           'spending on agency staff, adjusted to identify spending on GMC registered locum doctors within '
           'scope.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in wages and '
           'salaries.'],
  'costing': ['The costing estimates the additional output VAT on affected supplies and the offsetting '
              'increase in input VAT recovery.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+85m', '+95m', '+100m', '+100m', '+105m'],
  'table_61_line': '89',
  'measure_key': 'ab2026__vat_medical_deputies_staffing',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 99,
  'pages': [99],
  'table_page': 99,
  'title': 'Landfill Communities Fund: Increase the Landfill Tax credit cap from 1 April 2027',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of total forecasted LfT liabilities in England and Northern Ireland. This '
           'is estimated using HMRC administrative data.',
           'The tax base is grown over the forecast horizon using the OBR’s forecasts for population growth '
           'and the Retail Prices Index (RPI), alongside inputs from the Department for Environment, Food '
           'and Rural Affairs (Defra).'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax credit caps to the tax '
              'base described above. It is adjusted to account for expected utilisation of the cap.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the extent '
                  'to which landfill site operators utilise the increased cap.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '-10m', '-15m', '-15m', '-15m', '-15m'],
  'table_61_line': '90',
  'measure_key': 'ab2026__landfill_communities_fund_credit_cap',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England and Northern Ireland',
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 100,
  'pages': [100],
  'table_page': 100,
  'title': 'Higher Education: Introduce registration requirements for franchise providers with 300 or more '
           'students from 1 September 2028, to strengthen quality and oversight of franchised provision',
  'base_heading': 'The cost base',
  'base': ['The cost base is estimated using the last agreed undergraduate student finance forecast used for '
           'DfE accounts.'],
  'costing': ['The costing is estimated by comparing the pre- and post-measure forecasts, whereby new '
              'students at franchised providers who do not successfully register will not be able to access '
              'student finance from academic year 2028-29.',
              'The costing accounts for a behavioural response whereby provision shifts away from '
              'unregistered providers, resulting in some savings before the requirement takes effect. It '
              'also accounts for some providers registering with the OfS to continue provision after '
              'September 2028, with others leaving the market from September 2028.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+30m', '+70m', '+200m', '+220m', '+200m', '+225m'],
  'table_61_line': '91',
  'measure_key': 'ab2026__franchised_higher_education_registration',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 101,
  'pages': [101],
  'table_page': 101,
  'title': 'Local Authority Spending: Impact of adjustments to high needs budget on local authority spending',
  'base_heading': None,
  'base': [],
  'costing': ['The costing is the net impact of the additional pay grant, and adjustments to reflect the TPS '
              'valuation, on high needs funding.',
              'These figures have been publicly announced. On 8 July 2026, the government published i) '
              'details of additional funding for pay which would be made available to schools and Local '
              'Authorities through the Schools Budget Support Grant 2026, and ii) the methodology for the '
              'funding adjustments in schools and other education providers to account for the fall in '
              'teachers’ pension employer contributions.',
              'There is no behavioural impact of this measure.'],
  'uncertainty': ['This is a confirmed change in planned spending on the high needs budget, so there is no '
                  'uncertainty over the figures involved.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+105m', '+140m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': '92',
  'measure_key': 'ab2026__high_needs_local_authority_spending',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'spending_measure',
  'behavioural_adjustment': "none: 'There is no behavioural impact of this measure.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 102,
  'pages': [102],
  'table_page': 102,
  'title': 'High Value Council Tax Surcharge: Confirm eligibility for deferrals, discounts and exemptions '
           'from 1 April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of properties in England valued at £2 million or more that are estimated '
           'to receive a discount, an exemption or be eligible for the deferral scheme.',
           'The tax base is estimated using a combination of commercial valuation data, Council Tax '
           'statistics, SDLT transaction data, Wealth & Asset Survey data and Valuation Office data.',
           'The tax base is grown over the forecast horizon using OBR property price forecasts.'],
  'costing': ['The costing is estimated by applying the tax regime to the pre- and post-measure tax base '
              'described above.',
              'The costing assumes a behavioural response whereby a proportion of eligible taxpayers will '
              'use the deferral scheme.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response and '
                  'household-level data availability.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-5m', '-5m', '-45m', '-45m', '-50m', '-50m'],
  'table_61_line': '93',
  'measure_key': 'ab2026__hvcts_deferrals_discounts_exemptions',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 103,
  'pages': [103],
  'table_page': 103,
  'title': 'Benefits in Kind (BiKs): Delay mandatory payrolling of company cars, vans, fuel and medical '
           'benefits from 6 April 2026 to 6 April 2027, with remaining BiKs implemented from 6 April 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of taxable Benefits in Kind subject to mandatory payrolling. It is derived '
           'from HMRC outturn and forecasts of Class 1A National Insurance contribution liabilities. '
           'Adjustments exclude benefits outside the scope of mandatory payrolling and account for benefits '
           'whose implementation is deferred until 6 April 2028.',
           'The tax base is projected over the forecast period using forecasts of Class 1A National '
           'Insurance contributions.'],
  'costing': ['The costing is estimated by delaying and then phasing implementation of mandatory payrolling '
              'for most Benefits in Kind, therefore bringing forward the timing of payment for Class 1A. '
              'There is a behavioural response whereby mandatory payrolling improves compliance through more '
              'frequent reporting and electronic capture of information.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the behavioural response, '
                  'and the total number of globally mobile employees who are exempted from this policy.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-30m', '-5m', '+0m', '+0m', '-5m', '-5m'],
  'table_61_line': '94',
  'measure_key': 'ab2026__benefits_in_kind_payrolling_delay',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 104,
  'pages': [104],
  'table_page': 104,
  'title': 'Low Value Imports: Remove the £135 customs duty relief and introduce new customs arrangements '
           'from October 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the value of low value goods imported into the UK that are currently '
           'eligible for the customs duty relief for consignments valued at £135 or less. The tax base is '
           'estimated using HMRC customs declarations data, trader and postal operator data, and compliance '
           'information on low value imports.',
           'The tax base has been projected over the forecast using the OBR’s forecast for non-oil goods '
           'imports.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby sellers pass the additional customs '
              'duty on to consumers through higher prices, reducing demand for low value imported goods, and '
              'some taxpayers altering the timing of imports in response to the measure.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and behavioural '
                  'response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+215m', '+0m', '-10m', '-15m'],
  'table_61_line': '95',
  'measure_key': 'ab2026__low_value_imports_customs_relief_removed',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 105,
  'pages': [105],
  'table_page': 105,
  'title': 'Emissions Trading Scheme (ETS): Delay the inclusion of energy from waste in the ETS',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of the greenhouse gas emissions generated by the EfW and waste '
           'incineration sector. This is estimated using the Department for Energy Security and Net Zero EfW '
           'emissions forecast, which is derived from its Dynamic Dispatch Model.'],
  'costing': ['The costing is estimated by applying the UK carbon price forecast to the emissions that would '
              'have entered the UK ETS under the previous implementation timetable, compared with the '
              'post-measure position.'],
  'uncertainty': ['The main uncertainties in this costing relate to forecast greenhouse gas emissions from '
                  'EfW and waste incineration, and future UK ETS carbon prices.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '-125m', '-490m', '-450m', '-440m'],
  'table_61_line': '96',
  'measure_key': 'ab2026__ets_energy_from_waste_delay',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "not stated (the note's costing section does not use the word 'behaviour' or "
                            "'behavioural')",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 106,
  'pages': [106],
  'table_page': 106,
  'title': 'Corporation Tax: Spread the one-off impact of revenue recognition changes for qualifying gas '
           'distribution activities over five years for accounting periods ending on or after 31 December '
           '2026',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of deferred income of affected gas distribution companies that is liable '
           'for Corporation Tax. This is estimated using Ofgem administrative data.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing does not account for a behavioural response.'],
  'uncertainty': ['The main uncertainty in this costing relates to the size of the tax base.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['-160m', '+40m', '+40m', '+40m', '+40m', '+0m'],
  'table_61_line': '97',
  'measure_key': 'ab2026__gas_distribution_revenue_recognition_spread',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': "none: 'The costing does not account for a behavioural response.'",
  'static_impact': None,
  'mapping_note': ''},
 {'page': 107,
  'pages': [107],
  'table_page': 107,
  'title': 'International Investors: Relieve double taxation for UK investors in US Limited Liability '
           'Companies and similar entities from early 2028',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of income received by UK individuals from US Limited Liability Companies '
           'and similar foreign entities that are taxed transparently overseas but treated as opaque in the '
           'UK. The tax base is estimated using HMRC Self Assessment and compliance data.',
           'The tax base is grown over the forecast horizon using the OBR’s forecast for growth in dividend '
           'receipts for households.'],
  'costing': ['The costing is estimated by applying the pre- and post-measure tax regimes to the tax base '
              'described above.',
              'The costing accounts for a behavioural response whereby the reduction in double taxation is '
              'expected to increase reporting of reverse hybrid income, encourage more overseas income to be '
              'brought into the UK, and potentially incentivise some individuals to relocate to the UK, '
              'partially offsetting the Exchequer cost of the measure.'],
  'uncertainty': ['The main uncertainties in this costing relate to the size of the tax base and the '
                  'behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '-5m', '-10m', '-5m', '-5m'],
  'table_61_line': '98',
  'measure_key': 'ab2026__us_llc_double_taxation_relief',
  'proposed_measure_key': None,
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': None,
  'impact_channel': 'tax_measure',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': ''},
 {'page': 108,
  'pages': [108],
  'table_page': 108,
  'title': "Renters' Rights: Roll out a £65 fee for the 'Register your rental property' service for private "
           'landlords and private properties in England from 15 December 2026',
  'base_heading': 'The tax base',
  'base': ['The tax base consists of private rented properties in England that are required to be registered '
           'on the ‘Register your rental property’ service. The fee is charged on a per-property basis. The '
           'current estimate is that approximately 4.9 million eligible properties are in scope.',
           'The tax base is projected over the forecast period using the estimated number of eligible '
           'properties and the profile of registrations and annual renewals. The costing reflects the phased '
           'rollout of the service and, where applicable, pro-rating of the registration fee.'],
  'costing': ['The costing is estimated by applying the £65 annual registration fee to the forecast number '
              'of eligible properties required to register, taking account of the phased implementation of '
              'the service and pro-rating where applicable. The costing assumes the £65 fee remains static.',
              'The pre-behavioural costing represents the receipts that would arise from properties in scope '
              'registering as required. This is then adjusted for the assumed registration and renewal '
              'profile to produce the forecast receipts. The key behavioural adjustment is the proportion of '
              'eligible properties expected to be registered each year.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response. The costing '
                  'makes assumptions about the rate of registration, but ultimately it will be a legal '
                  'requirement for landlords to register their properties on the service, and local '
                  'authorities can carry out enforcement action against landlords who fail to register.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': ['Note: this is offset by increased DEL spending so is fiscally neutral.'],
  'values': ['+10m', '+135m', '+190m', '+215m', '+230m', '+235m'],
  'table_61_line': None,
  'measure_key': None,
  'proposed_measure_key': 'ab2026__private_landlord_register_fee_65',
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': 'England',
  'fiscally_neutral': "yes: 'Note: this is offset by increased DEL spending so is fiscally neutral.'",
  'impact_channel': 'not_on_table_6_1',
  'behavioural_adjustment': 'included (see note)',
  'static_impact': None,
  'mapping_note': "Table 6.1 leaves this measure out. Its footnote 2 reads 'Measures with no net increase to "
                  'borrowing are not included, these are debt relief for councils in severe financial '
                  'distress through the Public Works Loan Board and a landlord registration fee for the '
                  "Private Rented Sector.'"},
 {'page': 109,
  'pages': [109],
  'table_page': 109,
  'title': 'Public Works Loan Board (PWLB) Debt Relief for Councils in Severe Financial Distress',
  'base_heading': 'The cost base',
  'base': ['As this support was agreed individually with the affected councils, there is no cost base for '
           'this measure.'],
  'costing': ['This measure is fiscally neutral, as it is being delivered entirely through a transfer '
              'between two central government bodies (MHCLG and PWLB). No payments are being made to either '
              'council as part of this measure.',
              'Furthermore, as the relevant debt is judged to be unsustainable for either council to repay '
              'on their own, it is assumed that there will be no change in behaviour from either council as '
              'a result of receiving this support.'],
  'uncertainty': ['The main uncertainties in this costing relate to the behavioural response.'],
  'table_label': 'Exchequer impact',
  'table_row': 'Exchequer impact',
  'table_notes': [],
  'values': ['+0m', '+0m', '+0m', '+0m', '+0m', '+0m'],
  'table_61_line': None,
  'measure_key': None,
  'proposed_measure_key': 'ab2026__pwlb_debt_relief_councils_severe_distress',
  'row_type': 'measure',
  'component': None,
  'document_position': None,
  'measure_scope': None,
  'fiscally_neutral': "yes: 'This measure is fiscally neutral, as it is being delivered entirely through a "
                      "transfer between two central government bodies (MHCLG and PWLB).'",
  'impact_channel': 'not_on_table_6_1',
  'behavioural_adjustment': "none: 'Furthermore, as the relevant debt is judged to be unsustainable for "
                            'either council to repay on their own, it is assumed that there will be no '
                            "change in behaviour from either council as a result of receiving this support.'",
  'static_impact': None,
  'mapping_note': "Table 6.1 leaves this measure out. Its footnote 2 reads 'Measures with no net increase to "
                  'borrowing are not included, these are debt relief for councils in severe financial '
                  'distress through the Public Works Loan Board and a landlord registration fee for the '
                  "Private Rented Sector.'"}]

TEXT_CLAIMS = [{'page': 15,
  'section': 'The cost base',
  'quote': 'There are an estimated 166,000 fathers and partners and around 750 self-employed adopters who '
           'fall into these categories.',
  'value_raw': '166,000',
  'value': '166000',
  'scale': '1',
  'normalization': 'as printed',
  'metric': 'eligible_count',
  'unit_concept': 'persons',
  'value_kind': 'point',
  'period': 2026,
  'time_basis': 'point_in_time',
  'basis': 'outturn',
  'label': 'fathers and partners in the cost base (self-employed, recently employed or unemployed, or with a '
           'broken or irregular employment pattern)',
  'conditions': {'statistic': 'fathers and partners in the cost base (self-employed, recently employed or '
                              'unemployed, or with a broken or irregular employment pattern)'},
  'note': "Present-tense estimate ('There are an estimated'); the note prints no year, so period is the "
          'publication year as a point in time. The costing scales this population with OBR employment and '
          'births forecasts and applies 89% take-up.'},
 {'page': 15,
  'section': 'The cost base',
  'quote': 'There are an estimated 166,000 fathers and partners and around 750 self-employed adopters who '
           'fall into these categories.',
  'value_raw': 'around 750',
  'value': '750',
  'scale': '1',
  'normalization': 'as printed',
  'metric': 'eligible_count',
  'unit_concept': 'persons',
  'value_kind': 'point',
  'period': 2026,
  'time_basis': 'point_in_time',
  'basis': 'outturn',
  'label': 'self-employed adopters in the cost base',
  'conditions': {'statistic': 'self-employed adopters in the cost base'},
  'note': 'Present-tense estimate; the note prints no year, so period is the publication year as a point in '
          'time.'},
 {'page': 15,
  'section': 'Costing',
  'quote': 'The costing assumes an 89% take-up rate.',
  'value_raw': '89%',
  'value': '89',
  'scale': '1',
  'normalization': 'as printed',
  'proposed_metric': 'behavioural_parameter',
  'unit_concept': 'percent',
  'value_kind': 'point',
  'fys': ['2029-30'],
  'basis': 'forecast',
  'label': 'take-up rate of the Parental Allowance',
  'conditions': {'parameter': 'take-up rate of the Parental Allowance', 'scoring_method': 'final'},
  'note': "The note gives no year for this assumption; fy is the measure's first year, as in the AB2025 "
          'family.'},
 {'page': 28,
  'section': 'Costing',
  'quote': 'It is assumed that 25% of the additional income above the baseline is placed into MSAs’ '
           'reserves.',
  'value_raw': '25%',
  'value': '25',
  'scale': '1',
  'normalization': 'as printed',
  'proposed_metric': 'behavioural_parameter',
  'unit_concept': 'percent',
  'value_kind': 'point',
  'fys': ['2027-28'],
  'basis': 'forecast',
  'label': "share of additional retained income placed into Mayoral Strategic Authorities' reserves",
  'conditions': {'parameter': 'share of additional retained income placed into Mayoral Strategic '
                              "Authorities' reserves",
                 'scoring_method': 'final'},
  'note': "The note gives no year for this assumption; fy is the measure's first year, as in the AB2025 "
          'family.'},
 {'page': 33,
  'section': 'Costing',
  'quote': 'The programme is expected to be a net cost to both public sector net debt (PSND) (approx. £386m) '
           'and public sector net financial liabilities (PSNFL) (approx. £375m) over the period to 2031-32.',
  'value_raw': 'approx. £386m',
  'value': '-386',
  'scale': '1000000',
  'normalization': "GBP m x 1e6 -> GBP; sign from the wording ('a net cost to ... public sector net debt "
                   "(PSND)' -> negative)",
  'proposed_metric': 'psnd_impact',
  'unit_concept': 'gbp',
  'value_kind': 'cumulative',
  'period': 2032,
  'time_basis': 'fiscal_year',
  'basis': 'forecast',
  'label': 'net cost to public sector net debt (PSND) over the period to 2031-32',
  'conditions': {'statistic': 'net cost to public sector net debt (PSND) over the period to 2031-32',
                 'horizon': 'the period to 2031-32 (cumulative)',
                 'sign_convention': 'positive = lower PSND (an improvement, as a + Exchequer impact is a '
                                    'yield); negative = higher PSND (a cost). The printed figure is '
                                    "unsigned; the sign comes from the note's wording: 'a net cost to ... "
                                    "public sector net debt (PSND)' -> negative"},
  'note': 'The Exchequer impact table (PSNB) prints +0m in every year; the note says the portfolio becomes '
          'net-income generating beyond 2031-32.'},
 {'page': 33,
  'section': 'Costing',
  'quote': 'The programme is expected to be a net cost to both public sector net debt (PSND) (approx. £386m) '
           'and public sector net financial liabilities (PSNFL) (approx. £375m) over the period to 2031-32.',
  'value_raw': 'approx. £375m',
  'value': '-375',
  'scale': '1000000',
  'normalization': "GBP m x 1e6 -> GBP; sign from the wording ('a net cost to ... public sector net "
                   "financial liabilities (PSNFL)' -> negative)",
  'proposed_metric': 'psnfl_impact',
  'unit_concept': 'gbp',
  'value_kind': 'cumulative',
  'period': 2032,
  'time_basis': 'fiscal_year',
  'basis': 'forecast',
  'label': 'net cost to public sector net financial liabilities (PSNFL) over the period to 2031-32',
  'conditions': {'statistic': 'net cost to public sector net financial liabilities (PSNFL) over the period '
                              'to 2031-32',
                 'horizon': 'the period to 2031-32 (cumulative)',
                 'sign_convention': 'positive = lower PSNFL (an improvement, as a + Exchequer impact is a '
                                    'yield); negative = higher PSNFL (a cost). The printed figure is '
                                    "unsigned; the sign comes from the note's wording: 'a net cost to ... "
                                    "public sector net financial liabilities (PSNFL)' -> negative"},
  'note': ''},
 {'page': 34,
  'section': 'Costing',
  'quote': 'Public sector net debt (PSND) impact includes the cost and income generated above, as well as '
           'the net capital cost and return of the investment and lending expected. Over the period until '
           '2031-32, this is anticipated to be a cost of approximately £775m, with the portfolio expected to '
           'be profit generating for the Exchequer over its lifetime.',
  'value_raw': 'approximately £775m',
  'value': '-775',
  'scale': '1000000',
  'normalization': "GBP m x 1e6 -> GBP; sign from the wording ('a cost of' -> negative)",
  'proposed_metric': 'psnd_impact',
  'unit_concept': 'gbp',
  'value_kind': 'cumulative',
  'period': 2032,
  'time_basis': 'fiscal_year',
  'basis': 'forecast',
  'label': 'cost to public sector net debt (PSND) over the period until 2031-32',
  'conditions': {'statistic': 'cost to public sector net debt (PSND) over the period until 2031-32',
                 'horizon': 'the period to 2031-32 (cumulative)',
                 'sign_convention': 'positive = lower PSND (an improvement, as a + Exchequer impact is a '
                                    'yield); negative = higher PSND (a cost). The printed figure is '
                                    "unsigned; the sign comes from the note's wording: 'a cost of' -> "
                                    'negative'},
  'note': ''},
 {'page': 34,
  'section': 'Costing',
  'quote': 'Public sector net financial liabilities (PSNFL) also includes expected movements in the fair '
           'value of the portfolio. This is expected to add an additional cost of £68m in the period to '
           '2031-32 as the value of the portfolio matures.',
  'value_raw': '£68m',
  'value': '-68',
  'scale': '1000000',
  'normalization': "GBP m x 1e6 -> GBP; sign from the wording ('add an additional cost of' -> negative)",
  'proposed_metric': 'psnfl_fair_value_impact',
  'unit_concept': 'gbp',
  'value_kind': 'cumulative',
  'period': 2032,
  'time_basis': 'fiscal_year',
  'basis': 'forecast',
  'label': 'additional PSNFL cost from expected fair-value movements of the portfolio, on top of the PSND '
           'cost',
  'conditions': {'statistic': 'additional PSNFL cost from expected fair-value movements of the portfolio, on '
                              'top of the PSND cost',
                 'horizon': 'the period to 2031-32 (cumulative)',
                 'sign_convention': 'positive = lower PSNFL (an improvement, as a + Exchequer impact is a '
                                    'yield); negative = higher PSNFL (a cost). The printed figure is '
                                    "unsigned; the sign comes from the note's wording: 'add an additional "
                                    "cost of' -> negative"},
  'note': 'The £68m is the fair-value increment to PSNFL beyond the PSND cost, not the PSNFL total; the note '
          'prints no total PSNFL figure.'},
 {'page': 41,
  'section': 'Costing',
  'quote': 'There is also an impact on public sector net debt (PSND) which includes the cost and income '
           'generated above, as well as the net capital cost and return of the investment and lending '
           'expected. Over the period until 2031-32, this is anticipated to be a cost of approximately £32m, '
           'with the portfolio expected to be profit generating for the Exchequer over its lifetime.',
  'value_raw': 'approximately £32m',
  'value': '-32',
  'scale': '1000000',
  'normalization': "GBP m x 1e6 -> GBP; sign from the wording ('a cost of' -> negative)",
  'proposed_metric': 'psnd_impact',
  'unit_concept': 'gbp',
  'value_kind': 'cumulative',
  'period': 2032,
  'time_basis': 'fiscal_year',
  'basis': 'forecast',
  'label': 'cost to public sector net debt (PSND) over the period until 2031-32',
  'conditions': {'statistic': 'cost to public sector net debt (PSND) over the period until 2031-32',
                 'horizon': 'the period to 2031-32 (cumulative)',
                 'sign_convention': 'positive = lower PSND (an improvement, as a + Exchequer impact is a '
                                    'yield); negative = higher PSND (a cost). The printed figure is '
                                    "unsigned; the sign comes from the note's wording: 'a cost of' -> "
                                    'negative'},
  'note': ''},
 {'page': 41,
  'section': 'Costing',
  'quote': 'There is an additional impact on public sector net financial liabilities (PSNFL) due to expected '
           'movements in the fair value of the portfolio. This is to be net income generating as the value '
           'of the portfolio increases by approximately £86m (total PSNFL benefit of £54m).',
  'value_raw': 'approximately £86m',
  'value': '86',
  'scale': '1000000',
  'normalization': "GBP m x 1e6 -> GBP; sign from the wording ('the value of the portfolio increases by', "
                   'which lowers PSNFL -> positive)',
  'proposed_metric': 'psnfl_fair_value_impact',
  'unit_concept': 'gbp',
  'value_kind': 'cumulative',
  'period': 2032,
  'time_basis': 'fiscal_year',
  'basis': 'forecast',
  'label': "increase in the portfolio's fair value (the PSNFL component beyond PSND)",
  'conditions': {'statistic': "increase in the portfolio's fair value (the PSNFL component beyond PSND)",
                 'horizon': 'the period to 2031-32 (cumulative)',
                 'sign_convention': 'positive = lower PSNFL (an improvement, as a + Exchequer impact is a '
                                    'yield); negative = higher PSNFL (a cost). The printed figure is '
                                    "unsigned; the sign comes from the note's wording: 'the value of the "
                                    "portfolio increases by', which lowers PSNFL -> positive"},
  'note': "The £86m is the fair-value increment, not the PSNFL total. The note's figures agree: the £86m "
          "gain less the £32m PSND cost gives the £54m PSNFL benefit (a reader's check, not a staged row)."},
 {'page': 41,
  'section': 'Costing',
  'quote': 'There is an additional impact on public sector net financial liabilities (PSNFL) due to expected '
           'movements in the fair value of the portfolio. This is to be net income generating as the value '
           'of the portfolio increases by approximately £86m (total PSNFL benefit of £54m).',
  'value_raw': '£54m',
  'value': '54',
  'scale': '1000000',
  'normalization': "GBP m x 1e6 -> GBP; sign from the wording ('total PSNFL benefit' -> positive)",
  'proposed_metric': 'psnfl_impact',
  'unit_concept': 'gbp',
  'value_kind': 'cumulative',
  'period': 2032,
  'time_basis': 'fiscal_year',
  'basis': 'forecast',
  'label': 'total benefit to public sector net financial liabilities (PSNFL)',
  'conditions': {'statistic': 'total benefit to public sector net financial liabilities (PSNFL)',
                 'horizon': 'the period to 2031-32 (cumulative)',
                 'sign_convention': 'positive = lower PSNFL (an improvement, as a + Exchequer impact is a '
                                    'yield); negative = higher PSNFL (a cost). The printed figure is '
                                    "unsigned; the sign comes from the note's wording: 'total PSNFL benefit' "
                                    '-> positive'},
  'note': ''},
 {'page': 50,
  'section': 'The tax base',
  'quote': 'The UK tax gap in 2024 to 2025 is estimated to be 6.4% of total theoretical tax liabilities, or '
           '£59.2 billion in absolute terms.',
  'value_raw': '6.4%',
  'value': '6.4',
  'scale': '1',
  'normalization': 'as printed',
  'proposed_metric': 'tax_gap',
  'unit_concept': 'percent',
  'value_kind': 'point',
  'fys': ['2024-25'],
  'basis': 'outturn',
  'attribution': 'restated',
  'benchmark_class': 'administrative_fact',
  'source_model': 'administrative_data',
  'label': 'UK tax gap as a share of total theoretical tax liabilities',
  'conditions': {'statistic': 'UK tax gap as a share of total theoretical tax liabilities'},
  'note': "HMRC's tax gap estimate for 2024 to 2025, printed in the note's tax base section as the base's "
          "starting point: 'The tax base for this costing is the total tax gap less the additional tax "
          "revenues accounted for by previously announced Closing the Tax Gap (CTG) initiatives.' Staged as "
          'a tax-base input of the measure (README rule 8) and attributed restated, as uk_rf_ab2025 staged '
          'its tax_gap rows; the note does not cite the HMRC publication.'},
 {'page': 50,
  'section': 'The tax base',
  'quote': 'The UK tax gap in 2024 to 2025 is estimated to be 6.4% of total theoretical tax liabilities, or '
           '£59.2 billion in absolute terms.',
  'value_raw': '£59.2 billion',
  'value': '59.2',
  'scale': '1000000000',
  'normalization': 'GBP bn x 1e9 -> GBP',
  'proposed_metric': 'tax_gap',
  'unit_concept': 'gbp',
  'value_kind': 'point',
  'fys': ['2024-25'],
  'basis': 'outturn',
  'attribution': 'restated',
  'benchmark_class': 'administrative_fact',
  'source_model': 'administrative_data',
  'label': 'UK tax gap, absolute',
  'conditions': {'statistic': 'UK tax gap, absolute'},
  'note': "HMRC's tax gap estimate for 2024 to 2025, printed in the note's tax base section as the base's "
          "starting point: 'The tax base for this costing is the total tax gap less the additional tax "
          "revenues accounted for by previously announced Closing the Tax Gap (CTG) initiatives.' Staged as "
          'a tax-base input of the measure (README rule 8) and attributed restated, as uk_rf_ab2025 staged '
          'its tax_gap rows; the note does not cite the HMRC publication.'},
 {'page': 58,
  'section': 'Costing',
  'quote': 'The costing is accounted as a financial transaction, with an impact of +£130m estimated in '
           '2029-30 in cash terms, but the funding of the measure is accounted as public expenditure, with '
           'an impact of -£35m in 2029-30 in expenditure terms.',
  'value_raw': '+£130m',
  'value': '130',
  'scale': '1000000',
  'normalization': 'GBP m x 1e6 -> GBP',
  'proposed_metric': 'financial_transaction_cash_impact',
  'unit_concept': 'gbp',
  'value_kind': 'point',
  'fys': ['2029-30'],
  'basis': 'forecast',
  'label': 'financial transaction impact in cash terms',
  'conditions': {'statistic': 'financial transaction impact in cash terms',
                 'sign_convention': 'as printed (positive = cash inflow to the public sector, as in Table '
                                    '6.2)'},
  'note': "Proposal spelling as in uk_hmt_tables (Table 6.2). The same sentence's -£35m in 2029-30 'in "
          "expenditure terms' equals the Exchequer impact table's 2029-30 cell and is not staged twice."},
 {'page': 67,
  'section': 'Costing',
  'quote': 'An elasticity of -0.95 is used, with 25% of the reduction in stakes then assumed to substitute '
           'to Remote Gaming Duty.',
  'value_raw': '-0.95',
  'value': '-0.95',
  'scale': '1',
  'normalization': 'as printed',
  'proposed_metric': 'behavioural_parameter',
  'proposed_unit': 'elasticity',
  'value_kind': 'point',
  'fys': ['2027-28'],
  'basis': 'forecast',
  'label': 'elasticity of machine gambling demand to the duty rise passed on through a lower Return to '
           'Player',
  'conditions': {'parameter': 'elasticity of machine gambling demand to the duty rise passed on through a '
                              'lower Return to Player',
                 'scoring_method': 'final'},
  'note': "The note gives no year for this assumption; fy is the measure's first year, as in the AB2025 "
          'family.'},
 {'page': 67,
  'section': 'Costing',
  'quote': 'An elasticity of -0.95 is used, with 25% of the reduction in stakes then assumed to substitute '
           'to Remote Gaming Duty.',
  'value_raw': '25%',
  'value': '25',
  'scale': '1',
  'normalization': 'as printed',
  'proposed_metric': 'behavioural_parameter',
  'unit_concept': 'percent',
  'value_kind': 'point',
  'fys': ['2027-28'],
  'basis': 'forecast',
  'label': 'share of the reduction in stakes that substitutes to Remote Gaming Duty',
  'conditions': {'parameter': 'share of the reduction in stakes that substitutes to Remote Gaming Duty',
                 'scoring_method': 'final'},
  'note': "The note gives no year for this assumption; fy is the measure's first year, as in the AB2025 "
          'family.'},
 {'page': 84,
  'section': 'Costing',
  'quote': 'Borrowing is estimated as £20 million of additional capital borrowing annually from 2028-29 to '
           '2031-32, plus interest and minimum revenue provision; none is assumed without the zone.',
  'value_raw': '£20 million',
  'value': '20',
  'scale': '1000000',
  'normalization': 'GBP m x 1e6 -> GBP',
  'proposed_metric': 'behavioural_parameter',
  'unit_concept': 'gbp',
  'value_kind': 'point',
  'fys': ['2028-29', '2029-30', '2030-31', '2031-32'],
  'basis': 'forecast',
  'label': "additional capital borrowing assumed to be facilitated by the zone's retained business rates "
           '(before interest and minimum revenue provision)',
  'conditions': {'parameter': "additional capital borrowing assumed to be facilitated by the zone's retained "
                              'business rates (before interest and minimum revenue provision)',
                 'scoring_method': 'final'},
  'note': "A costing assumption ('Additional business rates income is assumed to facilitate borrowing "
          "against future revenue'); GBP behavioural_parameter as in uk_obr_tables. The sentence gives one "
          'figure for each year it names; one row per year.'},
 {'page': 108,
  'section': 'The tax base',
  'quote': 'The current estimate is that approximately 4.9 million eligible properties are in scope.',
  'value_raw': 'approximately 4.9 million',
  'value': '4.9',
  'scale': '1000000',
  'normalization': 'million x 1e6 -> properties',
  'proposed_metric': 'tax_base',
  'unit_concept': 'properties',
  'value_kind': 'point',
  'period': 2026,
  'time_basis': 'point_in_time',
  'basis': 'outturn',
  'label': 'eligible private rented properties in England in scope of the register',
  'conditions': {'statistic': 'eligible private rented properties in England in scope of the register'},
  'note': "'The current estimate'; the note prints no year, so period is the publication year as a point in "
          'time.'}]


def number(s):
    """A Decimal as an int when whole, else a float."""
    return int(s) if s == s.to_integral_value() else float(s)


def fy_period(fy):
    return int(fy[:4]) + 1


def mapping_conditions(n):
    c = {}
    for k in (
        "row_type",
        "component",
        "table_61_line",
        "proposed_measure_key",
        "document_position",
        "measure_scope",
        "fiscally_neutral",
    ):
        if n.get(k):
            c[k] = n[k]
    return c


def costing_rows(n):
    header = "Exchequer impact (£m) | " + " ".join(FYS) + " | "
    quote = header + n["table_label"] + " " + " ".join(n["values"])
    for fn in n["table_notes"]:
        quote += " | " + fn
    note = " || ".join(
        x
        for x in (
            n["mapping_note"],
            " ".join(n["base"]),
            " ".join(n["costing"]),
            "Areas of uncertainty: " + " ".join(n["uncertainty"]),
        )
        if x
    )
    for fy, raw in zip(FYS, n["values"]):
        c = {
            "basis": "forecast",
            "fiscal_event": "autumn_budget_2026",
            "fy": fy,
            "geography": "UK",
            "scoring_method": "final",
            "sign_convention": SIGN,
            "behavioural_adjustment": n["behavioural_adjustment"],
            "costing_leg_heading": "Exchequer impact (£m)",
            "impact_channel": n["impact_channel"],
            "national_accounts_basis": NATIONAL_ACCOUNTS,
            "table_row": n["table_row"],
        }
        if n.get("static_impact"):
            c["static_impact"] = n["static_impact"]
        if n["table_notes"]:
            c["table_footnote"] = " ".join(n["table_notes"])
        c.update(mapping_conditions(n))
        yield {
            **COMMON,
            "metric": "revenue_change",
            "proposed_metric": None,
            "unit_concept": "gbp",
            "proposed_unit": None,
            "value": number(Decimal(raw.replace(",", "").rstrip("m")) * 1_000_000),
            "value_raw": raw,
            "normalization": NORMALIZATION,
            "value_kind": "point",
            "period": fy_period(fy),
            "time_basis": "fiscal_year",
            "conditions": c,
            "reform_hint": n["title"],
            "measure_key": n["measure_key"],
            "attribution": "own",
            "benchmark_class": "different_model",
            "publication": {**PUBLICATION, "locator": f"p.{n['table_page']} (Exchequer impact (£m))"},
            "source_table": "Exchequer impact (£m) — " + n["title"],
            "source_column": fy,
            "quote": quote,
            "note": note,
            "parse_confidence": "high",
        }


def text_rows(t, n):
    """A context row (the tax gap) scores no measure: null key and reform_hint,
    no mapping conditions (README rule 3 of the AB2025 harvest)."""
    context = t.get("context", False)
    fys = t.get("fys") or [None]
    for fy in fys:
        c = {"basis": t["basis"], "fiscal_event": "autumn_budget_2026", "geography": "UK"}
        if fy:
            c["fy"] = fy
            period, time_basis = fy_period(fy), "fiscal_year"
        else:
            period, time_basis = t["period"], t["time_basis"]
        c.update(t["conditions"])
        if not context:
            c.update(mapping_conditions(n))
        value = number(Decimal(t["value"]) * Decimal(t["scale"]))
        yield {
            **COMMON,
            "source_model": t.get("source_model", COMMON["source_model"]),
            "metric": t.get("metric"),
            "proposed_metric": t.get("proposed_metric"),
            "unit_concept": t.get("unit_concept"),
            "proposed_unit": t.get("proposed_unit"),
            "value": value,
            "value_raw": t["value_raw"],
            "normalization": t["normalization"],
            "value_kind": t["value_kind"],
            "period": period,
            "time_basis": time_basis,
            "conditions": c,
            "reform_hint": None if context else n["title"],
            "measure_key": None if context else n["measure_key"],
            "attribution": t.get("attribution", "own"),
            "benchmark_class": t.get("benchmark_class", "different_model"),
            "publication": {**PUBLICATION, "locator": f"p.{t['page']} ({t['section']})"},
            "source_table": "Costing text — " + n["title"],
            "source_column": t["label"],
            "quote": t["quote"],
            "note": t["note"],
            "parse_confidence": "high",
        }


def build():
    by_page = {n["page"]: n for n in COSTINGS}
    texts = {}
    for t in TEXT_CLAIMS:
        texts.setdefault(t["page"], []).append(t)
    rows = []
    # reading order: each note's table first if it precedes the text on the page
    # would interleave sections; instead, per note: text claims in page order, then
    # the Exchequer table, which every note prints after its base and costing text.
    for n in COSTINGS:
        for t in texts.pop(n["page"], []):
            rows.extend(text_rows(t, n))
        rows.extend(costing_rows(n))
    assert not texts, texts
    assert len({n["page"] for n in COSTINGS}) == len(COSTINGS) == len(by_page)
    return rows


def gzip_bytes(rows):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in rows:
            gz.write((json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    return buf.getvalue()


def squash(s):
    return re.sub(r"\s+", " ", s.replace("•", " ")).strip()


def page_texts(pdf):
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout.split("\f")
    pages = {}
    for i, p in enumerate(text):
        out = ""
        lines = [x.strip() for x in p.split("\n") if x.strip()]
        if lines and lines[-1] == str(i + 1):
            lines.pop()  # the page-number footer
        for ln in lines:
            # the joining rule the prose in COSTINGS uses: a line-end hyphen is a
            # real hyphen, except a suspended one such as "18- to"
            if out.endswith("-") and not out.endswith(" -") and not re.match(r"(to|and|or) ", ln):
                out += ln
            else:
                out += (" " if out else "") + ln
        pages[i + 1] = squash(out)
    return pages


def value_matches_raw(r):
    """A text row's value is value_raw's number times the scale its
    normalization names, with the sign value_raw prints or, for an unsigned
    figure, the sign the normalization takes from the wording."""
    digits = re.search(r"[\d,]+(?:\.\d+)?", r["value_raw"]).group(0).replace(",", "")
    norm = r["normalization"]
    if "x 1e9" in norm:
        scale = Decimal(1_000_000_000)
    elif "x 1e6" in norm:
        scale = Decimal(1_000_000)
    else:
        scale = Decimal(1)
    if "-> negative" in norm or re.match(r"[-]", r["value_raw"]):
        sign = -1
    else:
        sign = 1
    return Decimal(str(r["value"])) == sign * Decimal(digits) * scale


def verify(pdf):
    rows = build()
    problems = []
    if OUT.read_bytes() != gzip_bytes(rows):
        problems.append("claims_staged.jsonl.gz differs from a fresh build")
    if hashlib.sha256(Path(pdf).read_bytes()).hexdigest() != PUBLICATION["primary_sha256"]:
        problems.append("the PDF's sha256 differs from the pinned primary")
    pages = page_texts(pdf)
    first_page = {n["title"]: n["page"] for n in COSTINGS}
    assert len(first_page) == len(COSTINGS)
    value = re.compile(r"[+-][\d,]+m$")
    for i, r in enumerate(rows):
        page = int(re.match(r"p\.(\d+)", r["publication"]["locator"]).group(1))
        body = pages[page]
        bad = []
        if r["source_table"].startswith("Exchequer impact"):
            heading, years, cells, *footnotes = r["quote"].split(" | ")
            vals = [x for x in cells.split() if value.match(x)]
            label = [x for x in cells.split() if not value.match(x)]
            if heading != "Exchequer impact (£m)" or heading not in body:
                bad.append("heading")
            if years.split() != FYS or years not in body:
                bad.append("years")
            if len(vals) != 6 or " ".join(vals) not in " ".join(re.findall(r"[+-][\d,]+m", body)):
                bad.append("six values")
            if vals[FYS.index(r["source_column"])] != r["value_raw"]:
                bad.append("column")
            # the label is everything between the year header and the next section
            # once the page's value tokens and all spaces are dropped: p.96 prints
            # "Exchequ er impact", p.82 prints its values inside "Exchequer impact
            # [AME ... savings only]"
            bare = re.sub(r"\s+", "", re.sub(r"[+-][\d,]+m", "", body))
            after = bare.split("".join(FYS), 1)[-1]
            printed = re.split(r"Areasofuncertainty|\*?Note:", after, maxsplit=1)[0]
            if "".join(label) != printed:
                bad.append("label")
            if not all(squash(f) in body for f in footnotes):
                bad.append("footnote")
        else:
            if squash(r["quote"]) not in body or r["value_raw"] not in r["quote"]:
                bad.append("quote")
            if not value_matches_raw(r):
                bad.append("value against value_raw")
        if r["reform_hint"] is not None:
            if squash(r["reform_hint"]) not in pages[first_page[r["reform_hint"]]]:
                bad.append("title")
        elif r["measure_key"] is not None or r["conditions"].get("proposed_measure_key"):
            bad.append("a keyed row needs its title")
        if bad:
            problems.append(f"row {i} {r['publication']['locator']} {r['value_raw']}: {', '.join(bad)}")
    for p in problems:
        print("PROBLEM", p)
    print(f"verify: {len(rows)} rows, {len(problems)} problems")
    return not problems


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--verify":
        sys.exit(0 if verify(sys.argv[2]) else 1)
    rows = build()
    data = gzip_bytes(rows)
    OUT.write_bytes(data)
    print(f"{len(rows)} rows, sha256 {hashlib.sha256(data).hexdigest()}")
