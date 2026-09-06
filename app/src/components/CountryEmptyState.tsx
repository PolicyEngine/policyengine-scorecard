import type { Country, LanesFeed } from "../types";
import { COUNTRY_LABELS, countryOf } from "../types";
import { LinkButton, Panel, Tag } from "./ui";
import { useNav } from "../navigation";

/**
 * A country without main-grid cells renders as a status panel, not a blank
 * page (issue #42): lanes and their stages stay visible. A completed lane may
 * intentionally live on Reform validation when its values are not comparable.
 */
export function CountryEmptyState({
  country,
  lanes,
}: {
  country: Country;
  lanes: LanesFeed | null;
}) {
  const nav = useNav();
  const countryLanes = (lanes?.lanes ?? []).filter(
    (l) => countryOf(l) === country,
  );
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Panel title={`No ${COUNTRY_LABELS[country]} comparison cells yet`}>
        <p className="text-sm leading-6 text-muted-foreground">
          {country === "BE"
            ? "Belgium registers two lanes. On Reform validation, SPF Finances, Cour des comptes and PolicyEngine estimates of the 15 July 2026 PIT reform sit side by side, the official horizon-2030 figures carried as constructed cross-attachments on an unresolved period basis. The JRC EUROMOD-BE lane has five model claims — EUROMOD totals simulated on uprated EU-SILC survey input, not administrative statistics; its six statistical rows and one non-simulated uprated EU-SILC survey input route to Chronicle, and its six ratios remain derived, not claims. Two demo-grade Axiom worker values appear on Reform validation as concept mismatches; no value is presented as comparable."
            : `The ${country} external lanes are mid-pipeline. Each lane reports its stage from data/lanes.json; as counterparts compute, rows appear here under the same descriptive status taxonomy as the US instance, model gaps and concept mismatches included.`}
        </p>
        <p className="mt-3">
          <LinkButton onClick={() => nav.go("validation")}>
            Open reform validation for {COUNTRY_LABELS[country]}
          </LinkButton>
        </p>
      </Panel>
      <Panel title="Registered lanes">
        {countryLanes.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No lanes registered for this country — see data/lanes.json.
          </p>
        ) : (
          <ul className="divide-y divide-border">
            {countryLanes.map((l) => (
              <li
                key={l.id}
                className="flex items-start justify-between gap-3 py-2 text-sm"
              >
                <span>
                  <span className="font-medium">{l.source}</span>
                  <span className="text-muted-foreground"> · {l.area}</span>
                </span>
                <Tag tone={l.running ? "primary" : "outline"}>{l.stage}</Tag>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}
