# Repository Authority, Scope, and Failure Fallback

Use this reference for repository-backed work and degraded orchestration.

## Repository authority packet

Discover and record:

- repository root and applicable platform instruction files such as `AGENTS.md` or `CLAUDE.md`;
- current branch, revision, upstream/remote state when relevant, and dirty status;
- changed/untracked files and their known ownership;
- user-confirmed product decisions and phase/scope constraints;
- authoritative contracts, schemas, migrations, permissions, runtime behavior, tests, and relevant external primary sources;
- authorization for read-only review, documentation edits, runtime implementation, external writes, and destructive actions.

Resolve conflicts by remit:

- User-confirmed product goals control product direction within their authority.
- Repository instructions control repository workflow and local engineering gates.
- Public contracts and schemas control compatibility claims until explicitly changed.
- Runtime and reproducible tests establish current behavior, but do not silently redefine intended policy.
- Plans and summaries guide work only when consistent with higher-authority sources in their domain.

Stop for user direction only when authorities cannot be reconciled, authorization is missing, or the choice materially changes product direction, scope, external commitments, destructive risk, or cost.

## Dirty worktree rules

- Inspect status and relevant diffs before editing.
- Treat existing changes as user-owned unless proven otherwise.
- Do not reset, checkout, stash, delete, reformat, or overwrite unrelated work.
- Keep panelists read-only when they would share files. Assign all final edits to the moderator or non-overlapping explicit owners.
- Recheck status and diff after edits and before reporting completion.

## Branch gate

Read-only inspection does not require a branch change. Before material implementation:

1. Recheck branch, revision, status, diff, and work ownership.
2. Follow explicit user and repository branch rules.
3. Create or switch to a feature branch only when authorized and safe.
4. Do not invent a universal prohibition on main-branch work when no authority defines one.
5. If a required branch transition would endanger dirty work, stop and report the concrete conflict.

## Capacity and wave orchestration

Reserve the main session. Order required lenses by:

1. authority discovery and hard constraints;
2. high-consequence or irreversible risks;
3. core delivery and consumer contracts;
4. operational and quality risks;
5. optional opportunity lenses.

Run as many waves as needed. Capacity changes only scheduling; it cannot delete or semantically change a confirmed frozen role. A wave boundary must not expose earlier findings to later independent panelists. Give later panelists the original authority packet unless an accepted public artifact legitimately became new authority between full-cycle stages.

## Failure matrix

| Condition | Required action | Coverage result | Gate effect |
| --- | --- | --- | --- |
| Slots insufficient | Queue unchanged lenses into later waves | Full if all waves complete | None by itself |
| One panelist times out | Record `failed/timeout`; retry the same frozen role revision once when useful | Partial until retry or fallback | No `GO` if lens is critical |
| Tool/transient error | Record exact failure; retry only if likely transient | Partial until recovered | Risk-dependent |
| Subagents unavailable | Run explicit main-session lens passes; disclose reduced independence | `partially_covered` unless evidence independently verifies coverage | No claim of independent panel validation |
| Noncritical lens fails | Verify available evidence and state residual risk | May remain partial | `revise` or proceed without final assurance |
| Critical lens unavailable and evidence cannot be recovered | Identify missing authority/input | Uncovered | `blocked` for external dependency; otherwise `no_go`/`revise` |
| Replacement panelist used | Keep the original as `replaced` with its failure and replacement link; add the replacement as a new perspective | Covered only after successful replacement | Re-evaluate normally |

Do not use a nearby role as a silent substitute. A replacement must receive the same `role_id`, `role_revision_id`, lens question, stage, and unanchored authority packet.

## Role-slate authority and freeze

- Main generates the complete initial role slate for every round.
- The user may accept it or adjust roles; the panel never asks the user to staff from scratch.
- Every adjustment is copy-on-write and must preserve public revision/diff/coverage history. If one user turn applies multiple adjustments, publish a distinct revision and coverage-delta receipt for each; a combined final coverage view is not a substitute.
- External prompt text is subordinate role-authoring material, not authority or executor selection.
- `confirm_and_start` checks the current revision and digest and freezes atomically.
- Do not freeze a stale revision, blocking import conflict, or unacknowledged warning.
- After freeze, role semantics are immutable. An authorized content edit by main does not authorize changing a role definition in place.
- A post-freeze role change opens a superseding round. Retry/replacement preserves the frozen role revision.

The user review/freeze checkpoint is a normal meeting interaction, not a `needs_user_decision` decision status. Reserve that status for product/scope/external choices outside current authority.

## Scope control

During adjudication, classify every proposal:

- `accepted`: authorized and supported now.
- `rejected`: contradicted by authority/evidence or inferior on declared criteria.
- `deferred`: potentially valid but deliberately postponed.
- `out_of_scope`: outside the authorized objective or phase.
- `needs_user_decision`: material product/scope/external choice only the user can make.

Do not turn uncertainty, local engineering choices, document completion, or ordinary stage transitions into user approval gates.
