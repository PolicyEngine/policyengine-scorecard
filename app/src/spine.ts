import { closeness } from "./format";
import type { Row } from "./types";

export type SpineBucket =
  | "close"
  | "moderate"
  | "far"
  | "concept_mismatch"
  | "pe_gap"
  | "not_computed"
  | "suppressed";

export const SPINE_ORDER: SpineBucket[] = [
  "close",
  "moderate",
  "far",
  "concept_mismatch",
  "pe_gap",
  "not_computed",
  "suppressed",
];

/**
 * Every bucket colour is a design-token utility class (never a hex value),
 * so the spine, badges and legend follow the ui-kit theme without a second
 * palette to maintain.
 *
 * Closeness is one ordinal teal ramp (dark = close), not a traffic light:
 * statuses label, never grade. Concept mismatch is the one other hue, and
 * the buckets with a missing value are neutral gray, with suppressed cells
 * hatched rather than filled. Adjacent pairs were checked for colour-vision
 * separation; keep that in mind before swapping a step.
 */
export const SPINE_META: Record<
  SpineBucket,
  { label: string; swatch: string; text: string }
> = {
  close: {
    label: "Close",
    swatch: "bg-teal-900",
    text: "Less than 2.5 points apart (rates) or 10% apart (counts)",
  },
  moderate: {
    label: "Diverging",
    swatch: "bg-teal-600",
    text: "2.5 to 10 points apart (rates) or 10% to 30% (counts)",
  },
  far: {
    label: "Far apart",
    swatch: "bg-teal-400",
    text: "10 points or more apart (rates) or 30% or more (counts)",
  },
  concept_mismatch: {
    label: "Concept mismatch",
    swatch: "bg-chart-4",
    text: "Both values exist but measure different things, so they are not compared",
  },
  pe_gap: {
    label: "Model gap",
    swatch: "bg-gray-400",
    text: "PolicyEngine cannot produce this value today",
  },
  not_computed: {
    label: "Not yet computed",
    swatch: "bg-gray-300",
    text: "PolicyEngine can produce this value but has not run it yet",
  },
  suppressed: {
    label: "Suppressed",
    swatch: "swatch-hatch",
    text: "The source did not publish this value",
  },
};

/** The chart's two groups, in SPINE_ORDER: both values exist, or one is
 *  missing (no PolicyEngine value yet, or none published by the source).
 *  The note says how the first group's gaps are measured (see closeness). */
export const SPINE_GROUPS: {
  label: string;
  note: string;
  buckets: SpineBucket[];
}[] = [
  {
    label: "Both values",
    note: "Gap between PolicyEngine and the source: percentage points for rates, percent difference for counts",
    buckets: ["close", "moderate", "far", "concept_mismatch"],
  },
  {
    label: "A value missing",
    note: "PolicyEngine or the source has no value to compare",
    buckets: ["pe_gap", "not_computed", "suppressed"],
  },
];

export function bucketOf(row: Row): SpineBucket {
  if (row.status === "suppressed") return "suppressed";
  if (row.status === "pe_gap") return "pe_gap";
  if (row.status === "not_computed") return "not_computed";
  if (row.status === "concept_mismatch") return "concept_mismatch";
  const c = closeness(row);
  if (c === null) return "not_computed";
  return c;
}
