import { Fragment, useMemo, useState } from "react";
import { relationshipNote } from "../data";
import { closeness, divergenceScore, fmtDivergence, fmtValue } from "../format";
import type { Row, SourceSlice } from "../types";
import { metricLabel, programLabel, labelize } from "../types";
import { type SpineBucket } from "../spine";
import { RelationshipBadge, StatusChip, VintageChip } from "./chips";
import { RowDetail } from "./BrowseTable";

const PROGRAM_ORDER = [
  "snap", "ssi", "tanf", "wic", "ccdf", "housing", "liheap", "eitc",
  "ctc_refund", "spm_poverty",
];
const METRIC_ORDER = [
  "eligible_count", "eligibility_rate", "participation_rate",
  "participation_gap_count", "poverty_rate", "poverty_rate_change",
  "poverty_count_change",
];
const MAX_RENDER = 600;

export interface UrbanFilters {
  program: string;
  metric: string;
  geography: string; // "US" | "states" | state code
  subgroup: string; // "total" | "all" | slug
  bucket: SpineBucket | null;
}

export const DEFAULT_URBAN_FILTERS: UrbanFilters = {
  program: "all",
  metric: "all",
  geography: "US",
  subgroup: "total",
  bucket: null,
};

/** The Urban SotSN grid: program × metric × subgroup × geography. */
export function ComparisonTable({
  slice,
  buckets,
  filters,
  setFilters,
}: {
  slice: SourceSlice;
  buckets: Map<Row, SpineBucket>;
  filters: UrbanFilters;
  setFilters: (f: UrbanFilters) => void;
}) {
  const [sortByDivergence, setSortByDivergence] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const subgroups = useMemo(
    () => [...new Set(slice.rows.map((r) => r.subgroup ?? "total"))].sort(),
    [slice],
  );
  const states = useMemo(
    () =>
      [...new Set(slice.rows.map((r) => r.geography))]
        .filter((g) => g !== "US")
        .sort(),
    [slice],
  );

  const filtered = useMemo(() => {
    let rows = slice.rows.filter((r) => {
      const sub = r.subgroup ?? "total";
      if (filters.program !== "all" && r.program !== filters.program)
        return false;
      if (filters.metric !== "all" && r.metric !== filters.metric)
        return false;
      if (filters.geography === "US" && r.geography !== "US") return false;
      if (filters.geography === "states" && r.geography === "US")
        return false;
      if (
        !["US", "states"].includes(filters.geography) &&
        r.geography !== filters.geography
      )
        return false;
      if (filters.subgroup !== "all" && sub !== filters.subgroup)
        return false;
      if (filters.bucket && buckets.get(r) !== filters.bucket) return false;
      return true;
    });
    const key = (r: Row) =>
      PROGRAM_ORDER.indexOf(r.program ?? "") * 100 +
      METRIC_ORDER.indexOf(r.metric) * 4 +
      (r.policy === "full_participation" ? 2 : 0) +
      (r.variant ? 1 : 0);
    rows = rows.sort((a, b) =>
      sortByDivergence
        ? divergenceScore(b) - divergenceScore(a)
        : key(a) - key(b) ||
          (a.subgroup ?? "total").localeCompare(b.subgroup ?? "total") ||
          a.geography.localeCompare(b.geography),
    );
    return rows;
  }, [slice, filters, buckets, sortByDivergence]);

  const sel = "h-8 rounded-md border border-border bg-background px-2 text-sm";

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
                {programLabel(p)}
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
                {metricLabel(m)}
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
              <Fragment key={r.id}>
                <RowLine
                  row={r}
                  slice={slice}
                  bucket={buckets.get(r)!}
                  expanded={expanded === r.id}
                  onToggle={() =>
                    setExpanded(expanded === r.id ? null : r.id)
                  }
                />
                {expanded === r.id && <RowDetail row={r} slice={slice} />}
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
  slice,
  bucket,
  expanded,
  onToggle,
}: {
  row: Row;
  slice: SourceSlice;
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
        {programLabel(row.program)}
        {row.policy === "full_participation" && (
          <span className="ml-1 rounded-sm bg-muted px-1 py-px text-[10px] text-muted-foreground">
            full participation
          </span>
        )}
        {row.variant ? (
          <span className="text-muted-foreground">
            {" "}
            · {labelize(row.variant)}
          </span>
        ) : null}
      </td>
      <td className="px-2 py-1.5 whitespace-nowrap">
        {metricLabel(row.metric)}
      </td>
      <td className="px-2 py-1.5 whitespace-nowrap text-muted-foreground">
        {row.subgroup ?? "total"}
      </td>
      <td className="px-2 py-1.5 fig">{row.geography}</td>
      <td className="px-2 py-1.5 text-right fig">
        {fmtValue(row.value ?? null, row)}
      </td>
      <td className="px-2 py-1.5 text-right fig">
        {fmtValue(row.pe?.value ?? null, row)}
      </td>
      <td className={"px-2 py-1.5 text-right fig " + divergenceColor}>
        {fmtDivergence(row)}
      </td>
      <td className="px-2 py-1.5 text-right fig text-muted-foreground">
        {row.pe_2026 !== undefined ? fmtValue(row.pe_2026, row) : ""}
      </td>
      <td className="px-2 py-1.5">
        <StatusChip bucket={bucket} status={row.status} />
        <RelationshipBadge row={row} note={relationshipNote(slice, row)} />
        {row.annotations && row.annotations.length > 0 && (
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
