<!--
Sync Impact Report:
- Version change: N/A → 1.0.0 (initial constitution)
- Modified principles: N/A (all new)
- Added sections: Core Principles, Development Workflow, Governance
- Removed sections: N/A
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md (Constitution Check section exists)
  ✅ .specify/templates/spec-template.md (no constitution-specific references)
  ✅ .specify/templates/tasks-template.md (no constitution-specific references)
  ✅ .cursor/commands/*.md (no agent-specific names requiring updates)
- Follow-up TODOs: None
-->

# Portrait Helper Constitution

## Core Principles

### I. Library-First

Every feature starts as a standalone library. Libraries MUST be self-contained,
independently testable, and documented. Clear purpose required - no
organizational-only libraries.

**Rationale**: Modular design enables reuse, easier testing, and clearer
boundaries between components.

### II. CLI Interface

Every library exposes functionality via CLI. Text in/out protocol: stdin/args →
stdout, errors → stderr. Support JSON + human-readable formats.

**Rationale**: CLI interfaces ensure debuggability, scriptability, and
integration with other tools.

### III. Test-First (NON-NEGOTIABLE)

TDD mandatory: Tests written → User approved → Tests fail → Then implement.
Red-Green-Refactor cycle strictly enforced.

**Rationale**: Test-first development catches defects early, documents expected
behavior, and enables confident refactoring.

### IV. Integration Testing

Focus areas requiring integration tests: New library contract tests, Contract
changes, Inter-service communication, Shared schemas.

**Rationale**: Integration tests verify that components work together correctly
and catch interface mismatches.

### V. Observability & Simplicity

Text I/O ensures debuggability. Structured logging required. Start simple, YAGNI
principles. Complexity must be justified.

**Rationale**: Simple designs are easier to understand, maintain, and debug.
Observability enables rapid diagnosis of issues in production.

## Development Workflow

All PRs/reviews MUST verify compliance with constitution principles. Code
reviews must check that tests exist for new functionality, that libraries are
self-contained, and that complexity is justified.

## Governance

This constitution supersedes all other practices. Amendments require
documentation, approval, and migration plan. All PRs/reviews must verify
compliance. Complexity must be justified. Use this constitution for runtime
development guidance.

**Version**: 1.0.0 | **Ratified**: 2025-11-15 | **Last Amended**: 2025-11-15
