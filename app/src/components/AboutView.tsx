import type { Comparison } from "../types";
import { Panel } from "./ui";

const REPO_DOCS =
  "https://github.com/PolicyEngine/policyengine-scorecard/tree/main/docs";

export function AboutView({ data }: { data: Comparison }) {
  const b = data.pe_bundle;
  return (
    <div className="space-y-4">
      <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
        This page describes the US Urban comparison — the country selector
        does not change it. UK, Belgium and New Zealand provenance and method
        notes travel with their own claims on Reform validation.
      </p>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="What the two columns are">
          <p className="text-sm leading-6">
            <b>Urban</b> simulates program <i>eligibility</i> with ATTIS on
            pooled 2022+2023 ACS data and divides actual administrative
            caseloads by those simulated eligible counts; estimates refer to
            the average month of 2023. <b>PolicyEngine</b> simulates both sides
            on the certified Populace artifact: statute-encoded eligibility
            rules plus seeded take-up flags, with calibration to thousands of
            administrative targets. For count-targeted programs (SNAP, SSI,
            Medicaid) the participation numerator is disciplined by the same
            class of admin counts Urban uses directly, so agreement there is
            partly by construction — stated on every affected row.
          </p>
        </Panel>
        <div className="space-y-4">
          <Panel title="Tolerances">
            <p className="text-sm leading-6">
              Rates: within 2.5 percentage points is close, within 10pp
              diverging, beyond that far apart. Counts: within 10% / 30%. These
              are display buckets, not scientific claims; the exact values sit
              on every row.
            </p>
          </Panel>
          <Panel title="The 2026 column">
            <p className="text-sm leading-6">
              Where present, the projected column ages the same certified
              artifact to 2026 under current law as encoded in the engine
              (input uprating; not re-calibrated to 2026 projections). It is
              attached only where the interchange run&apos;s 2024 value matches
              this pipeline&apos;s within 0.5% — a same-construction gate.
              Urban&apos;s tool publishes 2023 only; a live model can keep
              moving.
            </p>
          </Panel>
        </div>
      </div>
      <Panel title="Full-participation runs">
        <ul className="space-y-1">
          {Object.entries(data.pe_runs)
            .filter(([k]) => k !== "baseline")
            .map(([k, run]) => (
              <li key={k} className="fig text-xs text-muted-foreground">
                {k}: {run.flags_set_true.join(", ")}
              </li>
            ))}
        </ul>
      </Panel>
      <Panel
        title="Provenance"
        description="Every annotation traces to the comparison method, engine metadata, or a measured diagnostic. Divergences and concept mismatches stay visible."
      >
        <div className="overflow-x-auto">
          <table className="fig text-xs">
            <tbody>
              {[
                ["external source", data.source_meta.url],
                ["fetched", data.source_meta.fetched],
                ["dataset", b.runtime_dataset_uri],
                ["engine", `${b.model_package} ${b.model_version}`],
                ["bundle", b.bundle_id],
                ["artifact sha256", b.certified_data_artifact_sha256],
                ["built", data.built],
              ].map(([k, v]) => (
                <tr key={k}>
                  <td className="whitespace-nowrap py-0.5 pr-4 align-top text-muted-foreground">
                    {k}
                  </td>
                  <td className="break-all py-0.5">{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          The full comparison assessment (methodology, the three calibration
          regimes, per-program analysis) and the engine mechanics audit live in
          the repository under{" "}
          <a
            className="text-primary underline underline-offset-2"
            href={REPO_DOCS}
            target="_blank"
            rel="noreferrer"
          >
            docs/
          </a>
          .
        </p>
      </Panel>
    </div>
  );
}
