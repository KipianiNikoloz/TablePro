## Why

TablePro needs a strict UI rulebook before frontend implementation begins, so the browser app can feel like a dense, native-quality database cockpit instead of drifting into a generic SaaS admin interface.

This change makes `static/helixdb_design_deck.pdf` the authoritative visual reference for TablePro frontend identity, density, layout rhythm, component behavior, and UI quality gates while keeping OpenSpec product scope as the source of feature requirements.

## What Changes

- Establish `static/helixdb_design_deck.pdf` as the visual/design reference for TablePro frontend work.
- Add a new `tablepro-ui-design-system` capability with testable frontend visual, composition, density, accessibility, and browser-fidelity requirements.
- Add `docs/context/ui-design-system.md` as the canonical visual rulebook for implementation agents.
- Clarify that HelixDB branding in the deck translates to TablePro unless a future rename is explicitly approved.
- Clarify that future-facing or invented deck features, including schema diff, SSH settings, explain-plan depth, and advanced settings, are visual examples only until approved by a feature-specific OpenSpec change.
- Update agent and frontend context routing so frontend/UI work loads the UI design system before implementation.

## Capabilities

### New Capabilities

- `tablepro-ui-design-system`: Defines the deck-backed visual design system, compact dark app shell, data-grid/editor treatment, shadcn composition rules, and UI validation gates for TablePro frontends.

### Modified Capabilities

- None.

## Impact

- Adds OpenSpec artifacts under `openspec/changes/establish-ui-design-system/`.
- Adds `docs/context/ui-design-system.md`.
- Updates `AGENTS.md`, `docs/context/frontend.md`, and `docs/context/product.md`.
- Does not implement frontend code, initialize shadcn, or approve new product features depicted in the deck.
