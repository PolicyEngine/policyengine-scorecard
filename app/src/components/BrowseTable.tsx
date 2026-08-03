import { Fragment, useMemo, useState } from "react";
import { relationshipNote } from "../data";
import {
  closeness,
  divergenceScore,
  fmtDivergence,
  fmtPeriod,
  fmtValue,
} from "../format";
import { bucketOf, SPINE_META, SPINE_ORDER, type SpineBucket } from "../spine";
import type { IndexSource, Row, SourceSlice } from "../types";
import {
  metricLabel,
  policyLabel,
  programLabel,
  RELATIONSHIP_LABELS,
  labelize,
} from "../types";
import {
  BaselineChip,
  DiagnosisChip,
  RelationshipBadge,
  StatusChip,
  VintageChip,
} from "./chips";

const MAX_RENDER = 400;

export interface BrowseFilters {
  metric: string;
  geography: string; // all | US | states | code
  program: string;
  policy: string;
  bucket: SpineBucket | "all";
  relationship: string;
  search: string;
}

export const DEFAULT_BROWSE: BrowseFilters = {
  metric: "all",
  geography: "all",
  program: "all",
  policy: "all",
  bucket: "all",
  relationship: "all",
  search: "",
};

/** Cross-source comparisons table. Sources load lazily; every loaded row
 * renders with the same honesty structures the per-source pages carry. */
