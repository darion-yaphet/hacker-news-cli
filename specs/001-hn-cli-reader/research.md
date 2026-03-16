# Research

## Decision: HTTP requests approach

- **Decision**: Use `requests` with a persistent session, explicit timeouts,
  and retry handling for transient failures.
- **Rationale**: Improves reliability for CLI usage and keeps behavior
  consistent for repeated commands.
- **Alternatives considered**: urllib (lower-level), httpx (async-capable),
  aiohttp (async-only).

## Decision: JSON output contract

- **Decision**: Define a stable, versioned JSON schema for list, detail, and
  comments output to support scripting.
- **Rationale**: Enables predictable automation and aligns with the requirement
  for JSON output across user-facing commands.
- **Alternatives considered**: Ad-hoc JSON per command, text-only output.

## Decision: Terminal UI rendering

- **Decision**: Use Rich for tables, panels, and consistent styling in the
  terminal output.
- **Rationale**: Improves readability without sacrificing terminal-first
  simplicity.
- **Alternatives considered**: Plain text only, curses-based layouts.

## Decision: Dependency management

- **Decision**: Use uv to manage dependencies and lock versions.
- **Rationale**: Fast, reproducible installs with a clear lock file.
- **Alternatives considered**: pip + requirements.txt, poetry.

## Decision: Test strategy

- **Decision**: Use pytest with unit tests for formatters and parsing, and
  integration tests that mock network calls for list and detail flows.
- **Rationale**: Keeps tests fast while validating end-to-end CLI behavior.
- **Alternatives considered**: unittest, nose, pure integration tests.
