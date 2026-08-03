import type { IndexSource, ScorecardIndex, Status } from "../types";
import { metricLabel, STATUS_LABELS } from "../types";
import { SPINE_ORDER, SPINE_META, type SpineBucket } from "../spine";

const fmt = (n: number | undefined) => (n ?? 0).toLocaleString();

/** One card per external source; new DB ingests appear here automatically. */
export function SourceCards({
  index,
  onSelect,
}: {
  index: ScorecardIndex;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {index.sources.map((s) => (
        <SourceCard key={s.id} s={s} onSelect={() => onSelect(s.id)} />
      ))}
    </div>
  );
}

function statusToBucket(status: string): SpineBucket | null {
  // Card-level bar: statuses only (bins need row values; the per-source
  // page shows the full spine). Comparable/constructed draw with the
  // closest-bin color but keep their status labels.
  if (status === "comparable" || status === "constructed") return "close";
  if (SPINE_ORDER.includes(status as SpineBucket))
    return status as SpineBucket;
  return null;
}

function SourceCard({
  s,
  onSelect,
}: {
  s: IndexSource;
  onSelect: () => void;
}) {
  const total = s.claims || 1;
  const segments = Object.entries(s.by_status)
    .map(([status, n]) => ({
      status,
      bucket: statusToBucket(status),
      n: n ?? 0,
    }))
    .filter(
      (x): x is { status: string; bucket: SpineBucket; n: number } =>
        !!x.bucket,
    )
    .sort(
      (a, b) =>
        SPINE_ORDER.indexOf(a.bucket) - SPINE_ORDER.indexOf(b.bucket) ||
        a.status.localeCompare(b.status),
    );
  const rel = s.relationships;
  const period =
    s.period_min === s.period_max
      ? String(s.period_min)
      : `${s.period_min}–${s.period_max}`;

  return (
    <button
      onClick={onSelect}
      className="rounded-md border border-border p-3 text-left transition-colors hover:border-primary/60 hover:bg-muted/30"
    >
      <div className="flex items-baseline justify-between gap-2">
        <span className="font-semibold leading-5">{s.name}</span>
        <span className="fig shrink-0 text-sm text-muted-foreground">
          {fmt(s.claims)}
        </span>
      </div>
      <p className="mt-0.5 text-[11px] text-muted-foreground">
        {s.model ?? "model not cataloged"} · {period}
      </p>
      <div className="mt-2 flex h-2.5 w-full overflow-hidden rounded-sm border border-border/70">
        {segments.map(({ status, bucket, n }, i) => (
          <span
            key={i}
            title={`${STATUS_LABELS[status as Status] ?? status}: ${fmt(n)}`}
            style={{
              width: `${(n / total) * 100}%`,
              background: SPINE_META[bucket].color,
              opacity: status === "constructed" ? 0.75 : 1,
            }}
          />
        ))}
      </div>
      <p className="mt-2 text-[11px] leading-4 text-muted-foreground">
        <span className="fig">{fmt(s.computed)}</span> with PE counterparts
        {s.held_out_compared > 0 && (
          <>
            {" "}
            · <span className="fig">{fmt(s.held_out_compared)}</span> held-out
            compared
          </>
        )}
        {(rel.consumed_as_target ?? 0) + (rel.seed_source ?? 0) > 0 && (
          <>
            {" "}
            ·{" "}
            <span className="fig">
              {fmt((rel.consumed_as_target ?? 0) + (rel.seed_source ?? 0))}
            </span>{" "}
            target/seed labeled
          </>
        )}
      </p>
      <p className="mt-1 truncate text-[11px] text-muted-foreground">
        {s.metrics_top
          .slice(0, 3)
          .map((m) => metricLabel(String(m.value)))
          .join(" · ")}
      </p>
    </button>
  );
}
