import { useMemo } from "react";
import type { Row, SourceSlice } from "../types";
import { programLabel } from "../types";

/** Where PolicyEngine cannot yet see: gaps grouped by what closes them. */
export function GapsView({ slice }: { slice: SourceSlice }) {
  const groups = useMemo(() => {
    const gap = new Map<string, { rows: Row[]; annotation: string | null }>();
    for (const r of slice.rows) {
      if (!["pe_gap", "not_computed"].includes(r.status)) continue;
      const gapAnnotation =
        (r.annotations ?? []).find(
          (id) => slice.annotations?.[id]?.severity === "gap",
        ) ?? null;
      const key = `${r.status}:${r.program ?? r.metric}:${
        gapAnnotation ?? "backlog"
      }`;
      if (!gap.has(key)) gap.set(key, { rows: [], annotation: gapAnnotation });
      gap.get(key)!.rows.push(r);
    }
    return [...gap.entries()].sort(
      (a, b) => b[1].rows.length - a[1].rows.length,
    );
  }, [slice]);

  const suppressed = slice.rows.filter(
    (r) => r.status === "suppressed",
  ).length;

  return (
    <div>
      <p className="mb-4 max-w-3xl text-sm text-muted-foreground">
        Cells the source publishes that PolicyEngine does not yet produce.
        Out-of-model cells need engine or data work; not-yet-computed cells
        need only pipeline work. Each group links to what closes it.
      </p>
      <div className="grid gap-3 md:grid-cols-2">
        {groups.map(([key, g]) => {
          const r0 = g.rows[0];
          const a = g.annotation
            ? slice.annotations?.[g.annotation]
            : null;
          const metrics = [...new Set(g.rows.map((r) => r.metric))];
          const subgroups = [
            ...new Set(g.rows.map((r) => r.subgroup ?? "total")),
          ];
          return (
            <div key={key} className="rounded-md border border-border p-3">
              <div className="flex items-baseline justify-between">
                <span className="font-medium">
                  {programLabel(r0.program) || r0.metric}
                </span>
                <span className="fig text-sm text-muted-foreground">
                  {g.rows.length.toLocaleString()} cells
                </span>
              </div>
              <p className="mt-0.5 text-[11px] uppercase tracking-wide text-muted-foreground">
                {r0.status === "pe_gap" ? "out of model" : "pipeline backlog"}
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
      {suppressed > 0 && (
        <p className="mt-4 text-xs text-muted-foreground">
          The source suppressed {suppressed.toLocaleString()} cells ('.'),
          mostly metro/non-metro splits at the national level and small-state
          subgroup cells.
        </p>
      )}
    </div>
  );
}
