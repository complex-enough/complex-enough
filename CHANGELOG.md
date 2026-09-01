# Changelog

All notable changes are documented here. Repository releases use Semantic Versioning; public output schema compatibility is versioned separately in the payload's `schema_version`.

## [Unreleased]

## [1.1.0] - 2026-09-02

### Added

- A bilingual static website source with final privacy, terms, support, and brand pages; a release-tag-driven GitHub Pages workflow with manual recovery; and a staged custom-domain/DNS runbook.
- Public pre-directory installation instructions for a tag-pinned local plugin marketplace or Codex personal skill, with a branded `Complex Enough Releases` marketplace.
- Canonical SVG brand sources plus reproducible plugin listing PNGs included in the submission bundle.
- Public-surface validation covering publisher identity, policy completeness, local links, package assets, and tracking-free static pages.
- Reproducible skills-only plugin packaging with a validated manifest, generated local marketplace, deterministic submission ZIP, and runtime-manifest parity tests.
- Portal-oriented listing metadata, five positive and three negative submission cases, privacy/terms/support drafts, and a Chinese official-submission readiness record.
- Public contribution, security-reporting, and community conduct policies for the planned public repository.
- A machine-readable local plugin smoke record covering discovery, negative routing, lightweight selective routing, and the invalidated stale same-name installation attempt.
- A pre-round selective-routing gate that keeps low-value single-actor reversible work in an ordinary session unless the user explicitly requests a meeting.
- A minimum actual-user recovery closure covering unknown results, return/reselection, stale or replaced state, post-commit correction or human handoff, visible current truth, authority owner, and success signal.
- Neutral forward cases for ordinary-session routing, explicit low-value lightweight meetings, and customer-to-operator recovery closure.
- A current Codex behavioral `GO` scorecard with 26 isolated cases, 59 public turns, 120 assertions unanimously passed by three fresh blind public-output graders, and digest-bound per-case artifacts.
- `lightweight`, `standard`, and `critical` role-splitting complexity ranges that calibrate specialist-seat granularity without creating fixed rosters or headcount buckets.
- Simulated actual-user lenses with unanchored task openings and bounded public UI/UX critique, explicitly separated from professional proxies and real user research.
- `meeting-plan` schema `1.1` with a digest-bound PlanRevision `complexity_profile`; schema `1.0` remains compatible legacy input.
- Neutral proposal-only forward cases for `lightweight`, `standard`, and `critical` calibration, including actual-user/professional separation and no automatic specialist seats.

- Boss-led meeting rounds in which main generates the complete role slate before a required user review/freeze checkpoint.
- Copy-on-write role and plan revisions for edit, add, remove, merge, split, reset, and external-prompt import operations.
- External prompt normalization with public field diffs, blocking authority/invariant conflicts, acknowledgeable warnings, and internal-only execution.
- `meeting-plan` public schema `1.0`, canonical role/plan digests, semantic validator, stable enum lock, and positive fixture.
- `panel-output` schema `1.2` with additive meeting, round, frozen plan, role revision, and risk ownership provenance.
- Cross-document bundle validation for frozen digest, attempt lineage, authority snapshot, planned/actual coverage, and close gate.
- Multi-turn eval rendering and neutral generated-role, role-operation, import-conflict, stale-confirmation, and per-stage reselection cases.
- Historical scorecard integrity validation that preserves older evidence without allowing it to release a changed suite/runtime.
- A public evidence ledger that maps consequential findings, decisions, rejections, and residual risks to exact role revisions and evidence locators, preserving supported secondary-seat evidence.
- A Codex v1.1 behavioral `GO` scorecard for the preceding meeting-core runtime with 21 isolated cases, 49 public turns, 95 independently graded assertions, and digest-bound per-case artifacts; it remains historical evidence after the role-complexity runtime change.

### Changed

- Public project authorship and plugin developer metadata now identify the verified-individual candidate `Huan Min Wei`, use `support@complexenough.com`, and point to the Complex Enough Organization, website, and policy paths. Exact OpenAI Platform identity matching remains a submission-time gate.
- Adopted **Complex Enough** as the public plugin brand while preserving the stable `orchestrate-multi-perspective-panel` skill/plugin identifier, invocation name, schemas, and `1.x` contracts.
- Official skills-only plugin submission now precedes GUI implementation in the phase plan; publisher-owned identity, policy URLs, branding, availability, public release, and external submission remain explicit gates.
- Task size no longer acts as a meeting-value proxy: distinct consequences, state/decision handoffs, authority/evidence differences, and real stale-state harm drive routing and user-seat splitting.
- Actual-user surfaces no longer receive mirrored professional proxies unless those seats contribute separate supplied evidence, policy authority, or materially different consequences.
- Main synthesis may compress wording but must retain each selected actual-user surface's recovery state, safe action, authority owner, and success signal or an explicit authority-owned deferral.
- The full-cycle forward conversation now resolves its genuine convergence product gate in a separate user turn before generating and confirming the readiness-review slate.
- Material architecture, security, privacy, reliability, and similar concerns require explicit ownership but no longer automatically create dedicated specialist seats; the selected range and distinct evidence/consequence determine splitting.
- Role proposals and mutation receipts now show the selected complexity range and reasons, and a user-requested range change recomputes the whole slate rather than relabeling an unchanged roster.

- Role review is now a hard conversation-turn barrier: main must end the proposal/revision turn with the complete slate, and only a subsequent user-authored turn may confirm, freeze, and start; commentary and same-turn autonomous continuation cannot dispatch perspectives.
- An unambiguous one-action confirmation of the already displayed current role slate now acknowledges its visible non-blocking warnings, avoiding a redundant chat gate while preserving blocking-conflict and critical-coverage safeguards.
- Every narrow-mode round and full-cycle stage now regenerates roles and waits for user confirmation before internal fresh-context execution.
- Retry/replacement preserves the exact frozen role revision; capacity affects waves only.
- Installed runtime manifest now includes meeting lifecycle/import contracts, schemas, and deterministic contract validators.
- GUI implementation remains the next phase; the current selective-routing/recovery runtime has passed its fresh Codex behavioral release gate and is GUI-ready.
- Blocker/high discovery rounds now close `revise`/`no_go`; corrections are verified in a new reviewed and frozen round instead of rewriting the original finding into `go`.
- Meeting structure remains two-level: main binds distinct professional perspective roles directly. `department` is only an affiliation label, so one profession may contribute several evidence-distinct seats without a Department entity, compound weights, leader-mediated aggregation, or extra voting power; supported secondary-seat evidence remains visible to main.
- Main proposes per-profession participation counts through the concrete role slate, and users adjust them through copy-on-write role operations; displayed counts are derived from active bindings rather than a second headcount source.

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
