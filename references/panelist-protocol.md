# Panelist Task and Public Response Protocol

Use this protocol to create independent panelist tasks. Do not pass evaluator answers, other panelists' findings, or the moderator's preferred conclusion.

## Authority packet

Provide the smallest complete packet with:

```text
mode_or_stage:
objective:
terminal_condition:
scope:
non_goals:
authorities:
baseline:
artifacts:
authorization: read_only | edit_scoped_artifacts
preserve:
constraints:
required_verification:
```

Use artifact paths only when the panelist can read them. Otherwise include the relevant content. State which sources control which decisions instead of giving a universal authority order.

## Frozen role packet

Compile one unique EffectiveRole from the frozen plan:

```text
perspective_id:
role_id:
role_revision_id:
role_digest:
round_id:
name:
lens_question:
selection_reason:
responsibilities:
explicitly_excluded:
risk_surface_ids:
required_evidence:
expected_deliverables:
authority_limits:
execution_constraints:
mode_constraints:
stage_constraints:
optional_instructions:
```

Make exclusions concrete enough to reduce role overlap. Example: an API consumer role can own compatibility, error semantics, idempotency, and release coupling while excluding business-priority and accounting-policy decisions. Do not invent or revise role semantics after freeze.

The execution envelope contains the authority packet plus this EffectiveRole and the public response contract. It does not contain raw imported prompt text. An external provider label is provenance only; the executor remains an internal fresh context.

## Independence rules

- Start every panelist in a fresh context.
- Give peers the same authority packet but different lens packets.
- Do not include peer outputs, vote counts, suspected defects, intended fixes, or expected decisions.
- Keep panelists read-only unless a distinct artifact owner was explicitly assigned.
- Prohibit nested spawning unless the moderator explicitly authorizes it and accounts for slots.
- Ask for conclusions and concise public rationale, never hidden chain-of-thought.
- On retry/replacement, preserve `role_id`, `role_revision_id`, role digest, stage, and lens exactly; only `perspective_id` changes.

## Simulated actual-user protocol

Use this only when the frozen slate contains an actual customer/operator lens. The role is a task-consequence simulation, not a real interview, usability study, demographic persona, or statistical sample. State that authority limit in the role packet.

For a user-facing `design` round, execute the same frozen role in two bounded phases:

1. **Unanchored opening:** give only the common authority packet and the user's frozen role. Ask for task goals, information needed before/during/after action, likely misunderstandings, unacceptable failures, minimum success conditions, and how the user recovers when the result is unknown, state is stale, or a prior decision must change. Prohibit proposing a complete architecture or seeing peer/UI proposals.
2. **Public-claim critique:** after professional openings, main creates a short packet of only the UI steps, state labels, visible fields/actions, failure/recovery behavior, claim IDs, and public evidence locators relevant to that user surface. Ask the role to mark each claim `accept`, `revise`, or `question`, explain the operational consequence, and propose the smallest correction. Require it to identify any recovery category that the claims omit instead of silently accepting a happy-path-only flow.

Do not count the critique as a new role or vote. Preserve the same `role_id` and `role_revision_id`; record a separate attempt/phase identifier when the host can. Do not send raw peer reports, technical scratch work, or unrelated claims. Main adjudicates critiques against authority and evidence; a simulated preference cannot override safety, permissions, or a verified contract.

### Minimum recovery closure

Before Main closes a user-facing `design` synthesis, retain one concise public recovery entry per selected actual-user surface covering every applicable category:

```text
surface:
failure_or_change:
visible_authoritative_state:
safe_next_action:
authority_or_owner:
success_signal:
disposition: closed | authority_deferred | inapplicable
```

Check at least:

- submit/save result unknown or interrupted;
- return to edit, reselect, or change a prior decision;
- stale page, concurrent update, replaced proposal, or expired state;
- post-commit correction, bounded undo, or an existing human handoff when self-service is not authorized;
- the single current result and observable signal that the action actually took effect.

Do not require every category to become a new feature. `inapplicable` needs a reason. `authority_deferred` must name the existing owner, keep a safe visible state, and give the user/operator an actionable next step. Missing authority is not permission to invent policy. This closure is a synthesis invariant, not a reason to add architecture, frontend, backend, security, or operations seats.

## Public response

Request this structure in prose or JSON:

```text
perspective_id:
role_id:
role_revision_id:
status: completed | failed
summary:
items:
  - kind: idea | option | risk | finding | question
    statement:
    evidence:
      - source:
        locator:
        observation:
    impact:
    proposal:
    confidence: high | medium | low
conclusion: PASS | PASS_WITH_CHANGES | FAIL | null
public_rationale:
```

Apply these rules:

- Use the status wire values exactly: `completed` or `failed`; do not return `complete`, `ready`, or synonyms.
- Use only the five item kinds in the contract. Do not invent kinds such as `ownership`, `invariant`, `contract`, `recommendation`, or `decision_gate`.
- Map design responsibilities/contracts and convergence candidates to `option`; map harmful conditions to `risk`; map review defects to `finding`; map unresolved authority gaps to `question`.
- Keep `evidence` empty only for `idea` or `question`.
- Use `finding` only with locatable evidence and consequence.
- Omit severity in `ideate`. In `review`, add `blocker`, `high`, `medium`, or `low` to risks/findings.
- Use `conclusion` only for review.
- Keep `public_rationale` short and suitable for display to end users.
- Do not return scratch notes, hidden reasoning, internal messages, or raw transcripts.
- Merge repetitions. Target at most six materially distinct items and keep each item concise; exceed this only when separate blocker/high findings would otherwise be lost.

## Mode-specific prompt ending

- `ideate`: "Preserve differentiated framings and experiments; do not choose a winner."
- `design`: "Make responsibilities, contracts, state, failure handling, and trade-offs concrete."
- `converge`: "Adjudicate only the supplied decision set against the shared criteria."
- `review`: "Report only evidence-backed findings; label unsupported concerns as questions."

## Moderator normalization

Assign each returned material item a stable public item ID and map it to one source perspective, its `role_revision_id`, and public evidence locator before moderation. Deduplicate only at the decision layer so provenance remains intact. Preserve conflicting proposals until evidence-based adjudication is complete. In the public completion, expose a compact evidence ledger or equivalent inline mapping for consequential findings. Every completed same-department role must source at least one ledger item or be marked `no_material_finding`; a role-execution table alone cannot prove its evidence survived synthesis.

When actual-user critique changes a UI/UX claim, keep both the original public claim locator and the critique locator in the issue/ledger entry. Describe the accepted correction in user-facing terms; do not present simulated-user agreement count as research evidence.

For user-facing `design`, Main also maps each recovery entry to the relevant professional claim and actual-user critique locators. Compression may shorten wording, but it must not delete the visible state, safe action, authority owner, or success signal.
