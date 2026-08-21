import { describe, expect, test } from "bun:test";
import { countryOf } from "./types";

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
  });

  test("country scoping filter never drops US-era rows from the US view", () => {
    const rows = [{}, { country: "US" as const }, { country: "UK" as const }];
    expect(rows.filter((r) => countryOf(r) === "US")).toHaveLength(2);
    expect(rows.filter((r) => countryOf(r) === "UK")).toHaveLength(1);
  });
});
