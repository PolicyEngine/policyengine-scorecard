export type Status =
  | "comparable"
  | "constructed"
  | "concept_mismatch"
  | "pe_gap"
  | "not_computed"
  | "suppressed";

export interface Row {
  source: string;
  program: string;
  metric: string;
  subgroup: string;
  variant: string | null;
  geography: string;
  unit_concept: string;
  period: string;
  external_value: number | null;
  pe_value: number | null;
  pe_period: string | null;
  status: Status;
  pe_construction: string | null;
  ratio: number | null;
  delta: number | null;
  annotations: string[];
  source_column: string;
}

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
  concept_mismatch: "Concept mismatch",
  pe_gap: "Model gap",
  not_computed: "Not yet computed",
  suppressed: "Suppressed by source",
};
