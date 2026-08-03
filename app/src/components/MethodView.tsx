import type { ScorecardIndex } from "../types";
import { STATUS_LABELS, type Status } from "../types";

const STATUS_MEANING: Record<Status, string> = {
  comparable: "PolicyEngine measures the same concept",
  constructed:
    "PolicyEngine approximates the concept via a documented construction",
  concept_mismatch:
    "a PE value exists but measures a different concept — never netted into agreement figures",
  pe_gap: "the model or data artifact cannot produce this today",
  not_computed: "producible, but not yet in the pipeline",
  suppressed: "the source suppressed the cell; kept on the page",
};

/** The doctrine, once: what this site is and is not claiming. */
export function MethodView({ index }: { index: ScorecardIndex }) {
  const b = index.pe_bundle;
  const strand = index.tiles.random_strand;
  return (
    <div className="max-w-3xl space-y-6 text-sm leading-6">
      <section>
        <h2 className="mb-2 text-lg font-semibold">What this is</h2>
        <p>
          A repository of every external score we can find, with PolicyEngine
          scores alongside wherever the model can produce them:{" "}
          {index.catalog.claims.toLocaleString()} claims from{" "}
          {index.catalog.sources} sources, each stored with its publication
          provenance, policy world, baseline, and calibration relationship.
          The structure is PolicyEngine-native: every claim keys to a reform
          reference — current law for levels, a parametric or named-bill
          world for scores — and picks up its Ledger series id as cataloging
          lands. Each material divergence gets a decomposition into the
          documented choices that produce it — data vintage, income concept,
          scoring convention, baseline. Defect findings carry citations: an
          erratum, a tracked bug, an internal contradiction, linked from the
          row.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">The four home figures</h2>
        <p>
          <b>Coverage</b> — how much of the catalog has a PolicyEngine
          counterpart; uncovered claims stay visible. <b>Agreement
          profile</b> — the distance distribution over held-out comparisons,
          in bins (2.5pp/10pp for rates, 10%/30% for counts and dollars).{" "}
          <b>Explained share</b> — the fraction of material divergences with
          a published explanation; this is the metric the project optimizes.{" "}
          <b>Random strand</b> — a fixed-seed sample (seed {strand.seed})
          drawn across the whole catalog and published whatever the result,
          which keeps the published set uncurated.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Status taxonomy</h2>
        <table className="text-xs">
          <tbody>
            {(Object.keys(STATUS_MEANING) as Status[]).map((s) => (
              <tr key={s} className="border-t border-border/60">
                <td className="whitespace-nowrap py-1 pr-4 font-medium">
                  {STATUS_LABELS[s]}
                </td>
                <td className="py-1 text-muted-foreground">
                  {STATUS_MEANING[s]}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">
          Calibration relationships
        </h2>
        <p>
          Every claim is labeled <i>held out</i>, <i>target consumed</i>, or{" "}
          <i>seed source</i> against the certified build's documented target
          surface. Agreement on a consumed target is calibration, not
          validation — those rows are labeled and excluded from every
          aggregate agreement figure. Modeled-outcome statistics (poverty
          rates and other outputs of the simulated tax/benefit system) are
          permanent holdouts: fitting them would launder survey error back in
          and destroy the validation signal.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Baselines are first-class</h2>
        <p>
          A score's meaning is its (reform, baseline) pair. Claims scored
          against anything other than current law — TCJA extension, current
          policy, current law + Senate OBBBA Title VII, option-specific
          baselines — carry a baseline chip, and a PolicyEngine counterpart
          can only read as plain agreement when it runs the same pair.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">PolicyEngine side</h2>
        <table className="fig text-xs">
          <tbody>
            {[
              ["engine", `${b.model_package ?? ""} ${b.model_version ?? ""}`],
              ["dataset", b.runtime_dataset],
              ["certified bundle", b.certified_data_build_id],
              ["data package", `${b.data_package ?? ""} ${b.data_version ?? ""}`],
              ["built", index.built],
            ].map(([k, v]) => (
              <tr key={k}>
                <td className="py-0.5 pr-4 align-top whitespace-nowrap text-muted-foreground">
                  {k}
                </td>
                <td className="py-0.5 break-all">{v}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-2 text-xs text-muted-foreground">
          Dynamic-scoring claims are out of model: PolicyEngine is a static
          microsimulation, so only conventional rows can get counterparts.
          UK sources land through the same pipeline and will appear on the
          sources page automatically once ingested.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Reproduction</h2>
        <p className="text-muted-foreground">
          Everything renders from scorecard.db via pipeline/export_db.py in
          the policyengine-scorecard repo; adapters, the replication
          assessment, and the engine mechanics audit live there too. Every
          annotation traces to a document, engine metadata, or a measured
          diagnostic.
        </p>
      </section>
    </div>
  );
}
