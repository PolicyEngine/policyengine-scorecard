import { useMemo } from "react";
import { divergenceScore, fmtDivergence, fmtValue } from "../format";
import type { Comparison, Row } from "../types";
import { METRIC_LABELS, PROGRAM_LABELS } from "../types";
import type { SpineBucket } from "../spine";

/**
 * The diagnosis queue: the largest material divergences among rows where the
 * concepts are close enough that the delta means something (comparable +
 * constructed only), national totals first, then states.
 */
export function DivergenceBoard({
  data,
  buckets,
}: {
  data: Comparison;
  buckets: Map<Row, SpineBucket>;
}) {
  const candidates = useMemo(() => {
    const ok = new Set(["moderate", "far"]);
    return data.rows
      .filter(
        (r) =>
          ["comparable", "constructed"].includes(r.status) &&
          ok.has(buckets.get(r) as string) &&
          r.subgroup === "total" &&
          r.variant === null,
      )
      .sort((a, b) => divergenceScore(b) - divergenceScore(a));
  }, [data, buckets]);

  const national = candidates.filter((r) => r.geography === "US");
  const states = candidates.filter((r) => r.geography !== "US").slice(0, 30);

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      <section>
        <h2 className="mb-1 text-lg font-semibold">National</h2>
        <p className="mb-3 text-xs text-muted-foreground">
          Every national total-row divergence beyond tolerance, largest first.
          These seed the diagnosis pipeline.
        </p>
        <ol className="space-y-2">
          {national.map((r) => (
            <DivergenceCard key={r.source_column} row={r} data={data} />
          ))}
          {national.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No national divergences beyond tolerance.
            </p>
          )}
        </ol>
      </section>
      <section>
        <h2 className="mb-1 text-lg font-semibold">States</h2>
        <p className="mb-3 text-xs text-muted-foreground">
          The 30 largest state-level divergences (total rows).
        </p>
        <ol className="space-y-2">
          {states.map((r) => (
            <DivergenceCard
              key={r.source_column + r.geography}
              row={r}
              data={data}
            />
          ))}
        </ol>
      </section>
    </div>
  );
}

function DivergenceCard({ row, data }: { row: Row; data: Comparison }) {
  return (
    <li className="rounded-md border border-border p-3">
      <div className="flex items-baseline justify-between gap-3">
        <span className="font-medium">
          {PROGRAM_LABELS[row.program] ?? row.program} ·{" "}
          {METRIC_LABELS[row.metric] ?? row.metric}
          {row.geography !== "US" && (
            <span className="fig text-muted-foreground">
              {" "}
              · {row.geography}
            </span>
          )}
          <span
            className={
              "ml-1.5 align-middle rounded-sm border px-1 py-px text-[9px] uppercase tracking-wide " +
              (row.calibration_relationship === "held_out"
                ? "border-[var(--chart-1)] text-[var(--chart-3)]"
                : "border-dashed border-border text-muted-foreground")
            }
            title={row.calibration_basis}
          >
            {row.calibration_relationship.replace(/_/g, " ")}
          </span>
        </span>
        <span className="fig text-destructive">{fmtDivergence(row)}</span>
      </div>
      <p className="mt-1 fig text-sm text-muted-foreground">
        Urban {fmtValue(row.external_value, row.metric)} · PolicyEngine{" "}
        {fmtValue(row.pe_value, row.metric)}
      </p>
      {row.pe_construction && (
        <p className="mt-1 text-xs text-muted-foreground">
          {row.pe_construction}
        </p>
      )}
      {row.annotations.length > 0 && (
        <p className="mt-1 text-xs text-muted-foreground">
          {row.annotations
            .map((id) => data.annotations[id]?.severity)
            .filter(Boolean)
            .join(" · ")}{" "}
          annotations apply — see the scorecard row.
        </p>
      )}
    </li>
  );
}
