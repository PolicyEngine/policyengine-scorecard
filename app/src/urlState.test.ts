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
    expect(parseUrlState("")).toEqual({ country: "US", tab: "overview" });
  });

  test("country codes are case-insensitive", () => {
    expect(parseUrlState("?country=Uk").country).toBe("UK");
    expect(parseUrlState("?country=nZ").country).toBe("NZ");
  });

  test("values outside the closed vocabularies fall back to defaults", () => {
    expect(parseUrlState("?country=fr&view=admin")).toEqual({
      country: "US",
      tab: "overview",
    });
    expect(
      parseUrlState("?country=%3Cscript%3E&view=javascript%3Aalert(1)"),
    ).toEqual({ country: "US", tab: "overview" });
  });
});

describe("buildUrlQuery", () => {
  test("defaults stay out of the URL", () => {
    expect(buildUrlQuery("", "US", "overview")).toBe("");
  });

  test("the comparison view keeps its historical id in links", () => {
    expect(buildUrlQuery("", "US", "scorecard")).toBe("view=scorecard");
    expect(parseUrlState("?view=scorecard").tab).toBe("scorecard");
  });

  test("non-defaults are written lowercased", () => {
    expect(buildUrlQuery("", "BE", "validation")).toBe(
      "country=be&view=validation",
    );
  });

  test("switching back to defaults removes the params", () => {
    expect(buildUrlQuery("?country=be&view=validation", "US", "overview")).toBe(
      "",
    );
  });

  test("unrelated params survive the writeback", () => {
    expect(buildUrlQuery("?utm_source=email", "BE", "gaps")).toBe(
      "utm_source=email&country=be&view=gaps",
    );
  });

  test("round-trips through parseUrlState", () => {
    const query = buildUrlQuery("", "NZ", "divergences");
    expect(parseUrlState(`?${query}`)).toEqual({
      country: "NZ",
      tab: "divergences",
    });
  });
});
