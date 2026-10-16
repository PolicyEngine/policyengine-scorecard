import type { Country } from "./types";
import { COUNTRY_LABELS } from "./types";
import {
  METRIC_ORDER,
  PROGRAM_ORDER,
  defaultFilters,
  type Filters,
} from "./filters";

/**
 * Deep links (issue-free share URLs): ?country=be&view=validation.
 * App.tsx reads on load and on back/forward, and writes back as the
 * view nav and country selector change (a new history entry per view, so
 * the browser's back button works); defaults stay out of the URL so
 * the bare origin remains canonical. Pure over strings — no window.
 *
 * View ids are stable URL vocabulary: "scorecard" keeps its id for
 * existing links even though the view is labelled "Comparison".
 *
 * Two parameters travel only with their own view (issue #177):
 * ?view=validation&claim=<claim_id> opens that claim's row, and
 * ?view=scorecard&program=snap&metric=…&geography=VT sets the comparison
 * filters. Values outside their closed vocabularies are ignored, so a
 * malformed link lands on the defaults rather than a broken table.
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

/** The comparison filters a link carries; subgroup and status stay in the
 *  history entry only. */
const FILTER_PARAMS = ["program", "metric", "geography"] as const;
export type UrlFilters = Partial<
  Pick<Filters, (typeof FILTER_PARAMS)[number]>
>;

/** Claim ids are sha256 hex prefixes (scorecard_db Claim.claim_id). */
const CLAIM_ID = /^[0-9a-f]{1,64}$/;
/** Geography codes as comparison rows carry them: the national code (the
 *  country code) or a two-letter state code. "states" means all states. */
const GEOGRAPHY_CODE = /^[A-Z]{2}$/;

export interface UrlState {
  country: Country;
  tab: TabId;
  /** With view=validation only: the claim whose row opens. */
  claim?: string;
  /** With view=scorecard only: the comparison filters the link sets. */
  filters?: UrlFilters;
}

export function parseUrlState(search: string): UrlState {
  const params = new URLSearchParams(search);
  const c = (params.get("country") ?? "").toUpperCase();
  const v = (params.get("view") ?? "").toLowerCase();
  const state: UrlState = {
    country: c in COUNTRY_LABELS ? (c as Country) : "US",
    tab: TABS.some((t) => t.id === v) ? (v as TabId) : DEFAULT_TAB,
  };
  if (state.tab === "validation") {
    const claim = (params.get("claim") ?? "").toLowerCase();
    if (CLAIM_ID.test(claim)) state.claim = claim;
  }
  if (state.tab === "scorecard") {
    const filters = parseFilters(params);
    if (Object.keys(filters).length > 0) state.filters = filters;
  }
  return state;
}

/**
 * Comparison filters from the query. The table's filters never hold ""
 * (the Select's "__empty__" sentinel, see selectValue.ts), so an empty or
 * sentinel value is out of vocabulary like any other and reads as the
 * default.
 */
function parseFilters(params: URLSearchParams): UrlFilters {
  const out: UrlFilters = {};
  const program = (params.get("program") ?? "").toLowerCase();
  if (PROGRAM_ORDER.includes(program)) out.program = program;
  const metric = (params.get("metric") ?? "").toLowerCase();
  if (METRIC_ORDER.includes(metric)) out.metric = metric;
  const geography = (params.get("geography") ?? "").toUpperCase();
  if (geography === "STATES") out.geography = "states";
  else if (GEOGRAPHY_CODE.test(geography)) out.geography = geography;
  return out;
}

export function buildUrlQuery(
  search: string,
  country: Country,
  tab: TabId,
  {
    claim = null,
    filters,
  }: { claim?: string | null; filters?: UrlFilters } = {},
): string {
  const params = new URLSearchParams(search);
  if (country === "US") params.delete("country");
  else params.set("country", country.toLowerCase());
  if (tab === DEFAULT_TAB) params.delete("view");
  else params.set("view", tab);
  if (tab === "validation" && claim) params.set("claim", claim);
  else params.delete("claim");
  const defaults = defaultFilters(country);
  for (const key of FILTER_PARAMS) {
    const value = tab === "scorecard" ? filters?.[key] : undefined;
    if (value && value !== defaults[key]) params.set(key, value);
    else params.delete(key);
  }
  return params.toString();
}
