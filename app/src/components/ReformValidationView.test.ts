import { describe, expect, test } from "bun:test";
import { sourceLabel } from "../sourceLabels";
import { BE_REFORM_DESCRIPTION } from "./ReformValidationView";

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
