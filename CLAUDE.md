# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies, including the dev group (use uv)
uv sync

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/unit/test_client.py

# Run a single test by name
uv run pytest tests/unit/test_client.py::test_function_name

# Run tests with coverage (fails under 80%)
uv run pytest --cov=hn_cli

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Type check
uv run mypy src/hn_cli
```

## Architecture

The project is a layered CLI tool. Data flows: `cli.py` → `client.py` → `models.py`, and `cli.py` → `output.py` / `render.py` for presentation.

**`cli.py`** — Entry point. `build_parser()` defines all subcommands via `argparse`. `run()` dispatches to handler functions (`handle_list`, `handle_story`, etc.) which return `OutputPayload` structs. `output_payload()` then routes to either JSON (`output.py`) or text (`render.py`) based on `--format`. Interactive mode (`run_interactive`) is a REPL wrapping `run()`.

**`client.py`** — `HNClient` wraps the Firebase HN API (`hacker-news.firebaseio.com/v0`) and the HN web interface (`news.ycombinator.com`). `_get_json()` handles retries with exponential backoff. Login/logout scrape the HN web UI using `requests.Session` cookies.

**`auth.py`** — Persists login sessions as JSON to `~/.config/hn-cli/auth.json` (overridable via `HN_CLI_AUTH_FILE` env var). `apply_auth_session()` loads saved cookies into the client session; `persist_session()` saves them after login.

**`models.py`** — Immutable `@dataclass(frozen=True)` types: `Story` and `Comment`. Both use `from_api()` classmethods to construct from the raw API dict.

**`output.py`** — Serializes models to JSON-serializable dicts for `--format json`.

**`render.py`** — Formats output as human-readable text using the `rich` library for `--format text`. HTML in comments is converted to plain text via `html2text`.

## Test Layout

- `tests/unit/` — Unit tests for individual modules (client, models, output, render, auth, backoff)
- `tests/cli/` — Integration-style tests that call `run()` with mocked clients, covering each command and the interactive mode
- `tests/conftest.py` — Adds `src/` to `sys.path`

## Key Conventions

- All models are frozen dataclasses; construct via `from_api()` classmethods.
- `HNClientError` is the single exception type surfaced from the client; `CLIError` is for argument/logic errors in the CLI layer.
- The `list` command defaults to `--format text`; all other commands default to `--format json`.
- Tests use `HN_CLI_AUTH_FILE` to redirect auth storage to a temp path—don't hardcode `~/.config/hn-cli/auth.json` in tests.
