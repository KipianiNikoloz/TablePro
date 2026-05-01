# AI Assistant Context

## Role

The AI assistant is an optional context side panel. It prepares drafts and explanations but does not execute database actions.

## Allowed Drafts

- SQL query drafts.
- Query explanations.
- Import mapping suggestions.
- Inline edit suggestions.
- Schema-aware suggestions.

All drafts must move into normal editor or review surfaces before execution.

## Context Policy

Default context:

- active database dialect
- selected connection metadata that is safe to expose
- schema metadata
- active query text when user is working in an editor
- error messages selected by the user

Not included by default:

- row/sample data
- credentials
- secrets
- full query history
- exported files

Row/sample data requires explicit user inclusion.

## Provider Model

Use an `AIProvider` port. V1 should support configurable OpenAI-compatible HTTP endpoints with presets for popular local providers such as Ollama, LM Studio, vLLM, and llama.cpp.

Provider configuration includes:

- display name
- base URL
- API key secret reference if needed
- model name
- provider preset
- enabled capabilities

## Execution Boundary

AI output is never a privileged channel. Generated SQL or import/edit suggestions must be treated like user-authored drafts and pass through the same preview, confirmation, safety, and audit flow.
