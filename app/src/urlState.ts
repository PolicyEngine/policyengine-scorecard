import type { Country } from "./types";
import { COUNTRY_LABELS } from "./types";

/**
 * Deep links (issue-free share URLs): ?country=be&view=validation.
 * App.tsx reads once on load and writes back with replaceState as the
 * tab bar and country toggle change; defaults stay out of the URL so
 * the bare origin remains canonical. Pure over strings — no window.
 */
export const TABS = [
  { id: "scorecard", label: "Scorecard" },
  { id: "divergences", label: "Divergences" },
  { id: "validation", label: "Reform validation" },
  { id: "gaps", label: "Gaps" },
  { id: "about", label: "Method" },
] as const;
export type TabId = (typeof TABS)[number]["id"];

export function parseUrlState(search: string): {
  country: Country;
  tab: TabId;
} {
  const params = new URLSearchParams(search);
  const c = (params.get("country") ?? "").toUpperCase();
  const v = (params.get("view") ?? "").toLowerCase();
  return {
    country: c in COUNTRY_LABELS ? (c as Country) : "US",
    tab: TABS.some((t) => t.id === v) ? (v as TabId) : "scorecard",
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
  if (tab === "scorecard") params.delete("view");
  else params.set("view", tab);
  return params.toString();
}
