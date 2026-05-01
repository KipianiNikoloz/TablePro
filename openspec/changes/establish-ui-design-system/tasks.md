## 1. OpenSpec UI Design System

- [x] 1.1 Create `tablepro-ui-design-system` spec requirements for deck reference usage, dark-mode identity, layout metrics, typography and color tokens, data grid behavior, workspace composition, safety treatment, editor treatment, shadcn rules, and UI validation gates.
- [x] 1.2 Create the design document explaining how `static/helixdb_design_deck.pdf` maps into implementable frontend context.

## 2. Context Documentation

- [x] 2.1 Add `docs/context/ui-design-system.md` as the canonical frontend visual rulebook.
- [x] 2.2 Capture the deck contract that the PDF is visual-authoritative but feature-scope-non-authoritative.
- [x] 2.3 Capture TablePro naming as the implementation brand while borrowing deck visuals from HelixDB.
- [x] 2.4 Capture all deck-derived palette tokens, typography rules, layout metrics, composition rules, motion rules, and anti-generic rules.
- [x] 2.5 Include shadcn-compatible guidance without assuming a frontend project has already been initialized.

## 3. Context Routing Updates

- [x] 3.1 Update `AGENTS.md` to route UI/design work to `docs/context/ui-design-system.md`.
- [x] 3.2 Update `AGENTS.md` to require `docs/context/ui-design-system.md` before frontend implementation work.
- [x] 3.3 Update `docs/context/frontend.md` to reference the UI design system as mandatory visual context.
- [x] 3.4 Update `docs/context/product.md` to preserve TablePro naming while borrowing HelixDB deck visuals.

## 4. Validation

- [x] 4.1 Run `openspec validate establish-ui-design-system`.
- [x] 4.2 Verify `AGENTS.md` routes frontend/UI work to `docs/context/ui-design-system.md`.
- [x] 4.3 Verify `docs/context/ui-design-system.md` explicitly says the deck is visual-authoritative but feature-scope-non-authoritative.
- [x] 4.4 Verify all deck-derived tokens and layout metrics are captured.
- [x] 4.5 Verify shadcn rules are included without assuming a project has already been initialized.
- [x] 4.6 Verify UI quality gates include desktop/mobile screenshots and deck-fidelity comparison against relevant deck screens.
