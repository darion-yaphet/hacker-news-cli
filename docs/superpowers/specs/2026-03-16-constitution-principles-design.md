# Constitution Principles Design (hacker-news-cli)

**Date**: 2026-03-16  
**Status**: Draft  
**Scope**: Project constitution principles and governance alignment

## Problem

The constitution template is still placeholder-only and does not encode the
quality, testing, UX consistency, and performance expectations for this
terminal-first CLI. This makes project guidance ambiguous and hard to enforce.

## Goals

- Define five non-negotiable principles focused on code quality, testing,
  UX consistency, performance, and simplicity/YAGNI.
- Keep principles declarative and testable.
- Move enforceable details into a Quality Gates section for clarity.
- Preserve governance expectations with explicit amendment/versioning rules.

## Non-Goals

- Changing runtime functionality or implementing features.
- Introducing new tools or dependencies.

## Proposed Principles

1. Code Quality as a Gate  
   Changes MUST improve or preserve readability, structure, and lint/static
   analysis baselines. No knowingly degraded quality ships.
2. Test Discipline First  
   New or changed behavior MUST be covered by tests at the right level
   (unit/integration/CLI). Tests MUST fail before the fix.
3. Consistent CLI UX Contracts  
   Flags, output formats, error messages, and exit codes MUST remain consistent
   across commands and versions.
4. Performance Budgets  
   New features MUST stay within defined latency/memory limits and include
   measurement or regression checks.
5. Simplicity / YAGNI (Terminal-First)  
   Prefer the simplest solution that meets requirements; avoid abstraction or
   features without immediate CLI value.

## Sections Alignment

- Section 2: "Quality & Performance Gates"  
  Concrete gating criteria (linting, test coverage expectations, CLI UX
  contract checks, performance budgets).
- Section 3: "Workflow & Review"  
  Review expectations, test gates, and release checks to enforce principles.

## Governance

- Constitution supersedes all other practices.
- Amendments require documented rationale, version bump, and date update.
- Compliance review required for every significant change.

## Success Criteria

- Constitution has no placeholder tokens left.
- Principles are explicit (MUST/SHOULD) and testable.
- Quality gates are clear enough to enforce in reviews and CI.
