import { useMemo } from "react";
import type { Comparison, Row } from "../types";
import { PROGRAM_LABELS } from "../types";
import { useNav } from "../navigation";
import { LinkButton, Stat, Tag } from "./ui";

/** Where PolicyEngine cannot yet see: gaps grouped by what closes them. */
export function GapsView({ data }: { data: Comparison }) {
  const nav = useNav();
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

  const count = (status: string) =>
    data.rows.filter((r) => r.status === status).length;
  const modelGap = count("pe_gap");
  const backlog = count("not_computed");
  const suppressed = count("suppressed");

  return (
    <div className="space-y-4">
      <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
        Cells the source publishes that PolicyEngine does not yet produce.
        Model gaps need engine or data work; not-yet-computed cells need only
        pipeline work. Each group names what closes it.
      </p>
      <div className="grid gap-4 sm:grid-cols-3">
        <Stat
          label="Model gap"
          value={modelGap.toLocaleString()}
          sub={
            <LinkButton
              className="text-xs"
              onClick={() => nav.go("scorecard", { bucket: "pe_gap" })}
            >
              Show these cells
            </LinkButton>
          }
        />
        <Stat
          label="Not yet computed"
          value={backlog.toLocaleString()}
          sub={
            <LinkButton
              className="text-xs"
              onClick={() => nav.go("scorecard", { bucket: "not_computed" })}
            >
              Show these cells
            </LinkButton>
          }
        />
        <Stat
          label="Suppressed by source"
          value={suppressed.toLocaleString()}
          sub="Mostly metro/non-metro splits at the national level and small-state subgroup cells"
        />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {groups.map(([key, g]) => {
          const r0 = g.rows[0];
          const a = g.annotation ? data.annotations[g.annotation] : null;
          const metrics = [...new Set(g.rows.map((r) => r.metric))];
          const subgroups = [...new Set(g.rows.map((r) => r.subgroup))];
          return (
            <div
              key={key}
              className="rounded-lg border border-border bg-card p-4"
            >
              <div className="flex items-baseline justify-between gap-3">
                <span className="font-medium">
                  {PROGRAM_LABELS[r0.program] ?? r0.program}
                </span>
                <span className="fig text-sm text-muted-foreground">
                  {g.rows.length.toLocaleString()} cells
                </span>
              </div>
              <Tag
                tone={r0.status === "pe_gap" ? "solid" : "outline"}
                className="mt-1.5"
              >
                {r0.status === "pe_gap" ? "model gap" : "pipeline backlog"}
              </Tag>
              <p className="mt-2 text-xs leading-4 text-muted-foreground">
                {a
                  ? a.text
                  : `Metrics: ${metrics.join(", ")} · subgroups: ${
                      subgroups.length
                    }`}
              </p>
              {a && (
                <p className="mt-1 text-[11px] leading-4 text-muted-foreground">
                  {a.basis}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
