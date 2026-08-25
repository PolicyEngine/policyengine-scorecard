export type Status =
  | "comparable"
  | "constructed"
  | "baseline_unvalidated"
  | "concept_mismatch"
  | "pe_gap"
  | "not_computed"
  | "suppressed";

export type CalibrationRelationship =
  "consumed_as_target" | "seed_source" | "held_out";

/** The model instance a row or lane belongs to (issue #42). */
export type Country = "US" | "UK" | "BE";

export const COUNTRY_LABELS: Record<Country, string> = {
  US: "United States",
  UK: "United Kingdom",
  BE: "Belgium",
};

/** A concept_mismatch attachment must never render a divergence or ratio:
 * the comparison is declared not comparable (Belgium lane, PR #82). The
 * fallback string is what the caller shows instead of a computed figure. */
export function comparabilityFigure(
  statusEffective: string,
  fallback: string,
  compute: () => string,
): string {
  return statusEffective === "concept_mismatch" ? fallback : compute();
}

/**
 * Country of a row or lane. Historical US feeds predate the country key,
 * so a missing country always means "US" — never drop a row over it.
 */
export function countryOf(r: { country?: Country }): Country {
  return r.country ?? "US";
}

export interface Lane {
  id: string;
  /** data/lanes.json carries this explicitly; absent means "US". */
  country?: Country;
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

export interface Row {
  source: string;
  /** Absent on US-era exports; countryOf() defaults it to "US". */
  country?: Country;
  program: string;
  metric: string;
  subgroup: string;
  variant: string | null;
  geography: string;
  unit_concept: string;
  period: string;
  external_value: number | null;
  pe_value: number | null;
  pe_value_2026: number | null;
  pe_period: string | null;
  status: Status;
  pe_construction: string | null;
  ratio: number | null;
  delta: number | null;
  annotations: string[];
  source_column: string;
  calibration_relationship: CalibrationRelationship;
  calibration_basis: string;
  diagnosis: {
    queue_id: number;
    classification: string;
    confidence: string;
    title: string;
    fix_type: string | null;
  } | null;
}

export const RELATIONSHIP_LABELS: Record<CalibrationRelationship, string> = {
  consumed_as_target: "target consumed",
  seed_source: "seed source",
  held_out: "held out",
};

export interface Annotation {
  id: string;
  severity: string;
  text: string;
  basis: string;
}

export interface Comparison {
  built: string;
  source_meta: {
    id: string;
    name: string;
    url: string;
    fetched: string;
    period: string;
    model: { name: string; method: string };
  };
  pe_bundle: Record<string, string>;
  pe_runs: Record<string, { flags_set_true: string[] }>;
  annotations: Record<string, Annotation>;
  summary: { n_rows: number; by_status: Record<string, number> };
  rows: Row[];
}

/** Divergence bucket for a row that has both values. */
export type Closeness = "close" | "moderate" | "far";

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
};

export const METRIC_LABELS: Record<string, string> = {
  eligible_count: "Eligible",
  eligibility_rate: "Eligibility rate",
  participation_rate: "Participation rate",
  participation_gap_count: "Participation gap",
  poverty_rate: "Poverty rate",
  poverty_rate_fullpart: "Poverty rate, full participation",
  poverty_rate_relative_change_fullpart: "Poverty change, full participation",
  poverty_count_change_fullpart: "People lifted, full participation",
};

export const STATUS_LABELS: Record<Status, string> = {
  comparable: "Comparable",
  constructed: "Constructed",
  baseline_unvalidated: "Baseline unvalidated",
  concept_mismatch: "Concept mismatch",
  pe_gap: "Model gap",
  not_computed: "Not yet computed",
  suppressed: "Suppressed by source",
};

/** One PE computation of a claim at a certified release (populations feed). */
export interface ReleaseResult {
  value: number | null;
  status: Status;
  engine_version: string;
  data_bundle: string;
  release: string;
  construction: string;
  computed_at: string;
  annotations: string[];
  baseline: string | null;
  status_effective: Status;
}

/** A non-Urban claim from scorecard.db with its per-release history. */
export interface PopulationRow {
  claim_id: string;
  /** Absent on US-era exports; countryOf() defaults it to "US". */
  country?: Country;
  source: string;
  source_column: string;
  name: string;
  window: string;
  publication_title: string;
  url: string;
  metric: string;
  unit_concept: string;
  value_kind: string;
  period: number;
  time_basis: string;
  period_start: number | null;
  period_end: number | null;
  geography: string | null;
  program: string | null;
  conditions: Record<string, string>;
  reform_framework: string | null;
  reform_key: string;
  external_value: number | null;
  calibration_relationship: CalibrationRelationship;
  claim_baseline: string | null;
  latest: ReleaseResult & { ratio: number | null; delta: number | null };
  results: ReleaseResult[];
  diagnosis: {
    class: string;
    rationale: string;
    action_link: string;
  } | null;
}

export interface PopulationsFeed {
  built: string;
  note: string;
  summary: {
    claims: number;
    multi_release_claims: number;
    by_source: Record<string, number>;
    by_latest_status: Record<string, number>;
  };
  rows: PopulationRow[];
}
