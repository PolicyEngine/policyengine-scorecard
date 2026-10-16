import { SPINE_ORDER, type SpineBucket } from "./spine";
import type { Country } from "./types";

/** The comparison table's program and metric options, in table order; the
 *  same closed vocabularies a link's ?program= / ?metric= are read against. */
export const PROGRAM_ORDER = [
  "snap", "ssi", "tanf", "wic", "ccdf", "housing", "liheap", "eitc",
  "ctc_refund", "spm_poverty",
];
export const METRIC_ORDER = [
  "eligible_count", "eligibility_rate", "participation_rate",
  "participation_gap_count", "poverty_rate", "poverty_rate_fullpart",
  "poverty_rate_relative_change_fullpart", "poverty_count_change_fullpart",
];

export interface Filters {
  country: Country;
  program: string;
  metric: string;
  geography: string; // country code (national) | "states" | state code
  subgroup: string; // "total" | "all" | slug
  bucket: SpineBucket | null;
}

export function defaultFilters(country: Country): Filters {
  return {
    country,
    program: "all",
    metric: "all",
    geography: country,
    subgroup: "total",
    bucket: null,
  };
}

/** True when any row filter differs from the country's defaults. */
export function hasActiveFilters(f: Filters): boolean {
  const d = defaultFilters(f.country);
  return (
    f.program !== d.program ||
    f.metric !== d.metric ||
    f.geography !== d.geography ||
    f.subgroup !== d.subgroup ||
    f.bucket !== d.bucket
  );
}

/**
 * Filters saved in a browser history entry (back/forward, reload) for the
 * given country. history.state is untyped, so anything that is not this
 * app's own shape for this country falls back to the country's defaults.
 */
export function restoreFilters(saved: unknown, country: Country): Filters {
  const d = defaultFilters(country);
  if (typeof saved !== "object" || saved === null) return d;
  const f = saved as Record<string, unknown>;
  if (f.country !== country) return d;
  const str = (v: unknown, fallback: string) =>
    typeof v === "string" && v !== "" ? v : fallback;
  return {
    country,
    program: str(f.program, d.program),
    metric: str(f.metric, d.metric),
    geography: str(f.geography, d.geography),
    subgroup: str(f.subgroup, d.subgroup),
    bucket: SPINE_ORDER.includes(f.bucket as SpineBucket)
      ? (f.bucket as SpineBucket)
      : null,
  };
}
