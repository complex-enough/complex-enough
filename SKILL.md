---
name: orchestrate-multi-perspective-panel
description: Orchestrate independent, dynamically selected professional, operational, delivery, and user perspectives for ideation, product or architecture design, option convergence, evidence-based document or implementation review, readiness gates, and full-cycle decision support. Use when the user explicitly asks for a panel, multiple agents, independent perspectives, stakeholder lenses, adversarial review, or a synthesized multi-perspective conclusion, or when an authorized high-risk cross-functional review genuinely requires independent lenses. Do not use for routine single-lens questions, simple code review, or ordinary implementation that does not benefit from independent perspectives.
---

# Orchestrate Multi-Perspective Panel

Act as the moderator and final accountable owner. Select perspectives from the problem's risks; do not use a fixed roster or decide truth by voting. Give the user one synthesized result, not a bundle of panelist reports.

## 1. Fix the objective and mode

Choose exactly one entry mode from the user's requested outcome:

- `ideate`: create meaningfully different framings, opportunities, and experiments without selecting one winner.
- `design`: turn a bounded problem into responsibilities, contracts, flows, options, and explicit trade-offs.
- `converge`: adjudicate already available options into decisions, rejections, deferrals, and real user gates.
- `review`: inspect an artifact or runtime state against evidence and return findings plus a readiness gate.
- `full_cycle`: run the four stages in order, reselecting lenses and resetting stage instructions at every boundary.

Do not run `full_cycle` by default. Infer the narrowest mode that satisfies the request. Read [references/modes-and-selection.md](references/modes-and-selection.md) before dispatching panelists; apply its mode-specific inputs, behavior, and outputs.

## 2. Establish authority and authorization

Before dispatching work:

1. Classify the request as read-only advice/review or authorized editing/implementation. A panel does not expand authorization.
2. Discover the repository root when artifacts are repository-backed. Read the platform's applicable repository instruction files and task-relevant authoritative documents.
3. Inspect the baseline needed for the task: branch, revision, dirty worktree, existing diffs, runtime, schemas, contracts, consumers, permissions, tests, or primary external sources.
4. Record objective, mode, scope, non-goals, authorities, baseline, editable artifacts, preserved work, constraints, and terminal condition in an authority packet.
5. Resolve disagreements by each source's remit. Do not assume documentation always outranks runtime or runtime always outranks confirmed product policy.

For repository work, read and apply [references/authority-and-fallback.md](references/authority-and-fallback.md). Preserve dirty changes and ownership. Do not switch branches, stash, reset, edit, or create external state unless the user and repository rules authorize it.

## 3. Select perspectives dynamically

Create a risk-surface map before naming roles:

1. List distinct delivery surfaces, stakeholders, failure modes, irreversible decisions, evidence gaps, and external obligations.
2. For each material surface, define the question that must be answered and the evidence needed.
3. Select the smallest set of lenses that ask materially different questions or access different evidence.
4. Merge roles whose expected evidence and decision contribution overlap.
5. Add a lens when a material risk lacks an owner; stop when every material surface is covered and another lens has low expected information value relative to cost.

Do not set a default, minimum, or maximum panel size. Treat App, Web, API, end customer, tenant, platform operations, finance, security, privacy, reliability, accessibility, and compliance as candidates, never mandatory seats. Give accounting, identity, authorization, migration, irreversible data, and external commitments a dedicated lens when they are material.

Before spawning, tell the user in one short update which lenses were selected and why. Never present the lens list as a vote allocation.

## 4. Load the platform adapter and choose execution

Detect the current host before spawning. Read exactly one applicable adapter:

- Codex: [adapters/codex.md](adapters/codex.md)
- Claude Code: [adapters/claude-code.md](adapters/claude-code.md)

If no adapter matches, use only capabilities verified in the current runtime and mark the execution as an unverified adapter path. Keep the core authority, isolation, evidence, and output contracts unchanged.

Follow user and repository rules first. Otherwise:

- Keep the current default model and reasoning effort when it can reliably handle the lens.
- Prefer a stronger reasoning model/effort for ambiguous cross-module design, adversarial adjudication, security, identity, accounting, migrations, and other high-consequence work.
- Prefer a faster or lower-cost model only for bounded evidence collection with explicit artifacts and checks.
- Use named custom agents only within their declared scope. Never change persistent global agent settings for a single panel.
- Announce any per-invocation model or reasoning override when required by the active instructions; treat it as an approval gate only when cost, scope, or policy requires approval.

Reserve the main session for moderation. Calculate available child slots before spawning. If necessary, execute deterministic waves without dropping required lenses. Keep every lens in a fresh context; model diversity does not substitute for perspective diversity.

