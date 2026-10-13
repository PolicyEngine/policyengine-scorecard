import { describe, expect, test } from "bun:test";
import { compareSortValues, nextSort, sortRows } from "./tableSort";

describe("nextSort", () => {
  test("a new column starts in its natural direction", () => {
    expect(nextSort(null, "program", "asc")).toEqual({ key: "program", dir: "asc" });
    expect(nextSort({ key: "program", dir: "asc" }, "delta", "desc")).toEqual({
      key: "delta",
      dir: "desc",
    });
  });

  test("the same column reverses, then returns to the default order", () => {
    const first = nextSort(null, "delta", "desc");
    const second = nextSort(first, "delta", "desc");
    expect(second).toEqual({ key: "delta", dir: "asc" });
    expect(nextSort(second, "delta", "desc")).toBeNull();
  });
});

describe("compareSortValues", () => {
  test("empty cells sort last in both directions", () => {
    const values = [3, null, 1, Number.NaN, 2];
    const asc = [...values].sort((a, b) => compareSortValues(a, b, "asc"));
    const desc = [...values].sort((a, b) => compareSortValues(a, b, "desc"));
    expect(asc.slice(0, 3)).toEqual([1, 2, 3]);
    expect(desc.slice(0, 3)).toEqual([3, 2, 1]);
    for (const order of [asc, desc]) {
      expect(order.slice(3).every((v) => v === null || Number.isNaN(v))).toBe(true);
    }
  });

  test("text compares naturally, so state codes and numbered labels read right", () => {
    const labels = ["item 10", "item 2", "Item 1"];
    expect([...labels].sort((a, b) => compareSortValues(a, b, "asc"))).toEqual([
      "Item 1",
      "item 2",
      "item 10",
    ]);
  });
});

describe("sortRows", () => {
  const rows = [
    { id: "a", v: 2 },
    { id: "b", v: 1 },
    { id: "c", v: 2 },
    { id: "d", v: null },
  ];
  const value = (r: (typeof rows)[number]) => r.v;

  test("no sort keeps the incoming (default) order", () => {
    expect(sortRows(rows, null, value).map((r) => r.id)).toEqual(["a", "b", "c", "d"]);
  });

  test("ties keep their incoming order and empties go last", () => {
    expect(
      sortRows(rows, { key: "v", dir: "desc" }, value).map((r) => r.id),
    ).toEqual(["a", "c", "b", "d"]);
    expect(
      sortRows(rows, { key: "v", dir: "asc" }, value).map((r) => r.id),
    ).toEqual(["b", "a", "c", "d"]);
  });

  test("does not mutate the input", () => {
    sortRows(rows, { key: "v", dir: "asc" }, value);
    expect(rows.map((r) => r.id)).toEqual(["a", "b", "c", "d"]);
  });
});
