import type { Closeness, Row } from "./types";

/** Share-valued comparisons read in percentage points; counts and dollars
 * by ratio. Mirrors pipeline/export_db.py bin_of — one rule, two places,
 * both stated on the method page. */
export const isShareMetric = (row: Pick<Row, "unit" | "metric">) =>
  row.unit === "share" || row.metric.includes("rate");

export function fmtValue(
  v: number | null | undefined,
  row: Pick<Row, "unit" | "metric" | "value_kind">,
): string {
  if (v === null || v === undefined) return "—";
  if (isShareMetric(row)) return `${(v * 100).toFixed(1)}%`;
  if (row.unit === "percent") return `${v.toFixed(1)}%`;
  const a = Math.abs(v);
  const sign = v < 0 ? "−" : "";
  const dollar = row.value_kind === "usd" ? "$" : "";
  if (a >= 1e12) return `${sign}${dollar}${(a / 1e12).toFixed(2)}T`;
  if (a >= 1e9) return `${sign}${dollar}${(a / 1e9).toFixed(1)}B`;
  if (a >= 1e6) return `${sign}${dollar}${(a / 1e6).toFixed(2)}M`;
  if (a >= 1e3) return `${sign}${dollar}${(a / 1e3).toFixed(0)}k`;
  return `${sign}${dollar}${a.toFixed(row.value_kind === "usd" ? 0 : 0)}`;
}

const both = (row: Row): [number, number] | null =>
  row.value !== undefined && row.pe?.value !== undefined
    ? [row.value, row.pe.value]
    : null;

/** One compact divergence figure: pp for shares, % difference otherwise. */
export function fmtDivergence(row: Row): string {
  const v = both(row);
  if (!v) return "";
  const [ext, pe] = v;
  if (isShareMetric(row)) {
    const pp = (pe - ext) * 100;
    return `${pp >= 0 ? "+" : "−"}${Math.abs(pp).toFixed(1)}pp`;
  }
  if (ext === 0) return "";
  const pct = (pe / ext - 1) * 100;
  return `${pct >= 0 ? "+" : "−"}${Math.abs(pct).toFixed(0)}%`;
}

/**
 * Divergence bins — descriptive, stated in the legend, never pass/fail:
 * shares within 2.5pp / 10pp; counts and dollars within 10% / 30%.
 */
export function closeness(row: Row): Closeness | null {
  const v = both(row);
  if (!v) return null;
  const [ext, pe] = v;
  if (isShareMetric(row)) {
    const pp = Math.abs(pe - ext) * 100;
    return pp < 2.5 ? "close" : pp < 10 ? "moderate" : "far";
  }
  if (ext === 0) return null;
  const r = Math.abs(pe / ext - 1);
  return r < 0.1 ? "close" : r < 0.3 ? "moderate" : "far";
}

/** Rank score for divergence sorting (comparable units across metrics). */
export function divergenceScore(row: Row): number {
  const v = both(row);
  if (!v) return 0;
  const [ext, pe] = v;
  if (isShareMetric(row)) {
    return Math.abs(pe - ext) * 10; // 10pp -> 1.0
  }
  if (ext === 0 || pe === 0) return 0;
  return Math.abs(Math.log2(pe / ext)); // 2x -> 1.0
}

/** External period, compact: "2023" / "FY2026" / "FY2025–34". */
export function fmtPeriod(row: Row): string {
  const fy = row.time_basis === "fiscal_year" ? "FY" : "";
  if (row.period_start !== undefined && row.period_end !== undefined) {
    return `${fy}${row.period_start}–${String(row.period_end).slice(2)}`;
  }
  const month = row.conditions?.month;
  if (month) return month;
  return `${fy}${row.period}`;
}
