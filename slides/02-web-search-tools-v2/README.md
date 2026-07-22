# Module 02 slides — v2 draft

Working draft that applies the course review without replacing the reviewed deck in `../02-web-search-tools`.

## What changed vs v1

1. **Problem first** — new opening slide ties web search to the competitor-research project, with Nemotron 3 Nano cutoff (`June 25, 2025`) as evidence.
2. **Then principle** — Search / Extract stays next as the general solution model.
3. **Then setup** — Tavily signup screenshots kept (screencast can come later).
4. **Schema** — “Your app **must** call this directly.”
5. **Execution boundary** — redrawn as a single-ring loop with an explicit return, not a flat 2×3 grid.

## Run

```bash
cd slides/02-web-search-tools-v2
pnpm install   # first time
pnpm run dev   # http://localhost:3031
```

Assets are symlinked from `../02-web-search-tools/public`.
