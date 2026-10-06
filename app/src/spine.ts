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
    text: "Computed counterpart within descriptive tolerance (2.5pp / 10%)",
  },
  moderate: {
    label: "Diverging",
    swatch: "bg-teal-600",
    text: "Within 10pp / 30% — worth a look",
  },
  far: {
    label: "Far apart",
    swatch: "bg-teal-400",
    text: "Beyond 10pp / 30% — diagnosis candidates",
  },
  concept_mismatch: {
    label: "Concept mismatch",
    swatch: "bg-chart-4",
    text: "Values exist but measure different concepts",
  },
  pe_gap: {
    label: "Model gap",
    swatch: "bg-gray-400",
    text: "PolicyEngine cannot produce this today",
  },
  not_computed: {
    label: "Not yet computed",
    swatch: "bg-gray-300",
    text: "Producible, not yet in the pipeline",
  },
  suppressed: {
    label: "Suppressed",
    swatch: "swatch-hatch",
    text: "The source suppressed the cell",
  },
};

/** The bar's two halves, in SPINE_ORDER: both values exist, or one is
 *  missing (no PolicyEngine value yet, or none published by the source). */
export const SPINE_GROUPS: { label: string; buckets: SpineBucket[] }[] = [
  { label: "Both values", buckets: ["close", "moderate", "far", "concept_mismatch"] },
  { label: "A value missing", buckets: ["pe_gap", "not_computed", "suppressed"] },
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
