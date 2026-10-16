import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import { Label, Switch } from "@policyengine/ui-kit/primitives";
import type { Country, PopulationRow, PopulationsFeed } from "../types";
import {
  COUNTRY_LABELS,
  METRIC_LABELS,
  RELATIONSHIP_LABELS,
  STATUS_LABELS,
  comparabilityFigure,
  countryOf,
} from "../types";
import { sourceLabel } from "../sourceLabels";
import { decodeArchive, populationCounts } from "../populations";
import { withBasePath } from "../basePath";
import {
  LabeledSelect,
  Provenance,
  StatusPill,
  Summary,
  TableCard,
  Tag,
} from "./ui";

/**
 * The reform-validation registry (issue #20): every non-Urban claim with a PE
 * result, plus claims explicitly opted into pre-result display. Available
 * results are shown with their full per-release history — one result per
 * certified populace release, engine pins and OBBBA scoring mode in the
 * construction, so cross-release drift is visible. Descriptive only: statuses
 * and calibration relationships label, never grade.
 */
/**
 * The Belgian description is doctrine-bearing (self-attachment disclosure,
 * unresolved official period basis) and pinned by test — reword with care.
 */
export const BE_REFORM_DESCRIPTION =
  "seven Belgian PIT-reform claims plus two JRC EUROMOD-BE claims — EUROMOD J1.0+ totals simulated on uprated EU-SILC 2022 survey input (income year 2021, private households), not administrative statistics — with demo-grade Axiom worker concept-mismatch attachments. Five of the reform claims are PolicyEngine self-attachments: each claim and result records the same Axiom-over-Microcosm-BE computation for income years 2026–2030. The SPF Finances and Cour des comptes claims each carry a constructed cross-attachment. The two official horizon-2030 statements do not specify whether 2030 is an income or assessment year; no shared period basis with the PolicyEngine income-year rows is asserted";

const SCOPE_COPY: Record<Country, string> = {
  US: "the populace reform-validation registry (JCT scores, state fiscal notes, agency actuals, IRS and Census references) plus the compute campaign's TPC, CPSP, PWBM and CBO comparisons",
  UK: "the complete OBR Policy measures database from Budget 1970 to Autumn Budget 2025, including historical HM Treasury costings before the OBR existed, plus the HMRC ready-reckoner comparisons and Autumn Budget 2025 scores from 27 producers. Historical PMD scores load when a fiscal event is selected. Scores without a PolicyEngine result retain their external value and are labeled Not yet computed; a recorded gap finding does not count as a PolicyEngine value",
  BE: BE_REFORM_DESCRIPTION,
  NZ: "New Zealand Treasury official budget-score replication candidates, with fiscal timing and the IWTC termination scenario explicit before a PolicyEngine counterpart attaches",
};

/** Distinct values of one condition key across rows, sorted; rows that
 *  lack the key are counted under "" so a filter can still select them. */
export function conditionValues(
  rows: PopulationRow[],
  key: string,
): Record<string, number> {
  const out: Record<string, number> = {};
  for (const r of rows) {
    const v = r.conditions[key] ?? "";
    out[v] = (out[v] ?? 0) + 1;
  }
  return out;
}

export interface RowFilters {
  source: string;
  status: string;
  releasesOnly: boolean;
  fiscalEvent: string;
  benchmarkClass: string;
}

/** The table's filter, kept pure so it is testable without a DOM.
 *  "all" disables a filter; an empty string matches rows without the key. */
export function filterRows(rows: PopulationRow[], f: RowFilters): PopulationRow[] {
  return rows.filter((r) => {
    if (f.source !== "all" && r.source !== f.source) return false;
    if (f.status !== "all" && r.latest.status_effective !== f.status) return false;
    if (f.releasesOnly && r.results.length < 2) return false;
    if (f.fiscalEvent !== "all" && (r.conditions.fiscal_event ?? "") !== f.fiscalEvent)
      return false;
    if (
      f.benchmarkClass !== "all" &&
      (r.conditions.benchmark_class ?? "") !== f.benchmarkClass
    )
      return false;
    return true;
  });
}

