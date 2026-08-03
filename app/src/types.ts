export type Status =
  | "comparable"
  | "constructed"
  | "concept_mismatch"
  | "pe_gap"
  | "not_computed"
  | "suppressed";

export type CalibrationRelationship =
  | "consumed_as_target"
  | "seed_source"
  | "held_out";

/** Divergence bin for a row with both values — descriptive, never pass/fail. */
export type Closeness = "close" | "moderate" | "far";

export interface Lane {
  id: string;
  source: string;
  area: string;
  mode: number;
  stage: string;
  running: boolean;
  updated: string;
  note: string;
}

export interface LanesFeed {
  updated: string;
  lanes: Lane[];
}

export interface Diagnosis {
  class: string;
  /** Register gate (issue #9): verdict language only when a known issue is
   * cited via action_link. False → present as a descriptive explanation. */
  normative: boolean;
  title?: string;
  confidence?: string;
  fix_type?: string;
  rationale?: string;
  action_link?: string;
}

export interface Publication {
  title?: string;
  url?: string;
  page_url?: string;
  date?: string;
  vintage?: string;
  [key: string]: unknown;
}

/** One external claim × latest PE result, hydrated (defaults merged,
 * annotation sets expanded, source id injected). */
export interface Row {
  id: string;
  source: string;
  metric: string;
  unit: string;
  period: number;
  period_start?: number;
  period_end?: number;
  time_basis: string;
  geography: string;
  value_kind: string;
  relationship: CalibrationRelationship;
  pub: number;
  status: Status;
  conditions?: Record<string, string>;
  value?: number; // absent on suppressed rows
  program?: string;
  subgroup?: string;
  variant?: string;
  policy?: string;
  baseline?: string;
  source_column?: string;
  provenance?: Record<string, string>;
  pe?: { value: number; construction?: string };
  pe_2026?: number;
  delta?: number;
  ratio?: number;
  diagnosis?: Diagnosis;
  annotations?: string[];
}

export interface Annotation {
  id: string;
  severity: string;
  text: string;
  basis: string;
}

export interface SourceMeta {
  name: string;
  org?: string | null;
  model?: string | null;
  method?: string | null;
  url?: string | null;
  fetched?: string | null;
  period?: string;
  diagnosis_upstream?: string;
  harvest_dir?: string;
  auto?: boolean;
}

export interface SourceSummary {
  claims: number;
  ok: number;
  suppressed: number;
  by_status: Partial<Record<Status, number>>;
  relationships: Partial<Record<CalibrationRelationship, number>>;
  agreement_bins: Partial<Record<Closeness, number>>;
  held_out_compared: number;
  material_divergences: number;
  explained: number;
  period_min: number;
  period_max: number;
  models: string[];
}

export interface FacetEntry {
  value: string | number;
  n: number;
}

export interface SourceSlice {
  built: string;
  id: string;
  meta: SourceMeta;
  summary: SourceSummary;
  relationship_notes: Record<string, string>;
  facets: Record<string, FacetEntry[]>;
  pubs: Publication[];
  rows: Row[];
  annotations?: Record<string, Annotation>;
  pe_runs?: Record<string, { flags_set_true: string[] }>;
  pe_provenance?: {
    engine_version?: string;
    data_bundle?: string;
    runtime_dataset?: string;
    period?: string;
  };
}

export interface IndexSource extends SourceSummary {
  id: string;
  name: string;
  org?: string | null;
  model?: string | null;
  url?: string | null;
  fetched?: string | null;
  auto: boolean;
  computed: number;
  metrics_top: FacetEntry[];
  n_policies: number;
  n_baselines: number;
  n_geographies: number;
}

export interface Tiles {
  coverage: { ok: number; computed: number; sources: number };
  agreement: {
    held_out_compared: number;
    bins: Partial<Record<Closeness, number>>;
    excluded_labeled: Partial<Record<CalibrationRelationship, number>>;
  };
  explained: {
    material: number;
    explained: number;
    explanations_published: number;
  };
  random_strand: {
    seed: number;
    drawn: number;
    by_status: Partial<Record<Status, number>>;
    by_source: Record<string, number>;
    by_relationship: Partial<Record<CalibrationRelationship, number>>;
  };
}

export interface ExplanationEntry extends Diagnosis {
  source: string;
  claim_id: string;
  program?: string | null;
  metric: string;
  geography: string;
  subgroup?: string | null;
  period: number;
}

export interface ScorecardIndex {
  built: string;
  pe_bundle: Record<string, string | undefined>;
  catalog: {
    sources: number;
    claims: number;
    ok: number;
    suppressed: number;
    computed: number;
    by_status: Partial<Record<Status, number>>;
  };
  tiles: Tiles;
  sources: IndexSource[];
  explanations?: ExplanationEntry[];
}

export const RELATIONSHIP_LABELS: Record<CalibrationRelationship, string> = {
  consumed_as_target: "target consumed",
  seed_source: "seed source",
  held_out: "held out",
};

