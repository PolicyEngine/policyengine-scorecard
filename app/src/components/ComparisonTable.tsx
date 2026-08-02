import { Fragment, useMemo, useState } from "react";
import type { Filters } from "../App";
import { closeness, divergenceScore, fmtDivergence, fmtValue } from "../format";
import type { Comparison, Row } from "../types";
import { METRIC_LABELS, PROGRAM_LABELS, STATUS_LABELS } from "../types";
import { SPINE_META, type SpineBucket } from "../spine";

const PROGRAM_ORDER = [
  "snap", "ssi", "tanf", "wic", "ccdf", "housing", "liheap", "eitc",
  "ctc_refund", "spm_poverty",
];
const METRIC_ORDER = [
  "eligible_count", "eligibility_rate", "participation_rate",
  "participation_gap_count", "poverty_rate", "poverty_rate_fullpart",
  "poverty_rate_relative_change_fullpart", "poverty_count_change_fullpart",
];
const MAX_RENDER = 600;

export function ComparisonTable({
  data,
  buckets,
  filters,
  setFilters,
}: {
  data: Comparison;
  buckets: Map<Row, SpineBucket>;
  filters: Filters;
  setFilters: (f: Filters) => void;
}) {
  const [sortByDivergence, setSortByDivergence] = useState(false);
  const [expanded, setExpanded] = useState<Row | null>(null);

  const subgroups = useMemo(
    () => [...new Set(data.rows.map((r) => r.subgroup))].sort(),
    [data],
  );
  const states = useMemo(
    () =>
      [...new Set(data.rows.map((r) => r.geography))]
        .filter((g) => g !== "US")
        .sort(),
    [data],
  );

  const filtered = useMemo(() => {
    let rows = data.rows.filter((r) => {
      if (filters.program !== "all" && r.program !== filters.program)
        return false;
      if (filters.metric !== "all" && r.metric !== filters.metric) return false;
      if (filters.geography === "US" && r.geography !== "US") return false;
      if (filters.geography === "states" && r.geography === "US") return false;
      if (
        !["US", "states"].includes(filters.geography) &&
        r.geography !== filters.geography
      )
        return false;
      if (filters.subgroup !== "all" && r.subgroup !== filters.subgroup)
        return false;
      if (filters.bucket && buckets.get(r) !== filters.bucket) return false;
      return true;
    });
    const key = (r: Row) =>
      PROGRAM_ORDER.indexOf(r.program) * 100 +
      METRIC_ORDER.indexOf(r.metric) * 2 +
      (r.variant ? 1 : 0);
    rows = rows.sort((a, b) =>
      sortByDivergence
        ? divergenceScore(b) - divergenceScore(a)
        : key(a) - key(b) ||
          a.subgroup.localeCompare(b.subgroup) ||
          a.geography.localeCompare(b.geography),
    );
    return rows;
  }, [data, filters, buckets, sortByDivergence]);

  const sel =
    "h-8 rounded-md border border-border bg-background px-2 text-sm";

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <label className="text-xs text-muted-foreground">
          Program
          <br />
          <select
            className={sel}
            value={filters.program}
            onChange={(e) =>
              setFilters({ ...filters, program: e.target.value })
            }
          >
            <option value="all">All programs</option>
            {PROGRAM_ORDER.map((p) => (
              <option key={p} value={p}>
                {PROGRAM_LABELS[p] ?? p}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted-foreground">
          Metric
          <br />
          <select
            className={sel}
            value={filters.metric}
            onChange={(e) => setFilters({ ...filters, metric: e.target.value })}
          >
            <option value="all">All metrics</option>
            {METRIC_ORDER.map((m) => (
              <option key={m} value={m}>
                {METRIC_LABELS[m] ?? m}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted-foreground">
          Geography
          <br />
          <select
            className={sel}
            value={filters.geography}
            onChange={(e) =>
              setFilters({ ...filters, geography: e.target.value })
            }
          >
            <option value="US">National</option>
            <option value="states">All states</option>
            {states.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted-foreground">
          Subgroup
          <br />
          <select
            className={sel}
            value={filters.subgroup}
            onChange={(e) =>
              setFilters({ ...filters, subgroup: e.target.value })
            }
          >
            <option value="total">Total only</option>
            <option value="all">All subgroups</option>
            {subgroups
              .filter((s) => s !== "total")
              .map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
          </select>
        </label>
        <label className="flex h-8 items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={sortByDivergence}
            onChange={(e) => setSortByDivergence(e.target.checked)}
          />
          Sort by divergence
        </label>
        <span className="ml-auto text-xs text-muted-foreground fig">
          {filtered.length.toLocaleString()} rows
        </span>
      </div>

      <div className="overflow-x-auto rounded-md border border-border">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/60 text-left text-xs text-muted-foreground">
              <th className="px-2 py-2 font-medium">Program</th>
              <th className="px-2 py-2 font-medium">Metric</th>
              <th className="px-2 py-2 font-medium">Subgroup</th>
              <th className="px-2 py-2 font-medium">Geo</th>
              <th className="px-2 py-2 text-right font-medium">
                Urban <VintageChip label="2023 avg-month" tone="external" />
              </th>
              <th className="px-2 py-2 text-right font-medium">
                PolicyEngine <VintageChip label="2024 calibrated" tone="pe" />
              </th>
              <th className="px-2 py-2 text-right font-medium">Δ</th>
              <th className="px-2 py-2 text-right font-medium">
                <VintageChip label="2026+ projected" tone="proj" />
              </th>
              <th className="px-2 py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, MAX_RENDER).map((r) => (
              <Fragment key={r.source_column + r.geography}>
                <RowLine
                  row={r}
                  bucket={buckets.get(r)!}
                  expanded={expanded === r}
                  onToggle={() => setExpanded(expanded === r ? null : r)}
                />
                {expanded === r && <RowDetail row={r} data={data} />}
              </Fragment>
            ))}
          </tbody>
        </table>
        {filtered.length > MAX_RENDER && (
          <p className="border-t border-border px-2 py-2 text-xs text-muted-foreground">
            Showing the first {MAX_RENDER} of{" "}
            {filtered.length.toLocaleString()} rows — narrow the filters to see
            the rest.
          </p>
        )}
      </div>
    </div>
  );
}

function RowLine({
  row,
  bucket,
  expanded,
  onToggle,
}: {
  row: Row;
  bucket: SpineBucket;
  expanded: boolean;
  onToggle: () => void;
}) {
  const c = closeness(row);
  const divergenceColor =
    c === "far"
      ? "text-destructive"
      : c === "moderate"
        ? "text-[#B45309]"
        : "text-muted-foreground";
  return (
    <tr
      onClick={onToggle}
      className={
        "cursor-pointer border-b border-border/60 hover:bg-muted/40 " +
        (expanded ? "bg-muted/40" : "")
      }
    >
      <td className="px-2 py-1.5 whitespace-nowrap">
        {PROGRAM_LABELS[row.program] ?? row.program}
        {row.variant ? (
          <span className="text-muted-foreground"> · {row.variant}</span>
        ) : null}
      </td>
      <td className="px-2 py-1.5 whitespace-nowrap">
        {METRIC_LABELS[row.metric] ?? row.metric}
      </td>
      <td className="px-2 py-1.5 whitespace-nowrap text-muted-foreground">
        {row.subgroup}
      </td>
      <td className="px-2 py-1.5 fig">{row.geography}</td>
      <td className="px-2 py-1.5 text-right fig">
        {fmtValue(row.external_value, row.metric)}
      </td>
      <td className="px-2 py-1.5 text-right fig">
        {fmtValue(row.pe_value, row.metric)}
      </td>
      <td className={"px-2 py-1.5 text-right fig " + divergenceColor}>
        {fmtDivergence(row)}
      </td>
      <td className="px-2 py-1.5 text-right fig text-muted-foreground">
        {row.pe_value_2026 !== null
          ? fmtValue(row.pe_value_2026, row.metric)
          : ""}
      </td>
      <td className="px-2 py-1.5">
        <StatusChip bucket={bucket} status={row.status} />
        {row.calibration_relationship !== "held_out" && (
          <span
            className="ml-1 align-middle rounded-sm border border-dashed border-border px-1 py-px text-[9px] uppercase tracking-wide text-muted-foreground"
            title={row.calibration_basis}
          >
            {row.calibration_relationship === "seed_source"
              ? "seed"
              : "target"}
          </span>
        )}
        {row.annotations.length > 0 && (
          <span
            className="ml-1.5 align-middle text-[10px] text-muted-foreground"
            title={`${row.annotations.length} annotations — click row`}
          >
            ⓘ{row.annotations.length}
          </span>
        )}
      </td>
    </tr>
  );
}

function VintageChip({
  label,
  tone,
}: {
  label: string;
  tone: "external" | "pe" | "proj";
}) {
  const styles: Record<string, string> = {
    external: "border-border text-muted-foreground",
    pe: "border-[var(--chart-1)] text-[var(--chart-3)]",
    proj: "border-[var(--chart-2)] text-[var(--chart-4)]",
  };
  return (
    <span
      className={
        "ml-1 inline-block rounded-sm border px-1 py-px text-[9px] font-medium uppercase tracking-wide " +
        styles[tone]
      }
    >
      {label}
    </span>
  );
}

function StatusChip({
  bucket,
  status,
}: {
  bucket: SpineBucket;
  status: Row["status"];
}) {
  const meta = SPINE_META[bucket];
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-sm border border-border px-1.5 py-0.5 text-[11px] whitespace-nowrap"
      title={meta.text}
    >
      <span
        className="h-2 w-2 rounded-[2px]"
        style={{ background: meta.color }}
      />
      {["close", "moderate", "far"].includes(bucket)
        ? STATUS_LABELS[status]
        : meta.label}
    </span>
  );
}

function RowDetail({ row, data }: { row: Row; data: Comparison }) {
  return (
    <tr className="border-b border-border bg-muted/30">
      <td colSpan={9} className="px-4 py-3">
        <div className="grid gap-3 text-xs md:grid-cols-2">
          <div>
            <p className="mb-1 font-semibold">Construction</p>
            <p className="fig text-muted-foreground">
              {row.pe_construction ?? "no PE counterpart"}
            </p>
            <p className="mt-2 text-muted-foreground">
              Urban: {row.unit_concept}, {row.period} · PolicyEngine:{" "}
              {row.pe_period ?? "—"}
              {row.pe_value_2026 !== null &&
                " · 2026 projection: same artifact, engine-side uprating"}{" "}
              · source column <span className="fig">{row.source_column}</span>
            </p>
            <p className="mt-2 text-muted-foreground">
              <span className="mr-1.5 rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide">
                {row.calibration_relationship.replace(/_/g, " ")}
              </span>
              {row.calibration_basis}
            </p>
          </div>
          <div>
            <p className="mb-1 font-semibold">Annotations</p>
            {row.annotations.length === 0 && (
              <p className="text-muted-foreground">None.</p>
            )}
            <ul className="space-y-2">
              {row.annotations.map((id) => {
                const a = data.annotations[id];
                if (!a) return null;
                return (
                  <li key={id}>
                    <span className="mr-1.5 rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide">
                      {a.severity}
                    </span>
                    {a.text}{" "}
                    <span className="text-muted-foreground">({a.basis})</span>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      </td>
    </tr>
  );
}
