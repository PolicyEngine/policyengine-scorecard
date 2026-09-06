const SOURCE_SPECIAL: Record<string, string> = {
  jct: "JCT",
  cbo: "CBO",
  irs: "IRS",
  irs_soi: "IRS SOI",
  census: "Census",
  census_pep: "Census PEP",
  treasury: "Treasury",
  tpc: "TPC",
  pwbm: "PWBM",
  cpsp: "Columbia CPSP",
  budget_lab: "Budget Lab",
  tax_foundation: "Tax Foundation",
  obr: "OBR",
  hmrc: "HMRC",
  uk_hmrc: "HMRC",
  dwp: "DWP",
  dwp_takeup: "DWP take-up",
  dwp_hbai: "DWP HBAI",
  hmt: "HMT",
  hm_treasury: "HM Treasury",
  ifs: "IFS",
  rf: "Resolution Foundation",
  resolution_foundation: "Resolution Foundation",
  ukmod: "UKMOD",
  jrc_euromod: "JRC EUROMOD",
  spf_finances: "SPF Finances",
  cour_des_comptes: "Cour des comptes",
  nz_treasury: "New Zealand Treasury",
  policyengine: "PolicyEngine",
};

export function sourceLabel(s: string): string {
  if (SOURCE_SPECIAL[s]) return SOURCE_SPECIAL[s];
  const m = s.match(/^([a-z]{2})_(admin|fiscal_note)$/);
  if (m) return `${m[1].toUpperCase()} ${m[2].replace("_", " ")}`;
  return s;
}
