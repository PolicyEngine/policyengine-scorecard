import type { Row } from "../types";
import { SPINE_META, SPINE_ORDER, type SpineBucket } from "../spine";

/**
 * The signature element: one full-width stacked bar in which every published
 * cell appears, bucketed by how well PolicyEngine sees it. The gray segments
 * (gaps) are structurally inseparable from the teal ones — honesty as layout.
 * Clicking a segment filters the comparison table.
 */
export function CoverageSpine({
  rows,
  buckets,
  active,
  onSelect,
}: {
  rows: Row[];
  buckets: Map<Row, SpineBucket>;
  active: SpineBucket | null;
  onSelect: (b: SpineBucket | null) => void;
}) {
  const counts = new Map<SpineBucket, number>();
  for (const r of rows) {
    const b = buckets.get(r)!;
    counts.set(b, (counts.get(b) ?? 0) + 1);
  }
  const total = rows.length || 1;

  return (
    <figure aria-label="Coverage of published cells by comparison status">
      <div className="flex h-8 w-full overflow-hidden rounded-md border border-border">
        {SPINE_ORDER.map((b) => {
          const n = counts.get(b) ?? 0;
          if (!n) return null;
          const meta = SPINE_META[b];
          const pct = (n / total) * 100;
          const dimmed = active !== null && active !== b;
          return (
            <button
              key={b}
              type="button"
              title={`${meta.label}: ${n.toLocaleString()} cells — ${meta.text}`}
              aria-label={`${meta.label}: ${n.toLocaleString()} cells`}
              aria-pressed={active === b}
              onClick={() => onSelect(active === b ? null : b)}
              className={
                "h-full transition-opacity hover:opacity-80 " + meta.swatch
              }
              style={{
                width: `${pct}%`,
                opacity: dimmed ? 0.25 : undefined,
                minWidth: 3,
              }}
            />
          );
        })}
      </div>
      <figcaption className="mt-2 flex flex-wrap gap-x-4 gap-y-1.5">
        {SPINE_ORDER.map((b) => {
          const n = counts.get(b) ?? 0;
          if (!n) return null;
          const meta = SPINE_META[b];
          return (
            <button
              key={b}
              type="button"
              onClick={() => onSelect(active === b ? null : b)}
              title={meta.text}
              className={
                "flex items-center gap-1.5 text-xs " +
                (active === b
                  ? "font-semibold text-foreground"
                  : "text-muted-foreground hover:text-foreground")
              }
            >
              <span
                aria-hidden
                className={
                  "inline-block h-2.5 w-2.5 rounded-[2px] border border-border " +
                  meta.swatch
                }
              />
              {meta.label}
              <span className="fig">{n.toLocaleString()}</span>
            </button>
          );
        })}
        {active && (
          <button
            type="button"
            onClick={() => onSelect(null)}
            className="text-xs text-primary underline underline-offset-2"
          >
            Clear
          </button>
        )}
      </figcaption>
    </figure>
  );
}
