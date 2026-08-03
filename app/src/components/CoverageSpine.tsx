import type { Row } from "../types";
import { SPINE_META, SPINE_ORDER, type SpineBucket } from "../spine";

/**
 * The signature element: one full-width stacked bar in which every published
 * cell appears, bucketed by how well PolicyEngine sees it. The gray segments
 * (gaps) are structurally inseparable from the teal ones — honesty as layout.
 * Clicking a segment filters the scorecard.
 */
export function CoverageSpine({
  rows,
  buckets,
  active,
  onSelect,
  label,
}: {
  rows: Row[];
  buckets: Map<Row, SpineBucket>;
  active: SpineBucket | null;
  onSelect: (b: SpineBucket | null) => void;
  label: string;
}) {
  const counts = new Map<SpineBucket, number>();
  for (const r of rows) {
    const b = buckets.get(r)!;
    counts.set(b, (counts.get(b) ?? 0) + 1);
  }
  const total = rows.length || 1;

  return (
    <figure aria-label={label}>
      <div className="flex h-9 w-full overflow-hidden rounded-md border border-border">
        {SPINE_ORDER.map((b) => {
          const n = counts.get(b) ?? 0;
          if (!n) return null;
          const meta = SPINE_META[b];
          const pct = (n / total) * 100;
          const dimmed = active !== null && active !== b;
          return (
            <button
              key={b}
              title={`${meta.label}: ${n.toLocaleString()} cells — ${meta.text}`}
              aria-pressed={active === b}
              onClick={() => onSelect(active === b ? null : b)}
              className="h-full transition-opacity"
              style={{
                width: `${pct}%`,
                background: meta.color,
                opacity: dimmed ? 0.25 : 1,
                minWidth: 3,
              }}
            />
          );
        })}
      </div>
      <figcaption className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
        {SPINE_ORDER.map((b) => {
          const n = counts.get(b) ?? 0;
          if (!n) return null;
          const meta = SPINE_META[b];
          return (
            <button
              key={b}
              onClick={() => onSelect(active === b ? null : b)}
              className={
                "flex items-center gap-1.5 text-xs " +
                (active === b
                  ? "font-semibold text-foreground"
                  : "text-muted-foreground hover:text-foreground")
              }
            >
              <span
                className="inline-block h-2.5 w-2.5 rounded-[2px] border border-border"
                style={{ background: meta.color }}
              />
              {meta.label}
              <span className="fig">{n.toLocaleString()}</span>
            </button>
          );
        })}
        {active && (
          <button
            onClick={() => onSelect(null)}
            className="text-xs text-primary underline underline-offset-2"
          >
            clear filter
          </button>
        )}
      </figcaption>
    </figure>
  );
}