export function ReformValidationView({
  feed,
  country,
  claim,
  onClaimChange,
}: {
  feed: PopulationsFeed;
  /** Owned by the country selector — this view scopes to it (issue #42). */
  country: Country;
  /** The open row, owned by the address bar's ?claim= (issue #177). */
  claim: string | null;
  onClaimChange: (claim: string | null) => void;
}) {
  const [source, setSource] = useState("all");
  const [status, setStatus] = useState("all");
  const [releasesOnly, setReleasesOnly] = useState(false);
  const [fiscalEvent, setFiscalEvent] = useState("all");
  const [benchmarkClass, setBenchmarkClass] = useState("all");
  const [archiveRows, setArchiveRows] = useState<{
    event: string;
    rows: PopulationRow[];
  } | null>(null);
  const [archiveError, setArchiveError] = useState<string | null>(null);
  const archives = useMemo(
    () => (feed.event_archives ?? []).filter((archive) => archive.country === country),
    [feed, country],
  );
  const selectedArchive = archives.find((archive) => archive.fiscal_event === fiscalEvent);
  useEffect(() => {
    setArchiveError(null);
    if (!selectedArchive) return;
    const controller = new AbortController();
    fetch(withBasePath(selectedArchive.path), { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((archive) => {
        if (!controller.signal.aborted)
          setArchiveRows({
            event: selectedArchive.fiscal_event,
            rows: decodeArchive(archive),
          });
      })
      .catch((error) => {
        if (!controller.signal.aborted) setArchiveError(String(error));
      });
    return () => controller.abort();
  }, [selectedArchive]);

  // Facet counts cover the country's complete score inventory. The table
  // adds the selected event's detail to the country-scoped initial rows.
  const inCountry = useMemo(
    () => [
      ...feed.rows.filter((r) => countryOf(r) === country),
      ...(selectedArchive && archiveRows?.event === fiscalEvent
        ? archiveRows.rows.filter((row) => countryOf(row) === country)
        : []),
    ],
    [feed, country, archiveRows, fiscalEvent, selectedArchive],
  );
  const bySource = useMemo(() => {
    const out: Record<string, number> = {};
    for (const r of feed.rows.filter((row) => countryOf(row) === country))
      out[r.source] = (out[r.source] ?? 0) + 1;
    for (const archive of archives)
      out[archive.source] = (out[archive.source] ?? 0) + archive.claims;
    return out;
  }, [feed, country, archives]);
  const byStatus = useMemo(() => {
    const out: Record<string, number> = {};
    for (const r of feed.rows.filter((row) => countryOf(row) === country))
      out[r.latest.status_effective] = (out[r.latest.status_effective] ?? 0) + 1;
    for (const archive of archives)
      for (const [status, count] of Object.entries(archive.by_latest_status))
        out[status] = (out[status] ?? 0) + count;
    return out;
  }, [feed, country, archives]);
  const sources = useMemo(() => Object.keys(bySource).sort(), [bySource]);
  const allClaims = populationCounts(feed, country);
  // Retrieval by event and by benchmark class (#136): both are claim
  // conditions, so the option lists come from the rows, like sources.
  const byEvent = useMemo(() => {
    const out = conditionValues(feed.rows.filter((row) => countryOf(row) === country), "fiscal_event");
    for (const archive of archives)
      out[archive.fiscal_event] = (out[archive.fiscal_event] ?? 0) + archive.claims;
    return out;
  }, [feed, country, archives]);
  const byClass = useMemo(
    () => {
      const out = conditionValues(feed.rows.filter((row) => countryOf(row) === country), "benchmark_class");
      for (const archive of archives)
        for (const [classification, count] of Object.entries(archive.by_benchmark_class))
          out[classification] = (out[classification] ?? 0) + count;
      return out;
    },
    [feed, country, archives],
  );
  const rows = useMemo(
    () =>
      filterRows(inCountry, {
        source,
        status,
        releasesOnly,
        fiscalEvent,
        benchmarkClass,
      }),
    [inCountry, source, status, releasesOnly, fiscalEvent, benchmarkClass],
  );

  // A claim that arrives from the address bar (a deep link, back/forward)
  // is revealed once: filters that hide its row are cleared, then the row
  // is scrolled into view and focused. A row the reader clicks opens in
  // place, and a claim this country's rows lack opens nothing.
  const revealed = useRef<string | null>(null);
  const openRow = useRef<HTMLTableRowElement>(null);
  const toggle = (id: string) => {
    const next = claim === id ? null : id;
    revealed.current = next;
    onClaimChange(next);
  };
  useEffect(() => {
    if (claim === null || claim === revealed.current) return;
    const row = inCountry.find((r) => r.claim_id === claim);
    if (row && !rows.includes(row)) {
      setSource("all");
      setStatus("all");
      setReleasesOnly(false);
      setBenchmarkClass("all");
      if ((row.conditions.fiscal_event ?? "") !== fiscalEvent)
        setFiscalEvent("all");
      return; // revealed on the render that shows it
    }
    revealed.current = claim;
    openRow.current?.scrollIntoView({ block: "center" });
    openRow.current?.focus({ preventScroll: true });
  }, [claim, inCountry, rows, fiscalEvent]);

  const th = "px-3 py-2 font-medium";
  const peLabel = country === "BE" ? "Axiom" : "PolicyEngine";

  return (
    <div className="space-y-4">
      <Summary
        figures={[
          {
            label: "External claims",
            value: allClaims.claims.toLocaleString(),
            sub: `${COUNTRY_LABELS[country]} reform scores and references beyond the main comparison`,
          },
          {
            label: "With a PolicyEngine value",
            value: allClaims.with_value.toLocaleString(),
            sub: `${allClaims.with_result.toLocaleString()} recorded results, including gaps without a value`,
          },
          {
            label: "Without a PolicyEngine result",
            value: allClaims.without_result.toLocaleString(),
          },
          {
            label: "Multi-release claims",
            value: allClaims.multi_release_claims.toLocaleString(),
            sub: "Drift across releases is queryable; a scoring-construction change is labeled, not read as drift",
          },
        ]}
      >
        <details className="text-sm">
          <summary className="cursor-pointer font-medium">
            Scope and method note for {COUNTRY_LABELS[country]}
          </summary>
          <p className="mt-2 max-w-3xl leading-6 text-muted-foreground">
            This registry covers {SCOPE_COPY[country]}. Nothing here is a
            pass/fail grade: statuses and calibration relationships label, never
            grade.
          </p>
          <Provenance
            className="mt-2"
            items={[
              "populations feed · exported from scorecard.db",
              `built ${feed.built}`,
              `scope: ${COUNTRY_LABELS[country]} (the country selector owns it)`,
              "per-release results carry their own engine and data-bundle provenance",
            ]}
          />
        </details>
      </Summary>

      {archives.length > 0 && (
        <p className="text-sm text-muted-foreground" role="status">
          {archiveError ? (
            <>Could not load the selected event&apos;s scores ({archiveError}). Select another event and return to retry.</>
          ) : selectedArchive && archiveRows?.event !== fiscalEvent ? (
            <>Loading {selectedArchive.claims.toLocaleString()} scores for {selectedArchive.label}…</>
          ) : fiscalEvent === "all" ? (
            <>{archives.reduce((total, archive) => total + archive.claims, 0).toLocaleString()} additional PMD scores across {archives.length} fiscal events are included in the figures above. Select a fiscal event to view its scores.</>
          ) : null}
        </p>
      )}

      <TableCard
        toolbar={
          <>
            <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
              <LabeledSelect
                label="Source"
                value={source}
                onChange={setSource}
                options={[
                  { value: "all", label: "All sources" },
                  ...sources.map((s) => ({
                    value: s,
                    label: `${sourceLabel(s)} (${bySource[s]})`,
                  })),
                ]}
              />
              <LabeledSelect
                label="Latest status"
                value={status}
                onChange={setStatus}
                options={[
                  { value: "all", label: "All statuses" },
                  ...Object.entries(byStatus).map(([s, n]) => ({
                    value: s,
                    label: `${STATUS_LABELS[s as keyof typeof STATUS_LABELS] ?? s} (${n})`,
                  })),
                ]}
              />
              <LabeledSelect
                label="Fiscal event"
                value={fiscalEvent}
                onChange={setFiscalEvent}
                options={[
                  {
                    value: "all",
                    label: archives.length > 0 ? "Select an event for PMD scores" : "All events",
                  },
                  ...Object.entries(byEvent)
                    .sort()
                    .map(([v, n]) => ({
                      value: v,
                      label: `${v === "" ? "(none recorded)" : archives.find((archive) => archive.fiscal_event === v)?.label ?? v.replace(/_/g, " ")} (${n})`,
                    })),
                ]}
              />
              <LabeledSelect
                label="Benchmark class"
                value={benchmarkClass}
                onChange={setBenchmarkClass}
                options={[
                  { value: "all", label: "All classes" },
                  ...Object.entries(byClass)
                    .sort()
                    .map(([v, n]) => ({
                      value: v,
                      label: `${v === "" ? "(none recorded)" : v.replace(/_/g, " ")} (${n})`,
                    })),
                ]}
              />
            </div>
            <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-border pt-3">
              <div className="flex items-center gap-2">
                <Switch
                  id="multi-release"
                  checked={releasesOnly}
                  onCheckedChange={setReleasesOnly}
                />
                <Label htmlFor="multi-release" className="text-sm">
                  Multi-release only
                </Label>
              </div>
              <span className="fig ml-auto text-xs text-muted-foreground">
                {rows.length.toLocaleString()} claims shown
              </span>
            </div>
          </>
        }
      >
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-muted text-left text-xs text-muted-foreground">
              <th className={th}>Claim</th>
              <th className={th}>Source</th>
              <th className={th}>Window</th>
              <th className={th + " text-right"}>External</th>
              <th className={th + " text-right"}>{peLabel}</th>
              <th className={th + " text-right"}>Divergence</th>
              <th className={th}>Status</th>
              <th className={th}>Relationship</th>
              <th className={th + " text-right"}>Releases</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td
                  colSpan={9}
                  className="px-3 py-8 text-center text-sm text-muted-foreground"
                >
                  No claims match these filters.
                </td>
              </tr>
            )}
            {rows.map((r) => (
              <Fragment key={r.claim_id}>
                <tr
                  ref={claim === r.claim_id ? openRow : undefined}
                  className={
                    "cursor-pointer border-b border-border hover:bg-muted/60 " +
                    (claim === r.claim_id ? "bg-muted/60" : "")
                  }
                  tabIndex={0}
                  aria-expanded={claim === r.claim_id}
                  onClick={() => toggle(r.claim_id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      toggle(r.claim_id);
                    }
                  }}
                >
                  <td className="px-3 py-2">
                    <span className="line-clamp-2 block max-w-xs lg:max-w-sm">
                      {r.url ? (
                        <a
                          className="underline decoration-muted-foreground/50 underline-offset-2 hover:decoration-foreground"
                          href={r.url}
                          target="_blank"
                          rel="noreferrer"
                          title="Open the source document"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {r.name || r.source_column}
                          {" ↗"}
                        </a>
                      ) : (
                        r.name || r.source_column
                      )}
                    </span>
                    {r.conditions.fiscal_measure === "exchequer_impact" && (
                      <Tag className="mt-1">Exchequer impact</Tag>
                    )}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2">
                    {sourceLabel(r.source)}
                  </td>
                  <td className="fig px-3 py-2 text-xs text-muted-foreground">
                    <span className="block max-w-40">
                      {r.window || windowFromPeriod(r)}
                    </span>
                  </td>
                  <td className="fig whitespace-nowrap px-3 py-2 text-right">
                    {fmtV(r.external_value, r.value_kind)}
                  </td>
                  <td className="fig whitespace-nowrap px-3 py-2 text-right">
                    {fmtV(r.latest.value, r.value_kind)}
                  </td>
                  <td className="fig whitespace-nowrap px-3 py-2 text-right">
                    {r.results.length === 0
                      ? "—"
                      : comparabilityFigure(
                          r.latest.status_effective,
                          "not comparable",
                          () => fmtDiv(r),
                        )}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2">
                    <StatusPill status={r.latest.status_effective} />
                  </td>
                  <td className="whitespace-nowrap px-3 py-2">
                    <Tag
                      title={
                        r.calibration_relationship === "consumed_as_target"
                          ? "This value is on the calibration target surface — agreement is a tautology, labeled and never counted as validation."
                          : undefined
                      }
                    >
                      {RELATIONSHIP_LABELS[r.calibration_relationship]}
                    </Tag>
                  </td>
                  <td className="fig whitespace-nowrap px-3 py-2 text-right">
                    {r.results.length}
                  </td>
                </tr>
                {claim === r.claim_id && <RowDetail row={r} />}
              </Fragment>
            ))}
          </tbody>
        </table>
      </TableCard>
    </div>
  );
}

