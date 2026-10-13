/**
 * Radix Select reserves "" for "no selection" and throws when an item has
 * that value, which blanks the whole page. Filter options legitimately use ""
 * for rows that lack a condition (the "(none recorded)" option), so an empty
 * value travels to Radix under this sentinel and is mapped back before it
 * reaches the caller.
 */
export const EMPTY_SELECT_VALUE = "__empty__";

export function toSelectValue(value: string): string {
  return value === "" ? EMPTY_SELECT_VALUE : value;
}

export function fromSelectValue(value: string): string {
  return value === EMPTY_SELECT_VALUE ? "" : value;
}
