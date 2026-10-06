import { Fragment, useMemo, useState, type ReactNode } from "react";
import { Button } from "@policyengine/ui-kit/primitives";
import { defaultFilters, hasActiveFilters, type Filters } from "../filters";
import {
  divergenceScore,
  divergenceTextClass,
  fmtDivergence,
  fmtValue,
} from "../format";
import type { Comparison, Row } from "../types";
import { METRIC_LABELS, PROGRAM_LABELS } from "../types";
import { SPINE_META, SPINE_ORDER, type SpineBucket } from "../spine";
import {
  nextSort,
  sortRows,
  type SortDir,
  type SortState,
  type SortValue,
} from "../tableSort";
import { LabeledSelect, StatusBadge, TableCard, Tag } from "./ui";

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

/**
 * Sortable columns, in table order. Δ sorts by the size of the gap
 * (divergenceScore), so rates and counts rank together; status sorts in
 * coverage order (close → suppressed). Text starts A→Z, numbers largest
 * first.
 */
type ColKey =
  | "program"
  | "metric"
  | "subgroup"
  | "geography"
  | "external"
  | "pe"
  | "delta"
  | "pe2026"
  | "status";

const FIRST_DIR: Record<ColKey, SortDir> = {
  program: "asc",
  metric: "asc",
  subgroup: "asc",
  geography: "asc",
  external: "desc",
  pe: "desc",
  delta: "desc",
  pe2026: "desc",
  status: "asc",
};

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
  const [sort, setSort] = useState<SortState<ColKey> | null>(null);
  const onSort = (key: ColKey) => setSort((s) => nextSort(s, key, FIRST_DIR[key]));
  const [expanded, setExpanded] = useState<Row | null>(null);
  const externalLabel = filters.country === "US" ? "Urban" : "External";

  const subgroups = useMemo(
    () => [...new Set(data.rows.map((r) => r.subgroup))].sort(),
    [data],
  );
  // The national geography code equals the country code ("US" | "UK").
  const national = filters.country;
  const states = useMemo(
    () =>
      [...new Set(data.rows.map((r) => r.geography))]
        .filter((g) => g !== national)
        .sort(),
    [data, national],
  );

  const filtered = useMemo(() => {
    let rows = data.rows.filter((r) => {
      if (filters.program !== "all" && r.program !== filters.program)
        return false;
      if (filters.metric !== "all" && r.metric !== filters.metric) return false;
      if (filters.geography === "states" && r.geography === national)
        return false;
      if (filters.geography !== "states" && r.geography !== filters.geography)
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
    rows = rows.sort(
      (a, b) =>
        key(a) - key(b) ||
        a.subgroup.localeCompare(b.subgroup) ||
        a.geography.localeCompare(b.geography),
    );
    const value = (r: Row, col: ColKey): SortValue => {
      switch (col) {
        case "program":
          return PROGRAM_LABELS[r.program] ?? r.program;
        case "metric":
          return METRIC_LABELS[r.metric] ?? r.metric;
        case "subgroup":
          return r.subgroup;
        case "geography":
          return r.geography;
        case "external":
          return r.external_value;
        case "pe":
          return r.pe_value;
        case "delta":
          return fmtDivergence(r) === "" ? null : divergenceScore(r);
        case "pe2026":
          return r.pe_value_2026;
        case "status":
          return SPINE_ORDER.indexOf(buckets.get(r)!);
      }
    };
    return sortRows(rows, sort, value);
  }, [data, filters, buckets, sort, national]);

  return (
    <div className="space-y-4">
      <TableCard
        toolbar={
          <>
            <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-5">
              <LabeledSelect
                label="Program"
                value={filters.program}
                onChange={(program) => setFilters({ ...filters, program })}
                options={[
                  { value: "all", label: "All programs" },
                  ...PROGRAM_ORDER.map((p) => ({
                    value: p,
                    label: PROGRAM_LABELS[p] ?? p,
                  })),
                ]}
              />
              <LabeledSelect
                label="Metric"
                value={filters.metric}
                onChange={(metric) => setFilters({ ...filters, metric })}
                options={[
                  { value: "all", label: "All metrics" },
                  ...METRIC_ORDER.map((m) => ({
                    value: m,
                    label: METRIC_LABELS[m] ?? m,
                  })),
                ]}
              />
              <LabeledSelect
                label="Geography"
                value={filters.geography}
                onChange={(geography) => setFilters({ ...filters, geography })}
                options={[
                  { value: national, label: "National" },
                  { value: "states", label: "All states" },
                  ...states.map((s) => ({ value: s, label: s })),
                ]}
              />
              <LabeledSelect
                label="Subgroup"
                value={filters.subgroup}
                onChange={(subgroup) => setFilters({ ...filters, subgroup })}
                options={[
                  { value: "total", label: "Total only" },
                  { value: "all", label: "All subgroups" },
                  ...subgroups
                    .filter((s) => s !== "total")
                    .map((s) => ({ value: s, label: s })),
                ]}
              />
              <LabeledSelect
                label="Status"
                value={filters.bucket ?? "all"}
                onChange={(v) =>
                  setFilters({
                    ...filters,
                    bucket: v === "all" ? null : (v as SpineBucket),
                  })
                }
                options={[
                  { value: "all", label: "All statuses" },
                  ...SPINE_ORDER.map((b) => ({
                    value: b,
                    label: SPINE_META[b].label,
                  })),
                ]}
              />
            </div>
            {(hasActiveFilters(filters) || sort) && (
              <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-border pt-3">
                {hasActiveFilters(filters) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setFilters(defaultFilters(filters.country))}
                  >
                    Reset filters
                  </Button>
                )}
                {sort && (
                  <Button variant="ghost" size="sm" onClick={() => setSort(null)}>
                    Default order
                  </Button>
                )}
              </div>
            )}
          </>
        }
      >
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-muted text-left text-xs text-muted-foreground">
              <SortHeader col="program" sort={sort} onSort={onSort}>
                Program
              </SortHeader>
              <SortHeader col="metric" sort={sort} onSort={onSort}>
                Metric
              </SortHeader>
              <SortHeader col="subgroup" sort={sort} onSort={onSort}>
                Subgroup
              </SortHeader>
              <SortHeader col="geography" sort={sort} onSort={onSort}>
                Geo
              </SortHeader>
              <SortHeader
                col="external"
                sort={sort}
                onSort={onSort}
                right
                sub="2023 avg month"
              >
                {externalLabel}
              </SortHeader>
              <SortHeader
                col="pe"
                sort={sort}
                onSort={onSort}
                right
                sub="2024 calibrated"
              >
                PolicyEngine
              </SortHeader>
              <SortHeader
                col="delta"
                sort={sort}
                onSort={onSort}
                right
              >
                Δ
              </SortHeader>
              <SortHeader
                col="pe2026"
                sort={sort}
                onSort={onSort}
                right
                sub="2026"
              >
                Projected
              </SortHeader>
              <SortHeader col="status" sort={sort} onSort={onSort}>
                Status
              </SortHeader>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr>
                <td
                  colSpan={9}
                  className="px-3 py-8 text-center text-sm text-muted-foreground"
                >
                  No rows match these filters.
                </td>
              </tr>
            )}
            {filtered.slice(0, MAX_RENDER).map((r) => (
              <Fragment key={r.source_column + r.geography}>
                <RowLine
                  row={r}
                  bucket={buckets.get(r)!}
                  expanded={expanded === r}
                  onToggle={() => setExpanded(expanded === r ? null : r)}
                />
                {expanded === r && (
                  <RowDetail
                    row={r}
                    data={data}
                    externalLabel={externalLabel}
                  />
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
        {filtered.length > MAX_RENDER && (
          <p className="border-t border-border px-3 py-2 text-xs text-muted-foreground">
            Showing the first {MAX_RENDER} of{" "}
            {filtered.length.toLocaleString()} rows — narrow the filters to see
            the rest.
          </p>
        )}
      </TableCard>
    </div>
  );
}

/**
 * A column header that sorts the table. Label and sub-label each stay on
 * one line and headers sit on the row's baseline, so the labels line up
 * with their column. The arrow lives in the cell padding (a CSS glyph, so
 * it takes no width and stays out of copied text): faint on hover, solid
 * on the active column.
 */
function SortHeader({
  col,
  sort,
  onSort,
  right = false,
  sub,
  children,
}: {
  col: ColKey;
  sort: SortState<ColKey> | null;
  onSort: (col: ColKey) => void;
  right?: boolean;
  sub?: string;
  children: ReactNode;
}) {
  const dir = sort?.key === col ? sort.dir : null;
  return (
    <th
      className={
        "whitespace-nowrap px-3 py-2 align-bottom font-medium " +
        (right ? "text-right" : "text-left")
      }
      aria-sort={
        dir === "asc" ? "ascending" : dir === "desc" ? "descending" : undefined
      }
    >
      <button
        type="button"
        onClick={() => onSort(col)}
        className={
          "group cursor-pointer font-medium hover:text-foreground " +
          (right ? "text-right " : "text-left ") +
          (dir ? "text-foreground" : "")
        }
      >
        <span className="relative">
          {children}
          <span
            aria-hidden
            className={
              "pointer-events-none absolute top-0 w-3 text-center " +
              (right ? "-left-3.5 " : "-right-3.5 ") +
              (dir === "asc"
                ? "after:content-['↑']"
                : dir === "desc"
                  ? "after:content-['↓']"
                  : "opacity-0 group-hover:opacity-60 after:content-['↕']")
            }
          />
        </span>
        {sub && (
          <span className="block text-[11px] font-normal text-muted-foreground">
            {sub}
          </span>
        )}
      </button>
    </th>
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
  const td = "px-3 py-2";
  return (
    <tr
      onClick={onToggle}
      tabIndex={0}
      aria-expanded={expanded}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onToggle();
        }
      }}
      className={
        "cursor-pointer border-b border-border hover:bg-muted/60 " +
        (expanded ? "bg-muted/60" : "")
      }
    >
      <td className={td + " whitespace-nowrap font-medium"}>
        {PROGRAM_LABELS[row.program] ?? row.program}
        {row.variant ? (
          <span className="font-normal text-muted-foreground">
            {" "}
            · {row.variant}
          </span>
        ) : null}
      </td>
      <td className={td + " whitespace-nowrap"}>
        {METRIC_LABELS[row.metric] ?? row.metric}
      </td>
      <td className={td + " whitespace-nowrap text-muted-foreground"}>
        {row.subgroup}
      </td>
      <td className={td + " fig"}>{row.geography}</td>
      <td className={td + " fig text-right"}>
        {fmtValue(row.external_value, row.metric)}
      </td>
      <td className={td + " fig text-right"}>
        {fmtValue(row.pe_value, row.metric)}
      </td>
      <td className={td + " fig text-right " + divergenceTextClass(row)}>
        {fmtDivergence(row)}
      </td>
      <td className={td + " fig text-right text-muted-foreground"}>
        {row.pe_value_2026 !== null
          ? fmtValue(row.pe_value_2026, row.metric)
          : ""}
      </td>
      <td className={td + " whitespace-nowrap"}>
        <StatusBadge bucket={bucket} status={row.status} />
        {row.calibration_relationship !== "held_out" && (
          <Tag tone="dashed" className="ml-1" title={row.calibration_basis}>
            {row.calibration_relationship === "seed_source"
              ? "seed"
              : "target"}
          </Tag>
        )}
        {row.annotations.length > 0 && (
          <span
            className="ml-1.5 align-middle text-[10px] text-muted-foreground"
            title={`${row.annotations.length} annotations — open the row`}
          >
            ⓘ{row.annotations.length}
          </span>
        )}
      </td>
    </tr>
  );
}

function RowDetail({
  row,
  data,
  externalLabel,
}: {
  row: Row;
  data: Comparison;
  externalLabel: string;
}) {
  return (
    <tr className="border-b border-border bg-muted/40">
      <td colSpan={9} className="px-4 py-3">
        <div className="grid gap-4 text-xs md:grid-cols-2">
          <div>
            <p className="mb-1 font-semibold">Construction</p>
            <p className="fig text-muted-foreground">
              {row.pe_construction ?? "no PolicyEngine counterpart"}
            </p>
            <p className="mt-2 text-muted-foreground">
              {externalLabel}: {row.unit_concept}, {row.period} · PolicyEngine:{" "}
              {row.pe_period ?? "—"}
              {row.pe_value_2026 !== null &&
                " · 2026 projection: same artifact, engine-side uprating"}{" "}
              · source column <span className="fig">{row.source_column}</span>
            </p>
            <p className="mt-2 text-muted-foreground">
              <Tag className="mr-1.5">
                {row.calibration_relationship.replace(/_/g, " ")}
              </Tag>
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
                    <Tag className="mr-1.5">{a.severity}</Tag>
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
