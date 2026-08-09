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

## Lens packet

Add one unique lens:

```text
perspective_id:
name:
lens_question:
selection_reason:
responsibilities:
explicitly_excluded:
```

Make exclusions concrete enough to reduce role overlap. Example: an API consumer lens can own compatibility, error semantics, idempotency, and release coupling while excluding business-priority and accounting-policy decisions.

## Independence rules

- Start every panelist in a fresh context.
- Give peers the same authority packet but different lens packets.
- Do not include peer outputs, vote counts, suspected defects, intended fixes, or expected decisions.
- Keep panelists read-only unless a distinct artifact owner was explicitly assigned.
- Prohibit nested spawning unless the moderator explicitly authorizes it and accounts for slots.
- Ask for conclusions and concise public rationale, never hidden chain-of-thought.

## Public response

Request this structure in prose or JSON:

```text
perspective_id:
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

Map each returned item to one source perspective. Deduplicate only at the decision layer so provenance remains intact. Preserve conflicting proposals until evidence-based adjudication is complete.
