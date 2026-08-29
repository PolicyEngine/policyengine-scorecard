import { useEffect, useMemo, useState } from "react";
import type {
  Comparison,
  Country,
  LanesFeed,
  PopulationsFeed,
  Row,
} from "./types";
import { COUNTRY_LABELS, PROGRAM_LABELS, countryOf } from "./types";
import { bucketOf, type SpineBucket } from "./spine";
import { CoverageSpine } from "./components/CoverageSpine";
import { ComparisonTable } from "./components/ComparisonTable";
import { DivergenceBoard } from "./components/DivergenceBoard";
import { GapsView } from "./components/GapsView";
import { AboutView } from "./components/AboutView";
import { MissionControl } from "./components/MissionControl";
import { ReformValidationView } from "./components/ReformValidationView";
import { TABS, buildUrlQuery, parseUrlState, type TabId } from "./urlState";

export interface Filters {
  country: Country;
  program: string;
  metric: string;
  geography: string; // country code (national) | "states" | state code
  subgroup: string; // "total" | "all" | slug
  bucket: SpineBucket | null;
}

function initialUrlState(): { country: Country; tab: TabId } {
  return parseUrlState(window.location.search);
}

function writeUrlState(country: Country, tab: TabId) {
  const query = buildUrlQuery(window.location.search, country, tab);
  window.history.replaceState(
    null,
    "",
    (query ? `${window.location.pathname}?${query}` : window.location.pathname) +
      window.location.hash,
  );
}

const DEFAULT_FILTERS: Filters = {
  country: "US",
  program: "all",
  metric: "all",
  geography: "US",
  subgroup: "total",
  bucket: null,
};

const HEADER_COPY: Record<Country, { eyebrow: string; counterpart: string }> = {
  US: {
    eyebrow: "Model validation · instance 1",
    counterpart: "vs Urban Institute's State of the Safety Net",
  },
  UK: {
    eyebrow: "Model validation · UK lanes",
    counterpart: "vs DWP, HMRC, OBR and UKMOD",
  },
  BE: {
    eyebrow: "Model validation · Belgium lanes",
    counterpart: "vs SPF Finances, Cour des comptes and JRC EUROMOD-BE",
  },
  NZ: {
    eyebrow: "Model validation · New Zealand lanes",
    counterpart: "vs New Zealand official budget scores",
  },
};

