## ADDED Requirements

### Requirement: Deck reference usage
TablePro frontend work SHALL treat `static/tablepro_design_deck.pdf` as the authoritative visual reference for identity, density, layout rhythm, component behavior, and UI quality gates.

#### Scenario: Deck is visual-authoritative
- **WHEN** a contributor implements or reviews frontend UI
- **THEN** they use `static/tablepro_design_deck.pdf` and `docs/context/ui-design-system.md` as visual design references

#### Scenario: Deck is not feature-authoritative
- **WHEN** the deck depicts features that are not approved by OpenSpec, including schema diff, SSH settings, explain-plan depth, or advanced settings
- **THEN** those features are treated as visual examples only and are not implementation scope until a feature-specific OpenSpec change approves them

#### Scenario: Product naming is preserved
- **WHEN** the deck uses HelixDB naming or labels
- **THEN** TablePro implementation uses TablePro naming unless a future OpenSpec change explicitly approves a rename

### Requirement: Dark-mode visual identity
TablePro frontends SHALL use the deck-backed dark, technical, calm, premium, and restrained visual identity.

#### Scenario: Core palette is available
- **WHEN** frontend theme tokens are created
- **THEN** they include tokens for app background `#0D1117`, sidebar background `#0A0F14`, elevated panels `#121923`, data grid background `#0F141C`, hover `#172130`, active `#1D2A3A`, borders `#243142`, primary text `#E6EDF3`, secondary text `#AAB6C3`, muted text `#7E8A99`, accent `#4C8DFF`, success `#34C759`, warning `#FFB020`, error `#FF5D5D`, info `#58A6FF`, prod `#FF8A3D`, staging `#4C8DFF`, local `#32D17C`, read-only `#7D8590`, and dirty or unsaved `#D4A72C`

#### Scenario: Generic visual styles are rejected
- **WHEN** a UI proposal or component uses oversized marketing cards, decorative gradients, a one-note purple or blue theme, playful rounded SaaS dashboard styling, or low-density admin-page layouts
- **THEN** the design is rejected or revised to match the deck-backed database-cockpit identity

### Requirement: Layout metrics
TablePro frontends SHALL use the deck-derived compact layout metrics for app shell, panels, bars, rows, dialogs, spacing, icon sizing, and corner radius.

#### Scenario: Shell metrics are applied
- **WHEN** the app shell is implemented
- **THEN** it uses an icon rail around `56px`, sidebar between `240px` and `280px`, inspector between `280px` and `340px`, tab bar around `36px`, toolbar around `40px`, status bar around `24px`, and data-grid rows between `28px` and `32px`

#### Scenario: Modal and command metrics are applied
- **WHEN** dialogs or command surfaces are implemented
- **THEN** modal widths use the `480px`, `640px`, or `860px` size families and the command palette uses a `720px` maximum width

#### Scenario: Spacing and shape metrics are applied
- **WHEN** component spacing, icons, or corners are implemented
- **THEN** spacing uses the `4px`, `8px`, `12px`, `16px`, and `24px` scale; icons use `14px`, `16px`, or `18px` outline-first sizing with `1.75px` stroke; and corners stay square-rounded around `4px` without soft pill aesthetics

### Requirement: Typography and color tokens
TablePro frontends SHALL define typography and color through reusable theme tokens that preserve compact readability.

#### Scenario: Typeface roles are defined
- **WHEN** typography tokens are created
- **THEN** UI text uses Inter, SF Pro, or Geist and SQL/data text uses JetBrains Mono, Berkeley Mono, or SF Mono

#### Scenario: Text scales are defined
- **WHEN** frontend text styles are created
- **THEN** app chrome uses `12px`, sidebar items use `13px`, table cells use `12px`, section headers use `14px` semibold, tab labels use `12px`, SQL editor text uses `13px` mono, modal titles use `16px` semibold, command palette input uses `14px`, and line-height stays between `1.35` and `1.5`

#### Scenario: Component code uses semantic tokens
- **WHEN** a frontend component is implemented
- **THEN** component styling uses semantic theme tokens rather than raw Tailwind color utilities for deck-derived colors

### Requirement: Dense data grid behavior
TablePro result grids SHALL preserve the deck's dense, readable, technical data-grid behavior while respecting backend paging and browser memory constraints.

