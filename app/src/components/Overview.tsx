import { useMemo } from "react";
import {
  closeness,
  divergenceTextClass,
  fmtDivergence,
  fmtValue,
} from "../format";
import type {
  Comparison,
  Country,
  LanesFeed,
  PopulationsFeed,
  Row,
} from "../types";
import {
  COUNTRY_LABELS,
  METRIC_LABELS,
  PROGRAM_LABELS,
  STATUS_LABELS,
  countryOf,
} from "../types";
import type { SpineBucket } from "../spine";
import { sourceLabel } from "../sourceLabels";
import { useNav } from "../navigation";
import { CoverageSpine } from "./CoverageSpine";
import { LinkButton, Panel, Provenance, Stat, Tag } from "./ui";

/**
 * The landing view: what the instance covers, how the held-out record
 * stands, what is running, and where to go next. Every figure here is a
 * count over the country-scoped feeds — nothing is graded.
 */
export function Overview({
  data,
  scoped,
  buckets,
  lanes,
  populations,
  country,
}: {
  data: Comparison;
  scoped: Comparison;
  buckets: Map<Row, SpineBucket>;
  lanes: LanesFeed | null;
  populations: PopulationsFeed | null;
  country: Country;
}) {
  const nav = useNav();
  const rows = scoped.rows;
  const hasRows = rows.length > 0;
  const external = country === "US" ? "Urban" : "External";

  const counts = useMemo(() => {
    const out: Partial<Record<SpineBucket, number>> = {};
    for (const r of rows) {
      const b = buckets.get(r)!;
      out[b] = (out[b] ?? 0) + 1;
    }
    return out;
  }, [rows, buckets]);
  const compared =
    (counts.close ?? 0) + (counts.moderate ?? 0) + (counts.far ?? 0);
  const withValues = compared + (counts.concept_mismatch ?? 0);
  const published = rows.length - (counts.suppressed ?? 0);
  const programs = new Set(
    rows.map((r) => r.program).filter((p) => p !== "spm_poverty"),
  ).size;

  // Held-out record: the only published "validation" column (issue #1).
  const heldOut = rows.filter(
    (r) =>
      r.calibration_relationship === "held_out" &&
      ["comparable", "constructed"].includes(r.status) &&
      r.pe_value !== null &&
      r.external_value !== null,
  );
  const heldOutClose = heldOut.filter((r) => closeness(r) === "close").length;

  const topDivergences = useMemo(
    () =>
      rows
        .filter(
          (r) =>
            r.geography === countryOf(r) &&
            r.subgroup === "total" &&
            r.variant === null &&
            ["comparable", "constructed"].includes(r.status) &&
            ["moderate", "far"].includes(closeness(r) ?? ""),
        )
        .slice(0, 6),
    [rows],
  );

  const countryLanes = (lanes?.lanes ?? []).filter(
    (l) => countryOf(l) === country,
  );
  const running = countryLanes.filter((l) => l.running);
  const stageCounts = useMemo(() => {
    const out: Record<string, number> = {};
    for (const l of countryLanes) out[l.stage] = (out[l.stage] ?? 0) + 1;
    return Object.entries(out).sort((a, b) => b[1] - a[1]);
  }, [countryLanes]);

  const claims = useMemo(
    () => (populations?.rows ?? []).filter((r) => countryOf(r) === country),
    [populations, country],
  );
  const claimsWithResult = claims.filter((r) => r.results.length > 0).length;
  const claimsMulti = claims.filter((r) => r.results.length > 1).length;
  const claimsBySource = useMemo(() => {
    const out: Record<string, number> = {};
    for (const r of claims) out[r.source] = (out[r.source] ?? 0) + 1;
    return Object.entries(out).sort((a, b) => b[1] - a[1]);
  }, [claims]);
  const claimsByStatus = useMemo(() => {
    const out: Record<string, number> = {};
    for (const r of claims)
      out[r.latest.status_effective] =
        (out[r.latest.status_effective] ?? 0) + 1;
    return out;
  }, [claims]);

  const pct = (a: number, b: number) =>
    b === 0 ? undefined : `${Math.round((a / b) * 100)}%`;
  const b = data.pe_bundle;
  const datasetId = (b.certified_data_build_id ?? "").split("-").slice(-2)[0];

  return (
    <div className="space-y-4">
      {hasRows ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Stat
            label="Published cells"
            value={published.toLocaleString()}
            sub={`${programs} programs${
              country === "US" ? " and the poverty counterfactual" : ""
            }`}
          />
          <Stat
            label="With a PolicyEngine counterpart"
            value={withValues.toLocaleString()}
            unit={pct(withValues, published)}
          />
          <Stat
            label="Within tolerance"
            value={(counts.close ?? 0).toLocaleString()}
            unit={pct(counts.close ?? 0, compared)}
            sub="Of compared cells"
          />
          <Stat
            label="Held-out within tolerance"
            value={heldOutClose.toLocaleString()}
            unit={`of ${heldOut.length.toLocaleString()}`}
            sub="Cells PolicyEngine never calibrated toward"
          />
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Stat
            label="External claims"
            value={claims.length.toLocaleString()}
            sub="On reform validation"
          />
          <Stat
            label="With a PolicyEngine result"
            value={claimsWithResult.toLocaleString()}
            unit={pct(claimsWithResult, claims.length)}
          />
          <Stat
            label="Comparable or constructed"
            value={(
              (claimsByStatus.comparable ?? 0) +
              (claimsByStatus.constructed ?? 0)
            ).toLocaleString()}
            sub={Object.entries(claimsByStatus)
              .map(
                ([s, n]) =>
                  `${n} ${(STATUS_LABELS[s as keyof typeof STATUS_LABELS] ?? s).toLowerCase()}`,
              )
              .join(" · ")}
          />
          <Stat
            label="Multi-release claims"
            value={claimsMulti.toLocaleString()}
          />
        </div>
      )}

      {hasRows ? (
        <Panel
          title="Coverage"
          description="Select a segment to open the comparison table filtered to it."
        >
          <CoverageSpine
            rows={rows}
            buckets={buckets}
            active={null}
            onSelect={(bucket) => nav.go("scorecard", { bucket })}
          />
          {country === "US" && (
            <p className="mt-3 text-xs text-muted-foreground">
              {PROGRAM_LABELS.liheap} and {PROGRAM_LABELS.ccdf} are honest
              gaps: no PolicyEngine model consumes those cells today.
            </p>
          )}
        </Panel>
      ) : (
        <Panel title={`Where ${COUNTRY_LABELS[country]} stands`}>
          <p className="text-sm leading-6 text-muted-foreground">
            <CountryScopeNote country={country} laneCount={countryLanes.length} />
          </p>
        </Panel>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {hasRows ? (
          <Panel
            className="lg:col-span-2"
            title="Largest national divergences"
            action={
              <LinkButton onClick={() => nav.go("divergences")}>
                All divergences
              </LinkButton>
            }
          >
            {topDivergences.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No national divergences beyond tolerance.
              </p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-muted-foreground">
                      <th className="pb-2 pr-3 font-medium">Program · metric</th>
                      <th className="pb-2 pr-3 text-right font-medium">
                        {external}
                      </th>
                      <th className="pb-2 pr-3 text-right font-medium">
                        PolicyEngine
                      </th>
                      <th className="pb-2 text-right font-medium">Δ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {topDivergences.map((r) => (
                      <tr key={r.source_column} className="border-t border-border">
                        <td className="py-2 pr-3">
                          <span className="font-medium">
                            {PROGRAM_LABELS[r.program] ?? r.program}
                          </span>
                          <span className="text-muted-foreground">
                            {" "}
                            · {METRIC_LABELS[r.metric] ?? r.metric}
                          </span>
                          {r.calibration_relationship !== "held_out" && (
                            <Tag
                              tone="dashed"
                              className="ml-1.5"
                              title={r.calibration_basis}
                            >
                              {r.calibration_relationship === "seed_source"
                                ? "seed"
                                : "target"}
                            </Tag>
                          )}
                        </td>
                        <td className="fig py-2 pr-3 text-right">
                          {fmtValue(r.external_value, r.metric)}
                        </td>
                        <td className="fig py-2 pr-3 text-right">
                          {fmtValue(r.pe_value, r.metric)}
                        </td>
                        <td
                          className={
                            "fig py-2 text-right " + divergenceTextClass(r)
                          }
                        >
                          {fmtDivergence(r)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>
        ) : (
          <Panel
            className="lg:col-span-2"
            title="Reform validation by source"
            action={
              <LinkButton onClick={() => nav.go("validation")}>
                All claims
              </LinkButton>
            }
          >
            {claimsBySource.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No claims registered for {COUNTRY_LABELS[country]} yet.
              </p>
            ) : (
              <ul className="divide-y divide-border">
                {claimsBySource.slice(0, 6).map(([s, n]) => (
                  <li
                    key={s}
                    className="flex items-baseline justify-between gap-3 py-2 text-sm"
                  >
                    <span>{sourceLabel(s)}</span>
                    <span className="fig text-muted-foreground">{n}</span>
                  </li>
                ))}
              </ul>
            )}
          </Panel>
        )}

        <Panel title="Pipeline">
          {countryLanes.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No lanes registered for this country.
            </p>
          ) : (
            <>
              {running.length > 0 ? (
                <ul className="space-y-2">
                  {running.map((l) => (
                    <li key={l.id} className="flex items-start gap-2 text-sm">
                      <span
                        aria-hidden
                        className="mt-2 inline-block h-1.5 w-1.5 shrink-0 animate-pulse rounded-full bg-chart-1"
                      />
                      <span className="min-w-0">
                        <span className="font-medium">{l.source}</span>
                        <span className="text-muted-foreground">
                          {" "}
                          · {l.area}
                        </span>
                        <span className="block text-xs text-muted-foreground">
                          {l.stage} · updated {l.updated}
                        </span>
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No lanes running.
                </p>
              )}
              <ul className="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-border pt-3 text-xs text-muted-foreground">
                {stageCounts.map(([stage, n]) => (
                  <li key={stage}>
                    <span className="fig text-foreground">{n}</span> {stage}
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-xs text-muted-foreground">
                {countryLanes.length} lanes registered in data/lanes.json.
              </p>
            </>
          )}
        </Panel>
      </div>

      <Provenance
        className="px-1"
        items={
          country === "US"
            ? [
                `${data.source_meta.id} · fetched ${data.source_meta.fetched} · ${data.source_meta.period}`,
                `${b.runtime_dataset} @ ${datasetId} · ${b.model_package} ${b.model_version} · annual 2024`,
                `built ${data.built}`,
              ]
            : [
                `populations feed built ${populations?.built ?? "—"}`,
                `lanes updated ${lanes?.updated ?? "—"}`,
              ]
        }
      />
    </div>
  );
}

/** Doctrine-bearing per-country scope notes (issue #42); reword with care. */
function CountryScopeNote({
  country,
  laneCount,
}: {
  country: Country;
  laneCount: number;
}) {
  if (country === "BE")
    return (
      <>
        Belgium&apos;s registered claims — seven on the 15 July 2026 PIT reform
        from SPF Finances, Cour des comptes and PolicyEngine, plus five JRC
        EUROMOD-BE model claims (EUROMOD totals simulated on uprated EU-SILC
        survey input, not administrative statistics) — live on Reform
        validation. The two available Axiom values on the JRC claims have
        period, population-basis and scope gaps, so they are labeled concept
        mismatch there rather than entering this comparison grid.
      </>
    );
  if (country === "NZ")
    return (
      <>
        New Zealand Treasury official budget scores live on Reform validation.
        Claims appear there even before a PolicyEngine result is available,
        labeled Not yet computed; their external values stay visible as
        replicated estimates are added.
      </>
    );
  if (country === "UK")
    return (
      <>
        The first UK PolicyEngine results — 14 HMRC ready-reckoner scores,
        held-out relationship on a constructed comparison basis (PolicyEngine
        current-law statics against HMRC&apos;s indexed-baseline FY
        projections) — are on Reform validation. The ingested DWP, HBAI, OBR
        and UKMOD claims are waiting on PolicyEngine computes; a UK record
        lands on this overview when UK comparisons join the feed.
      </>
    );
  return (
    <>
      No {country} comparison cells yet — {laneCount} {country} lanes are
      registered in data/lanes.json and tracked below. The country stays on the
      page while its pipeline runs.
    </>
  );
}
