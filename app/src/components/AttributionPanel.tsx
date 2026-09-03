import { useEffect, useState } from "react";
import type { Country } from "../types";
import { PROGRAM_LABELS } from "../types";
import { withBasePath } from "../basePath";

interface ExhibitRow {
  program: string;
  geography: string;
  subgroup: string;
  value: number;
  baseline_value: number;
  delta: number;
}

interface Exhibits {
  note: string;
  non_additivity: { solo_sum_pp: number; joint_all_programs_pp: number };
  rows: ExhibitRow[];
}

/**
 * PE-only exhibit (no external claim): force ONE program's take-up to 100%
 * and difference SPM poverty — which take-up gap is the poverty lever.
 *
 * exhibits.json is a US-only feed (SPM poverty, state geographies), so the
 * panel is gated by the selected country: under any other country it
 * renders nothing rather than US attribution.
 */
export function AttributionPanel({ country }: { country: Country }) {
  const [data, setData] = useState<Exhibits | null>(null);
  useEffect(() => {
    fetch(withBasePath("data/exhibits.json"))
      .then((r) => (r.ok ? r.json() : null))
      .then(setData)
      .catch(() => setData(null));
  }, []);
  if (country !== "US" || !data) return null;

  const programs = [...new Set(data.rows.map((r) => r.program))];
  const summary = programs
    .map((p) => {
      const us = (sub: string) =>
        data.rows.find(
          (r) =>
            r.program === p && r.geography === "US" && r.subgroup === sub,
        );
      const states = data.rows.filter(
        (r) =>
          r.program === p && r.geography !== "US" && r.subgroup === "total",
      );
      const biggest = states.reduce(
        (a, b) => (b.delta < a.delta ? b : a),
        states[0],
      );
      return {
        program: p,
        total: us("total")?.delta ?? 0,
        child: us("child")?.delta ?? 0,
        biggest,
      };
    })
    .sort((a, b) => a.total - b.total);

  const pp = (v: number) => `${(v * 100).toFixed(2)}pp`;

  return (
    <section className="mt-8 rounded-md border border-border p-4">
      <h2 className="text-lg font-semibold">
        Take-up-gap poverty attribution
      </h2>
      <p className="mt-1 text-xs text-muted-foreground">
        PE-only exhibit, beyond Urban's report: one program's take-up forced
        to 100%, SPM poverty differenced against baseline (annual 2024,
        certified artifact). Solo effects are non-additive — they sum to{" "}
        <span className="fig">{data.non_additivity.solo_sum_pp}pp</span> vs
        the joint counterfactual's{" "}
        <span className="fig">{data.non_additivity.joint_all_programs_pp}pp</span>.
      </p>
      <table className="mt-3 text-sm">
        <thead>
          <tr className="text-left text-xs text-muted-foreground">
            <th className="pr-6 py-1 font-medium">Take-up → 100%</th>
            <th className="pr-6 py-1 text-right font-medium">Poverty Δ</th>
            <th className="pr-6 py-1 text-right font-medium">Child Δ</th>
            <th className="py-1 font-medium">Largest state</th>
          </tr>
        </thead>
        <tbody>
          {summary.map((s) => (
            <tr key={s.program} className="border-t border-border/60">
              <td className="pr-6 py-1.5">
                {PROGRAM_LABELS[s.program] ?? s.program}
              </td>
              <td className="pr-6 py-1.5 text-right fig">{pp(s.total)}</td>
              <td className="pr-6 py-1.5 text-right fig">{pp(s.child)}</td>
              <td className="py-1.5 fig text-muted-foreground">
                {s.biggest?.geography} {pp(s.biggest?.delta ?? 0)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-3 text-[11px] leading-4 text-muted-foreground">
        {data.note}
      </p>
    </section>
  );
}
