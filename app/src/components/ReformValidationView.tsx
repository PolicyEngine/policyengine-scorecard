import { Fragment, useMemo, useState } from "react";
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
import { LabeledSelect, Provenance, Stat, StatusPill, Tag } from "./ui";

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
  UK: "the compute campaign's HMRC ready-reckoner comparisons (each PE score is a current-law static change; HMRC's are projected-FY direct effects against an indexed baseline, so every comparison is constructed-basis by design)",
  BE: BE_REFORM_DESCRIPTION,
  NZ: "New Zealand Treasury official budget-score replication candidates, with fiscal timing and the IWTC termination scenario explicit before a PolicyEngine counterpart attaches",
};

export function ReformValidationView({
  feed,
  country,
}: {
  feed: PopulationsFeed;
  /** Owned by the country selector — this view scopes to it (issue #42). */
  country: Country;
}) {
  const [source, setSource] = useState("all");
  const [status, setStatus] = useState("all");
  const [releasesOnly, setReleasesOnly] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  // Everything below is computed from the COUNTRY-SCOPED slice, never the
  // global summary: the country selection owns this view too, and
  // source/status counts must describe what the table can actually show.
  const inCountry = useMemo(
    () => feed.rows.filter((r) => countryOf(r) === country),
    [feed, country],
  );
  const bySource = useMemo(() => {
    const out: Record<string, number> = {};
    for (const r of inCountry) out[r.source] = (out[r.source] ?? 0) + 1;
    return out;
  }, [inCountry]);
  const byStatus = useMemo(() => {
    const out: Record<string, number> = {};
    for (const r of inCountry)
      out[r.latest.status_effective] = (out[r.latest.status_effective] ?? 0) + 1;
    return out;
  }, [inCountry]);
  const sources = useMemo(() => Object.keys(bySource).sort(), [bySource]);
  const withResult = useMemo(
    () => inCountry.filter((r) => r.results.length > 0).length,
    [inCountry],
  );
  const multiRelease = useMemo(
    () => inCountry.filter((r) => r.results.length > 1).length,
    [inCountry],
  );
  const rows = useMemo(
    () =>
      inCountry.filter((r) => {
        if (source !== "all" && r.source !== source) return false;
        if (status !== "all" && r.latest.status_effective !== status)
          return false;
        if (releasesOnly && r.results.length < 2) return false;
        return true;
      }),
    [inCountry, source, status, releasesOnly],
  );

  const th = "px-3 py-2 font-medium";
  const peLabel = country === "BE" ? "Axiom" : "PolicyEngine";

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-3">
        <Stat
          label="External claims"
          value={inCountry.length.toLocaleString()}
          sub={`${COUNTRY_LABELS[country]} reform scores and references beyond the main comparison`}
        />
        <Stat
          label="With a PolicyEngine result"
          value={withResult.toLocaleString()}
          sub="Each result carries its certified release's exact engine pins"
        />
        <Stat
          label="Multi-release claims"
          value={multiRelease.toLocaleString()}
          sub="Drift across releases is queryable; a scoring-construction change is labeled, not read as drift"
        />
      </div>

      <details className="rounded-lg border border-border bg-card px-4 py-3 text-sm">
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

      <div className="rounded-lg border border-border bg-card p-4">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
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
          <div className="flex items-end gap-2 pb-1">
            <Switch
              id="multi-release"
              checked={releasesOnly}
              onCheckedChange={setReleasesOnly}
            />
            <Label htmlFor="multi-release" className="text-sm">
              Multi-release only
            </Label>
          </div>
          <span className="fig self-end pb-1 text-xs text-muted-foreground sm:text-right">
            {rows.length.toLocaleString()} claims
          </span>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border bg-card">
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
                  className={
                    "cursor-pointer border-b border-border hover:bg-muted/60 " +
                    (expanded === r.claim_id ? "bg-muted/60" : "")
                  }
                  tabIndex={0}
                  aria-expanded={expanded === r.claim_id}
                  onClick={() =>
                    setExpanded(expanded === r.claim_id ? null : r.claim_id)
                  }
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setExpanded(expanded === r.claim_id ? null : r.claim_id);
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
                {expanded === r.claim_id && <RowDetail row={r} />}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
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
                        No PolicyEngine result has been computed for this
                        claim.
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
              {row.source_column} · {METRIC_LABELS[row.metric] ?? row.metric} ·{" "}
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
              </p>
            )}
          </div>
        </div>
      </td>
    </tr>
  );
}

function windowFromPeriod(r: PopulationRow): string {
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
