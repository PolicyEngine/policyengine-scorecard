import type { LanesFeed, ScorecardIndex } from "../types";

const STAGE_ORDER = [
  "diagnosing",
  "computed",
  "ingested",
  "cataloged",
  "registered",
  "published",
  "regressed",
];

const STAGE_BLURB: Record<string, string> = {
  diagnosing: "divergences being decomposed",
  computed: "PE counterparts computed",
  ingested: "claims in the database",
  cataloged: "claims cataloged, not yet ingested",
  registered: "queued — known source, no claims yet",
  published: "live on this site",
  regressed: "moved on a newer certified build",
};

/**
 * The work, visible (issue #7): every lane the project runs, grouped by
 * stage — in-progress and queued work published next to results.
 */
export function MissionControl({
  lanes,
  index,
}: {
  lanes: LanesFeed | null;
  index: ScorecardIndex;
}) {
  const all = lanes?.lanes ?? [];
  const running = all.filter((l) => l.running);
  const stages = STAGE_ORDER.filter((s) =>
    all.some((l) => l.stage === s),
  ).map((s) => ({ stage: s, lanes: all.filter((l) => l.stage === s) }));

  return (
    <div>
      <p className="mb-4 max-w-3xl text-sm text-muted-foreground">
        Every comparison lane this project tracks — {all.length} lanes,{" "}
        {running.length} active. New sources join by registering a lane;
        ingested claims appear on the browse page automatically. PE results
        so far come from a single certified data bundle
        {index.pe_bundle.certified_data_build_id
          ? ` (${index.pe_bundle.certified_data_build_id})`
          : ""}
        ; per-release regression panels start when the next certified build
        lands.
      </p>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {stages.map(({ stage, lanes: group }) => (
          <section
            key={stage}
            className="rounded-md border border-border p-3"
          >
            <h2 className="flex items-baseline justify-between text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {stage}
              <span className="fig">{group.length}</span>
            </h2>
            <p className="mt-0.5 text-[11px] text-muted-foreground">
              {STAGE_BLURB[stage] ?? ""}
            </p>
            <ul className="mt-2 space-y-2">
              {group.map((l) => (
                <li key={l.id} className="text-xs leading-4">
                  <span className="flex items-start gap-1.5">
                    {l.running && (
                      <span className="mt-1 inline-block h-1.5 w-1.5 shrink-0 animate-pulse rounded-full bg-[var(--chart-1)]" />
                    )}
                    <span>
                      <b>{l.source}</b> · {l.area}
                      <span className="block text-muted-foreground">
                        {l.note}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {l.updated}
                      </span>
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
