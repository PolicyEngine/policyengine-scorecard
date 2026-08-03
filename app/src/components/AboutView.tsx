import type { SourceSlice } from "../types";

/** Urban-instance methodology: what the two columns are, how the 2026
 * column is built, run definitions, provenance. */
export function AboutView({
  slice,
  peBundle,
}: {
  slice: SourceSlice;
  peBundle: Record<string, string | undefined>;
}) {
  const prov = slice.pe_provenance ?? {};
  return (
    <div className="max-w-3xl space-y-6 text-sm leading-6">
      <section>
        <h2 className="mb-2 text-lg font-semibold">What the two columns are</h2>
        <p>
          <b>Urban</b> simulates program <i>eligibility</i> with ATTIS on
          pooled 2022+2023 ACS data and divides actual administrative caseloads
          by those simulated eligible counts; estimates refer to the average
          month of 2023. <b>PolicyEngine</b> simulates both sides on the
          certified Populace artifact: statute-encoded eligibility rules plus
          seeded take-up flags, with calibration to thousands of administrative
          targets. For count-targeted programs (SNAP, SSI) the participation
          numerator is disciplined by the same class of admin counts Urban
          uses directly, so agreement there is partly by construction — stated
          on every affected row.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Distance bins</h2>
        <p>
          Rates within 2.5 percentage points sit in the closest bin, within
          10pp the middle one, beyond that the outer one. Counts: within 10% /
          30%. These are display bins; the exact values sit on every row.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">The 2026 column</h2>
        <p>
          Where present, the projected column ages the same certified
          artifact to 2026 under current law as encoded in the engine
          (input uprating; not re-calibrated to 2026 projections). It is
          attached only where the interchange run's 2024 value matches this
          pipeline's within 0.5% — a same-construction gate. Urban's tool
          publishes 2023 only; a live model can keep moving.
        </p>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Full-participation runs</h2>
        {Object.entries(slice.pe_runs ?? {})
          .filter(([k]) => k !== "baseline")
          .map(([k, run]) => (
            <p key={k} className="fig text-xs text-muted-foreground">
              {k}: {run.flags_set_true.join(", ")}
            </p>
          ))}
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Provenance</h2>
        <table className="fig text-xs">
          <tbody>
            {[
              ["external source", slice.meta.url],
              ["fetched", slice.meta.fetched],
              ["dataset", prov.runtime_dataset],
              [
                "engine",
                `${peBundle.model_package ?? ""} ${
                  prov.engine_version ?? peBundle.model_version ?? ""
                }`,
              ],
              ["data bundle", prov.data_bundle],
              ["built", slice.built],
            ].map(([k, v]) => (
              <tr key={k}>
                <td className="pr-4 py-0.5 text-muted-foreground whitespace-nowrap align-top">
                  {k}
                </td>
                <td className="py-0.5 break-all">{v}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Docs</h2>
        <p className="text-muted-foreground">
          The full replication assessment (methodology, the three calibration
          regimes, per-program findings) and the engine mechanics audit live
          in this repo under docs/.
        </p>
      </section>
    </div>
  );
}
