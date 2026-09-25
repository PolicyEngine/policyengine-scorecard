import { expect, test } from "bun:test";
import { withBasePath } from "./basePath";

test("builds a URL beneath the configured application base path", () => {
  expect(withBasePath("data/comparison.json", "/scorecard/")).toBe(
    "/scorecard/data/comparison.json",
  );
});

test("normalizes missing and duplicate path separators", () => {
  expect(withBasePath("/data/lanes.json", "/scorecard")).toBe(
    "/scorecard/data/lanes.json",
  );
});
