# HN CLI Improvements Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add text output mode, HTML-to-text comment rendering, retry/backoff flags, and quality gates (ruff, mypy, CI).

**Architecture:** Extend CLI parsing to support output format and client controls, add text rendering helpers, and update the HTTP client for retry backoff. Quality checks live in `pyproject.toml` and a GitHub Actions workflow.

**Tech Stack:** Python 3, requests, rich, html2text, pytest, ruff, mypy, uv

---

## Chunk 1: Dependencies and Quality Gates

### Task 1: Add dependencies and tooling config

**Files:**
- Modify: `/Users/darion.yaphet/hacker-news-cli/pyproject.toml`
- Modify: `/Users/darion.yaphet/hacker-news-cli/uv.lock`
- Create: `/Users/darion.yaphet/hacker-news-cli/.github/workflows/ci.yml`

- [ ] **Step 1: Update dependencies**

Add `html2text` to project dependencies and `ruff`, `mypy` to dev dependency group.

- [ ] **Step 2: Add ruff and mypy config**

Add minimal `[tool.ruff]`, `[tool.ruff.format]`, and `[tool.mypy]` sections to
`pyproject.toml` (line length 100, ignore virtualenv and cache dirs, mypy
non-strict defaults).

- [ ] **Step 3: Update lockfile**

Run: `uv sync`  
Expected: `uv.lock` updated with new dependencies.

- [ ] **Step 4: Add CI workflow**

Create `.github/workflows/ci.yml` to run `uv sync`, `ruff format --check`,
`ruff check`, `mypy`, and `pytest`.

---

## Chunk 2: Output Format and Text Rendering

### Task 2: Add format flag and text output plumbing (TDD)

**Files:**
- Modify: `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/cli.py`
- Modify: `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/render.py`
- Create: `/Users/darion.yaphet/hacker-news-cli/tests/cli/test_format_flag.py`
- Create: `/Users/darion.yaphet/hacker-news-cli/tests/unit/test_text_render.py`

- [ ] **Step 1: Write failing CLI format test**

Add tests asserting `--format text` returns plain text (not JSON) and default
remains JSON in `tests/cli/test_format_flag.py`.

- [ ] **Step 2: Run tests to confirm failure**

Run: `.venv/bin/pytest tests/cli/test_format_flag.py -q`  
Expected: FAIL (format flag not implemented).

- [ ] **Step 3: Write failing text renderer tests**

Add tests for list/story/comments/link text rendering in
`tests/unit/test_text_render.py` (assert key labels present).

- [ ] **Step 4: Run tests to confirm failure**

Run: `.venv/bin/pytest tests/unit/test_text_render.py -q`  
Expected: FAIL (text rendering not implemented).

- [ ] **Step 5: Implement format flag and text renderers**

Update CLI to parse `--format` and call either JSON output or text output
helpers. Implement text render helpers in `render.py` for list, story, comments,
and link.

- [ ] **Step 6: Run tests to confirm pass**

Run: `.venv/bin/pytest tests/cli/test_format_flag.py tests/unit/test_text_render.py -q`  
Expected: PASS.

---

## Chunk 3: Comment HTML → Text

### Task 3: Convert comment HTML for text output (TDD)

**Files:**
- Modify: `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/render.py`
- Create: `/Users/darion.yaphet/hacker-news-cli/tests/unit/test_html_render.py`

- [ ] **Step 1: Write failing HTML conversion tests**

Create tests for HTML conversion and deleted/empty markers in
`tests/unit/test_html_render.py`.

- [ ] **Step 2: Run tests to confirm failure**

Run: `.venv/bin/pytest tests/unit/test_html_render.py -q`  
Expected: FAIL.

- [ ] **Step 3: Implement HTML-to-text conversion**

Use `html2text` for text output. If conversion fails, fall back to basic
stripping. For empty/deleted comments, output `[deleted]` or `[empty]`.

- [ ] **Step 4: Run tests to confirm pass**

Run: `.venv/bin/pytest tests/unit/test_html_render.py -q`  
Expected: PASS.

---

## Chunk 4: Retry/Timeout/Backoff Controls

### Task 4: Add retry/backoff flags and client behavior (TDD)

**Files:**
- Modify: `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/cli.py`
- Modify: `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/client.py`
- Create: `/Users/darion.yaphet/hacker-news-cli/tests/unit/test_backoff.py`

- [ ] **Step 1: Write failing backoff test**

Add a test that injects a fake sleep function and asserts exponential backoff
delays are used for retries in `tests/unit/test_backoff.py`.

- [ ] **Step 2: Run tests to confirm failure**

Run: `.venv/bin/pytest tests/unit/test_backoff.py -q`  
Expected: FAIL.

- [ ] **Step 3: Implement backoff and flags**

Add `--timeout`, `--retries`, `--backoff` flags to CLI, pass to `HNClient`.
Implement backoff with max interval of 4s and injected sleep for tests.

- [ ] **Step 4: Run tests to confirm pass**

Run: `.venv/bin/pytest tests/unit/test_backoff.py -q`  
Expected: PASS.

---

## Chunk 5: Full Verification

### Task 5: Run full test suite and linting

**Files:**
- Modify: `/Users/darion.yaphet/hacker-news-cli/specs/001-hn-cli-reader/tasks.md`

- [ ] **Step 1: Run test suite**

Run: `.venv/bin/pytest -q`  
Expected: PASS.

- [ ] **Step 2: Run ruff + mypy**

Run: `.venv/bin/ruff format --check .`  
Run: `.venv/bin/ruff check .`  
Run: `.venv/bin/mypy src`

- [ ] **Step 3: Update task status**

Mark completed items in `specs/001-hn-cli-reader/tasks.md`.
