import { useMemo, useState } from "react";
import type {
  IndexSource,
  Row,
  ScorecardIndex,
  SourceSlice,
} from "../types";
import { RELATIONSHIP_LABELS } from "../types";
import { bucketOf, SPINE_META, type SpineBucket } from "../spine";
import { CoverageSpine } from "./CoverageSpine";
import {
  ComparisonTable,
  DEFAULT_URBAN_FILTERS,
  type UrbanFilters,
} from "./ComparisonTable";
import { DivergenceBoard } from "./DivergenceBoard";
import { GapsView } from "./GapsView";
import { AboutView } from "./AboutView";
import { BrowseTable } from "./BrowseTable";

const fmt = (n: number | undefined) => (n ?? 0).toLocaleString();

/** One external source's page: its identity, its honesty summary, and its
 * rows. Urban keeps the full spine + scorecard/divergences/gaps views; other
 * sources get the scoped table until their PE counterparts land. */
export function SourcePage({
  id,
  index,
  slices,
  loading,
  onBack,
}: {
  id: string;
  index: ScorecardIndex;
  slices: Map<string, SourceSlice>;
  loading: Set<string>;
  onBack: () => void;
}) {
  const src = index.sources.find((s) => s.id === id);
  const slice = slices.get(id);

  return (
    <div className="mx-auto max-w-content px-4">
      <button
        onClick={onBack}
        className="mt-4 text-sm text-primary underline-offset-2 hover:underline"
      >
        ← All sources
      </button>
      {src && <SourceHeader src={src} slice={slice} />}
      {!slice ? (
        <p className="py-8 text-muted-foreground">Loading rows…</p>
      ) : id === "urban_sotsn" ? (
        <UrbanBody slice={slice} peBundle={index.pe_bundle} />
      ) : (
        <GenericBody
          slice={slice}
          src={src}
          index={index}
          slices={slices}
          loading={loading}
        />
      )}
    </div>
  );
}

function SourceHeader({
  src,
  slice,
}: {
  src: IndexSource;
  slice?: SourceSlice;
}) {
  const meta = slice?.meta;
  const rel = src.relationships;
  const period =
    src.period_min === src.period_max
      ? String(src.period_min)
      : `${src.period_min}–${src.period_max}`;
  return (
    <header className="pt-3 pb-4">
      <h1 className="text-2xl font-bold tracking-tight">
        {src.name}{" "}
        <span className="text-base font-normal text-muted-foreground">
          {src.model ?? ""}
        </span>
      </h1>
      {meta?.method && (
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          {meta.method}
        </p>
      )}
      <p className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
        {meta?.url && (
          <a
            className="text-primary underline underline-offset-2"
            href={meta.url}
            target="_blank"
            rel="noreferrer"
          >
            {new URL(meta.url).hostname}
          </a>
        )}
        {src.fetched && <span>fetched {src.fetched}</span>}
        <span>claims {period}</span>
        <span className="fig">
          {fmt(src.claims)} claims · {fmt(src.computed)} with PE counterparts
          {src.suppressed > 0 && ` · ${fmt(src.suppressed)} suppressed`}
        </span>
        <span>
          {(
            Object.entries(rel) as [keyof typeof rel, number | undefined][]
          )
            .filter(([, n]) => (n ?? 0) > 0)
            .map(
              ([k, n]) =>
                `${fmt(n)} ${RELATIONSHIP_LABELS[k as keyof typeof RELATIONSHIP_LABELS]}`,
            )
            .join(" · ")}
        </span>
      </p>
      {meta?.diagnosis_upstream && (
        <p className="mt-1 text-[11px] text-muted-foreground">
          {meta.diagnosis_upstream}
        </p>
      )}
    </header>
  );
}

const URBAN_TABS = [
  { id: "scorecard", label: "Scorecard" },
  { id: "divergences", label: "Divergences" },
  { id: "gaps", label: "Gaps" },
  { id: "about", label: "Method" },
] as const;
type UrbanTabId = (typeof URBAN_TABS)[number]["id"];

function UrbanBody({
  slice,
  peBundle,
}: {
  slice: SourceSlice;
  peBundle: Record<string, string | undefined>;
}) {
  const [tab, setTab] = useState<UrbanTabId>("scorecard");
  const [filters, setFilters] = useState<UrbanFilters>(DEFAULT_URBAN_FILTERS);
  const buckets = useMemo(
    () => new Map<Row, SpineBucket>(slice.rows.map((r) => [r, bucketOf(r)])),
    [slice],
  );

  return (
    <div>
      <CoverageSpine
        rows={slice.rows}
        buckets={buckets}
        active={filters.bucket}
        onSelect={(bucket) => {
          setFilters({ ...filters, bucket });
          setTab("scorecard");
        }}
        label="Coverage of the source's published cells by comparison status"
      />
      <nav
        className="mt-6 flex gap-1 border-b border-border"
        aria-label="Source views"
      >
        {URBAN_TABS.map((t) => (
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
      <div className="py-6">
        {tab === "scorecard" && (
          <ComparisonTable
            slice={slice}
            buckets={buckets}
            filters={filters}
            setFilters={setFilters}
          />
        )}
        {tab === "divergences" && (
          <DivergenceBoard slice={slice} buckets={buckets} />
        )}
        {tab === "gaps" && <GapsView slice={slice} />}
        {tab === "about" && <AboutView slice={slice} peBundle={peBundle} />}
      </div>
    </div>
  );
}

function GenericBody({
  slice,
  src,
  index,
  slices,
  loading,
}: {
  slice: SourceSlice;
  src?: IndexSource;
  index: ScorecardIndex;
  slices: Map<string, SourceSlice>;
  loading: Set<string>;
}) {
  const [showPubs, setShowPubs] = useState(false);
  const bins = slice.summary.agreement_bins;
  const binTotal = Object.values(bins).reduce((a, b) => a + (b ?? 0), 0);
  return (
    <div className="pb-6">
      {binTotal > 0 && (
        <p className="mb-3 text-xs text-muted-foreground">
          Held-out agreement profile:{" "}
          {(["close", "moderate", "far"] as const)
            .filter((b) => (bins[b] ?? 0) > 0)
            .map((b) => `${fmt(bins[b])} ${SPINE_META[b].label}`)
            .join(" · ")}
        </p>
      )}
      {src && src.computed === 0 && (
        <p className="mb-4 max-w-3xl text-sm text-muted-foreground">
          No PolicyEngine counterparts computed for this source yet — the
          claims are cataloged and every row below shows its current status.
          Conventional reform scores queue behind constructed reform runs;
          dynamic-scoring rows are out of model (PolicyEngine is static).
        </p>
      )}
      <BrowseTable
        sources={index.sources}
        slices={slices}
        loading={loading}
        selected={new Set([slice.id])}
        onToggleSource={() => {}}
        lockSource={slice.id}
      />
      <section className="mt-6">
        <button
          onClick={() => setShowPubs(!showPubs)}
          className="text-sm text-primary underline-offset-2 hover:underline"
        >
          {showPubs ? "Hide" : "Show"} the {fmt(slice.pubs.length)} cataloged
          publications
        </button>
        {showPubs && (
          <ul className="mt-2 grid gap-1 text-xs md:grid-cols-2">
            {slice.pubs.map((p, i) => (
              <li key={i} className="truncate text-muted-foreground">
                {p.url || p.page_url ? (
                  <a
                    className="text-primary underline underline-offset-2"
                    href={String(p.page_url ?? p.url)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {p.title ?? String(p.url)}
                  </a>
                ) : (
                  (p.title ?? "untitled")
                )}
                {p.date ? ` (${p.date})` : ""}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
