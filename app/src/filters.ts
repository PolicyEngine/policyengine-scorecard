import type { SpineBucket } from "./spine";
import type { Country } from "./types";

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
