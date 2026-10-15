import { describe, expect, test } from "bun:test";
import { decodeArchive, populationCounts } from "./populations";
import type { PopulationRow, PopulationsFeed } from "./types";

function row(id: string, value: number | null, history: boolean): PopulationRow {
  return {
    claim_id: id,
    country: "UK",
    conditions: { fiscal_event: "budget_1970" },
    external_value: 0,
    latest: { value, status_effective: history ? "pe_gap" : "not_computed" },
    results: history ? [{ value }] : [],
  } as PopulationRow;
}

function feed(rows: PopulationRow[]): PopulationsFeed {
  return {
    built: "2026-10-11",
    note: "",
    summary: { claims: rows.length, multi_release_claims: 0, by_source: {}, by_latest_status: {} },
    rows,
  };
}

describe("population coverage", () => {
  test("a zero numerical result is answered; a recorded gap without a value is separate", () => {
    const payload = feed([
      row("zero", 0, true),
      row("gap", null, true),
      row("waiting", null, false),
    ]);
    expect(populationCounts(payload, "UK")).toEqual({
      claims: 3,
      with_result: 2,
      with_value: 1,
      without_result: 1,
      multi_release_claims: 0,
    });
  });

  test("headline counts include unloaded event scores", () => {
    const payload = feed([row("waiting", null, false)]);
    payload.summary.by_country = {
      UK: { claims: 24001, with_result: 0, with_value: 0, without_result: 24001, multi_release_claims: 0 },
    };
    expect(populationCounts(payload, "UK").claims).toBe(24001);
    expect(populationCounts(payload, "UK").without_result).toBe(24001);
    expect(populationCounts(payload, "US").claims).toBe(0);
  });
});

test("event detail restores shared fields, explicit zero values and each cell's conditions", () => {
  const rows = decodeArchive({
    common: { country: "UK", results: [], external_value: 0 },
    common_conditions: { fiscal_event: "budget_1970", country: "UK" },
    rows: [
      { claim_id: "a", conditions: { fy: "1970-71" } },
      { claim_id: "b", external_value: -2, conditions: { fy: "1971-72" } },
    ],
  });
  expect(rows.map((row) => row.external_value)).toEqual([0, -2]);
  expect(rows.map((row) => row.conditions.fy)).toEqual(["1970-71", "1971-72"]);
  expect(rows.every((row) => row.conditions.fiscal_event === "budget_1970")).toBe(true);
  expect(rows.every((row) => row.results.length === 0)).toBe(true);
});
