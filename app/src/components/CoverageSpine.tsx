import type { Row } from "../types";
import { SPINE_GROUPS, SPINE_META, type SpineBucket } from "../spine";

/**
 * The signature element: every published cell, counted by how well
 * PolicyEngine sees it, as one horizontal bar per bucket on a shared scale.
 * The gap buckets sit beside the compared ones at the same scale — honesty
 * as layout. Clicking a bar filters the comparison table.
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
  // One scale for every bar, so a gap bucket and a compared bucket of the
  // same size draw the same length.
  const max = Math.max(1, ...counts.values());

  return (
    <figure aria-label="Published cells by comparison status">
      <div className="grid gap-x-10 gap-y-5 md:grid-cols-2">
        {SPINE_GROUPS.map((g) => {
          const present = g.buckets.filter((b) => counts.get(b));
          if (!present.length) return null;
          const sum = present.reduce((s, b) => s + (counts.get(b) ?? 0), 0);
          return (
            <div key={g.label}>
              <div className="mb-1.5 border-b border-border pb-1.5">
                <p className="flex items-baseline justify-between gap-3 text-xs">
                  <span className="font-medium text-foreground">{g.label}</span>
                  <span className="fig text-muted-foreground">
                    {sum.toLocaleString()}
                  </span>
                </p>
                <p className="mt-0.5 text-[11px] leading-4 text-muted-foreground">
                  {g.note}
                </p>
              </div>
              <ul>
                {present.map((b) => {
                  const n = counts.get(b) ?? 0;
                  const meta = SPINE_META[b];
                  const dimmed = active !== null && active !== b;
                  return (
                    <li key={b}>
                      <button
                        type="button"
                        aria-label={`${meta.label}: ${n.toLocaleString()} cells. ${meta.text}`}
                        aria-pressed={active === b}
                        onClick={() => onSelect(active === b ? null : b)}
                        className="group grid w-full grid-cols-[7.5rem_1fr_3.75rem] items-center gap-x-3 gap-y-0.5 rounded-sm py-1.5 text-left text-xs transition-opacity hover:bg-muted/60"
                        style={{ opacity: dimmed ? 0.35 : undefined }}
                      >
                        <span
                          className={
                            active === b
                              ? "font-semibold text-foreground"
                              : "text-muted-foreground group-hover:text-foreground"
                          }
                        >
                          {meta.label}
                        </span>
                        <span className="block h-3 border-l border-border-dark">
                          <span
                            className={
                              "block h-full rounded-r-[4px] " + meta.swatch
                            }
                            style={{
                              width: `${(n / max) * 100}%`,
                              minWidth: 2,
                            }}
                          />
                        </span>
                        <span className="fig text-right text-foreground">
                          {n.toLocaleString()}
                        </span>
                        <span className="col-span-3 text-[11px] leading-4 text-muted-foreground">
                          {meta.text}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </div>
      {active && (
        <button
          type="button"
          onClick={() => onSelect(null)}
          className="mt-2 text-xs text-primary underline underline-offset-2"
        >
          Clear
        </button>
      )}
    </figure>
  );
}
