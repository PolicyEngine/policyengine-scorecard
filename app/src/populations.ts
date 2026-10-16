import { countryOf } from "./types";
import type {
  Country,
  PopulationArchiveFeed,
  PopulationCounts,
  PopulationRow,
  PopulationsFeed,
} from "./types";

/** Archive counts describe the entire database population, regardless of
 * which event's detail is loaded. A gap history is never an answered score. */
export function populationCounts(
  feed: PopulationsFeed | null,
  country: Country,
): PopulationCounts {
  const supplied = feed?.summary.by_country?.[country];
  if (supplied) return supplied;
  const rows = (feed?.rows ?? []).filter((row) => countryOf(row) === country);
  return {
    claims: rows.length,
    with_result: rows.filter((row) => row.results.length > 0).length,
    with_value: rows.filter((row) => row.latest.value !== null).length,
    without_result: rows.filter((row) => row.results.length === 0).length,
    multi_release_claims: rows.filter((row) => row.results.length > 1).length,
  };
}

export function decodeArchive(feed: PopulationArchiveFeed): PopulationRow[] {
  return feed.rows.map((row) => ({
    ...feed.common,
    ...row,
    conditions: { ...feed.common_conditions, ...row.conditions },
  })) as PopulationRow[];
}
