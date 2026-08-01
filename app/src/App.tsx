import { useEffect, useMemo, useState } from "react";
import type { Comparison, Row } from "./types";
import { PROGRAM_LABELS } from "./types";
import { bucketOf, type SpineBucket } from "./spine";
import { CoverageSpine } from "./components/CoverageSpine";
import { ComparisonTable } from "./components/ComparisonTable";
import { DivergenceBoard } from "./components/DivergenceBoard";
import { GapsView } from "./components/GapsView";
import { AboutView } from "./components/AboutView";

const TABS = [
  { id: "scorecard", label: "Scorecard" },
  { id: "divergences", label: "Divergences" },
  { id: "gaps", label: "Gaps" },
  { id: "about", label: "Method" },
] as const;
type TabId = (typeof TABS)[number]["id"];

export interface Filters {
  program: string;
  metric: string;
  geography: string; // "US" | "states" | state code
  subgroup: string; // "total" | "all" | slug
  bucket: SpineBucket | null;
}

const DEFAULT_FILTERS: Filters = {
  program: "all",
  metric: "all",
  geography: "US",
  subgroup: "total",
  bucket: null,
};

export default function App() {
  const [data, setData] = useState<Comparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>("scorecard");
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);

  useEffect(() => {
    fetch("./data/comparison.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  const buckets = useMemo(() => {
    if (!data) return new Map<Row, SpineBucket>();
    return new Map(data.rows.map((r) => [r, bucketOf(r)] as const));
  }, [data]);

  if (error) {
    return (
      <div className="mx-auto max-w-content p-8">
        <p className="text-destructive">
          Could not load data/comparison.json ({error}). Run the pipeline,
          then copy data into app/public/data/.
        </p>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="mx-auto max-w-content p-8 text-muted-foreground">
        Loading comparison data…
      </div>
    );
  }

  const b = data.pe_bundle;
  const datasetId = (b.certified_data_build_id ?? "").split("-").slice(-2)[0];

  return (
    <div className="min-h-screen">
      {/* provenance stamp */}
      <div className="border-b border-border bg-muted/60">
        <div className="mx-auto max-w-content px-4 py-1.5 fig text-[11px] leading-4 text-muted-foreground flex flex-wrap gap-x-4">
          <span>
            external · {data.source_meta.id} · fetched{" "}
            {data.source_meta.fetched} · {data.source_meta.period}
          </span>
          <span>
            policyengine · {b.runtime_dataset} @ {datasetId} ·{" "}
            {b.model_package} {b.model_version} · annual 2024
          </span>
          <span>built {data.built}</span>
        </div>
      </div>

      <header className="mx-auto max-w-content px-4 pt-8 pb-2">
        <p className="text-xs font-semibold uppercase tracking-widest text-primary">
          Model validation · instance 1
        </p>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">
          PolicyEngine scorecard{" "}
          <span className="font-normal text-muted-foreground">
            vs Urban Institute's State of the Safety Net
          </span>
        </h1>
        <Headline data={data} buckets={buckets} />
      </header>

      <div className="mx-auto max-w-content px-4">
        <CoverageSpine
          rows={data.rows}
          buckets={buckets}
          active={filters.bucket}
          onSelect={(bucket) => {
            setFilters({ ...filters, bucket });
            setTab("scorecard");
          }}
        />
      </div>

      <nav
        className="mx-auto max-w-content px-4 mt-6 border-b border-border flex gap-1"
        aria-label="Views"
      >
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={
              "px-4 py-2 text-sm rounded-t-md border border-b-0 " +
              (tab === t.id
                ? "border-border bg-background font-semibold text-primary -mb-px"
                : "border-transparent text-muted-foreground hover:text-foreground")
            }
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="mx-auto max-w-content px-4 py-6">
        {tab === "scorecard" && (
          <ComparisonTable
            data={data}
            buckets={buckets}
            filters={filters}
            setFilters={setFilters}
          />
        )}
        {tab === "divergences" && (
          <DivergenceBoard data={data} buckets={buckets} />
        )}
        {tab === "gaps" && <GapsView data={data} />}
        {tab === "about" && <AboutView data={data} />}
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-content px-4 py-4 text-xs text-muted-foreground">
          Every annotation traces to the replication assessment, engine
          metadata, or a measured diagnostic — see the method tab. Misses stay
          on the page.
        </div>
      </footer>
    </div>
  );
}

function Headline({
  data,
  buckets,
}: {
  data: Comparison;
  buckets: Map<Row, SpineBucket>;
}) {
  const counts: Record<string, number> = {};
  for (const r of data.rows) {
    const bucket = buckets.get(r)!;
    counts[bucket] = (counts[bucket] ?? 0) + 1;
  }
  const compared =
    (counts.close ?? 0) + (counts.moderate ?? 0) + (counts.far ?? 0);
  const withValues = compared + (counts.concept_mismatch ?? 0);
  const n = data.rows.length - (counts.suppressed ?? 0);
  const programs = new Set(
    data.rows.map((r) => r.program).filter((p) => p !== "spm_poverty"),
  ).size;
  return (
    <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
      Urban publishes{" "}
      <b className="text-foreground fig">{n.toLocaleString()}</b> unsuppressed
      cells across {programs} programs and the poverty counterfactual.
      PolicyEngine currently produces a counterpart for{" "}
      <b className="text-foreground fig">{withValues.toLocaleString()}</b> of
      them ({Math.round((withValues / n) * 100)}%);{" "}
      <b className="text-foreground fig">
        {(counts.close ?? 0).toLocaleString()}
      </b>{" "}
      land within tolerance. {PROGRAM_LABELS.liheap} and{" "}
      {PROGRAM_LABELS.ccdf} are honest gaps. Click a segment to filter.
    </p>
  );
}
