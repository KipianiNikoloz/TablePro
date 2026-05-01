## Context

TablePro currently has product and architecture context, but no frontend implementation. Before UI code begins, the project needs a durable visual rulebook that agents can apply consistently across app shell, grids, editors, dialogs, safety states, and future shadcn composition.

The local file `static/helixdb_design_deck.pdf` contains the desired frontend visual language. It uses HelixDB naming and includes some future-facing database-product screens. This change treats the deck as a visual source of truth only. Product scope, feature authorization, and implementation sequence remain governed by OpenSpec capabilities and `docs/context/` domain shards.

## Goals / Non-Goals

**Goals:**

- Make `static/helixdb_design_deck.pdf` the authoritative visual reference for frontend identity, density, layout rhythm, and UI quality.
- Translate deck branding from HelixDB to TablePro unless a future rename is explicitly approved.
- Capture a compact dark design system with concrete palette, typography, layout metrics, motion rules, composition rules, and anti-generic constraints.
- Define shadcn-compatible implementation expectations without requiring shadcn to be initialized in this docs-only change.
- Add validation gates for accessibility, browser fidelity, responsive behavior, and deck fidelity.

**Non-Goals:**

- Do not implement frontend code, components, tokens, Tailwind config, or shadcn setup.
- Do not approve new product features depicted in the deck.
- Do not make the deck authoritative for TablePro product scope, workflows, or backend capability.
- Do not rename TablePro to HelixDB.

## Decisions

### Decision: Use the deck as visual authority only

The UI design system will reference `static/helixdb_design_deck.pdf` as the visual source of truth for dark-mode identity, density, layout rhythm, native-tool feel, and component treatment.

Alternatives considered:

- Treat the deck as product scope: rejected because it includes invented or future-facing features that have not been approved.
- Treat the deck as loose inspiration: rejected because frontend implementation needs a strict rulebook before code exists.

Rationale: a visual-only contract gives implementation agents enough specificity to build a coherent UI while preserving OpenSpec as the product-scope authority.

### Decision: Store implementable visual rules in `docs/context/ui-design-system.md`

The new context shard will be the canonical frontend visual rulebook. `AGENTS.md` and `docs/context/frontend.md` will route all frontend/UI work to it.

Alternatives considered:

- Keep all visual details only in the OpenSpec spec: too rigid and too verbose for everyday agent use.
- Link only to the PDF: too ambiguous for implementation and validation.

Rationale: the spec defines testable requirements; the context doc translates the deck into usable tokens, metrics, composition rules, and quality gates.

### Decision: Keep TablePro naming

Any HelixDB labels in the deck are visual-brand artifacts. TablePro frontend implementation will use TablePro naming unless a future OpenSpec change approves a rename.

Alternatives considered:

- Rename the product now: rejected because this change is about UI design system context, not product identity.
- Preserve HelixDB labels in UI mockups: rejected because it would confuse product context and implementation.

Rationale: the visual system can be reused without changing the product name.

### Decision: Require compact, token-driven shadcn composition

Future shadcn-based UI work will use source components where appropriate, semantic theme tokens, compact composition, accessible titles, supported icon sizing, and patterns such as FieldGroup, Field, InputGroup, ToggleGroup, Tabs, Sidebar, Resizable, ScrollArea, Dialog, Sheet, Command, Table, Badge, Skeleton, Tooltip, and Separator.

Alternatives considered:

- Use raw Tailwind color utilities in component code: rejected because it makes deck fidelity hard to maintain.
- Hand-roll all primitives: rejected because shadcn source components provide accessible, inspectable building blocks.

Rationale: token-driven shadcn composition can preserve the deck's compact, dark, native-tool feel while staying maintainable.

### Decision: Validate UI work against browser and deck fidelity gates

Frontend changes will require desktop and mobile browser screenshots when UI is affected, plus comparison against relevant deck screens where applicable.

Alternatives considered:

- Rely only on unit tests: insufficient for visual density, layout, and browser fidelity.
- Require pixel-perfect matching: too brittle because the deck is a reference, not implementation assets.

Rationale: screenshots and deck comparisons catch spacing, density, contrast, and composition drift without overfitting exact pixels.

## Risks / Trade-offs

- Deck features could be mistaken for approved scope -> The spec and UI context explicitly state that future-facing deck features are visual examples only until a feature-specific OpenSpec change approves them.
- A strict visual rulebook could slow early implementation -> The rulebook focuses on reusable tokens and layout metrics so implementation can move quickly without re-deciding visual language.
- shadcn guidance could imply an initialized frontend stack -> The spec states shadcn-compatible rules without requiring initialization in this docs-only change.
- Dark, dense UI could harm accessibility -> The spec requires contrast, keyboard, focus, responsive, and screenshot validation gates.

## Migration Plan

1. Create the OpenSpec change artifacts and new `tablepro-ui-design-system` capability.
2. Add `docs/context/ui-design-system.md`.
3. Update `AGENTS.md`, `docs/context/frontend.md`, and `docs/context/product.md` to route frontend/UI work through the new visual context.
4. Validate the OpenSpec change.
5. Leave component implementation and frontend token files for a future implementation change.

Rollback is straightforward because this change only adds and updates documentation/specification files.

## Open Questions

- None for this design-system context change.
