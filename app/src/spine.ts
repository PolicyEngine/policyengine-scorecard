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

export const SPINE_META: Record<
  SpineBucket,
  { label: string; color: string; text: string }
> = {
  close: {
    label: "Reproduced",
    color: "var(--chart-1)",
    text: "PE counterpart within tolerance (2.5pp / 10%)",
  },
  moderate: {
    label: "Diverging",
    color: "#FEC601",
    text: "Within 10pp / 30% — worth a look",
  },
  far: {
    label: "Far apart",
    color: "var(--destructive)",
    text: "Beyond 10pp / 30% — diagnosis candidates",
  },
  concept_mismatch: {
    label: "Concept mismatch",
    color: "var(--chart-4)",
    text: "Values exist but measure different concepts",
  },
  pe_gap: {
    label: "Model gap",
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
    text: "Urban suppressed the cell",
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
