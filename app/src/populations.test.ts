import { describe, expect, test } from "bun:test";
import {
  claimCountry,
  comparablePair,
  decodeArchive,
  populationCounts,
} from "./populations";
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

describe("claim links", () => {
  const rows = [
    row("4290148a46a76bfa6ffa", null, false),
    { ...row("2eed4d168d9d386cd57f", null, false), country: "BE" },
    { ...row("87166869af304dad43b8", null, false), country: undefined },
  ] as PopulationRow[];

  test("a linked claim opens in its own country", () => {
    expect(claimCountry(rows, "4290148a46a76bfa6ffa")).toBe("UK");
    expect(claimCountry(rows, "2eed4d168d9d386cd57f")).toBe("BE");
  });

  test("a claim from a US-era export without a country key is a US claim", () => {
    expect(claimCountry(rows, "87166869af304dad43b8")).toBe("US");
  });

  test("an id the feed does not have opens nothing", () => {
    expect(claimCountry(rows, "0000000000000000000a")).toBeNull();
    expect(claimCountry([], "4290148a46a76bfa6ffa")).toBeNull();
  });
});

describe("comparable pair (issue #198)", () => {
  const signed = (
    external_value: number | null,
    sign_relative_to_pe: PopulationRow["sign_relative_to_pe"],
    external_value_pe_sign: number | null,
  ) => ({ external_value, sign_relative_to_pe, external_value_pe_sign });

  test("an unsigned reckoner magnitude compares absolute values", () => {
    // HMRC: "Change personal allowance by 1%" = 1e9; PE revenue change -1.13e9
    const pair = comparablePair(-1.13e9, signed(1e9, "magnitude", null));
    expect(pair).toEqual([1.13e9, 1e9]);
    expect((pair![0] / pair![1] - 1) * 100).toBeCloseTo(13, 5);
  });

  test("an opposite convention compares the re-signed published value", () => {
    // positive = increase in borrowing: a 2.4bn cost is -2.4bn of revenue
    expect(comparablePair(-1.1e9, signed(2.4e9, "opposite", -2.4e9))).toEqual([
      -1.1e9, -2.4e9,
    ]);
  });

  test("same compares as published; unknown falls back to the raw value", () => {
    expect(comparablePair(5, signed(4, "same", 4))).toEqual([5, 4]);
    expect(comparablePair(5, signed(-4, "unknown", null))).toEqual([5, -4]);
  });

  test("a missing value on either side has no pair", () => {
    expect(comparablePair(null, signed(4, "same", 4))).toBeNull();
    expect(comparablePair(5, signed(null, "same", null))).toBeNull();
  });
});

