import { describe, expect, test } from "bun:test";
import { defaultFilters } from "./filters";
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

describe("claim links", () => {
  const id = "4290148a46a76bfa6ffa";

  test("a claim link opens that claim on the validation view", () => {
    expect(parseUrlState(`?view=validation&claim=${id}`)).toEqual({
      country: "US",
      tab: "validation",
      claim: id,
    });
    expect(parseUrlState(`?country=uk&view=validation&claim=${id}`).claim).toBe(
      id,
    );
  });

  test("claim ids are read case-insensitively", () => {
    expect(
      parseUrlState(`?view=validation&claim=${id.toUpperCase()}`).claim,
    ).toBe(id);
  });

  test("malformed claim ids are ignored", () => {
    for (const claim of [
      "",
      "%3Cscript%3E",
      "javascript%3Aalert(1)",
      "not-a-claim",
      "a".repeat(65),
    ]) {
      expect(parseUrlState(`?view=validation&claim=${claim}`)).toEqual({
        country: "US",
        tab: "validation",
      });
    }
  });

  test("a claim is only read with the validation view", () => {
    expect(parseUrlState(`?claim=${id}`)).toEqual({
      country: "US",
      tab: "overview",
    });
    expect(parseUrlState(`?view=scorecard&claim=${id}`).claim).toBeUndefined();
  });

  test("an open claim is written after the view", () => {
    expect(buildUrlQuery("", "UK", "validation", { claim: id })).toBe(
      `country=uk&view=validation&claim=${id}`,
    );
  });

  test("closing the claim or leaving the view removes it", () => {
    const search = `?view=validation&claim=${id}`;
    expect(buildUrlQuery(search, "US", "validation", { claim: null })).toBe(
      "view=validation",
    );
    expect(buildUrlQuery(search, "US", "validation")).toBe("view=validation");
    expect(buildUrlQuery(search, "US", "gaps", { claim: id })).toBe(
      "view=gaps",
    );
  });

  test("round-trips through parseUrlState", () => {
    const query = buildUrlQuery("", "NZ", "validation", { claim: id });
    expect(parseUrlState(`?${query}`)).toEqual({
      country: "NZ",
      tab: "validation",
      claim: id,
    });
  });
});

describe("comparison filter links", () => {
  const us = defaultFilters("US");

  test("a filter link opens the comparison view filtered", () => {
    expect(parseUrlState("?view=scorecard&program=snap&geography=VT")).toEqual({
      country: "US",
      tab: "scorecard",
      filters: { program: "snap", geography: "VT" },
    });
    expect(
      parseUrlState("?view=scorecard&metric=participation_rate").filters,
    ).toEqual({ metric: "participation_rate" });
  });

  test("filter values are read case-insensitively", () => {
    expect(
      parseUrlState("?view=scorecard&program=SNAP&metric=Eligible_Count&geography=vt")
        .filters,
    ).toEqual({ program: "snap", metric: "eligible_count", geography: "VT" });
    expect(parseUrlState("?view=scorecard&geography=STATES").filters).toEqual({
      geography: "states",
    });
  });

  test("values outside the comparison vocabularies are ignored", () => {
    expect(
      parseUrlState(
        "?view=scorecard&program=medicaid&metric=%3Cscript%3E&geography=Vermont",
      ),
    ).toEqual({ country: "US", tab: "scorecard" });
    expect(
      parseUrlState("?view=scorecard&program=all&metric=&geography=V1").filters,
    ).toBeUndefined();
  });

  test("the empty Select sentinel is never a filter value", () => {
    expect(
      parseUrlState(
        "?view=scorecard&program=__empty__&metric=__empty__&geography=__empty__",
      ).filters,
    ).toBeUndefined();
  });

  test("filters are only read with the comparison view", () => {
    expect(parseUrlState("?program=snap&geography=VT")).toEqual({
      country: "US",
      tab: "overview",
    });
    expect(
      parseUrlState("?view=validation&program=snap").filters,
    ).toBeUndefined();
  });

  test("filters that differ from the defaults are written after the view", () => {
    expect(
      buildUrlQuery("", "US", "scorecard", {
        filters: { ...us, program: "snap", geography: "VT" },
      }),
    ).toBe("view=scorecard&program=snap&geography=VT");
    expect(
      buildUrlQuery("", "US", "scorecard", {
        filters: { ...us, metric: "eligible_count", geography: "states" },
      }),
    ).toBe("view=scorecard&metric=eligible_count&geography=states");
  });

  test("default filters, including the national geography, stay out of the URL", () => {
    expect(buildUrlQuery("", "US", "scorecard", { filters: us })).toBe(
      "view=scorecard",
    );
    expect(
      buildUrlQuery("", "UK", "scorecard", { filters: defaultFilters("UK") }),
    ).toBe("country=uk&view=scorecard");
  });

  test("filters leave the URL with the comparison view or when reset", () => {
    const search = "?view=scorecard&program=snap&geography=VT";
    const snap = { ...us, program: "snap", geography: "VT" };
    expect(buildUrlQuery(search, "US", "divergences", { filters: snap })).toBe(
      "view=divergences",
    );
    expect(buildUrlQuery(search, "US", "scorecard", { filters: us })).toBe(
      "view=scorecard",
    );
  });

  test("unrelated params survive the writeback", () => {
    expect(
      buildUrlQuery("?utm_source=email&view=scorecard", "US", "scorecard", {
        filters: { ...us, program: "ssi" },
      }),
    ).toBe("utm_source=email&view=scorecard&program=ssi");
  });

  test("round-trips through parseUrlState", () => {
    const filters = {
      ...us,
      program: "tanf",
      metric: "participation_rate",
      geography: "DC",
    };
    const query = buildUrlQuery("", "US", "scorecard", { filters });
    expect(parseUrlState(`?${query}`)).toEqual({
      country: "US",
      tab: "scorecard",
      filters: {
        program: "tanf",
        metric: "participation_rate",
        geography: "DC",
      },
    });
  });
});
