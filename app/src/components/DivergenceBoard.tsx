import { useMemo } from "react";
import { Badge } from "@policyengine/ui-kit/primitives";
import {
  divergenceScore,
  divergenceTextClass,
  fmtDivergence,
  fmtValue,
} from "../format";
import type { Comparison, Country, Row } from "../types";
import { METRIC_LABELS, PROGRAM_LABELS, countryOf } from "../types";
import type { SpineBucket } from "../spine";
import { AttributionPanel } from "./AttributionPanel";
import { Panel, Tag } from "./ui";

/**
 * The diagnosis queue: the largest material divergences among rows where the
 * concepts are close enough that the delta means something (comparable +
 * constructed only), national totals first, then states.
 */
export function DivergenceBoard({
  data,
  buckets,
  country,
}: {
  data: Comparison;
  buckets: Map<Row, SpineBucket>;
  country: Country;
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

  // A national row's geography code equals its country code ("US" | "UK").
  const national = candidates.filter((r) => r.geography === countryOf(r));
  const states = candidates
    .filter((r) => r.geography !== countryOf(r))
    .slice(0, 30);
  const diagnosed = candidates.filter((r) => r.diagnosis).length;

  return (
    <div className="space-y-4">
      <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
        Total rows beyond tolerance where the two concepts are close enough
        for the difference to mean something (comparable and constructed rows
        only), largest first. National rows seed the diagnosis pipeline;{" "}
        <span className="fig text-foreground">{diagnosed}</span> of{" "}
        <span className="fig text-foreground">{candidates.length}</span>{" "}
        carry a diagnosis.
      </p>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel
          title="National"
          description="Every national total-row divergence beyond tolerance."
        >
          {national.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No national divergences beyond tolerance.
            </p>
          ) : (
            <ol className="space-y-3">
              {national.map((r) => (
                <DivergenceCard key={r.source_column} row={r} data={data} />
              ))}
            </ol>
          )}
        </Panel>
        <Panel
          title="States"
          description="The 30 largest state-level divergences (total rows)."
        >
          {states.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No state divergences beyond tolerance.
            </p>
          ) : (
            <ol className="space-y-3">
              {states.map((r) => (
                <DivergenceCard
                  key={r.source_column + r.geography}
                  row={r}
                  data={data}
                />
              ))}
            </ol>
          )}
        </Panel>
      </div>
      <AttributionPanel country={country} />
    </div>
  );
}

function DivergenceCard({ row, data }: { row: Row; data: Comparison }) {
  const external = countryOf(row) === "US" ? "Urban" : "External";
  return (
    <li className="rounded-md border border-border p-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="font-medium">
            {PROGRAM_LABELS[row.program] ?? row.program}
            <span className="text-muted-foreground">
              {" "}
              · {METRIC_LABELS[row.metric] ?? row.metric}
            </span>
            {row.geography !== countryOf(row) && (
              <span className="fig text-muted-foreground">
                {" "}
                · {row.geography}
              </span>
            )}
          </p>
          <p className="fig mt-0.5 text-xs text-muted-foreground">
            {external} {fmtValue(row.external_value, row.metric)} ·
            PolicyEngine {fmtValue(row.pe_value, row.metric)}
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          <span className={"fig text-lg font-semibold " + divergenceTextClass(row)}>
            {fmtDivergence(row)}
          </span>
          <Tag
            tone={row.calibration_relationship === "held_out" ? "primary" : "dashed"}
            title={row.calibration_basis}
          >
            {row.calibration_relationship.replace(/_/g, " ")}
          </Tag>
        </div>
      </div>
      {row.diagnosis && (
        <p className="mt-2 text-xs">
          <Badge
            variant={
              row.diagnosis.classification === "external_model_issue"
                ? "default"
                : row.diagnosis.classification === "pe_gap"
                  ? "destructive"
                  : "secondary"
            }
            className="mr-1.5 align-middle"
          >
            diagnosed: {row.diagnosis.classification.replace(/_/g, " ")}
          </Badge>
          {row.diagnosis.title} ({row.diagnosis.confidence} confidence
          {row.diagnosis.fix_type
            ? `, fix drafted: ${row.diagnosis.fix_type.replace(/_/g, " ")}`
            : ""}
          )
        </p>
      )}
      {row.pe_construction && (
        <p className="mt-1.5 text-xs text-muted-foreground">
          {row.pe_construction}
        </p>
      )}
      {row.annotations.length > 0 && (
        <p className="mt-1 text-xs text-muted-foreground">
          {row.annotations
            .map((id) => data.annotations[id]?.severity)
            .filter(Boolean)
            .join(" · ")}{" "}
          annotations apply — see the comparison row.
        </p>
      )}
    </li>
  );
}
