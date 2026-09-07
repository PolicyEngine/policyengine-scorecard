# AI engineering guidance

This document is the model-independent source of repository guidance for AI
coding assistants. Model-specific instruction files should point here rather
than duplicate these rules.

## Required checks

For changes to the web application, run from `app/`:

```bash
bun test src
bun run lint
bun run build
```

For changes to Python ingestion or database code, run the relevant tests under
`tests/` with `pytest`.

## Application base path (`BASE_PATH`)

The deployed application is mounted at `/scorecard`, not at the website root.
In this repository, `BASE_PATH` refers to that deployment prefix; it is not a
separate environment variable.

- `app/vite.config.ts` configures the Vite `base` as `/scorecard/`. Vite emits
  generated JavaScript, CSS, and processed public-file URLs beneath that path.
- Runtime requests are not rewritten automatically by Vite. Construct them
  with `withBasePath()` from `app/src/basePath.ts`, which reads
  `import.meta.env.BASE_URL`.
- Do not use root-relative URLs such as `/data/example.json` or document-relative
  URLs such as `./data/example.json` for runtime data requests.
- `app/vercel.json` maps `/scorecard`, `/scorecard/`, and `/scorecard/*` requests
  to the application document and generated files. Keep those mappings aligned
  with the Vite base.

See `docs/ARCHITECTURE.md` for the scorecard data model, source-adapter
contract, and comparison workflow.
