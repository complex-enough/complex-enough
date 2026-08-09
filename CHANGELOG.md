# Changelog

All notable changes are documented here. Repository releases use Semantic Versioning; public output schema compatibility is versioned separately in the payload's `schema_version`.

## [Unreleased]

## [1.0.0] - 2026-08-10

### Added

- Productized Codex skill with dynamic risk-surface perspective selection and no fixed roster.
- Platform-neutral Agent Skill core with thin Codex and Claude Code execution adapters.
- Distinct `ideate`, `design`, `converge`, `review`, and `full_cycle` workflows.
- Independent fresh-context panelist protocol and moderator evidence adjudication.
- Model/reasoning selection guidance and deterministic wave orchestration.
- Timeout, unavailable-agent, capacity, replacement, and partial-coverage fallbacks.
- Repository authority, dirty-worktree, branch, and scope-authorization gates.
- Public panel output schema `1.1` with backward-compatible `1.0` fixtures.
- Repeatable eval suite covering product, architecture, consumer, high-risk, conflict, runtime evidence, failure, concise output, GUI output, full cycle, trigger boundaries, and cross-platform adapters.
- Deterministic validators and a safe global-skill installer.

### Changed from v0

- Narrowed implicit trigger boundaries to avoid routine single-lens work.
- Replaced role-list-first selection with explicit risk-surface and marginal-information tests.
- Made full-cycle stage provenance and panel reselection explicit.
- Distinguished independent subagent execution from degraded main-session fallback.
- Formalized public-only rationale and prohibited private reasoning/transcript fields.
- Constrained panelist wire enums and item budgets after forward tests exposed invented kinds and oversized raw reports.
- Hardened the release eval gate so result filename/host, complete assertions, suite version, runtime SHA-256, execution status, and final gate cannot be self-declared inconsistently.
- Removed trigger-eval contamination and made prompt rendering host-neutral; trigger cases now exercise normal installed-skill discovery without an explicit skill path.
- Enforced evidence-backed coverage, execution/degradation consistency, wave membership, full-cycle stage order, replacement graphs, and platform-neutral schema identity after fresh pre-release audit.
- Closed second-audit release bypasses by requiring behavioral Codex executions with nonempty evidence, unprimed natural trigger prompts, non-vacuous `GO`, completed-perspective coverage, stage-linked items/decisions, and later-wave replacements.
- Preserved v1 non-`GO` compatibility by enforcing non-vacuous panels at the semantic gate instead of globally, and rejected source-less full-cycle decisions.
- Bound release scorecards to all suite and fixture bytes, separated execution from revision verification time, rejected placeholder runner/evidence, and derived failure-injection provenance from capability-case execution.
- Rejected contradictory `GO`, down-labeled v1.1 payloads, failed-perspective full-cycle decisions, unordered cross-executor replacements, and invalid v1 enum-lock majors while retaining legacy v1.0 `GO` compatibility.
- Refused cross-platform target reuse so Claude installs cannot silently retain Codex-only managed metadata; made public installation commands account-neutral.
- Hardened installation against symlink/reparse-point redirection and partial mixed-version updates with verified same-filesystem staging and rollback.
- Bound every passing behavioral case to a versioned public-output artifact, exact rendered-prompt digest, run ID, runtime/suite revisions, and artifact digest; raw panelist/private reasoning remains excluded.
