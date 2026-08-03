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

/** Bin labels are descriptive distances, never verdicts (issue #9). */
export const SPINE_META: Record<
  SpineBucket,
  { label: string; color: string; text: string }
> = {
  close: {
    label: "Within 2.5pp / 10%",
    color: "var(--chart-1)",
    text: "Both values exist and sit within the closest descriptive bin",
  },
  moderate: {
    label: "Within 10pp / 30%",
    color: "#FEC601",
    text: "Both values exist; middle bin",
  },
  far: {
    label: "Beyond 10pp / 30%",
    color: "var(--destructive)",
    text: "Both values exist; outer bin — decomposition material",
  },
  concept_mismatch: {
    label: "Concept mismatch",
    color: "var(--chart-4)",
    text: "Values exist but measure different concepts",
  },
  pe_gap: {
    label: "Out of model",
    color: "#475569",
    text: "PolicyEngine cannot produce this today",
  },
  not_computed: {
    label: "Not yet computed",
    color: "#CBD5E1",
    text: "Producible, not yet in the pipeline",
  },
  suppressed: {
    label: "Suppressed",
    color: "#F2F4F7",
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
