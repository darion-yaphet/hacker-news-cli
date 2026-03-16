# HN CLI Improvements Design

**Date**: 2026-03-17  
**Status**: Draft  
**Scope**: Output formats, HTML-to-text comments, retry/backoff controls, quality gates

## Problem

The CLI currently outputs only JSON, does not normalize HTML comment bodies for
terminal reading, has limited retry behavior, and lacks automated quality gates
in CI.

## Goals

- Add a global `--format` flag with `json|text`, defaulting to JSON.
- Render human-readable text output for list, story, comments, and link.
- Convert comment HTML to readable text for text output.
- Provide configurable network timeout/retry/backoff defaults.
- Add lint, type checking, and CI enforcement.

## Non-Goals

- No config file support in this iteration.
- No new features beyond output, reliability, and quality gates.

## Proposed Changes

### Output Formats

- Add `--format {json|text}` to all commands, default `json`.
- JSON output stays identical to existing contracts.
- Text output:
  - `list`: Rich table with title, score, author, age, comments, URL (trimmed).
  - `story`: Rich panel with key fields.
  - `comments`: Indented list with author/age header + wrapped body.
  - `link`: Print URL only.

### Comment HTML → Text

- Add dependency `html2text`.
- For text output, convert comment HTML to readable text.
- For deleted or empty comments, show `[deleted]` or `[empty]` markers.
- If conversion fails, fall back to basic tag stripping.

### Retry/Timeout/Backoff

- Add flags: `--timeout` (seconds), `--retries` (int), `--backoff` (seconds).
- Defaults: `timeout=10`, `retries=2`, `backoff=0.5`, exponential backoff
  (0.5s, 1s, 2s) with max interval of 4s.
- Apply to all HTTP calls through the client.

### Quality Gates

- Add `ruff` and `mypy` to dev dependencies.
- Configure ruff for lint + format.
- Add a GitHub Actions workflow to run `ruff`, `mypy`, and `pytest` on PRs.

## UX and Constraints

- JSON remains the default to preserve scripting compatibility.
- Text output must remain stable and readable for terminal users.
- Rich is used for formatting, but output stays non-interactive.

## Success Criteria

- `--format text` renders legible output for all commands.
- Comment bodies are readable in text output without raw HTML.
- Retry settings are configurable and used for all requests.
- CI enforces lint, type checks, and tests.
