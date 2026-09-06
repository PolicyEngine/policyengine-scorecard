# Scorecard app

The scorecard UI: a Vite + React app on the `@policyengine/ui-kit` design
system (shared PolicyEngine header and footer, theme tokens, primitives).

```bash
bun install
bun dev          # copies ../data/*.json into public/data/ first
bun test src
bun run lint
bun run build
```

## Structure

- `src/App.tsx` — the shell: PolicyEngine header/footer, title band, country
  selector and the view tabs. Reads and writes `?country=` / `?view=`.
- `src/components/Overview.tsx` — landing view: headline counts, the
  coverage bar, top divergences, pipeline lanes and gap counts.
- `src/components/ComparisonTable.tsx` — every published cell next to its
  PolicyEngine counterpart, with filters and expandable row detail.
- `src/components/DivergenceBoard.tsx` — the ranked diagnosis queue.
- `src/components/ReformValidationView.tsx` — reform scores and references
  with per-release history.
- `src/components/GapsView.tsx`, `AboutView.tsx` — gaps and method notes.
- `src/components/ui.tsx` — shared pieces (stat cards, panels, status badges,
  labelled selects) built on ui-kit primitives.
- `src/spine.ts` — coverage buckets; every colour is a token utility class.
- `src/urlState.ts` — deep-link vocabulary; view ids are stable URL values.

Runtime data requests go through `withBasePath()` (`src/basePath.ts`) because
the app is mounted at `/scorecard` — see `docs/AI_GUIDANCE.md`.