export const PROGRAM_LABELS: Record<string, string> = {
  snap: "SNAP",
  ssi: "SSI",
  tanf: "TANF",
  wic: "WIC",
  ccdf: "CCDF child care",
  housing: "Housing assistance",
  liheap: "LIHEAP",
  eitc: "EITC",
  ctc_refund: "Refundable CTC",
  spm_poverty: "SPM poverty",
  medicaid: "Medicaid",
  chip: "CHIP",
  unemployment_compensation: "Unemployment compensation",
  social_security_oasi: "Social Security OASI",
  social_security_di: "Social Security DI",
  eitc_ctc_other_credits: "EITC, CTC + other credits",
  aca_premium_tax_credits_and_related: "ACA premium tax credits",
  family_support_foster_care: "Family support + foster care",
  child_nutrition: "Child nutrition",
};

export const METRIC_LABELS: Record<string, string> = {
  eligible_count: "Eligible",
  eligibility_rate: "Eligibility rate",
  participation_rate: "Participation rate",
  participation_gap_count: "Participation gap",
  participant_count: "Participants",
  poverty_rate: "Poverty rate",
  poverty_rate_change: "Poverty rate change",
  poverty_count_change: "Poverty count change",
  poverty_count: "People in poverty",
  revenue_change: "Revenue change",
  benefit_cost: "Benefit cost",
  enrollment: "Enrollment",
  caseload: "Caseload",
  pct_change_after_tax_income: "% change, after-tax income",
  avg_tax_change_usd: "Avg tax change ($)",
  avg_change_after_tax_income_usd: "Avg after-tax income change ($)",
  share_with_tax_cut: "Share with a tax cut",
  primary_deficit_change: "Primary deficit change",
  income_aggregate: "Income aggregate",
  deduction_aggregate: "Deduction aggregate",
  tax_liability: "Tax liability",
  return_count: "Returns",
  tax_credits_applied: "Tax credits applied",
  average_monthly_benefit: "Avg monthly benefit",
  maximum_monthly_benefit: "Max monthly benefit",
  average_weekly_benefit: "Avg weekly benefit",
  first_payment_count: "First payments",
  tax_expenditure: "Tax expenditure",
};

export const STATUS_LABELS: Record<Status, string> = {
  comparable: "Comparable",
  constructed: "Constructed",
  concept_mismatch: "Concept mismatch",
  pe_gap: "Out of model",
  not_computed: "Not yet computed",
  suppressed: "Suppressed by source",
};

export const POLICY_LABELS: Record<string, string> = {
  full_participation: "full participation",
  pe_parametric_reform: "parametric reform",
  obbba_enacted_title_vii: "OBBBA enacted — Title VII",
  obbba_enacted_pl119_21: "OBBBA enacted (PL 119-21)",
  obbba_house_passed_tax_provisions: "OBBBA House-passed tax provisions",
  obbba_house_wm_reported_202505: "OBBBA House W&M reported (May 2025)",
  obbba_house_wm_markup_20250513: "OBBBA House W&M markup (May 13 2025)",
  obbba_senate_finance_substitute: "OBBBA Senate Finance substitute",
  obbba_senate_managers_20250628: "OBBBA Senate managers (Jun 28 2025)",
  obbba_provision_standalone: "OBBBA provision, standalone",
  obbba_house_proposals_202505: "OBBBA House proposals (May 2025)",
  obbba_senate_ctc_top_rate_options: "OBBBA Senate CTC / top-rate options",
  snap_tfp_2021_revoked: "SNAP TFP 2021 revocation",
  trump_tariffs_2025_2026: "2025–26 tariffs",
  trump_tariffs_announced_20250120_20260723: "Tariffs announced 2025–26",
  kypa_full_package: "Keep Your Pay Act",
  watca: "WATCA",
  family_first_act: "Family First Act",
  american_family_act_119th: "American Family Act (119th)",
  tcja_permanence: "TCJA permanence",
  ss_benefits_tax_elimination: "SS benefit-tax elimination",
  state_refundable_ctc_design: "State refundable CTC design",
  bl_ctc_option: "CTC option",
  bl_ctc_option_permanent: "CTC option (permanent)",
  qbi_199a_options: "QBI §199A options",
  wptra: "WPTRA",
  wptra_plus_min_eitc_under4: "WPTRA + min EITC under 4",
};

export const BASELINE_LABELS: Record<string, string> = {
  current_policy: "current policy",
  tcja_extension: "TCJA extension",
  current_law_pre_2025_tariffs: "current law, pre-2025 tariffs",
  current_law_plus_senate_obbba_title_vii:
    "current law + Senate OBBBA Title VII",
  tcja_ctc: "TCJA CTC",
  no_ctc: "no CTC",
  bl_ctc_option: "CTC option baseline",
  bl_ctc_option_permanent: "CTC option baseline (permanent)",
};

/** Fallback prettifier so new slugs (future sources) render without app
 * edits: underscores to spaces, no other transformation. */
export const labelize = (slug: string): string => slug.replace(/_/g, " ");

export const programLabel = (p?: string): string =>
  p ? (PROGRAM_LABELS[p] ?? labelize(p)) : "";
export const metricLabel = (m: string): string =>
  METRIC_LABELS[m] ?? labelize(m);
export const policyLabel = (p: string): string =>
  POLICY_LABELS[p] ?? labelize(p);
export const baselineLabel = (b: string): string =>
  BASELINE_LABELS[b] ?? labelize(b);
