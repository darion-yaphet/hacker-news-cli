<!--
Sync Impact Report
Version change: placeholder → 1.0.0
Modified principles:
- PRINCIPLE_1_NAME placeholder → I. Code Quality as a Gate
- PRINCIPLE_2_NAME placeholder → II. Test Discipline First
- PRINCIPLE_3_NAME placeholder → III. Consistent CLI UX Contracts
- PRINCIPLE_4_NAME placeholder → IV. Performance Budgets
- PRINCIPLE_5_NAME placeholder → V. Simplicity / YAGNI (Terminal-First)
Added sections:
- Quality & Performance Gates
- Workflow & Review
Removed sections:
- None
Templates requiring updates:
- ✅ .specify/templates/plan-template.md
- ✅ .specify/templates/spec-template.md
- ✅ .specify/templates/tasks-template.md
- ⚠ .specify/templates/commands/*.md (directory missing)
- ⚠ README*/docs (not present)
Follow-up TODOs:
- TODO(RATIFICATION_DATE): original adoption date unknown
-->
# hacker-news-cli Constitution

## Core Principles

### I. Code Quality as a Gate
Changes MUST improve or preserve readability, structure, and lint or static
analysis baselines. No knowingly degraded quality ships.

### II. Test Discipline First
New or changed behavior MUST be covered by tests at the right level
(unit, integration, CLI). Tests MUST fail before the fix.

### III. Consistent CLI UX Contracts
Flags, output formats, error messages, and exit codes MUST remain consistent
across commands and versions.

### IV. Performance Budgets
New features MUST stay within defined latency and memory limits and include
measurement or regression checks.

### V. Simplicity / YAGNI (Terminal-First)
Prefer the simplest solution that meets requirements; avoid abstraction or
features without immediate CLI value.

## Quality & Performance Gates

- Linting, formatting, and static analysis MUST pass with no new warnings.
- Behavior changes MUST include tests at the right level: unit for pure logic;
  integration for I/O or external services; CLI contract tests for user-facing
  commands and outputs.
- CLI UX contracts MUST be verified for changes affecting flags, outputs,
  errors, or exit codes; breaking changes require explicit migration notes.
- Performance budgets MUST be stated per command or feature in the spec or PR;
  changes must include measurements showing budgets met or a justified update.

## Workflow & Review

- All changes MUST undergo review (PR review or documented self-review if solo).
- Constitution Check in plans and specs MUST be completed before implementation
  and rechecked before merge.
- Tests MUST be green before merge for any behavior change.
- User-facing CLI changes MUST include release notes or documentation updates.

## Governance

- This constitution supersedes other guidance; conflicts resolve in its favor.
- Amendments require documented rationale, a Sync Impact Report, semantic
  version bump, and updated dates.
- Compliance review is required for significant changes, and reviewers MUST
  verify adherence to principles and gates.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption
date unknown | **Last Amended**: 2026-03-16
