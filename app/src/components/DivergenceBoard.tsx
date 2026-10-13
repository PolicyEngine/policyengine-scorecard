import { useMemo } from "react";
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
import { useNav } from "../navigation";
import { LinkButton, Panel, Summary, Tag } from "./ui";

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
      <Summary
        intro={
          <>
            Total rows beyond tolerance where the two concepts are close enough
            for the difference to mean something (comparable and constructed
            rows only), largest first. National rows seed the diagnosis
            pipeline; <span className="fig text-foreground">{diagnosed}</span>{" "}
            of <span className="fig text-foreground">{candidates.length}</span>{" "}
            carry a diagnosis.
          </>
        }
      />
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
            <ol className="-my-4 divide-y divide-border">
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
            <ol className="-my-4 divide-y divide-border">
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
  const nav = useNav();
  const external = countryOf(row) === "US" ? "Urban" : "External";
  // One entry per annotation severity, in first-seen order, with its count:
  // "period · construction · period · period" reads as period ×3, construction.
  const severities = new Map<string, number>();
  for (const id of row.annotations) {
    const sev = data.annotations[id]?.severity;
    if (sev) severities.set(sev, (severities.get(sev) ?? 0) + 1);
  }
  const d = row.diagnosis;
  return (
    <li className="py-4">
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
          <p className="mt-1 flex flex-wrap gap-x-4 text-sm">
            <span className="whitespace-nowrap">
              <span className="text-muted-foreground">{external}</span>{" "}
              <span className="fig">{fmtValue(row.external_value, row.metric)}</span>
            </span>
            <span className="whitespace-nowrap">
              <span className="text-muted-foreground">PolicyEngine</span>{" "}
              <span className="fig">{fmtValue(row.pe_value, row.metric)}</span>
            </span>
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
      {(d || row.pe_construction || severities.size > 0) && (
        <dl className="mt-3 grid gap-x-4 gap-y-1 text-xs leading-5 sm:grid-cols-[6.5rem_1fr] sm:gap-y-2">
          {d && (
            <>
              <dt className="text-muted-foreground">Diagnosis</dt>
              <dd className="mb-1 sm:mb-0">
                <span className="font-medium">
                  {sentence(d.classification.replace(/_/g, " "))}
                </span>
                {" — "}
                {d.title}
                <span className="block text-muted-foreground">
                  {sentence(d.confidence)} confidence
                  {d.fix_type
                    ? ` · fix drafted: ${d.fix_type.replace(/_/g, " ")}`
                    : ""}
                </span>
              </dd>
            </>
          )}
          {row.pe_construction && (
            <>
              <dt className="text-muted-foreground">Construction</dt>
              <dd className="fig mb-1 text-muted-foreground sm:mb-0">
                {row.pe_construction}
              </dd>
            </>
          )}
          {severities.size > 0 && (
            <>
              <dt className="text-muted-foreground">Annotations</dt>
              <dd className="flex flex-wrap items-center gap-1.5">
                {[...severities].map(([sev, n]) => (
                  <Tag key={sev} tone="outline">
                    {n > 1 ? `${sev} ×${n}` : sev}
                  </Tag>
                ))}
                <LinkButton
                  className="ml-1 text-xs"
                  onClick={() =>
                    nav.go("scorecard", {
                      program: row.program,
                      metric: row.metric,
                      geography: row.geography,
                      subgroup: "total",
                      bucket: null,
                    })
                  }
                >
                  View row
                </LinkButton>
              </dd>
            </>
          )}
        </dl>
      )}
    </li>
  );
}

const sentence = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
