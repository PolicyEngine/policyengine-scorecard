import { expect, test } from "bun:test";
import { EMPTY_SELECT_VALUE, fromSelectValue, toSelectValue } from "./selectValue";

test("never hands Radix an empty item value", () => {
  expect(toSelectValue("")).toBe(EMPTY_SELECT_VALUE);
  expect(toSelectValue("")).not.toBe("");
});

test("round-trips the empty value and leaves others unchanged", () => {
  for (const v of ["", "all", "autumn_budget_2025", "different_model"]) {
    expect(fromSelectValue(toSelectValue(v))).toBe(v);
  }
  expect(toSelectValue("all")).toBe("all");
});
