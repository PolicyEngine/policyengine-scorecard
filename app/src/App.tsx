import { useEffect, useMemo, useState } from "react";
import {
  PolicyEngineShell,
  getPolicyEngineFooterLinks,
  getPolicyEngineNavItems,
  getPolicyEngineUrl,
} from "@policyengine/ui-kit/layout";
import {
  SegmentedControl,
  Tabs,
  TabsList,
  TabsTrigger,
} from "@policyengine/ui-kit/primitives";
import type {
  Comparison,
  Country,
  LanesFeed,
  PopulationsFeed,
  Row,
} from "./types";
import { COUNTRY_LABELS, countryOf } from "./types";
import { bucketOf, type SpineBucket } from "./spine";
import { defaultFilters, type Filters } from "./filters";
import { NavContext } from "./navigation";
import { COUNTERPART } from "./copy";
import { ComparisonTable } from "./components/ComparisonTable";
import { DivergenceBoard } from "./components/DivergenceBoard";
import { GapsView } from "./components/GapsView";
import { AboutView } from "./components/AboutView";
import { Overview } from "./components/Overview";
import { CountryEmptyState } from "./components/CountryEmptyState";
import { ReformValidationView } from "./components/ReformValidationView";
import { TABS, buildUrlQuery, parseUrlState, type TabId } from "./urlState";
import { withBasePath } from "./basePath";

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

const COUNTRIES = Object.keys(COUNTRY_LABELS) as Country[];

const FLAGS: Record<Country, string> = {
  US: "🇺🇸",
  UK: "🇬🇧",
  BE: "🇧🇪",
  NZ: "🇳🇿",
};

export default function App() {
  const [data, setData] = useState<Comparison | null>(null);
  const [lanes, setLanes] = useState<LanesFeed | null>(null);
  const [populations, setPopulations] = useState<PopulationsFeed | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>(() => initialUrlState().tab);
  const [filters, setFilters] = useState<Filters>(() =>
    defaultFilters(initialUrlState().country),
  );
  const country = filters.country;

  useEffect(() => {
    writeUrlState(country, tab);
  }, [country, tab]);

  useEffect(() => {
    fetch(withBasePath("data/comparison.json"))
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(String(e)));
    fetch(withBasePath("data/lanes.json"))
      .then((r) => (r.ok ? r.json() : null))
      .then(setLanes)
      .catch(() => setLanes(null));
    fetch(withBasePath("data/populations.json"))
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
      rows: data.rows.filter((r) => countryOf(r) === country),
    };
  }, [data, country]);

  // Switching country resets row filters: geography codes, buckets and
  // subgroups don't carry across countries.
  const selectCountry = (c: Country) => setFilters(defaultFilters(c));

  const nav = useMemo(
    () => ({
      go: (next: TabId, patch?: Partial<Filters>) => {
        if (patch) setFilters((f) => ({ ...f, ...patch }));
        setTab(next);
        window.scrollTo({ top: 0 });
      },
    }),
    [],
  );

  // The shared PolicyEngine header/footer only know the site countries;
  // BE and NZ instances borrow the US site chrome.
  const siteCountry = country === "UK" ? "uk" : "us";
  const hasRows = (scoped?.rows.length ?? 0) > 0;

  return (
    <NavContext.Provider value={nav}>
      <PolicyEngineShell
        country={siteCountry}
        mainClassName="bg-muted"
        headerProps={{
          navItems: getPolicyEngineNavItems(siteCountry),
          logoHref: getPolicyEngineUrl(siteCountry),
          countries: COUNTRIES.map((c) => ({
            id: c.toLowerCase(),
            label: COUNTRY_LABELS[c],
            flagEmoji: FLAGS[c],
          })),
          onCountryChange: (id) => selectCountry(id.toUpperCase() as Country),
        }}
        footerProps={{ links: getPolicyEngineFooterLinks(siteCountry) }}
      >
        <div className="border-b border-border bg-background">
          <div className="mx-auto max-w-[75rem] px-4 pt-6 sm:px-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Scorecard</h1>
                <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
                  {COUNTERPART[country]}
                </p>
              </div>
              <div className="max-w-full overflow-x-auto">
                <SegmentedControl
                  value={country}
                  onValueChange={(v) => selectCountry(v as Country)}
                  options={COUNTRIES.map((c) => ({
                    value: c,
                    label: COUNTRY_LABELS[c],
                  }))}
                />
              </div>
            </div>
            <Tabs
              value={tab}
              onValueChange={(v) => nav.go(v as TabId)}
              className="mt-5"
            >
              <TabsList
                variant="line"
                className="h-auto w-full justify-start gap-1 overflow-x-auto"
                aria-label="Views"
              >
                {TABS.map((t) => (
                  <TabsTrigger
                    key={t.id}
                    value={t.id}
                    title={t.blurb}
                    className="flex-none px-3 pb-2"
                  >
                    {t.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </Tabs>
          </div>
        </div>

        <div className="mx-auto max-w-[75rem] px-4 py-6 sm:px-6">
          {error ? (
            <p className="text-sm text-destructive">
              Could not load data/comparison.json ({error}). Run the pipeline,
              then copy data into app/public/data/.
            </p>
          ) : !data || !scoped ? (
            <p className="text-sm text-muted-foreground">
              Loading comparison data…
            </p>
          ) : (
            <>
              {tab === "overview" && (
                <Overview
                  data={data}
                  scoped={scoped}
                  buckets={buckets}
                  lanes={lanes}
                  populations={populations}
                  country={country}
                />
              )}
              {tab === "scorecard" &&
                (hasRows ? (
                  <ComparisonTable
                    data={scoped}
                    buckets={buckets}
                    filters={filters}
                    setFilters={setFilters}
                  />
                ) : (
                  <CountryEmptyState country={country} lanes={lanes} />
                ))}
              {tab === "divergences" &&
                (hasRows ? (
                  <DivergenceBoard
                    data={scoped}
                    buckets={buckets}
                    country={country}
                  />
                ) : (
                  <CountryEmptyState country={country} lanes={lanes} />
                ))}
              {tab === "validation" &&
                (populations ? (
                  <ReformValidationView
                    key={country}
                    feed={populations}
                    country={country}
                  />
                ) : (
                  <p className="text-sm text-muted-foreground">
                    No populations feed — run scorecard_db.export_populations,
                    then copy data into app/public/data/.
                  </p>
                ))}
              {tab === "gaps" &&
                (hasRows ? (
                  <GapsView data={scoped} />
                ) : (
                  <CountryEmptyState country={country} lanes={lanes} />
                ))}
              {tab === "about" && <AboutView data={data} />}
            </>
          )}
        </div>
      </PolicyEngineShell>
    </NavContext.Provider>
  );
}
