import type { Country } from "./types";
import { COUNTRY_LABELS } from "./types";

/**
 * Deep links (issue-free share URLs): ?country=be&view=validation.
 * App.tsx reads once on load and writes back with replaceState as the
 * view nav and country selector change; defaults stay out of the URL so
 * the bare origin remains canonical. Pure over strings — no window.
 *
 * View ids are stable URL vocabulary: "scorecard" keeps its id for
 * existing links even though the view is labelled "Comparison".
 */
export const TABS = [
  {
    id: "overview",
    label: "Overview",
    blurb: "Coverage, agreement record and pipeline status at a glance",
  },
  {
    id: "scorecard",
    label: "Comparison",
    blurb: "Every published cell next to its PolicyEngine counterpart",
  },
  {
    id: "divergences",
    label: "Divergences",
    blurb: "The largest disagreements, ranked, with diagnoses",
  },
  {
    id: "validation",
    label: "Reform validation",
    blurb: "Reform scores and references with per-release history",
  },
  {
    id: "gaps",
    label: "Gaps",
    blurb: "Where PolicyEngine cannot yet produce a counterpart",
  },
  {
    id: "about",
    label: "Method",
    blurb: "Sources, tolerances and provenance",
  },
] as const;
export type TabId = (typeof TABS)[number]["id"];

export const DEFAULT_TAB: TabId = "overview";

export function parseUrlState(search: string): {
  country: Country;
  tab: TabId;
} {
  const params = new URLSearchParams(search);
  const c = (params.get("country") ?? "").toUpperCase();
  const v = (params.get("view") ?? "").toLowerCase();
  return {
    country: c in COUNTRY_LABELS ? (c as Country) : "US",
    tab: TABS.some((t) => t.id === v) ? (v as TabId) : DEFAULT_TAB,
  };
}

export function buildUrlQuery(
  search: string,
  country: Country,
  tab: TabId,
): string {
  const params = new URLSearchParams(search);
  if (country === "US") params.delete("country");
  else params.set("country", country.toLowerCase());
  if (tab === DEFAULT_TAB) params.delete("view");
  else params.set("view", tab);
  return params.toString();
}
