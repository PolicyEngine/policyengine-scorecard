import { Fragment, useMemo, useState } from "react";
import type { Country, PopulationRow, PopulationsFeed } from "../types";
import {
  COUNTRY_LABELS,
  RELATIONSHIP_LABELS,
  STATUS_LABELS,
  comparabilityFigure,
  countryOf,
} from "../types";
import { sourceLabel } from "../sourceLabels";

/**
 * The reform-validation registry (issue #20): every non-Urban claim in
 * scorecard.db with a PE result, shown with its full per-release history —
 * one result per certified populace release, engine pins and OBBBA scoring
 * mode in the construction, so cross-release drift is visible. Descriptive
 * only: statuses and calibration relationships label, never grade.
 */
/**
 * The Belgian description is doctrine-bearing (self-attachment disclosure,
 * unresolved official period basis) and pinned by test — reword with care.
 */
export const BE_REFORM_DESCRIPTION =
  "two JRC EUROMOD-BE claims with demo-grade Axiom worker concept-mismatch attachments, plus seven Belgian PIT-reform claims. Five are PolicyEngine self-attachments: each claim and result records the same Axiom-over-Microcosm-BE computation for income years 2026–2030. The SPF Finances and Cour des comptes claims each carry a constructed cross-attachment. The two official horizon-2030 statements do not specify whether 2030 is an income or assessment year; no shared period basis with the PolicyEngine income-year rows is asserted";