export default function App() {
  const [data, setData] = useState<Comparison | null>(null);
  const [lanes, setLanes] = useState<LanesFeed | null>(null);
  const [populations, setPopulations] = useState<PopulationsFeed | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>(() => initialUrlState().tab);
  const [filters, setFilters] = useState<Filters>(() => {
    const { country } = initialUrlState();
    return { ...DEFAULT_FILTERS, country, geography: country };
  });

  useEffect(() => {
    writeUrlState(filters.country, tab);
  }, [filters.country, tab]);

  useEffect(() => {
    fetch("./data/comparison.json")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(String(e)));
    fetch("./data/lanes.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setLanes)
      .catch(() => setLanes(null));
    fetch("./data/populations.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setPopulations)
      .catch(() => setPopulations(null));
  }, []);

  const buckets = useMemo(() => {
    if (!data) return new Map<Row, SpineBucket>();
    return new Map(data.rows.map((r) => [r, bucketOf(r)] as const));
  }, [data]);

  // Country-scoped view of the comparison: rows without a country key are
  // US-era exports (countryOf defaults them), so nothing is ever dropped.
  const scoped = useMemo(() => {
    if (!data) return null;
    return {
      ...data,
      rows: data.rows.filter((r) => countryOf(r) === filters.country),
    };
  }, [data, filters.country]);

  if (error) {
    return (
      <div className="mx-auto max-w-content p-8">
        <p className="text-destructive">
          Could not load data/comparison.json ({error}). Run the pipeline, then
          copy data into app/public/data/.
        </p>
      </div>
    );
  }
  if (!data || !scoped) {
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
            external (US comparison) · {data.source_meta.id} · fetched{" "}
            {data.source_meta.fetched} · {data.source_meta.period}
          </span>
          <span>
            policyengine · {b.runtime_dataset} @ {datasetId} · {b.model_package}{" "}
            {b.model_version} · annual 2024
          </span>
          <span>built {data.built}</span>
        </div>
      </div>

      <header className="mx-auto max-w-content px-4 pt-8 pb-2">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs font-semibold uppercase tracking-widest text-primary">
            {HEADER_COPY[filters.country].eyebrow}
          </p>
          <CountryToggle
            country={filters.country}
            onSelect={(country) =>
              // Reset row filters on switch: geography codes, buckets and
              // subgroups don't carry across countries.
              setFilters({ ...DEFAULT_FILTERS, country, geography: country })
            }
          />
        </div>
        <h1 className="mt-1 text-3xl font-bold tracking-tight">
          PolicyEngine scorecard{" "}
          <span className="font-normal text-muted-foreground">
            {HEADER_COPY[filters.country].counterpart}
          </span>
        </h1>
        <Headline
          data={scoped}
          buckets={buckets}
          country={filters.country}
          lanes={lanes}
        />
      </header>

      <div className="mx-auto max-w-content px-4">
        {scoped.rows.length > 0 && (
          <CoverageSpine
            rows={scoped.rows}
            buckets={buckets}
            active={filters.bucket}
            onSelect={(bucket) => {
              setFilters({ ...filters, bucket });
              setTab("scorecard");
            }}
          />
        )}
        <MissionControl data={data} lanes={lanes} country={filters.country} />
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
        {tab === "scorecard" &&
          (scoped.rows.length > 0 ? (
            <ComparisonTable
              data={scoped}
              buckets={buckets}
              filters={filters}
              setFilters={setFilters}
            />
          ) : (
            <CountryEmptyState country={filters.country} lanes={lanes} />
          ))}
        {tab === "divergences" &&
          (scoped.rows.length > 0 ? (
            <DivergenceBoard data={scoped} buckets={buckets} country={filters.country} />
          ) : (
            <CountryEmptyState country={filters.country} lanes={lanes} />
          ))}
        {tab === "validation" &&
          (populations ? (
            <ReformValidationView
              key={filters.country}
              feed={populations}
              country={filters.country}
            />
          ) : (
            <p className="text-sm text-muted-foreground">
              No populations feed — run scorecard_db.export_populations, then
              copy data into app/public/data/.
            </p>
          ))}
        {tab === "gaps" &&
          (scoped.rows.length > 0 ? (
            <GapsView data={scoped} />
          ) : (
            <CountryEmptyState country={filters.country} lanes={lanes} />
          ))}
        {tab === "about" && <AboutView data={data} />}
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto max-w-content px-4 py-4 text-xs text-muted-foreground">
          Every annotation traces to the comparison method, engine metadata,
          or a measured diagnostic — see the method tab. Divergences and
          concept mismatches stay visible.
        </div>
      </footer>
    </div>
  );
}

function CountryToggle({
  country,
  onSelect,
}: {
  country: Country;
  onSelect: (c: Country) => void;
}) {
  return (
    <div
      className="inline-flex overflow-hidden rounded-md border border-border"
      role="group"
      aria-label="Country"
    >
      {(Object.keys(COUNTRY_LABELS) as Country[]).map((c) => (
        <button
          key={c}
          onClick={() => onSelect(c)}
          aria-pressed={country === c}
          title={COUNTRY_LABELS[c]}
          className={
            "px-3 py-1 text-xs font-semibold " +
            (country === c
              ? "bg-primary text-primary-foreground"
              : "bg-background text-muted-foreground hover:text-foreground")
          }
        >
          {c}
        </button>
      ))}
    </div>
  );
}

/**
 * A country without main-grid cells renders as a status panel, not a blank
 * page (issue #42): lanes and their stages stay visible. A completed lane may
 * intentionally live on Reform validation when its values are not comparable.
 */
function CountryEmptyState({
  country,
  lanes,
}: {
  country: Country;
  lanes: LanesFeed | null;
}) {
  const countryLanes = (lanes?.lanes ?? []).filter(
    (l) => countryOf(l) === country,
  );
  const emptyCopy =
    country === "BE"
      ? "Belgium registers two lanes. On Reform validation, SPF Finances, Cour des comptes and PolicyEngine estimates of the 15 July 2026 PIT reform sit side by side, the official horizon-2030 figures carried as constructed cross-attachments on an unresolved period basis. The JRC EUROMOD-BE lane has five model claims — EUROMOD totals simulated on uprated EU-SILC survey input, not administrative statistics; its six statistical rows and one non-simulated uprated EU-SILC survey input route to Chronicle, and its six ratios remain derived, not claims. Two demo-grade Axiom worker values appear on Reform validation as concept mismatches; no value is presented as comparable."
      : `No ${COUNTRY_LABELS[country]} rows in this view yet — the ${country} external lanes are mid-pipeline. Each lane below reports its stage from data/lanes.json; as counterparts compute, rows appear here under the same descriptive status taxonomy as the US instance, model gaps and concept mismatches included.`;
  return (
    <div className="max-w-3xl">
      <p className="text-sm leading-6 text-muted-foreground">
        {emptyCopy}
      </p>
      <ul className="mt-3 space-y-1.5">
        {countryLanes.map((l) => (
          <li key={l.id} className="text-xs">
            <b>{l.source}</b> · {l.area}
            <span className="text-muted-foreground"> — {l.stage}</span>
          </li>
        ))}
        {countryLanes.length === 0 && (
          <li className="text-xs text-muted-foreground">
            No lanes registered for this country — see data/lanes.json.
          </li>
        )}
      </ul>
    </div>
  );
}

function Headline({
  data,
  buckets,
  country,
  lanes,
}: {
  data: Comparison;
  buckets: Map<Row, SpineBucket>;
  country: Country;
  lanes: LanesFeed | null;
}) {
  if (data.rows.length === 0) {
    const countryLanes = (lanes?.lanes ?? []).filter(
      (l) => countryOf(l) === country,
    );
    return (
      <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
        {country === "BE" ? (
          <>
            Belgium&apos;s registered claims — seven on the 15 July 2026 PIT
            reform from SPF Finances, Cour des comptes and PolicyEngine, plus
            five JRC EUROMOD-BE model claims (EUROMOD totals simulated on
            uprated EU-SILC survey input, not administrative statistics) —
            live on Reform validation. The two available Axiom values on the
            JRC claims have period, population-basis and scope gaps, so they
            are labeled concept mismatch there rather than entering this
            comparison grid.
          </>
        ) : country === "NZ" ? (
          <>
            New Zealand Treasury official budget scores live on Reform
            validation. Claims appear there even before a PolicyEngine result
            is available, labeled Not yet computed; their external values stay
            visible as replicated estimates are added.
          </>
        ) : (
          <>
            No {country} comparison cells yet —{" "}
            <b className="text-foreground fig">{countryLanes.length}</b>{" "}
            {country} lanes (
            {countryLanes.map((l) => l.source).join(", ") || "none"}) are
            registered in data/lanes.json and tracked on mission control
            below. The country stays on the page while its pipeline runs.
          </>
        )}
      </p>
    );
  }
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
      {country === "US"
        ? "Urban publishes"
        : country === "UK"
          ? "UK sources publish"
          : country === "BE"
            ? "JRC EUROMOD-BE publishes"
            : "New Zealand sources publish"}{" "}
      <b className="text-foreground fig">{n.toLocaleString()}</b> unsuppressed
      cells across {programs} programs
      {country === "US" && " and the poverty counterfactual"}. The computed
      model currently produces a counterpart for{" "}
      <b className="text-foreground fig">{withValues.toLocaleString()}</b> of
      them ({Math.round((withValues / n) * 100)}%);{" "}
      <b className="text-foreground fig">
        {(counts.close ?? 0).toLocaleString()}
      </b>{" "}
      land within tolerance.
      {country === "US" && (
        <>
          {" "}
          {PROGRAM_LABELS.liheap} and {PROGRAM_LABELS.ccdf} are honest gaps.
        </>
      )}{" "}
      Click a segment to filter.
    </p>
  );
}
