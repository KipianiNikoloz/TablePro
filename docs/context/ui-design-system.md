# UI Design System Context

## Deck Contract

`static/helixdb_design_deck.pdf` is the visual source of truth for TablePro frontends. Use it for visual identity, dark-mode atmosphere, density, layout rhythm, component behavior, and quality gates.

The deck is not a product-scope source of truth. Future or invented features shown in the deck, including schema diff, SSH settings, explain-plan depth, advanced settings, or any other unapproved workflow, are visual examples only until a feature-specific OpenSpec change approves them.

In short: the deck is visual-authoritative but feature-scope-non-authoritative.

The deck says HelixDB. Implementation says TablePro unless a future OpenSpec change explicitly approves a rename.

## Design Thesis

TablePro should feel like a native database cockpit: dense but readable, technical but calm, premium but restrained, powerful but safe. It should feel closer to a local developer workstation than a marketing SaaS dashboard.

## Palette Tokens

- App background: `#0D1117`
- Sidebar background: `#0A0F14`
- Elevated panels: `#121923`
- Data grid background: `#0F141C`
- Hover: `#172130`
- Active: `#1D2A3A`
- Borders: `#243142`
- Primary text: `#E6EDF3`
- Secondary text: `#AAB6C3`
- Muted text: `#7E8A99`
- Accent: `#4C8DFF`
- Success: `#34C759`
- Warning: `#FFB020`
- Error: `#FF5D5D`
- Info: `#58A6FF`
- Prod: `#FF8A3D`
- Staging: `#4C8DFF`
- Local: `#32D17C`
- Read-only: `#7D8590`
- Dirty/unsaved: `#D4A72C`

Use semantic theme tokens for these values. Component code should not hard-code raw Tailwind color utilities for deck-derived colors.

## Typography

- UI font stack: Inter, SF Pro, Geist
- SQL/data font stack: JetBrains Mono, Berkeley Mono, SF Mono
- App chrome: `12px`
- Sidebar items: `13px`
- Table cells: `12px`
- Section headers: `14px` semibold
- Tab labels: `12px`
- SQL editor: `13px` mono
- Modal titles: `16px` semibold
- Command palette input: `14px`
- Line-height: `1.35` to `1.5`, tight but legible

Use compact text intentionally. Do not inflate headings or control labels inside tool surfaces.

## Layout Metrics

- Icon rail: `56px`
- Sidebar: `240px` to `280px`
- Inspector: `280px` to `340px`
- Tab bar: `36px`
- Toolbar: `40px`
- Status bar: `24px`
- Data grid rows: `28px` to `32px`
- Modal widths: `480px`, `640px`, `860px`
- Command palette: `720px` max width
- Spacing scale: `4px`, `8px`, `12px`, `16px`, `24px`
- Icons: `14px`, `16px`, `18px`; outline-first; `1.75px` stroke
- Corners: square-rounded around `4px`; avoid soft SaaS pill aesthetics

Use stable dimensions for fixed-format surfaces such as rails, tabs, toolbars, icon buttons, data rows, counters, grids, and status bars.

## Composition Rules

- App shell: full-screen work surface, not a landing page.
- Icon rail: narrow global tool and mode rail.
- Connection/sidebar area: compact connection list, schema tree, and navigation.
- Schema tree: dense, keyboard-friendly, scrollable, with clear active, hover, loading, and error states.
- Central work area: tabbed SQL/editor/result panes with compact toolbars and predictable split behavior.
- Right inspector: contextual metadata, details, safety review, or assistant content within `280px` to `340px`.
- Status bar: persistent low-height feedback for connection, job, session, transaction, and safety state.
- Command palette: fast keyboard surface with `720px` max width and compact grouped results.

Avoid page sections styled as floating cards. Use cards only for repeated items, modal content, and genuinely framed tools.

## Data Grid Rules

The grid is the product's visual center of gravity. It must feel dense, calm, and inspectable.

- Use `28px` to `32px` rows.
- Preserve visible row and column structure.
- Support hover, active cell, selected range, dirty cell, loading, empty, and error states.
- Keep data readable at `12px` with suitable mono treatment for data-heavy cells.
- Use virtualization and server paging for large result sets.
- Do not design as a loose admin table with large cells, oversized filters, or card-like row blocks.

## Query And Editor Rules

- SQL editor text uses `13px` mono.
- Toolbars stay compact around `40px`.
- Run, cancel, transaction, session, timing, row count, error, and limit states should be visible and calm.
- AI-drafted SQL, imports, and edits must enter normal editor or review surfaces for explicit user execution.
- Production or destructive-query friction should be visible without turning the app into a warning wall.

## Production-Safety Treatment

Use environment and safety color consistently:

- Local: `#32D17C`
- Staging: `#4C8DFF`
- Production: `#FF8A3D`
- Read-only: `#7D8590`
- Dirty/unsaved: `#D4A72C`
- Success: `#34C759`
- Warning: `#FFB020`
- Error: `#FF5D5D`

Expose safety state near the object it affects: connection rows, tab labels, editor toolbars, result grids, review surfaces, and destructive confirmations.

## shadcn Composition Rules

Use shadcn source components where available, while preserving the compact deck identity through theme tokens and composition.

- Prefer semantic theme tokens over raw Tailwind color utilities in component code.
- Use `gap-*`, not `space-x-*` or `space-y-*`.
- Use `size-*` for square icon and button dimensions.
- Use FieldGroup, Field, InputGroup, ToggleGroup, Tabs, Sidebar, Resizable, ScrollArea, Dialog, Sheet, Command, Table, Badge, Skeleton, Tooltip, and Separator patterns where appropriate.
- Icons inside buttons use component-supported icon sizing and `data-icon`.
- Dialogs, sheets, drawers, and command surfaces must have accessible titles.
- Do not assume shadcn has already been initialized; apply these rules when a frontend implementation change creates or adopts the component system.

## Motion Rules

- Hover and panel transitions: `120ms` to `180ms`.
- Palette and dialog transitions: `180ms` to `220ms`.
- Use subtle state transitions only.
- Do not add decorative animation, animated backgrounds, or motion that distracts from database work.

## Anti-Generic Rules

- No oversized marketing cards.
- No decorative gradients.
- No one-note purple or blue theme.
- No playful rounded SaaS dashboard style.
- No low-density admin-page layouts.
- No landing-page framing inside the app.
- No decorative illustration-first empty states when a compact operational state would be clearer.

## Quality Gates

For frontend/UI work:

- Read this file before implementation.
- Compare relevant surfaces with `static/helixdb_design_deck.pdf`.
- Capture desktop and mobile browser screenshots for UI changes.
- Check text fit, overlap, focus visibility, keyboard access, accessible titles, and contrast.
- Verify deck fidelity for palette, density, typography, shell composition, data-grid rhythm, and native-tool feel.
