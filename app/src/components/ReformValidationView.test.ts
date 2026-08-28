import { describe, expect, test } from "bun:test";
import { sourceLabel } from "../sourceLabels";

describe("Belgian reform source labels", () => {
  test("uses publication-friendly names for each PIT-reform source", () => {
    expect(sourceLabel("spf_finances")).toBe("SPF Finances");
    expect(sourceLabel("cour_des_comptes")).toBe("Cour des comptes");
    expect(sourceLabel("policyengine")).toBe("PolicyEngine");
  });
});
