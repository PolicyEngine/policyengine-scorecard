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
 * so the spine, badges and legend follow the ui-kit theme — including any
 * dark-mode override — without a second palette to maintain.
 */
export const SPINE_META: Record<
  SpineBucket,
  { label: string; swatch: string; text: string }
> = {
  close: {
    label: "Close",
    swatch: "bg-chart-1",
    text: "Computed counterpart within descriptive tolerance (2.5pp / 10%)",
  },
  moderate: {
    label: "Diverging",
    swatch: "bg-warning",
    text: "Within 10pp / 30% — worth a look",
  },
  far: {
    label: "Far apart",
    swatch: "bg-destructive",
    text: "Beyond 10pp / 30% — diagnosis candidates",
  },
  concept_mismatch: {
    label: "Concept mismatch",
    swatch: "bg-chart-4",
    text: "Values exist but measure different concepts",
  },
  pe_gap: {
    label: "Model gap",
    swatch: "bg-gray-600",
    text: "PolicyEngine cannot produce this today",
  },
  not_computed: {
    label: "Not yet computed",
    swatch: "bg-gray-300",
    text: "Producible, not yet in the pipeline",
  },
  suppressed: {
    label: "Suppressed",
    swatch: "bg-gray-100",
    text: "The source suppressed the cell",
  },
};

export function bucketOf(row: Row): SpineBucket {
  if (row.status === "suppressed") return "suppressed";
  if (row.status === "pe_gap") return "pe_gap";
  if (row.status === "not_computed") return "not_computed";
  if (row.status === "concept_mismatch") return "concept_mismatch";
  const c = closeness(row);
  if (c === null) return "not_computed";
  return c;
}