For nontrivial model, reasoning, or capacity choices, read [references/model-and-execution-policy.md](references/model-and-execution-policy.md). Do not spend a frontier/high-reasoning panelist on a duplicated lens or a deterministic lookup.

## 5. Dispatch independent panelists

Give every panelist the same task-local authority packet and one unique lens. Do not reveal other panelists' findings, the moderator's preferred answer, expected defects, evaluator criteria, or an intended fix. Exclude unrelated context to reduce anchoring.

Panelists are read-only by default and must not spawn other agents unless explicitly authorized. Their task must state:

- mode or full-cycle stage, objective, unique lens, and excluded responsibilities;
- artifact paths or supplied content, authorities, baseline, scope, non-goals, and authorization;
- evidence and verification expectations;
- the public response fields and exact wire enums to return;
- that hidden chain-of-thought must not be requested or returned.

Read [references/panelist-protocol.md](references/panelist-protocol.md) and use its task and response contract. Require exact enum values and concise material observations, evidence, proposals, conclusions, and public rationale only.

## 6. Preserve mode behavior

Apply these boundaries even when panelists suggest crossing them:

- In `ideate`, preserve useful divergence. Do not rank with severity, force consensus, or reject untested ideas as defects.
- In `design`, compare concrete boundaries, ownership, contracts, states, UX, failure handling, migration, and operations. Expose only consequential decision gates.
- In `converge`, adjudicate supplied options using authority, evidence, principles, reversibility, and total cost. Do not reopen unconstrained ideation.
- In `review`, require locatable evidence for findings, separate questions from defects, and use `PASS`, `PASS_WITH_CHANGES`, or `FAIL` per reviewer.
- In `full_cycle`, close each stage with its own output, carry only public decisions and artifacts forward, and reselect lenses for the next stage.

## 7. Normalize, verify, and adjudicate

After all waves:

1. Normalize items and deduplicate equivalent observations while preserving conflicting proposals.
2. Personally verify every blocker/high-severity claim, every claim that changes product direction, and every conflict where one side cites stronger authority or runtime evidence. Sample lower-severity evidence proportionately.
3. Treat the number of agreeing panelists as context, never proof. A minority view with reproducible evidence outranks an unsupported majority.
4. Mark decisions `accepted`, `rejected`, `deferred`, `out_of_scope`, or `needs_user_decision`. Give rejected items a concrete authority- or evidence-based public rationale.
5. Make local, reversible, authorized decisions directly. Escalate only genuine product, scope, external-commitment, destructive, authorization, or irreconcilable authority gates.
6. If editing is authorized, let the main session own edits and tests. After a material correction, run a focused fresh-context follow-up for affected lenses.
7. Check that panel advice did not introduce scope creep, duplicate an existing domain, overwrite dirty work, or silently advance to a later phase.

For `review`, issue final `GO` only when no unresolved blocker/high item remains, critical risk surfaces have evidence-backed coverage, authorities are consistent, affected runtime/consumers are included, and execution gates are actionable. Otherwise issue `NO_GO` or a non-final revision state.

## 8. Handle limited capacity and failures

Do not confuse execution degradation with task success:

- With insufficient slots, run waves in a stable order: authority-critical and high-consequence lenses first, then other required lenses. Do not delete lenses merely to fit concurrency.
- On timeout or tool failure, record the failed lens and failure code. Retry the same lens once only when time/cost permits and a retry can change the result.
- If subagents are unavailable, perform explicit lens-by-lens main-session passes, reset instructions between passes, and disclose reduced independence. Never label this fallback as independent subagent review.
- If a critical lens remains uncovered, do not issue `GO`. Use `blocked` only when missing external authority/input prevents progress; otherwise use `revise` or `no_go` with the missing coverage.
- If noncritical coverage is partial, continue only when the moderator can verify the evidence and the residual risk is explicit.

Record replacement and fallback honestly. See [references/authority-and-fallback.md](references/authority-and-fallback.md) for the failure matrix.

## 9. Return one integrated result

Lead with the conclusion, current stage, or gate. Briefly state the selected lenses and why. Then give only the most important ideas, decisions, accepted changes, rejected proposals with reasons, validation, unresolved risks, and genuine user decisions. Match the requested brevity and never paste raw panelist reports by default.

For `ideate`, return differentiated candidates and smallest useful experiments. For `design`, return the recommended design or bounded options and decision gates. For `converge`, return the decision record and next action. For `review`, return prioritized findings and the gate.

When the user, GUI, API, or persistence layer requests machine-readable output, read [references/panel-output-contract.md](references/panel-output-contract.md) and emit the current stable schema from [schemas/panel-output.schema.json](schemas/panel-output.schema.json). Include only public observations, evidence, proposals, decisions, and concise rationale. Never include hidden chain-of-thought, private scratch work, or raw internal transcripts.
