import { describe, expect, test } from "bun:test";
import { sourceLabel } from "../sourceLabels";
import {
  BE_REFORM_DESCRIPTION,
  conditionValues,
  filterRows,
} from "./ReformValidationView";
import type { PopulationRow } from "../types";

describe("Belgian reform source labels", () => {
  test("uses publication-friendly names for each PIT-reform source", () => {
    expect(sourceLabel("spf_finances")).toBe("SPF Finances");
    expect(sourceLabel("cour_des_comptes")).toBe("Cour des comptes");
    expect(sourceLabel("policyengine")).toBe("PolicyEngine");
  });
});

describe("Belgian reform description doctrine", () => {
  test("discloses that PolicyEngine rows are same-computation self-attachments", () => {
    expect(BE_REFORM_DESCRIPTION).toContain("self-attachments");
    expect(BE_REFORM_DESCRIPTION).toContain(
      "each claim and result records the same",
    );
  });

  test("names the EU-SILC input basis of the EUROMOD claims", () => {
    expect(BE_REFORM_DESCRIPTION).toContain("EU-SILC");
    expect(BE_REFORM_DESCRIPTION).toContain("not administrative statistics");
  });

  test("leaves the official period basis unresolved", () => {
    expect(BE_REFORM_DESCRIPTION).toContain(
      "do not specify whether 2030 is an income or assessment year",
    );
    expect(BE_REFORM_DESCRIPTION).toContain("no shared period basis");
  });

  test("never grades the comparison", () => {
    expect(BE_REFORM_DESCRIPTION.toLowerCase()).not.toMatch(
      /\b(wins?|closest|agrees?|match(es|ed)?|confirm(s|ed)?)\b/,
    );
  });
});

describe("Autumn Budget 2025 producer labels (#136)", () => {
  test("every AB2025 producer slug has a publication-friendly name", () => {
    expect(sourceLabel("obr_efo")).toBe("OBR (EFO tables)");
    expect(sourceLabel("tax_policy_associates")).toBe("Tax Policy Associates");
    expect(sourceLabel("trussell_wpi")).toBe("Trussell / WPI Economics");
    expect(sourceLabel("fabian_society")).toBe("Fabian Society");
  });
});

function row(partial: Partial<PopulationRow> & { claim_id: string }): PopulationRow {
  return {
    source: "ifs",
    country: "UK",
    source_column: "",
    name: "",
    window: "",
    publication_title: "",
    url: "",
    metric: "revenue_change",
    unit_concept: "gbp",
    value_kind: "gbp",
    period: 2027,
    time_basis: "fiscal_year",
    period_start: null,
    period_end: null,
    geography: "UK",
    program: null,
    conditions: {},
    reform_framework: "policy_ref",
    reform_key: "k",
    external_value: 1,
    calibration_relationship: "held_out",
    claim_baseline: null,
    latest: {
      status: "not_computed",
      status_effective: "not_computed",
      value: null,
      ratio: null,
      delta: null,
    } as PopulationRow["latest"],
    results: [],
    diagnosis: null,
    ...partial,
  } as PopulationRow;
}

describe("retrieval by event and benchmark class (#136)", () => {
  const rows = [
    row({
      claim_id: "a",
      conditions: { fiscal_event: "autumn_budget_2025", benchmark_class: "different_model" },
    }),
    row({
      claim_id: "b",
      source: "hm_treasury",
      conditions: { fiscal_event: "autumn_budget_2025", benchmark_class: "administrative_fact" },
    }),
    row({ claim_id: "c", source: "uk_hmrc", conditions: {} }),
  ];
  const all = {
    source: "all",
    status: "all",
    releasesOnly: false,
    fiscalEvent: "all",
    benchmarkClass: "all",
  };

  test("option lists come from the rows and count rows without the key", () => {
    expect(conditionValues(rows, "fiscal_event")).toEqual({
      autumn_budget_2025: 2,
      "": 1,
    });
    expect(conditionValues(rows, "benchmark_class")).toEqual({
      different_model: 1,
      administrative_fact: 1,
      "": 1,
    });
  });

  test("filters compose and 'all' disables each one", () => {
    expect(filterRows(rows, all).map((r) => r.claim_id)).toEqual(["a", "b", "c"]);
    expect(
      filterRows(rows, { ...all, fiscalEvent: "autumn_budget_2025" }).map(
        (r) => r.claim_id,
      ),
    ).toEqual(["a", "b"]);
    expect(
      filterRows(rows, {
        ...all,
        fiscalEvent: "autumn_budget_2025",
        benchmarkClass: "administrative_fact",
      }).map((r) => r.claim_id),
    ).toEqual(["b"]);
    expect(filterRows(rows, { ...all, fiscalEvent: "" }).map((r) => r.claim_id)).toEqual(
      ["c"],
    );
    expect(
      filterRows(rows, { ...all, source: "ifs", benchmarkClass: "different_model" }).map(
        (r) => r.claim_id,
      ),
    ).toEqual(["a"]);
  });
});
