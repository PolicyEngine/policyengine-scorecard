import { closeness, fmtDivergence } from "../format";
import type { Comparison, Country, Lane, LanesFeed } from "../types";
import { METRIC_LABELS, PROGRAM_LABELS, countryOf } from "../types";

/**
 * The home view is mission control (issue #7): running lanes, the held-out
 * win/miss record, and the freshest divergences — in-progress work visible,
 * not just results. Scoped to the header's country (issue #42): the
 * comparison feed is the US Urban comparison, so its record and divergences
 * render only under US; the UK panels describe the UK lanes' own state.
 */
export function MissionControl({
  data,
  lanes,
  country,
}: {
  data: Comparison;
  lanes: LanesFeed | null;
  country: Country;
}) {
  const countryLanes = (lanes?.lanes ?? []).filter(
    (l) => countryOf(l) === country,
  );
  const running = countryLanes.filter((l) => l.running);
  const backlog = countryLanes.filter(
    (l) => !l.running && l.stage === "registered",
  );

  // Held-out record: the only published "validation" column (issue #1).
  // data is the US Urban comparison feed — US-scope only, never shown as
  // if it described the UK.
  const heldOut =
    country === "US"
      ? data.rows.filter(
          (r) =>
            r.calibration_relationship === "held_out" &&
            ["comparable", "constructed"].includes(r.status) &&
            r.pe_value !== null &&
            r.external_value !== null,
        )
      : [];
  const wins = heldOut.filter((r) => closeness(r) === "close").length;

  const freshest =
    country === "US"
      ? data.rows
          .filter(
            (r) =>
              // national row: geography code equals the row's country code
              r.geography === countryOf(r) &&
              r.subgroup === "total" &&
              r.variant === null &&
              ["comparable", "constructed"].includes(r.status) &&
              ["moderate", "far"].includes(closeness(r) ?? ""),
          )
          .slice(0, 3)
      : [];

  return (
    <div className="mt-5 grid gap-3 md:grid-cols-3">
      <section className="rounded-md border border-border p-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Held-out record
        </h2>
        {country === "US" ? (
          <>
            <p className="mt-1.5 text-2xl font-bold fig">
              {wins.toLocaleString()}
              <span className="text-base font-normal text-muted-foreground">
                {" "}
                / {heldOut.length.toLocaleString()}
              </span>
            </p>
            <p className="mt-1 text-xs leading-4 text-muted-foreground">
              Held-out comparisons within tolerance — numbers PolicyEngine
              never calibrated toward. Consumed-target agreement is a
              tautology and is labeled, never counted.
            </p>
          </>
        ) : (
          <p className="mt-1.5 text-xs leading-4 text-muted-foreground">
            No UK rows in the comparison feed yet. The first UK PE results —
            14 HMRC ready-reckoner scores, held-out relationship on a
            constructed comparison basis (PE current-law statics against
            HMRC's indexed-baseline FY projections) — are on the Reform
            validation tab; a UK record lands here when UK comparisons join
            this feed.
          </p>
        )}
      </section>

      <section className="rounded-md border border-border p-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Running lanes
        </h2>
        <ul className="mt-1.5 space-y-1.5">
          {running.map((l) => (
            <li key={l.id} className="flex items-start gap-2 text-xs">
              <span className="mt-1 inline-block h-1.5 w-1.5 shrink-0 animate-pulse rounded-full bg-[var(--chart-1)]" />
              <span>
                <b>{l.source}</b> · {l.area}
                <span className="text-muted-foreground"> — {l.stage}</span>
                <CountryChip lane={l} />
              </span>
            </li>
          ))}
          {running.length === 0 && (
            <li className="text-xs text-muted-foreground">
              No lanes running.
            </li>
          )}
        </ul>
        {country === "UK" && (
          <>
            <h3 className="mt-3 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
              UK pipeline
            </h3>
            <ul className="mt-1 space-y-1">
              {countryLanes
                .filter((l) => !l.running)
                .map((l) => (
                  <li key={l.id} className="text-xs">
                    <b>{l.source}</b> · {l.area}
                    <span className="text-muted-foreground"> — {l.stage}</span>
                  </li>
                ))}
            </ul>
          </>
        )}
        <p className="mt-2 text-[11px] text-muted-foreground">
          {backlog.length} registered {country} lanes queued — see
          data/lanes.json.
        </p>
      </section>

      <section className="rounded-md border border-border p-3">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Freshest divergences
        </h2>
        {country === "US" ? (
          <ul className="mt-1.5 space-y-1.5">
            {freshest.map((r) => (
              <li key={r.source_column} className="text-xs">
                <b>
                  {PROGRAM_LABELS[r.program] ?? r.program} ·{" "}
                  {METRIC_LABELS[r.metric] ?? r.metric}
                </b>{" "}
                <span className="fig text-destructive">{fmtDivergence(r)}</span>
                {r.calibration_relationship !== "held_out" && (
                  <span className="ml-1 text-muted-foreground">
                    ({r.calibration_relationship === "seed_source"
                      ? "seed source"
                      : "target consumed"})
                  </span>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-1.5 text-xs leading-4 text-muted-foreground">
            Arrives with the first UK held-out results — the ingested DWP,
            HBAI, OBR and UKMOD claims are waiting on PE computes (the
            compute pipeline lane).
          </p>
        )}
      </section>
    </div>
  );
}

/** Non-US lanes carry a small country tag; US stays unlabeled (the default). */
function CountryChip({ lane }: { lane: Lane }) {
  const c = countryOf(lane);
  if (c === "US") return null;
  return (
    <span className="ml-1.5 rounded-sm border border-border px-1 py-px text-[9px] uppercase tracking-wide text-muted-foreground">
      {c}
    </span>
  );
}
