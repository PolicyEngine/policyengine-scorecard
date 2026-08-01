import { useMemo } from "react";
import type { Comparison, Row } from "../types";
import { PROGRAM_LABELS } from "../types";

/** Where PolicyEngine cannot yet see: gaps grouped by what closes them. */
export function GapsView({ data }: { data: Comparison }) {
  const groups = useMemo(() => {
    const gap = new Map<string, { rows: Row[]; annotation: string | null }>();
    for (const r of data.rows) {
      if (!["pe_gap", "not_computed"].includes(r.status)) continue;
      const gapAnnotation =
        r.annotations.find((id) =>
          ["gap"].includes(data.annotations[id]?.severity),
        ) ?? null;
      const key = `${r.status}:${r.program}:${gapAnnotation ?? "backlog"}`;
      if (!gap.has(key)) gap.set(key, { rows: [], annotation: gapAnnotation });
      gap.get(key)!.rows.push(r);
    }
    return [...gap.entries()].sort((a, b) => b[1].rows.length - a[1].rows.length);
  }, [data]);

  const suppressed = data.rows.filter((r) => r.status === "suppressed").length;

  return (
    <div>
      <p className="mb-4 max-w-3xl text-sm text-muted-foreground">
        Cells Urban publishes that PolicyEngine does not yet produce. Model
        gaps need engine or data work; not-yet-computed cells need only
        pipeline work. Each group links to what closes it.
      </p>
      <div className="grid gap-3 md:grid-cols-2">
        {groups.map(([key, g]) => {
          const r0 = g.rows[0];
          const a = g.annotation ? data.annotations[g.annotation] : null;
          const metrics = [...new Set(g.rows.map((r) => r.metric))];
          const subgroups = [...new Set(g.rows.map((r) => r.subgroup))];
          return (
            <div key={key} className="rounded-md border border-border p-3">
              <div className="flex items-baseline justify-between">
                <span className="font-medium">
                  {PROGRAM_LABELS[r0.program] ?? r0.program}
                </span>
                <span className="fig text-sm text-muted-foreground">
                  {g.rows.length.toLocaleString()} cells
                </span>
              </div>
              <p className="mt-0.5 text-[11px] uppercase tracking-wide text-muted-foreground">
                {r0.status === "pe_gap" ? "model gap" : "pipeline backlog"}
              </p>
              <p className="mt-1.5 text-xs text-muted-foreground">
                {a
                  ? a.text
                  : `Metrics: ${metrics.join(", ")} · subgroups: ${
                      subgroups.length
                    }`}
              </p>
              {a && (
                <p className="mt-1 text-[11px] text-muted-foreground">
                  {a.basis}
                </p>
              )}
            </div>
          );
        })}
      </div>
      <p className="mt-4 text-xs text-muted-foreground">
        Urban suppressed {suppressed.toLocaleString()} cells ('.'), mostly
        metro/non-metro splits at the national level and small-state subgroup
        cells.
      </p>
    </div>
  );
}
