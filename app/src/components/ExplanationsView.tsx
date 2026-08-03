import type { ScorecardIndex } from "../types";
import { metricLabel, programLabel } from "../types";
import { AttributionPanel } from "./AttributionPanel";
import { DiagnosisChip } from "./chips";

/**
 * How the models differ: published explanations of material divergences.
 * An entry traces one divergence to the documented choices behind it;
 * known-issue chips (erratum, tracked bug, internal contradiction) carry
 * their citations on the chip.
 */
export function ExplanationsView({
  index,
  onOpenSource,
}: {
  index: ScorecardIndex;
  onOpenSource: (id: string) => void;
}) {
  const explanations = index.explanations ?? [];
  const sourceName = (id: string) =>
    index.sources.find((s) => s.id === id)?.name ?? id;

  return (
    <div>
      <p className="mb-4 max-w-3xl text-sm text-muted-foreground">
        Each entry explains one divergence: which documented choices produce
        it, in which model, and where each choice is stated. Known-issue
        chips — an erratum, a tracked bug, an internal contradiction — link
        to their citations.
      </p>
      <ol className="grid gap-3 md:grid-cols-2">
        {explanations.map((e) => (
          <li key={e.claim_id} className="rounded-md border border-border p-3">
            <div className="flex items-baseline justify-between gap-2">
              <span className="text-sm font-medium">
                {e.program ? `${programLabel(e.program)} · ` : ""}
                {metricLabel(e.metric)}
                <span className="fig text-muted-foreground">
                  {" "}
                  · {e.geography}
                  {e.subgroup ? ` · ${e.subgroup}` : ""} · {e.period}
                </span>
              </span>
              <button
                onClick={() => onOpenSource(e.source)}
                className="shrink-0 text-xs text-primary underline-offset-2 hover:underline"
              >
                {sourceName(e.source)}
              </button>
            </div>
            <p className="mt-1.5 text-xs">
              <DiagnosisChip d={e} />
              {e.title ?? ""}
              {e.rationale && (
                <span className="text-muted-foreground"> {e.rationale}</span>
              )}
              {e.confidence && (
                <span className="text-muted-foreground">
                  {" "}
                  ({e.confidence} confidence)
                </span>
              )}
            </p>
          </li>
        ))}
      </ol>
      {explanations.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No explanations published yet.
        </p>
      )}
      <AttributionPanel />
    </div>
  );
}
