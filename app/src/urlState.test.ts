import { describe, expect, test } from "bun:test";
import { buildUrlQuery, parseUrlState } from "./urlState";

describe("parseUrlState", () => {
  test("deep link lands on the exact view", () => {
    expect(parseUrlState("?country=be&view=validation")).toEqual({
      country: "BE",
      tab: "validation",
    });
  });

  test("bare origin gives the defaults", () => {
    expect(parseUrlState("")).toEqual({ country: "US", tab: "scorecard" });
  });

  test("country codes are case-insensitive", () => {
    expect(parseUrlState("?country=Uk").country).toBe("UK");
  });

  test("values outside the closed vocabularies fall back to defaults", () => {
    expect(parseUrlState("?country=fr&view=admin")).toEqual({
      country: "US",
      tab: "scorecard",
    });
    expect(
      parseUrlState("?country=%3Cscript%3E&view=javascript%3Aalert(1)"),
    ).toEqual({ country: "US", tab: "scorecard" });
  });
});

describe("buildUrlQuery", () => {
  test("defaults stay out of the URL", () => {
    expect(buildUrlQuery("", "US", "scorecard")).toBe("");
  });

  test("non-defaults are written lowercased", () => {
    expect(buildUrlQuery("", "BE", "validation")).toBe(
      "country=be&view=validation",
    );
  });

  test("switching back to defaults removes the params", () => {
    expect(buildUrlQuery("?country=be&view=validation", "US", "scorecard")).toBe(
      "",
    );
  });

  test("unrelated params survive the writeback", () => {
    expect(buildUrlQuery("?utm_source=email", "BE", "gaps")).toBe(
      "utm_source=email&country=be&view=gaps",
    );
  });

  test("round-trips through parseUrlState", () => {
    const query = buildUrlQuery("", "UK", "divergences");
    expect(parseUrlState(`?${query}`)).toEqual({
      country: "UK",
      tab: "divergences",
    });
  });
});
