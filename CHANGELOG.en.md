English | [中文版](CHANGELOG.md)

# Changelog

All notable maintenance changes to this fork of **reverse-skill** are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This file records only **fork maintenance history** (starting 2026-10-03).
Upstream [`zhaoxuya520/reverse-skill`](https://github.com/zhaoxuya520/reverse-skill) product evolution
can be found in its commit history and [`docs/UPSTREAM.md`](docs/UPSTREAM.md).
Adoption and deferral rationale is documented in [`docs/DECISIONS.md`](docs/DECISIONS.md).

---

## [Unreleased]

### Fixed

- Case reinitialization retains the original `created` timestamp, records `updated`, and distinguishes scope updates from initial creation in timeline summaries.
- npm bootstrap now propagates nonzero setup-script exits instead of reporting a successful capability installation.
- PowerShell deep-review regressions: reinitializing a named case appends a scope-update event and preserves existing work items. Empty routing suites, including empty Quick selections, exit 2 instead of reporting green. Bootstrap exits 1 for unknown capabilities and fails when npm post-install commands are unavailable or return a nonzero exit code. Added offline regressions without installation side effects.

- `tools/check_dependency_freshness.py`: a GitHub Action pin carrying a `# freshness-hold: <reason>` comment always reported `CHECK FAILED` and never the intended `HELD: <reason>`; `--strict` (the CI gate) still failed even though `AGENTS.md` documents the hold comment as the marker that clears the check. Reproduced with a failing test, then fixed `check_failed` and the report rendering (commit `d272355`).

## [1.0.1] - 2026-10-03

### Added

- **Windows-first maintenance scaffolding**:
  - Consolidated `AGENTS.md` as the authoritative single source of truth for agents (retaining upstream consent markers), removing standalone `CLAUDE.md`.
  - Added `NOTICE.md`, `FORK.md`, `docs/DEVELOPMENT.md`, `docs/UPSTREAM.md`, `docs/DECISIONS.md`, and `REVIEW.md`.
  - Added maintenance tooling under `tools/`:
    - `dev_check.ps1`: Windows local verification gate (Python compile, Ruff E9+F, Pytest, link checking, repository security boundaries, routing coherence, quick routing regression).
    - `check_upstream_updates.py`: 3-axis upstream update checker for commits, PRs, and issues.
    - `check_dependency_freshness.py`: audits GitHub Actions SHA pins and `requirements-dev.txt` freshness.
    - `check_links.py`: relative link integrity checker for maintained documentation.
    - `upstream_baseline.json`: recorded baseline SHA `cab634b`, PR #170, and Issue #166.
  - Added maintenance test suite under `tests/`:
    - `test_upstream_check.py`: baseline schema and watermark verification.
    - `test_dependency_freshness.py`: dependency and action pin comparison contract tests.
    - `test_links.py`: link resolution and bilingual README cross-link tests.
    - `test_fork_docs.py`: contract verification for fork documentation.
  - Added `.cursor/rules/no-upstream-pr.mdc` restricting PR target to `SanHsien/reverse-skill`.
  - Added `.editorconfig` for consistent formatting.
  - Added GitHub Workflows:
    - `.github/workflows/upstream-check.yml`: weekly upstream review run.
    - `.github/workflows/dependency-freshness.yml`: monthly dependency freshness tracking.
- **Bilingual documentation entrance**:
  - `README.md` rewritten in Traditional Chinese as the primary portal, framing reverse-skill as a security router between AI development and production release.
  - Upstream English README preserved as `README.en.md` with bilingual navigation headers.
