import type { Closeness, Row } from "./types";

export const isRateMetric = (metric: string) =>
  metric.includes("rate");

export function fmtValue(v: number | null, metric: string): string {
  if (v === null || v === undefined) return "—";
  if (isRateMetric(metric)) {
    return `${(v * 100).toFixed(1)}%`;
  }
  const a = Math.abs(v);
  const sign = v < 0 ? "−" : "";
  if (a >= 1e6) return `${sign}${(a / 1e6).toFixed(2)}M`;
  if (a >= 1e3) return `${sign}${(a / 1e3).toFixed(0)}k`;
  return `${sign}${a.toFixed(0)}`;
}

/** One compact divergence figure: pp for rates, % difference for counts. */
export function fmtDivergence(row: Row): string {
  if (row.pe_value === null || row.external_value === null) return "";
  if (isRateMetric(row.metric)) {
    const pp = (row.pe_value - row.external_value) * 100;
    return `${pp >= 0 ? "+" : "−"}${Math.abs(pp).toFixed(1)}pp`;
  }
  if (row.external_value === 0) return "";
  const pct = (row.pe_value / row.external_value - 1) * 100;
  return `${pct >= 0 ? "+" : "−"}${Math.abs(pct).toFixed(0)}%`;
}

/**
 * Divergence buckets. Thresholds (stated in the legend): rates within
 * 2.5pp are close, within 10pp moderate; counts within 10% close, within
 * 30% moderate.
 */
export function closeness(row: Row): Closeness | null {
  if (row.pe_value === null || row.external_value === null) return null;
  if (isRateMetric(row.metric)) {
    const pp = Math.abs(row.pe_value - row.external_value) * 100;
    return pp < 2.5 ? "close" : pp < 10 ? "moderate" : "far";
  }
  if (row.external_value === 0) return null;
  const r = Math.abs(row.pe_value / row.external_value - 1);
  return r < 0.1 ? "close" : r < 0.3 ? "moderate" : "far";
}

/** Rank score for the divergence board (comparable units across metrics). */
export function divergenceScore(row: Row): number {
  if (row.pe_value === null || row.external_value === null) return 0;
  if (isRateMetric(row.metric)) {
    return Math.abs(row.pe_value - row.external_value) * 10; // 10pp -> 1.0
  }
  if (row.external_value === 0 || row.pe_value === 0) return 0;
  return Math.abs(Math.log2(row.pe_value / row.external_value)); // 2x -> 1.0
}
