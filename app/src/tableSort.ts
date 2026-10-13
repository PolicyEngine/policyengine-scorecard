/**
 * Click-to-sort table headers, kept pure so the ordering rules are testable
 * without a DOM.
 */
export type SortDir = "asc" | "desc";

export interface SortState<K extends string> {
  key: K;
  dir: SortDir;
}

/**
 * The sort after a header click: a new column starts in its natural
 * direction (A→Z for text, largest first for numbers), a second click
 * reverses it, and a third returns the table to its default order.
 */
export function nextSort<K extends string>(
  current: SortState<K> | null,
  key: K,
  firstDir: SortDir,
): SortState<K> | null {
  if (current?.key !== key) return { key, dir: firstDir };
  if (current.dir === firstDir)
    return { key, dir: firstDir === "asc" ? "desc" : "asc" };
  return null;
}

export type SortValue = string | number | null;

/** Compare two cell values; empty cells sort last in either direction. */
export function compareSortValues(
  a: SortValue,
  b: SortValue,
  dir: SortDir,
): number {
  const emptyA = a === null || (typeof a === "number" && Number.isNaN(a));
  const emptyB = b === null || (typeof b === "number" && Number.isNaN(b));
  if (emptyA || emptyB) return emptyA === emptyB ? 0 : emptyA ? 1 : -1;
  const c =
    typeof a === "number" && typeof b === "number"
      ? a - b
      : String(a).localeCompare(String(b), undefined, { numeric: true });
  return dir === "asc" ? c : -c;
}

/**
 * Sort rows by one column. The sort is stable, so rows that tie keep the
 * order they arrived in (the table's default order).
 */
export function sortRows<T, K extends string>(
  rows: T[],
  sort: SortState<K> | null,
  value: (row: T, key: K) => SortValue,
): T[] {
  if (!sort) return rows;
  return [...rows].sort((a, b) =>
    compareSortValues(value(a, sort.key), value(b, sort.key), sort.dir),
  );
}