function RowDetail({ row }: { row: PopulationRow }) {
  return (
    <tr className="border-b border-border bg-muted/40">
      <td colSpan={9} className="px-4 py-3">
        <div className="grid gap-4 text-xs md:grid-cols-2">
          <div className="min-w-0">
            <p className="mb-1 font-semibold">Per-release history</p>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="text-left text-muted-foreground">
                    <th className="py-1 pr-3 font-medium">Release</th>
                    <th className="py-1 pr-3 font-medium">Engine</th>
                    <th className="py-1 pr-3 text-right font-medium">Value</th>
                    <th className="py-1 pr-3 text-right font-medium">Ratio</th>
                    <th className="py-1 font-medium">Construction</th>
                  </tr>
                </thead>
                <tbody>
                  {row.results.length === 0 ? (
                    <tr className="border-t border-border">
                      <td colSpan={5} className="py-2 text-muted-foreground">
                        No PolicyEngine result is recorded for this claim.
                      </td>
                    </tr>
                  ) : (
                    row.results.map((res) => (
                      <tr key={res.data_bundle} className="border-t border-border">
                        <td className="fig py-1 pr-3">{res.release}</td>
                        <td className="fig break-all py-1 pr-3">
                          {res.engine_version}
                          {res.status_effective !== res.status && (
                            <Tag
                              className="ml-1.5"
                              title="The recorded status is downgraded by the baseline guard (issue #13): the executed baseline differs from, or is unverifiable against, the claim's world."
                            >
                              {STATUS_LABELS[res.status_effective]}
                            </Tag>
                          )}
                        </td>
                        <td className="fig py-1 pr-3 text-right">
                          {fmtV(res.value, row.value_kind)}
                        </td>
                        <td className="fig py-1 pr-3 text-right">
                          {comparabilityFigure(
                            res.status_effective,
                            "—",
                            () => ratioOf(res.value, row.external_value),
                          )}
                        </td>
                        <td className="fig break-all py-1 text-muted-foreground">
                          {res.construction || "—"}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            {row.results.some((res) => res.annotations.length > 0) && (
              <ul className="mt-2 space-y-1 text-muted-foreground">
                {row.results.flatMap((res) =>
                  res.annotations.map((a, i) => (
                    <li key={`${res.data_bundle}-${i}`}>
                      <Tag className="mr-1.5">{res.release}</Tag>
                      {a}
                    </li>
                  )),
                )}
              </ul>
            )}
            {row.results.length > 0 && (
              <p className="mt-2 text-muted-foreground">
                A construction change between releases (e.g. an OBBBA scoring
                mode) is part of the label above — compare values only within
                the same construction.
              </p>
            )}
          </div>
          <div className="min-w-0">
            <p className="mb-1 font-semibold">Claim</p>
            <p className="text-muted-foreground">
              {row.publication_title || "—"}
              {row.url && (
                <>
                  {" · "}
                  <a
                    className="underline"
                    href={row.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    source
                  </a>
                </>
              )}
            </p>
            <p className="fig mt-2 break-words text-muted-foreground">
              {row.source_column} ·{" "}
              {row.conditions.fiscal_measure === "exchequer_impact"
                ? "Exchequer impact"
                : METRIC_LABELS[row.metric] ?? row.metric} ·{" "}
              {row.time_basis} {row.period}
              {row.period_start !== null &&
                ` (window ${row.period_start}–${row.period_end})`}
            </p>
            {Object.entries(row.conditions).length > 0 && (
              <p className="mt-2 break-words text-muted-foreground">
                {Object.entries(row.conditions)
                  .map(([k, v]) => `${k}: ${v}`)
                  .join(" · ")}
              </p>
            )}
            {row.diagnosis && (
              <p className="mt-2">
                <Tag className="mr-1.5">
                  {row.diagnosis.class.replace(/_/g, " ")}
                </Tag>
                {row.diagnosis.rationale}
                {row.diagnosis.action_link && (
                  <>
                    {" "}
                    <a
                      href={row.diagnosis.action_link}
                      target="_blank"
                      rel="noreferrer"
                      className="underline underline-offset-2"
                    >
                      where this is tracked
                    </a>
                  </>
                )}
              </p>
            )}
          </div>
        </div>
      </td>
    </tr>
  );
}

function windowFromPeriod(r: PopulationRow): string {
  if (r.time_basis === "fiscal_year" && r.conditions.fy)
    return `FY${r.conditions.fy}`;
  const basis = r.time_basis === "fiscal_year" ? "FY" : "";
  return `${basis}${r.period}`;
}

function fmtV(v: number | null, kind: string): string {
  if (v === null || v === undefined) return "—";
  if (kind === "share") return `${(v * 100).toFixed(1)}%`;
  if (kind === "percent") return `${v.toFixed(1)}%`;
  if (kind === "index") return v.toFixed(3);
  // Currency follows value_kind, never a $ default: GBP and NZD rows use
  // their own symbols, while count rows carry no symbol at all.
  const cur = kind.startsWith("gbp")
    ? "£"
    : kind.startsWith("eur")
      ? "€"
      : kind.startsWith("nzd")
        ? "NZ$"
        : kind.startsWith("usd") || kind === "usd"
          ? "$"
          : kind === "count"
            ? ""
            : "$";
  const a = Math.abs(v);
  const sign = v < 0 ? "−" : "";
  if (a >= 1e9) return `${sign}${cur}${(a / 1e9).toFixed(2)}B`;
  if (a >= 1e6) return `${sign}${cur}${(a / 1e6).toFixed(1)}M`;
  if (a >= 1e3) return `${sign}${cur}${(a / 1e3).toFixed(0)}k`;
  return `${sign}${cur}${a.toFixed(0)}`;
}

function fmtDiv(r: PopulationRow): string {
  const pe = r.latest.value;
  const ext = r.external_value;
  if (pe === null || ext === null) return "";
  if (r.value_kind === "share") {
    const pp = (pe - ext) * 100;
    return `${pp >= 0 ? "+" : "−"}${Math.abs(pp).toFixed(1)}pp`;
  }
  if (ext === 0) return "";
  const pct = (pe / ext - 1) * 100;
  return `${pct >= 0 ? "+" : "−"}${Math.abs(pct).toFixed(0)}%`;
}

function ratioOf(pe: number | null, ext: number | null): string {
  if (pe === null || ext === null || ext === 0) return "—";
  return (pe / ext).toFixed(2);
}
