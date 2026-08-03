import { useCallback, useEffect, useState } from "react";
import { fetchIndex, fetchSlice } from "./data";
import type { LanesFeed, ScorecardIndex, SourceSlice } from "./types";
import { Tiles } from "./components/Tiles";
import { SourceCards } from "./components/SourceCards";
import { BrowseTable } from "./components/BrowseTable";
import { SourcePage } from "./components/SourcePage";
import { ExplanationsView } from "./components/ExplanationsView";
import { MissionControl } from "./components/MissionControl";
import { MethodView } from "./components/MethodView";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "browse", label: "Browse" },
  { id: "explanations", label: "How models differ" },
  { id: "mission", label: "Mission control" },
  { id: "method", label: "Method" },
] as const;
type TabId = (typeof TABS)[number]["id"];

export default function App() {
  const [index, setIndex] = useState<ScorecardIndex | null>(null);
  const [lanes, setLanes] = useState<LanesFeed | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>("overview");
  const [sourcePage, setSourcePage] = useState<string | null>(null);
  const [slices, setSlices] = useState<Map<string, SourceSlice>>(new Map());
  const [loading, setLoading] = useState<Set<string>>(new Set());
  const [browseSelected, setBrowseSelected] = useState<Set<string>>(
    new Set(),
  );

  useEffect(() => {
    fetchIndex()
      .then((ix) => {
        setIndex(ix);
        setBrowseSelected(new Set(ix.sources.map((s) => s.id)));
      })
      .catch((e) => setError(String(e)));
    fetch("./data/lanes.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setLanes)
      .catch(() => setLanes(null));
  }, []);

  const ensureSlice = useCallback(
    (id: string) => {
      if (slices.has(id) || loading.has(id)) return;
      setLoading((prev) => new Set(prev).add(id));
      fetchSlice(id)
        .then((slice) => {
          setSlices((prev) => new Map(prev).set(id, slice));
        })
        .catch(() => {})
        .finally(() => {
          setLoading((prev) => {
            const next = new Set(prev);
            next.delete(id);
            return next;
          });
        });
    },
    [slices, loading],
  );

  // Browse loads every toggled-on source; the source page loads its own.
  useEffect(() => {
    if (tab === "browse" && !sourcePage) {
      for (const id of browseSelected) ensureSlice(id);
    }
  }, [tab, sourcePage, browseSelected, ensureSlice]);
  useEffect(() => {
    if (sourcePage) ensureSlice(sourcePage);
  }, [sourcePage, ensureSlice]);

  const openSource = (id: string) => {
    setSourcePage(id);
    window.scrollTo(0, 0);
  };

  if (error) {
    return (
      <div className="mx-auto max-w-content p-8">
        <p className="text-destructive">
          Could not load data/index.json ({error}). Run
          pipeline/export_db.py, which writes app/public/data/.
        </p>
      </div>
    );
  }
  if (!index) {
    return (
      <div className="mx-auto max-w-content p-8 text-muted-foreground">
        Loading the scorecard index…
      </div>
    );
  }

  const b = index.pe_bundle;
  const datasetId = (b.certified_data_build_id ?? "").split("-").slice(-2)[0];

  return (
    <div className="min-h-screen">
      {/* provenance stamp */}
      <div className="border-b border-border bg-muted/60">
        <div className="mx-auto max-w-content px-4 py-1.5 fig text-[11px] leading-4 text-muted-foreground flex flex-wrap gap-x-4">
          <span>
            external · {index.catalog.sources} sources ·{" "}
            {index.catalog.claims.toLocaleString()} claims
          </span>
          <span>
            policyengine · {b.runtime_dataset} @ {datasetId} ·{" "}
            {b.model_package} {b.model_version} · annual 2024
          </span>
          <span>built {index.built}</span>
        </div>
      </div>

      {sourcePage ? (
        <SourcePage
          id={sourcePage}
          index={index}
          slices={slices}
          loading={loading}
          onBack={() => setSourcePage(null)}
        />
      ) : (
        <>
          <header className="mx-auto max-w-content px-4 pt-8 pb-2">
            <p className="text-xs font-semibold uppercase tracking-widest text-primary">
              Model validation · every comparison published
            </p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight">
              PolicyEngine scorecard{" "}
              <span className="font-normal text-muted-foreground">
                vs {index.catalog.sources} external models
              </span>
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
              {index.catalog.sources} sources publish{" "}
              <b className="text-foreground fig">
                {index.catalog.ok.toLocaleString()}
              </b>{" "}
              claims this project can hold PolicyEngine against — safety-net
              statistics, revenue scores, distribution tables, poverty
              series. PolicyEngine currently produces a counterpart for{" "}
              <b className="text-foreground fig">
                {index.catalog.computed.toLocaleString()}
              </b>{" "}
              of them; the rest stay on the page as out-of-model or
              not-yet-computed rows. Distances are shown in descriptive
              bins — in model-vs-model comparison, divergence is material
              for explanation, not a verdict.
            </p>
          </header>

          <nav
            className="mx-auto max-w-content px-4 mt-4 border-b border-border flex gap-1 overflow-x-auto"
            aria-label="Views"
          >
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={
                  "px-4 py-2 text-sm rounded-t-md border border-b-0 whitespace-nowrap " +
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
            {tab === "overview" && (
              <>
                <Tiles index={index} />
                <h2 className="mt-8 text-lg font-semibold">Sources</h2>
                <p className="mt-1 text-xs text-muted-foreground">
                  One card per external model. Click through for its full
                  claim set; new ingests (UK sources next) appear here
                  automatically.
                </p>
                <SourceCards index={index} onSelect={openSource} />
              </>
            )}
            {tab === "browse" && (
              <BrowseTable
                sources={index.sources}
                slices={slices}
                loading={loading}
                selected={browseSelected}
                onToggleSource={(id) => {
                  setBrowseSelected((prev) => {
                    const next = new Set(prev);
                    if (next.has(id)) {
                      next.delete(id);
                    } else {
                      next.add(id);
                      ensureSlice(id);
                    }
                    return next;
                  });
                }}
              />
            )}
            {tab === "explanations" && (
              <ExplanationsView index={index} onOpenSource={openSource} />
            )}
            {tab === "mission" && (
              <MissionControl lanes={lanes} index={index} />
            )}
            {tab === "method" && <MethodView index={index} />}
          </main>
        </>
      )}

      <footer className="border-t border-border">
        <div className="mx-auto max-w-content px-4 py-4 text-xs text-muted-foreground">
          Every annotation traces to a source document, engine metadata, or a
          measured diagnostic — see the method page. Misses stay on the page.
        </div>
      </footer>
    </div>
  );
}
