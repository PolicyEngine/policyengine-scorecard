import { Fragment, useMemo, useState } from "react";
import type { PopulationRow, PopulationsFeed } from "../types";
import {
  COUNTRY_LABELS,
  RELATIONSHIP_LABELS,
  STATUS_LABELS,
  countryOf,
} from "../types";

/**
 * The reform-validation registry (issue #20): every non-Urban claim in
 * scorecard.db with a PE result, shown with its full per-release history —
 * one result per certified populace release, engine pins and OBBBA scoring
 * mode in the construction, so cross-release drift is visible. Descriptive
 * only: statuses and calibration relationships label, never grade.
 */
export function ReformValidationView({ feed }: { feed: PopulationsFeed }) {
  const [source, setSource] = useState("all");
  const [status, setStatus] = useState("all");
  const [country, setCountry] = useState("all");
  const [releasesOnly, setReleasesOnly] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const sources = useMemo(
    () => Object.keys(feed.summary.by_source).sort(),
    [feed],
  );
  // Countries present in the feed; rows without a country key are US-era
  // exports. One country -> state the scope explicitly instead of filtering.
  const countries = useMemo(
    () => [...new Set(feed.rows.map(countryOf))].sort(),
    [feed],
  );
  const rows = useMemo(
    () =>
      feed.rows.filter((r) => {
        if (country !== "all" && countryOf(r) !== country) return false;
        if (source !== "all" && r.source !== source) return false;
        if (status !== "all" && r.latest.status_effective !== status)
          return false;
        if (releasesOnly && r.results.length < 2) return false;
        return true;
      }),
    [feed, country, source, status, releasesOnly],
  );

  const sel = "h-8 rounded-md border border-border bg-background px-2 text-sm";

  return (
    <div>
      <p className="mb-4 max-w-3xl text-sm leading-6 text-muted-foreground">
        Reform scores and references beyond the Urban comparison:{" "}
        <b className="fig text-foreground">
          {feed.summary.claims.toLocaleString()}
        </b>{" "}
        external claims — the populace reform-validation registry (JCT scores,
        state fiscal notes, agency actuals, IRS and Census references) plus the
        compute campaign's TPC, CPSP, PWBM and CBO comparisons — where each
        available result carries its certified release's exact engine pins.{" "}
        <b className="fig text-foreground">
          {feed.summary.multi_release_claims.toLocaleString()}
        </b>{" "}
        carry results from more than one release, so drift across releases is
        queryable, and a scoring-construction change is labeled in the history
        rather than read as drift. Nothing here is a pass/fail grade.
      </p>
      <p className="mb-4 fig text-[11px] text-muted-foreground">
        populations feed · exported from scorecard.db · built {feed.built} ·
        per-release results carry their own engine + data-bundle provenance (the
        page-top stamp describes the Urban comparison only)
        {countries.length === 1 && (
          <>
            {" "}
            · scope: {COUNTRY_LABELS[countries[0]]} only — every claim in the
            current registry is a {countries[0]} claim; a country filter
            appears here once claims from another country land
          </>
        )}
      </p>

      <div className="mb-3 flex flex-wrap items-end gap-3">
        {countries.length > 1 && (
          <label className="text-xs text-muted-foreground">
            Country
            <br />
            <select
              className={sel}
              value={country}
              onChange={(e) => setCountry(e.target.value)}
            >
              <option value="all">All countries</option>
              {countries.map((c) => (
                <option key={c} value={c}>
                  {COUNTRY_LABELS[c]}
                </option>
              ))}
            </select>
          </label>
        )}
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
                {sourceLabel(s)} ({feed.summary.by_source[s]})
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
            {Object.entries(feed.summary.by_latest_status).map(([s, n]) => (
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
              <th className="px-2 py-2 text-right font-medium">PolicyEngine</th>
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
                    {fmtDiv(r)}
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
          <div>
            <p className="mb-1 font-semibold">Per-release history</p>
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
                    <td className="py-1 pr-3 fig">
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
                      {ratioOf(res.value, row.external_value)}
                    </td>
                    <td className="py-1 fig text-muted-foreground">
                      {res.construction || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
          <div>
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
            <p className="mt-2 fig text-muted-foreground">
              {row.source_column} · {row.metric} · {row.time_basis} {row.period}
              {row.period_start !== null &&
                ` (window ${row.period_start}–${row.period_end})`}
            </p>
            {Object.entries(row.conditions).length > 0 && (
              <p className="mt-2 text-muted-foreground">
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

const SOURCE_SPECIAL: Record<string, string> = {
  jct: "JCT",
  cbo: "CBO",
  irs: "IRS",
  irs_soi: "IRS SOI",
  census: "Census",
  census_pep: "Census PEP",
  treasury: "Treasury",
  tpc: "TPC",
  pwbm: "PWBM",
  cpsp: "Columbia CPSP",
  budget_lab: "Budget Lab",
  tax_foundation: "Tax Foundation",
  obr: "OBR",
  hmrc: "HMRC",
  dwp: "DWP",
  hmt: "HMT",
  ifs: "IFS",
  rf: "Resolution Foundation",
  ukmod: "UKMOD",
};

function sourceLabel(s: string): string {
  if (SOURCE_SPECIAL[s]) return SOURCE_SPECIAL[s];
  const m = s.match(/^([a-z]{2})_(admin|fiscal_note)$/);
  if (m) return `${m[1].toUpperCase()} ${m[2].replace("_", " ")}`;
  return s;
}

function windowFromPeriod(r: PopulationRow): string {
  const basis = r.time_basis === "fiscal_year" ? "FY" : "";
  return `${basis}${r.period}`;
}

function fmtV(v: number | null, kind: string): string {
  if (v === null || v === undefined) return "—";
  if (kind === "share") return `${(v * 100).toFixed(1)}%`;
  const a = Math.abs(v);
  const sign = v < 0 ? "−" : "";
  if (a >= 1e9) return `${sign}$${(a / 1e9).toFixed(2)}B`;
  if (a >= 1e6) return `${sign}$${(a / 1e6).toFixed(1)}M`;
  if (a >= 1e3) return `${sign}$${(a / 1e3).toFixed(0)}k`;
  return `${sign}$${a.toFixed(0)}`;
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
