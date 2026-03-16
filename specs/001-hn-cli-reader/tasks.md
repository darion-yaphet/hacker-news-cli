---

description: "Task list template for feature implementation"
---

# Tasks: Hacker News CLI Reader

**Input**: Design documents from `/specs/001-hn-cli-reader/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Required for behavior changes; tests will be written and executed
per task following TDD even if not listed as separate tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Create package layout at `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/` and test folders at `/Users/darion.yaphet/hacker-news-cli/tests/`
- [X] T002 [P] Initialize `/Users/darion.yaphet/hacker-news-cli/pyproject.toml` with Python 3, requests, rich, and pytest (dev) plus CLI entry point `hn`
- [X] T003 Generate `/Users/darion.yaphet/hacker-news-cli/uv.lock` using uv sync

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Implement core data models in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/models.py`
- [X] T005 [P] Implement HTTP client base (session, timeouts, retries, JSON parsing) in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/client.py`
- [X] T006 [P] Implement JSON output helpers in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/output.py`
- [X] T007 [P] Implement Rich-based error and help rendering in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/render.py`
- [X] T008 Implement CLI command skeleton and shared options in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/cli.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Browse Story Lists (Priority: P1) 🎯 MVP

**Goal**: List ranked stories from a selected feed in the terminal.

**Independent Test**: Run `hn list --feed top --limit 30` and verify JSON output
includes items with title, author, score, age, comment_count, and url.

### Implementation for User Story 1

- [X] T009 [P] [US1] Implement feed listing in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/client.py`
- [X] T010 [P] [US1] Implement list JSON schema mapping in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/output.py`
- [X] T011 [US1] Implement `hn list` command handler in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/cli.py`

**Checkpoint**: User Story 1 can be executed and returns valid JSON for list output

---

## Phase 4: User Story 2 - View Story Details and Comments (Priority: P2)

**Goal**: View story metadata and comment threads for a selected story.

**Independent Test**: Run `hn story --id <id>` and `hn comments --id <id>` and
verify JSON output for story metadata and comment threads.

### Implementation for User Story 2

- [X] T012 [US2] Implement story detail fetch in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/client.py`
- [X] T013 [US2] Implement comment thread fetch and ordering in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/client.py`
- [X] T014 [US2] Implement story detail JSON mapping in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/output.py`
- [X] T015 [US2] Implement comments JSON mapping in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/output.py`
- [X] T016 [US2] Implement `hn story` and `hn comments` handlers in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/cli.py`

**Checkpoint**: User Story 2 can be executed and returns valid JSON for details and comments

---

## Phase 5: User Story 3 - Access Story Links (Priority: P3)

**Goal**: Provide a direct story URL from the terminal for a selected story.

**Independent Test**: Run `hn link --id <id>` and verify JSON output contains
the correct URL.

### Implementation for User Story 3

- [X] T017 [US3] Implement story link JSON mapping in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/output.py`
- [X] T018 [US3] Implement `hn link` handler in `/Users/darion.yaphet/hacker-news-cli/src/hn_cli/cli.py`

**Checkpoint**: User Story 3 can be executed and returns JSON with story URL

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T019 [P] Update `/Users/darion.yaphet/hacker-news-cli/specs/001-hn-cli-reader/quickstart.md` if CLI syntax differs from implementation
- [X] T020 Validate JSON contracts in `/Users/darion.yaphet/hacker-news-cli/specs/001-hn-cli-reader/contracts/commands.md` against implemented output keys

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May reuse list outputs
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses story detail data

### Within Each User Story

- Models and shared helpers before command handlers
- Client data retrieval before output mapping
- Output mapping before CLI handlers

### Parallel Opportunities

- T001 and T002 can run in parallel
- T004, T005, T006, and T007 can run in parallel
- T009 and T010 can run in parallel

---

## Parallel Example: User Story 1

```bash
Task: "Implement feed listing in /Users/darion.yaphet/hacker-news-cli/src/hn_cli/client.py"
Task: "Implement list JSON schema mapping in /Users/darion.yaphet/hacker-news-cli/src/hn_cli/output.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify list JSON output matches contract
5. Demo or release MVP if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Validate JSON list output
3. Add User Story 2 → Validate detail and comment JSON output
4. Add User Story 3 → Validate link JSON output
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
