import type { ScorecardIndex, Status } from "../types";
import { STATUS_LABELS } from "../types";
import { SPINE_META } from "../spine";

const fmt = (n: number | undefined) => (n ?? 0).toLocaleString();

/**
 * The four home tiles (issue #9, as amended): coverage · agreement profile
 * in descriptive bins · explained share · random-strand breadth —
 * distances, counts, and what has an explanation.
 */
export function Tiles({ index }: { index: ScorecardIndex }) {
  const t = index.tiles;
  const bins = t.agreement.bins;
  const binTotal =
    (bins.close ?? 0) + (bins.moderate ?? 0) + (bins.far ?? 0) || 1;
  const excluded = Object.values(t.agreement.excluded_labeled).reduce(
    (a, b) => a + (b ?? 0),
    0,
  );
  const strand = t.random_strand;
  const strandStatuses = Object.entries(strand.by_status).sort(
    (a, b) => (b[1] ?? 0) - (a[1] ?? 0),
  );

  return (
    <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <Tile
        label="Coverage"
        headline={
          <>
            {fmt(t.coverage.computed)}
            <span className="text-base font-normal text-muted-foreground">
              {" "}
              / {fmt(t.coverage.ok)}
            </span>
          </>
        }
      >
        External claims with a PolicyEngine counterpart today, across{" "}
        {t.coverage.sources} sources. Every uncovered claim stays on the
        page as an out-of-model or not-yet-computed row.
      </Tile>

      <Tile
        label="Agreement profile"
        headline={
          <span className="flex h-6 w-full overflow-hidden rounded-sm border border-border">
            {(["close", "moderate", "far"] as const).map((b) => (
              <span
                key={b}
                title={`${SPINE_META[b].label}: ${fmt(bins[b])}`}
                style={{
                  width: `${((bins[b] ?? 0) / binTotal) * 100}%`,
                  background: SPINE_META[b].color,
                }}
              />
            ))}
          </span>
        }
      >
        {fmt(t.agreement.held_out_compared)} held-out comparisons in
        descriptive distance bins: {fmt(bins.close)} within 2.5pp/10%,{" "}
        {fmt(bins.moderate)} within 10pp/30%, {fmt(bins.far)} beyond.{" "}
        {fmt(excluded)} consumed-target/seed rows are labeled and excluded.
      </Tile>

      <Tile
        label="Explained share"
        headline={
          <>
            {fmt(t.explained.explained)}
            <span className="text-base font-normal text-muted-foreground">
              {" "}
              / {fmt(t.explained.material)}
            </span>
          </>
        }
      >
        Material divergences (beyond the closest bin) with a published
        explanation — the quality metric this project optimizes.{" "}
        {fmt(t.explained.explanations_published)} explanations published so
        far.
      </Tile>

      <Tile
        label="Random strand"
        headline={
          <>
            {fmt(strand.drawn)}
            <span className="text-base font-normal text-muted-foreground">
              {" "}
              drawn blind
            </span>
          </>
        }
      >
        Fixed-seed sample ({strand.seed}) across the whole catalog,
        published regardless of result:{" "}
        {strandStatuses
          .map(
            ([s, n]) =>
              `${fmt(n)} ${(
                STATUS_LABELS[s as Status] ?? s.replace(/_/g, " ")
              ).toLowerCase()}`,
          )
          .join(", ")}
        . The anti-curation guarantee.
      </Tile>
    </div>
  );
}

function Tile({
  label,
  headline,
  children,
}: {
  label: string;
  headline: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-md border border-border p-3">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </h2>
      <p className="mt-1.5 text-2xl font-bold fig">{headline}</p>
      <p className="mt-1 text-xs leading-4 text-muted-foreground">
        {children}
      </p>
    </section>
  );
}