export function BrowseTable({
  sources,
  slices,
  loading,
  selected,
  onToggleSource,
  lockSource,
  initialFilters,
}: {
  sources: IndexSource[];
  slices: Map<string, SourceSlice>;
  loading: Set<string>;
  selected: Set<string>;
  onToggleSource: (id: string) => void;
  lockSource?: string;
  initialFilters?: Partial<BrowseFilters>;
}) {
  const [filters, setFilters] = useState<BrowseFilters>({
    ...DEFAULT_BROWSE,
    ...initialFilters,
  });
  const [sortByDivergence, setSortByDivergence] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const activeIds = lockSource
    ? [lockSource]
    : sources.map((s) => s.id).filter((id) => selected.has(id));
  const activeSlices = activeIds
    .map((id) => slices.get(id))
    .filter((s): s is SourceSlice => !!s);

  const rows = useMemo(
    () => activeSlices.flatMap((s) => s.rows),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [activeSlices.map((s) => s.id).join(",")],
  );

  const options = useMemo(() => {
    const metrics = new Map<string, number>();
    const programs = new Map<string, number>();
    const policies = new Map<string, number>();
    const geos = new Set<string>();
    for (const r of rows) {
      metrics.set(r.metric, (metrics.get(r.metric) ?? 0) + 1);
      if (r.program)
        programs.set(r.program, (programs.get(r.program) ?? 0) + 1);
      if (r.policy)
        policies.set(r.policy, (policies.get(r.policy) ?? 0) + 1);
      geos.add(r.geography);
    }
    const sort = (m: Map<string, number>) =>
      [...m.entries()].sort((a, b) => b[1] - a[1]).map(([v]) => v);
    return {
      metrics: sort(metrics),
      programs: sort(programs),
      policies: sort(policies),
      geos: [...geos].filter((g) => g !== "US").sort(),
    };
  }, [rows]);

  const filtered = useMemo(() => {
    const q = filters.search.trim().toLowerCase();
    let out = rows.filter((r) => {
      if (filters.metric !== "all" && r.metric !== filters.metric)
        return false;
      if (filters.program !== "all" && r.program !== filters.program)
        return false;
      if (filters.policy !== "all" && (r.policy ?? "") !== filters.policy)
        return false;
      if (filters.geography === "US" && r.geography !== "US") return false;
      if (filters.geography === "states" && r.geography === "US")
        return false;
      if (
        !["all", "US", "states"].includes(filters.geography) &&
        r.geography !== filters.geography
      )
        return false;
      if (filters.bucket !== "all" && bucketOf(r) !== filters.bucket)
        return false;
      if (
        filters.relationship !== "all" &&
        r.relationship !== filters.relationship
      )
        return false;
      if (q) {
        const hay = [
          r.source_column,
          r.policy,
          r.program,
          r.subgroup,
          ...(r.conditions ? Object.values(r.conditions) : []),
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    if (sortByDivergence) {
      out = [...out].sort((a, b) => divergenceScore(b) - divergenceScore(a));
    } else {
      const sourceOrder = new Map(sources.map((s, i) => [s.id, i]));
      const key = (r: Row) =>
        `${r.program ?? ""}|${r.policy ?? ""}|${r.metric}|${
          r.subgroup ?? ""
        }|${r.geography}|${r.period}`;
      out = [...out].sort(
        (a, b) =>
          (sourceOrder.get(a.source) ?? 99) -
            (sourceOrder.get(b.source) ?? 99) ||
          key(a).localeCompare(key(b)),
      );
    }
    return out;
  }, [rows, filters, sortByDivergence, sources]);

  const sel = "h-8 rounded-md border border-border bg-background px-2 text-sm";
  const sliceById = new Map(activeSlices.map((s) => [s.id, s]));

  return (
    <div>
      {!lockSource && (
        <div className="mb-3 flex flex-wrap items-center gap-1.5">
          {sources.map((s) => {
            const on = selected.has(s.id);
            return (
              <button
                key={s.id}
                onClick={() => onToggleSource(s.id)}
                aria-pressed={on}
                className={
                  "rounded-full border px-2.5 py-1 text-xs transition-colors " +
                  (on
                    ? "border-primary bg-primary/10 font-medium text-primary"
                    : "border-border text-muted-foreground hover:text-foreground")
                }
              >
                {s.name}
                {loading.has(s.id) && on ? " …" : ""}
              </button>
            );
          })}
        </div>
      )}

      <div className="mb-4 flex flex-wrap items-end gap-3">
        {options.programs.length > 0 && (
          <Select
            label="Program"
            value={filters.program}
            onChange={(v) => setFilters({ ...filters, program: v })}
            options={[["all", "All programs"]].concat(
              options.programs.map((p) => [p, programLabel(p)]),
            )}
            className={sel}
          />
        )}
        {options.policies.length > 0 && (
          <Select
            label="Policy world"
            value={filters.policy}
            onChange={(v) => setFilters({ ...filters, policy: v })}
            options={[["all", "All policies"]].concat(
              options.policies.map((p) => [p, policyLabel(p)]),
            )}
            className={sel}
          />
        )}
        <Select
          label="Metric"
          value={filters.metric}
          onChange={(v) => setFilters({ ...filters, metric: v })}
          options={[["all", "All metrics"]].concat(
            options.metrics.map((m) => [m, metricLabel(m)]),
          )}
          className={sel}
        />
        <Select
          label="Geography"
          value={filters.geography}
          onChange={(v) => setFilters({ ...filters, geography: v })}
          options={[
            ["all", "All geographies"],
            ["US", "National"],
            ["states", "All states"],
            ...options.geos.map((g) => [g, g] as [string, string]),
          ]}
          className={sel}
        />
        <Select
          label="Bin / status"
          value={filters.bucket}
          onChange={(v) =>
            setFilters({ ...filters, bucket: v as BrowseFilters["bucket"] })
          }
          options={[["all", "All"]].concat(
            SPINE_ORDER.map((b) => [b, SPINE_META[b].label]),
          )}
          className={sel}
        />
        <Select
          label="Calibration"
          value={filters.relationship}
          onChange={(v) => setFilters({ ...filters, relationship: v })}
          options={[
            ["all", "All rows"],
            ["held_out", "Held out"],
            ["consumed_as_target", "Target consumed"],
            ["seed_source", "Seed source"],
          ]}
          className={sel}
        />
        <label className="text-xs text-muted-foreground">
          Search
          <br />
          <input
            className={sel}
            placeholder="provision, subgroup…"
            value={filters.search}
            onChange={(e) =>
              setFilters({ ...filters, search: e.target.value })
            }
          />
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
              {!lockSource && <th className="px-2 py-2 font-medium">Source</th>}
              <th className="px-2 py-2 font-medium">Item</th>
              <th className="px-2 py-2 font-medium">Metric</th>
              <th className="px-2 py-2 font-medium">Geo</th>
              <th className="px-2 py-2 font-medium">Period</th>
              <th className="px-2 py-2 text-right font-medium">
                External <VintageChip label="as published" tone="external" />
              </th>
              <th className="px-2 py-2 text-right font-medium">
                PolicyEngine <VintageChip label="2024 calibrated" tone="pe" />
              </th>
              <th className="px-2 py-2 text-right font-medium">Δ</th>
              <th className="px-2 py-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, MAX_RENDER).map((r) => (
              <Fragment key={r.id}>
                <BrowseRow
                  row={r}
                  slice={sliceById.get(r.source)}
                  sourceName={
                    sources.find((s) => s.id === r.source)?.name ?? r.source
                  }
                  showSource={!lockSource}
                  expanded={expanded === r.id}
                  onToggle={() =>
                    setExpanded(expanded === r.id ? null : r.id)
                  }
                />
                {expanded === r.id && (
                  <RowDetail row={r} slice={sliceById.get(r.source)} />
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
        {activeIds.length === 0 && (
          <p className="px-3 py-6 text-sm text-muted-foreground">
            Pick at least one source above.
          </p>
        )}
        {activeIds.length > 0 &&
          activeSlices.length < activeIds.length && (
            <p className="border-t border-border px-2 py-2 text-xs text-muted-foreground">
              Loading{" "}
              {activeIds.filter((id) => !sliceById.has(id)).join(", ")}…
            </p>
          )}
        {filtered.length > MAX_RENDER && (
          <p className="border-t border-border px-2 py-2 text-xs text-muted-foreground">
            Showing the first {MAX_RENDER} of{" "}
            {filtered.length.toLocaleString()} rows — narrow the filters to
            see the rest.
          </p>
        )}
      </div>
    </div>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
  className,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: [string, string][] | string[][];
  className: string;
}) {
  return (
    <label className="text-xs text-muted-foreground">
      {label}
      <br />
      <select
        className={className}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </label>
  );
}

/** The row's "what is this" cell: program or policy world + the most
 * specific published label we have (subgroup, provision, income group…). */
function itemLabel(row: Row): { main: string; detail: string | null } {
  const c = row.conditions ?? {};
  const main = row.program
    ? programLabel(row.program)
    : row.policy
      ? policyLabel(row.policy)
      : metricLabel(row.metric);
  const detailParts: string[] = [];
  if (row.program && row.policy && row.policy !== "full_participation") {
    detailParts.push(policyLabel(row.policy));
  }
  if (row.subgroup && row.subgroup !== "total")
    detailParts.push(labelize(row.subgroup));
  if (row.variant) detailParts.push(labelize(row.variant));
  for (const key of ["provision", "income_group", "option", "tax", "concept"]) {
    if (c[key]) {
      detailParts.push(c[key]);
      break;
    }
  }
  if (c.scoring && c.scoring !== "conventional") detailParts.push(c.scoring);
  return { main, detail: detailParts.join(" · ") || null };
}

function BrowseRow({
  row,
  slice,
  sourceName,
  showSource,
  expanded,
  onToggle,
}: {
  row: Row;
  slice: SourceSlice | undefined;
  sourceName: string;
  showSource: boolean;
  expanded: boolean;
  onToggle: () => void;
}) {
  const bucket = bucketOf(row);
  const c = closeness(row);
  const divergenceColor =
    c === "far"
      ? "text-destructive"
      : c === "moderate"
        ? "text-[#B45309]"
        : "text-muted-foreground";
  const { main, detail } = itemLabel(row);
  return (
    <tr
      onClick={onToggle}
      className={
        "cursor-pointer border-b border-border/60 hover:bg-muted/40 " +
        (expanded ? "bg-muted/40" : "")
      }
    >
      {showSource && (
        <td className="px-2 py-1.5 whitespace-nowrap text-muted-foreground">
          {sourceName}
        </td>
      )}
      <td className="max-w-[26rem] px-2 py-1.5">
        <span className="whitespace-nowrap">
          {row.policy === "full_participation" ? (
            <>
              {main}
              <span className="ml-1 rounded-sm bg-muted px-1 py-px text-[10px] text-muted-foreground">
                full participation
              </span>
            </>
          ) : (
            main
          )}
          <BaselineChip baseline={row.baseline} />
        </span>
        {detail && (
          <span className="block truncate text-[11px] text-muted-foreground">
            {detail}
          </span>
        )}
      </td>
      <td className="px-2 py-1.5 whitespace-nowrap">
        {metricLabel(row.metric)}
      </td>
      <td className="px-2 py-1.5 fig">{row.geography}</td>
      <td className="px-2 py-1.5 fig whitespace-nowrap text-muted-foreground">
        {fmtPeriod(row)}
      </td>
      <td className="px-2 py-1.5 text-right fig whitespace-nowrap">
        {fmtValue(row.value ?? null, row)}
      </td>
      <td className="px-2 py-1.5 text-right fig whitespace-nowrap">
        {fmtValue(row.pe?.value ?? null, row)}
      </td>
      <td
        className={
          "px-2 py-1.5 text-right fig whitespace-nowrap " + divergenceColor
        }
      >
        {fmtDivergence(row)}
      </td>
      <td className="px-2 py-1.5 whitespace-nowrap">
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
        {row.diagnosis && (
          <span className="ml-1.5 align-middle text-[10px] text-muted-foreground">
            ◆
          </span>
        )}
      </td>
    </tr>
  );
}

export function RowDetail({
  row,
  slice,
}: {
  row: Row;
  slice: SourceSlice | undefined;
}) {
  const pub = slice?.pubs?.[row.pub];
  const note = relationshipNote(slice, row);
  const conditions = {
    geography: row.geography,
    ...(row.program ? { program: row.program } : {}),
    ...(row.subgroup && row.subgroup !== "total"
      ? { subgroup: row.subgroup }
      : {}),
    ...(row.variant ? { variant: row.variant } : {}),
    ...row.conditions,
  };
  return (
    <tr className="border-b border-border bg-muted/30">
      <td colSpan={10} className="px-4 py-3">
        <div className="grid gap-3 text-xs md:grid-cols-3">
          <div>
            <p className="mb-1 font-semibold">Claim</p>
            <p className="text-muted-foreground">
              {pub?.title ?? "publication not cataloged"}
              {pub?.date ? ` (${pub.date})` : ""}
              {(pub?.page_url || pub?.url) && (
                <>
                  {" · "}
                  <a
                    className="text-primary underline underline-offset-2"
                    href={String(pub?.page_url ?? pub?.url)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    source
                  </a>
                </>
              )}
            </p>
            {row.source_column && (
              <p className="mt-1 fig text-muted-foreground">
                column: {row.source_column}
              </p>
            )}
            {row.provenance &&
              Object.entries(row.provenance).map(([k, v]) => (
                <p key={k} className="mt-1 fig text-muted-foreground">
                  {labelize(k)}: {String(v)}
                </p>
              ))}
            <p className="mt-1 text-muted-foreground">
              unit {row.unit} · {row.time_basis.replace(/_/g, " ")} ·{" "}
              {fmtPeriod(row)}
              {row.conditions?.window_kind
                ? ` (${row.conditions.window_kind.replace(/_/g, " ")})`
                : ""}
            </p>
          </div>
          <div>
            <p className="mb-1 font-semibold">Conditions + construction</p>
            <p className="fig text-muted-foreground">
              {Object.entries(conditions)
                .map(([k, v]) => `${k}=${v}`)
                .join(" · ")}
            </p>
            {row.baseline && (
              <p className="mt-1 text-muted-foreground">
                Scored against a stated baseline:{" "}
                <BaselineChip baseline={row.baseline} />
              </p>
            )}
            <p className="mt-2 fig text-muted-foreground">
              {row.pe?.construction ??
                (row.pe ? "same-concept lookup" : "no PE counterpart yet")}
            </p>
            <p className="mt-2 text-muted-foreground">
              <span className="mr-1.5 rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide">
                {RELATIONSHIP_LABELS[row.relationship]}
              </span>
              {note ?? ""}
            </p>
          </div>
          <div>
            <p className="mb-1 font-semibold">Explanation + annotations</p>
            {row.diagnosis ? (
              <p>
                <DiagnosisChip d={row.diagnosis} />
                {row.diagnosis.title ?? ""}
                {row.diagnosis.rationale && (
                  <span className="text-muted-foreground">
                    {" "}
                    {row.diagnosis.rationale}
                  </span>
                )}
                {row.diagnosis.confidence && (
                  <span className="text-muted-foreground">
                    {" "}
                    ({row.diagnosis.confidence} confidence)
                  </span>
                )}
              </p>
            ) : (
              <p className="text-muted-foreground">
                No published explanation for this row.
              </p>
            )}
            {row.annotations && row.annotations.length > 0 && (
              <ul className="mt-2 space-y-2">
                {row.annotations.map((id) => {
                  const a = slice?.annotations?.[id];
                  if (!a) return null;
                  return (
                    <li key={id}>
                      <span className="mr-1.5 rounded-sm bg-border px-1 py-0.5 text-[10px] uppercase tracking-wide">
                        {a.severity}
                      </span>
                      {a.text}{" "}
                      <span className="text-muted-foreground">
                        ({a.basis})
                      </span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      </td>
    </tr>
  );
}
