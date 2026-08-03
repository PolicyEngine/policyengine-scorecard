import type { Diagnosis, Row } from "../types";
import { baselineLabel, policyLabel } from "../types";
import { SPINE_META, type SpineBucket } from "../spine";
import { STATUS_LABELS } from "../types";

export function StatusChip({
  bucket,
  status,
}: {
  bucket: SpineBucket;
  status: Row["status"];
}) {
  const meta = SPINE_META[bucket];
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-sm border border-border px-1.5 py-0.5 text-[11px] whitespace-nowrap"
      title={meta.text}
    >
      <span
        className="h-2 w-2 rounded-[2px]"
        style={{ background: meta.color }}
      />
      {["close", "moderate", "far"].includes(bucket)
        ? STATUS_LABELS[status]
        : meta.label}
    </span>
  );
}

/** Consumed/seed rows are labeled everywhere they appear; agreement on
 * them is calibration, not validation, and they stay out of aggregates. */
export function RelationshipBadge({
  row,
  note,
}: {
  row: Row;
  note?: string;
}) {
  if (row.relationship === "held_out") return null;
  return (
    <span
      className="ml-1 align-middle rounded-sm border border-dashed border-border px-1 py-px text-[9px] uppercase tracking-wide text-muted-foreground"
      title={note}
    >
      {row.relationship === "seed_source" ? "seed" : "target"}
    </span>
  );
}

export function VintageChip({
  label,
  tone,
}: {
  label: string;
  tone: "external" | "pe" | "proj";
}) {
  const styles: Record<string, string> = {
    external: "border-border text-muted-foreground",
    pe: "border-[var(--chart-1)] text-[var(--chart-3)]",
    proj: "border-[var(--chart-2)] text-[var(--chart-4)]",
  };
  return (
    <span
      className={
        "ml-1 inline-block rounded-sm border px-1 py-px text-[9px] font-medium uppercase tracking-wide " +
        styles[tone]
      }
    >
      {label}
    </span>
  );
}

/** Baseline is first-class (#13): show a chip whenever a claim scores
 * against anything other than current law. */
export function BaselineChip({ baseline }: { baseline?: string }) {
  if (!baseline) return null;
  return (
    <span
      className="ml-1 align-middle rounded-sm border border-[var(--chart-2)] px-1 py-px text-[9px] uppercase tracking-wide text-[var(--chart-4)] whitespace-nowrap"
      title={`Scored against a non-current-law baseline: ${baselineLabel(baseline)}`}
    >
      vs {baselineLabel(baseline)}
    </span>
  );
}

export function PolicyChip({ policy }: { policy?: string }) {
  if (!policy) return null;
  return (
    <span className="ml-1 align-middle rounded-sm bg-muted px-1 py-px text-[10px] text-muted-foreground whitespace-nowrap">
      {policyLabel(policy)}
    </span>
  );
}

/**
 * Register-gated diagnosis chip (issue #9): a class reads as a verdict
 * only when `normative` (action_link cites a known issue). Everything
 * else presents as a descriptive explanation.
 */
export function DiagnosisChip({ d }: { d: Diagnosis }) {
  const label = d.normative ? d.class.replace(/_/g, " ") : "explanation";
  const cls = d.normative
    ? d.class === "external_issue"
      ? "bg-[var(--chart-2)] text-white"
      : "bg-[var(--destructive)] text-white"
    : "bg-border text-foreground";
  const chip = (
    <span
      className={
        "mr-1.5 rounded-sm px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide " +
        cls
      }
    >
      {label}
    </span>
  );
  return d.normative && d.action_link ? (
    <a
      href={d.action_link}
      target="_blank"
      rel="noreferrer"
      className="underline-offset-2 hover:underline"
    >
      {chip}
    </a>
  ) : (
    chip
  );
}