export function ReformValidationView({
  feed,
  country,
}: {
  feed: PopulationsFeed;
  /** Owned by the header toggle — this view scopes to it (issue #42). */
  country: Country;
}) {
  const [source, setSource] = useState("all");
  const [status, setStatus] = useState("all");
  const [releasesOnly, setReleasesOnly] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  // Everything below is computed from the COUNTRY-SCOPED slice, never the
  // global summary: the header's country selection owns this view too, and
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

  const sel = "h-8 rounded-md border border-border bg-background px-2 text-sm";

  return (
    <div>
      <p className="mb-4 max-w-3xl text-sm leading-6 text-muted-foreground">
        Reform scores and references beyond the Urban comparison:{" "}
        <b className="fig text-foreground">{inCountry.length.toLocaleString()}</b>{" "}
        {COUNTRY_LABELS[country]} external claims —{" "}
        {country === "US"
          ? "the populace reform-validation registry (JCT scores, state fiscal notes, agency actuals, IRS and Census references) plus the compute campaign's TPC, CPSP, PWBM and CBO comparisons"
          : country === "UK"
            ? "the compute campaign's HMRC ready-reckoner comparisons (each PE score is a current-law static change; HMRC's are projected-FY direct effects against an indexed baseline, so every comparison is constructed-basis by design)"
            : BE_REFORM_DESCRIPTION}{" "}
        — where each available result carries its certified release's exact
        engine pins.{" "}
        <b className="fig text-foreground">{multiRelease.toLocaleString()}</b>{" "}
        carry results from more than one release, so drift across releases is
        queryable, and a scoring-construction change is labeled in the history
        rather than read as drift. Nothing here is a pass/fail grade.
      </p>
      <p className="mb-4 fig text-[11px] text-muted-foreground">
        populations feed · exported from scorecard.db · built {feed.built} ·
        scope: {COUNTRY_LABELS[country]} (the header toggle owns it) ·
        per-release results carry their own engine + data-bundle provenance (the
        page-top stamp describes the Urban comparison only)
      </p>

      <div className="mb-3 flex flex-wrap items-end gap-3">
        <label className="text-xs text-muted-foreground">
          Source
          <br />
          <select
            className={sel}
            value={source}
            onChange={(e) => setSource(e.target.value)}
          >
            <option value="all">All sources</option>
            {sources.map((s) => (
              <option key={s} value={s}>
                {sourceLabel(s)} ({bySource[s]})
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted-foreground">
          Latest status
          <br />
          <select
            className={sel}
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="all">All statuses</option>
            {Object.entries(byStatus).map(([s, n]) => (
              <option key={s} value={s}>
                {STATUS_LABELS[s as keyof typeof STATUS_LABELS] ?? s} ({n})
              </option>
            ))}
          </select>
        </label>
        <label className="flex h-8 items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={releasesOnly}
            onChange={(e) => setReleasesOnly(e.target.checked)}
          />
          Multi-release only
        </label>
        <span className="ml-auto text-xs text-muted-foreground fig">
          {rows.length.toLocaleString()} claims
        </span>
      </div>

      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/60 text-left text-xs text-muted-foreground">
              <th className="px-2 py-2 font-medium">Claim</th>
              <th className="px-2 py-2 font-medium">Source</th>
              <th className="px-2 py-2 font-medium">Window</th>
              <th className="px-2 py-2 text-right font-medium">External</th>
              <th className="px-2 py-2 text-right font-medium">
                {country === "BE" ? "Axiom" : "PolicyEngine"}
              </th>
              <th className="px-2 py-2 text-right font-medium">Divergence</th>
              <th className="px-2 py-2 font-medium">Status</th>
              <th className="px-2 py-2 font-medium">Relationship</th>
              <th className="px-2 py-2 text-right font-medium">Releases</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <Fragment key={r.claim_id}>
                <tr
                  className="cursor-pointer border-b border-border hover:bg-muted/40"
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
                  <td className="max-w-md px-2 py-1.5">
                    <span className="line-clamp-2">
                      {r.name || r.source_column}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5">
                    {sourceLabel(r.source)}
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5 fig text-xs text-muted-foreground">
                    {r.window || windowFromPeriod(r)}
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5 text-right fig">
                    {fmtV(r.external_value, r.value_kind)}
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5 text-right fig">
                    {fmtV(r.latest.value, r.value_kind)}
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5 text-right fig">
                    {comparabilityFigure(
                      r.latest.status_effective,
                      "not comparable",
                      () => fmtDiv(r),
                    )}
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5">
                    <StatusPill status={r.latest.status_effective} />
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5">
                    <span
                      className="rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide"
                      title={
                        r.calibration_relationship === "consumed_as_target"
                          ? "This value is on the calibration target surface — agreement is a tautology, labeled and never counted as validation."
                          : undefined
                      }
                    >
                      {RELATIONSHIP_LABELS[r.calibration_relationship]}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-2 py-1.5 text-right fig">
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
    <tr className="border-b border-border bg-muted/30">
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
                {row.results.map((res) => (
                  <tr key={res.data_bundle} className="border-t border-border">
                    <td className="py-1 pr-3 fig">{res.release}</td>
                    <td className="py-1 pr-3 fig break-all">
                      {res.engine_version}
                      {res.status_effective !== res.status && (
                        <span
                          className="ml-1.5 rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide"
                          title="The recorded status is downgraded by the baseline guard (issue #13): the executed baseline differs from, or is unverifiable against, the claim's world."
                        >
                          {STATUS_LABELS[res.status_effective]}
                        </span>
                      )}
                    </td>
                    <td className="py-1 pr-3 text-right fig">
                      {fmtV(res.value, row.value_kind)}
                    </td>
                    <td className="py-1 pr-3 text-right fig">
                      {comparabilityFigure(
                        res.status_effective,
                        "—",
                        () => ratioOf(res.value, row.external_value),
                      )}
                    </td>
                    <td className="py-1 fig text-muted-foreground break-all">
                      {res.construction || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
              </table>
            </div>
            {row.results.some((res) => res.annotations.length > 0) && (
              <ul className="mt-2 space-y-1 text-muted-foreground">
                {row.results.flatMap((res) =>
                  res.annotations.map((a, i) => (
                    <li key={`${res.data_bundle}-${i}`}>
                      <span className="mr-1.5 rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide">
                        {res.release}
                      </span>
                      {a}
                    </li>
                  )),
                )}
              </ul>
            )}
            <p className="mt-2 text-muted-foreground">
              A construction change between releases (e.g. an OBBBA scoring
              mode) is part of the label above — compare values only within the
              same construction.
            </p>
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
            <p className="mt-2 fig break-words text-muted-foreground">
              {row.source_column} · {row.metric} · {row.time_basis} {row.period}
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
                <span className="mr-1.5 rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide">
                  {row.diagnosis.class.replace(/_/g, " ")}
                </span>
                {row.diagnosis.rationale}
              </p>
            )}
          </div>
        </div>
      </td>
    </tr>
  );
}

function StatusPill({ status }: { status: PopulationRow["latest"]["status"] }) {
  return (
    <span className="inline-flex items-center rounded-sm border border-border px-1.5 py-0.5 text-[11px] whitespace-nowrap">
      {STATUS_LABELS[status] ?? status}
    </span>
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
  // currency follows the value_kind, never a $ default: gbp* rows are
  // pounds, count rows carry no symbol at all
  const cur = kind.startsWith("gbp")
    ? "£"
    : kind.startsWith("eur")
      ? "€"
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
