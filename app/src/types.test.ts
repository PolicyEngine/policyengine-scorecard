import { describe, expect, test } from "bun:test";
import { comparabilityFigure, countryOf } from "./types";

// The load-bearing backward-compat contract: historical US feeds predate
// the country key, so a missing country must always mean "US" — a row is
// never dropped or re-homed over an absent key.
describe("countryOf", () => {
  test("missing country defaults to US (US-era exports)", () => {
    expect(countryOf({})).toBe("US");
    expect(countryOf({ country: undefined })).toBe("US");
  });

  test("explicit countries pass through", () => {
    expect(countryOf({ country: "US" })).toBe("US");
    expect(countryOf({ country: "UK" })).toBe("UK");
    expect(countryOf({ country: "BE" })).toBe("BE");
  });

  test("country scoping filter never drops US-era rows from the US view", () => {
    const rows = [
      {},
      { country: "US" as const },
      { country: "UK" as const },
      { country: "BE" as const },
    ];
    expect(rows.filter((r) => countryOf(r) === "US")).toHaveLength(2);
    expect(rows.filter((r) => countryOf(r) === "UK")).toHaveLength(1);
    expect(rows.filter((r) => countryOf(r) === "BE")).toHaveLength(1);
  });
});


test("comparabilityFigure suppresses figures for concept_mismatch", () => {
  expect(comparabilityFigure("concept_mismatch", "not comparable", () => "1.23")).toBe(
    "not comparable",
  );
  expect(comparabilityFigure("concept_mismatch", "—", () => "0.99")).toBe("—");
});

test("comparabilityFigure computes for every other status", () => {
  for (const status of ["comparable", "constructed", "baseline_unvalidated"]) {
    expect(comparabilityFigure(status, "not comparable", () => "1.23")).toBe("1.23");
  }
});
