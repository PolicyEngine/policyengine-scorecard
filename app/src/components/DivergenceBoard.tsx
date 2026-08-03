import { useMemo } from "react";
import { relationshipNote } from "../data";
import { divergenceScore, fmtDivergence, fmtValue } from "../format";
import type { Row, SourceSlice } from "../types";
import { metricLabel, programLabel, RELATIONSHIP_LABELS } from "../types";
import type { SpineBucket } from "../spine";
import { AttributionPanel } from "./AttributionPanel";
import { DiagnosisChip } from "./chips";

/**
 * The decomposition queue: the largest divergences among rows where the
 * concepts are close enough that the distance means something (comparable +
 * constructed only), national totals first, then states. Descriptive — a
 * big number here is material for explanation, not a verdict.
 */
export function DivergenceBoard({
  slice,
  buckets,
}: {
  slice: SourceSlice;
  buckets: Map<Row, SpineBucket>;
}) {
  const candidates = useMemo(() => {
    const ok = new Set(["moderate", "far"]);
    return slice.rows
      .filter(
        (r) =>
          ["comparable", "constructed"].includes(r.status) &&
          ok.has(buckets.get(r) as string) &&
          (r.subgroup ?? "total") === "total" &&
          !r.variant,
      )
      .sort((a, b) => divergenceScore(b) - divergenceScore(a));
  }, [slice, buckets]);

  const national = candidates.filter((r) => r.geography === "US");
  const states = candidates.filter((r) => r.geography !== "US").slice(0, 30);

  return (
    <div>
      <div className="grid gap-8 lg:grid-cols-2">
        <section>
          <h2 className="mb-1 text-lg font-semibold">National</h2>
          <p className="mb-3 text-xs text-muted-foreground">
            Every national total-row divergence beyond the closest bin,
            largest first. These seed the explanation pipeline.
          </p>
          <ol className="space-y-2">
            {national.map((r) => (
              <DivergenceCard key={r.id} row={r} slice={slice} />
            ))}
            {national.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No national divergences beyond the closest bin.
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
              <DivergenceCard key={r.id} row={r} slice={slice} />
            ))}
          </ol>
        </section>
      </div>
      <AttributionPanel />
    </div>
  );
}

function DivergenceCard({ row, slice }: { row: Row; slice: SourceSlice }) {
  const note = relationshipNote(slice, row);
  return (
    <li className="rounded-md border border-border p-3">
      <div className="flex items-baseline justify-between gap-3">
        <span className="font-medium">
          {programLabel(row.program)} · {metricLabel(row.metric)}
          {row.policy === "full_participation" && (
            <span className="ml-1 rounded-sm bg-muted px-1 py-px text-[10px] font-normal text-muted-foreground">
              full participation
            </span>
          )}
          {row.geography !== "US" && (
            <span className="fig text-muted-foreground">
              {" "}
              · {row.geography}
            </span>
          )}
          <span
            className={
              "ml-1.5 align-middle rounded-sm border px-1 py-px text-[9px] uppercase tracking-wide " +
              (row.relationship === "held_out"
                ? "border-[var(--chart-1)] text-[var(--chart-3)]"
                : "border-dashed border-border text-muted-foreground")
            }
            title={note}
          >
            {RELATIONSHIP_LABELS[row.relationship]}
          </span>
        </span>
        <span className="fig text-destructive">{fmtDivergence(row)}</span>
      </div>
      <p className="mt-1 fig text-sm text-muted-foreground">
        External {fmtValue(row.value ?? null, row)} · PolicyEngine{" "}
        {fmtValue(row.pe?.value ?? null, row)}
      </p>
      {row.diagnosis && (
        <p className="mt-1.5 text-xs">
          <DiagnosisChip d={row.diagnosis} />
          {row.diagnosis.title}
          {row.diagnosis.confidence && (
            <> ({row.diagnosis.confidence} confidence)</>
          )}
        </p>
      )}
      {row.pe?.construction && (
        <p className="mt-1 text-xs text-muted-foreground">
          {row.pe.construction}
        </p>
      )}
      {row.annotations && row.annotations.length > 0 && (
        <p className="mt-1 text-xs text-muted-foreground">
          {[
            ...new Set(
              row.annotations
                .map((id) => slice.annotations?.[id]?.severity)
                .filter(Boolean),
            ),
          ].join(" · ")}{" "}
          annotations apply — see the scorecard row.
        </p>
      )}
    </li>
  );
}