#### Scenario: Grid density is preserved
- **WHEN** a result grid renders table data
- **THEN** it uses compact row heights, visible grid boundaries, mono-friendly numeric/data alignment where appropriate, and readable hover, active, selection, dirty, loading, and error states

#### Scenario: Grid remains scalable
- **WHEN** the grid displays large or wide result sets
- **THEN** it uses virtualization and server paging rather than assuming all result rows are loaded into browser memory

### Requirement: Workspace and pane composition
TablePro frontends SHALL use a database-workstation composition with app shell, icon rail, connection/sidebar area, schema tree, central work area, right inspector, status bar, and command palette.

#### Scenario: App shell composition is recognizable
- **WHEN** the main workspace renders
- **THEN** the layout clearly separates global navigation, connection/schema navigation, editor/grid work area, contextual inspector, and persistent status feedback

#### Scenario: Pane composition stays compact
- **WHEN** tabs, split panes, toolbars, or inspectors are implemented
- **THEN** they preserve compact density, predictable resize behavior, and native-tool layout rhythm rather than card-based page sections

### Requirement: Production-safety UI treatment
TablePro frontends SHALL visually distinguish local, staging, production, read-only, and dirty or unsaved states using the deck-derived safety palette and restrained friction.

#### Scenario: Environment labels are visible
- **WHEN** a connection, tab, editor, result grid, or destructive action is associated with local, staging, production, or read-only state
- **THEN** the UI exposes that state using the local `#32D17C`, staging `#4C8DFF`, prod `#FF8A3D`, or read-only `#7D8590` treatment

#### Scenario: Dirty state is visible
- **WHEN** a pane, cell, query, import plan, or edit batch has unsaved or unapplied changes
- **THEN** the UI exposes a dirty or unsaved state using `#D4A72C` treatment without overwhelming the workspace

### Requirement: Query and editor UI treatment
TablePro query and editor surfaces SHALL follow the deck's compact, technical, safe execution model.

#### Scenario: SQL editor styling is applied
- **WHEN** SQL editor panes are implemented
- **THEN** they use `13px` mono text, compact toolbars, visible run/cancel/status controls, and states for active session, transaction, results, errors, and unsaved edits

#### Scenario: Query action surfaces preserve execution boundary
- **WHEN** SQL, import, edit, or AI-drafted actions are presented to the user
- **THEN** they appear in normal editor or review surfaces with explicit user execution rather than decorative or hidden action flows

### Requirement: shadcn composition rules
TablePro frontend implementation SHALL use shadcn-compatible source-component composition where available while preserving the deck's compact, dark, native-tool feel.

#### Scenario: shadcn patterns are preferred
- **WHEN** a future frontend project has shadcn available
- **THEN** implementation uses source components and patterns such as FieldGroup, Field, InputGroup, ToggleGroup, Tabs, Sidebar, Resizable, ScrollArea, Dialog, Sheet, Command, Table, Badge, Skeleton, Tooltip, and Separator where appropriate

#### Scenario: utility usage stays consistent
- **WHEN** component layout utilities are authored
- **THEN** implementation uses `gap-*` instead of `space-x-*` or `space-y-*`, uses `size-*` for square icon/button dimensions, and uses component-supported icon sizing with `data-icon` for icons inside buttons

#### Scenario: overlays remain accessible
- **WHEN** dialogs, sheets, drawers, command palettes, or similar overlays are implemented
- **THEN** they include accessible titles and preserve keyboard and focus behavior

### Requirement: Accessibility and browser fidelity gates
TablePro UI work SHALL pass accessibility, responsive-browser, and deck-fidelity validation before completion.

#### Scenario: Accessibility gates pass
- **WHEN** frontend UI is implemented or changed
- **THEN** the change validates keyboard navigation, focus visibility, accessible names or titles, contrast, and readable text at the deck-derived density

#### Scenario: Browser screenshots are captured
- **WHEN** frontend UI is implemented or changed
- **THEN** desktop and mobile browser screenshots are captured to verify layout, text fit, non-overlap, density, and visual states

#### Scenario: Deck fidelity is checked
- **WHEN** a UI surface maps to a relevant screen or pattern in `static/tablepro_design_deck.pdf`
- **THEN** the implementation is compared against that deck reference for palette, typography, density, component rhythm, and overall native-tool feel
