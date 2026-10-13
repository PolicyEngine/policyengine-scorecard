import { describe, expect, test } from "bun:test";
import { defaultFilters, restoreFilters } from "./filters";

describe("restoreFilters", () => {
  test("restores this app's own saved filters", () => {
    const saved = {
      country: "US",
      program: "snap",
      metric: "participation_rate",
      geography: "US",
      subgroup: "total",
      bucket: "far",
    };
    expect(restoreFilters(saved, "US")).toEqual(saved);
  });

  test("anything that is not a filters object gives the defaults", () => {
    for (const saved of [null, undefined, "far", 42, []]) {
      expect(restoreFilters(saved, "US")).toEqual(defaultFilters("US"));
    }
  });

  test("filters saved under another country are not carried over", () => {
    const saved = { ...defaultFilters("UK"), program: "snap" };
    expect(restoreFilters(saved, "US")).toEqual(defaultFilters("US"));
  });

  test("unknown buckets and malformed fields fall back field by field", () => {
    const saved = {
      country: "US",
      program: 7,
      metric: "eligible_count",
      bucket: "<script>",
    };
    expect(restoreFilters(saved, "US")).toEqual({
      ...defaultFilters("US"),
      metric: "eligible_count",
    });
  });
});
