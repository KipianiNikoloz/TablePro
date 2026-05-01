# Frontend Context

## Stack

Use a static Next.js app shell that behaves as a React SPA after load. FastAPI serves the built assets in production.

Before frontend implementation, read `docs/context/ui-design-system.md`. It is the mandatory visual context for dark-mode identity, density, layout metrics, data-grid rhythm, editor treatment, shadcn composition, and browser-fidelity gates.

## Performance Bias

- Lazy-load heavy surfaces such as SQL editor, virtualized grid, AI panel, and future diagrams.
- Use client-side cache/deduping for REST reads.
- Treat WebSocket events as invalidations or live state updates from the backend.
- Avoid shipping server-only or dialect-heavy logic to the browser.

## Main Surfaces

- Connection list and connection editor.
- Workspace shell.
- Schema browser.
- SQL editor panes/tabs.
- Result grid.
- Query history and bookmarks.
- Inline edit diff/review surface.
- CSV import wizard.
- AI side panel.

## Workspaces

Workspaces are browser-visible but backend-authoritative. The frontend renders panes/tabs and sends user actions to the backend. Multiple browser windows receive WebSocket updates and use last-writer-wins for layout/query text conflicts, with visible active-window/presence indicators.

## Result Grid

Use a virtualized grid. The grid must support:

- large row counts through server paging
- wide result sets
- selection and copying
- loading/error states
- edit markers
- changed-cell diff display
- export triggers

The grid must not assume all result rows are loaded into browser memory.

## API Model

- Typed REST for commands and fetches.
- Typed WebSocket events for job status, session state, workspace changes, and invalidations.
- Browser never receives raw database credentials.
