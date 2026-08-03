import type { Row, ScorecardIndex, SourceSlice } from "./types";

/** Fetch + hydrate the static feeds the export pipeline writes.
 *
 * Slices arrive compacted: modal scalar values live in `row_defaults`,
 * annotation id arrays are interned in `annotation_sets`, and hoisted
 * condition keys (geography/program/subgroup) sit on the row itself.
 * Hydration merges all of that back into full Row objects once, so every
 * component downstream works with plain rows.
 */

interface RawSlice extends Omit<SourceSlice, "rows"> {
  row_defaults: Partial<Row>;
  annotation_sets: string[][];
  rows: (Omit<Row, "annotations" | "source"> & {
    annotations?: number;
  })[];
}

const sliceCache = new Map<string, Promise<SourceSlice>>();

async function fetchJson<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${path}`);
  return r.json();
}

export function fetchIndex(): Promise<ScorecardIndex> {
  return fetchJson<ScorecardIndex>("./data/index.json");
}

export function fetchSlice(id: string): Promise<SourceSlice> {
  let p = sliceCache.get(id);
  if (!p) {
    p = fetchJson<RawSlice>(`./data/sources/${id}.json`).then((raw) => {
      const defaults = raw.row_defaults ?? {};
      const annSets = raw.annotation_sets ?? [];
      const rows: Row[] = raw.rows.map((r) => {
        const row = { ...defaults, ...r, source: raw.id } as Row;
        if (typeof r.annotations === "number") {
          row.annotations = annSets[r.annotations];
        }
        return row;
      });
      return { ...raw, rows } as SourceSlice;
    });
    sliceCache.set(id, p);
  }
  return p;
}

/** The per-(program|metric) or per-relationship note explaining a row's
 * calibration relationship, resolved against the slice's note map. */
export function relationshipNote(
  slice: SourceSlice | undefined,
  row: Row,
): string | undefined {
  if (!slice) return undefined;
  const notes = slice.relationship_notes ?? {};
  return (
    notes[`${row.program ?? ""}|${row.metric}`] ?? notes[row.relationship]
  );
}
