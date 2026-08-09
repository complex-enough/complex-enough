# Modes and Dynamic Perspective Selection

Read this reference before dispatching a panel. Use the narrowest mode that completes the requested job.

## Mode matrix

| Mode | Required starting material | Diversity behavior | Moderator output | Normal gate |
| --- | --- | --- | --- | --- |
| `ideate` | Problem, target users, constraints, known assumptions | Maximize distinct framings and opportunity mechanisms; preserve disagreement | Candidate set, assumptions, risks, smallest experiments | `continue` |
| `design` | Bounded problem and relevant current contracts/state | Compare responsibilities, data ownership, interfaces, flows, and trade-offs | Recommended design or bounded options plus consequential gates | `continue` or `revise` |
| `converge` | Named options or a finite decision set | Challenge options against the same criteria; avoid new unbounded concepts | Accepted/rejected/deferred record and next action | `continue`, `revise`, or `blocked` |
| `review` | Reviewable artifact/runtime baseline and readiness criteria | Seek disconfirming evidence and uncovered failure modes | Prioritized findings, adjudication, validation, `GO`/`NO_GO` | `go`, `no_go`, `revise`, or `blocked` |
| `full_cycle` | Product objective and authorization for the requested stages | Reset lens selection and prompts at every stage | Stage artifacts and final review gate | Stage-dependent |

## Ideate

Ask panelists to produce different problem framings before solutions. For each candidate, include:

- target user and problem;
- value mechanism;
- key assumption;
- principal risk without severity ranking;
- smallest discriminating experiment.

Do not ask for a winner, `PASS`/`FAIL`, or premature implementation detail. The moderator may group related candidates but must preserve materially different mechanisms and tensions.

## Design

Ask panelists to make proposals concrete across:

- domain and component responsibilities;
- data ownership and source of truth;
- API/event/UI contracts and consumers;
- state transitions, idempotency, and failure recovery;
- identity, permission, privacy, audit, accounting, and reliability where material;
- migration, rollout, observability, and operating cost.

Reject fake options that existing authority already decides. Escalate only choices that change product direction, public contracts, risk posture, irreversible data, or material cost.

## Converge

Define shared adjudication criteria before dispatch. Common criteria include authority alignment, evidence, user value, safety, reversibility, compatibility, delivery cost, and operating cost.

Require each option to finish in exactly one public status:

- `accepted`
- `rejected`
- `deferred`
- `out_of_scope`
- `needs_user_decision`

Do not invent additional options unless all supplied options fail a non-negotiable constraint. If that happens, identify the failed constraint and propose only the smallest viable replacement.

## Review

Define the review target and readiness criteria. A finding must contain a reproducible observation, locator, consequence, and scope-safe correction. Use:

- `blocker`: unsafe or impossible to proceed; invalidates the requested terminal condition.
- `high`: material failure likely enough that it must be resolved before `GO`.
- `medium`: important but can be scheduled with an explicit owner and risk treatment.
- `low`: localized quality or maintainability improvement.

Use `question` for unresolved concerns without evidence. Reviewer conclusions are `PASS`, `PASS_WITH_CHANGES`, or `FAIL`; they are inputs to adjudication, not votes. The moderator's gate is separate.

## Full cycle

Run `ideate -> design -> converge -> review` only when the user requested end-to-end orchestration or its terminal condition requires all four stages.

At each stage boundary:

1. Close and persist only public stage artifacts and decisions.
2. Recompute risk surfaces and lens coverage.
3. Start new panelists with fresh contexts and stage-specific instructions.
4. Do not expose prior raw panelist reports; provide only the authority packet and accepted public artifacts.
5. Stop when authorization ends or a genuine decision gate blocks the next stage.

## Perspective selection algorithm

Build a table internally with these columns:

| Risk surface | Decision question | Needed evidence | Candidate lens | Distinct from | Criticality | Cost |
| --- | --- | --- | --- | --- | --- | --- |

Use these tests:

1. **Distinct-question test:** Would this lens ask a question no selected lens owns?
2. **Distinct-evidence test:** Can this lens inspect evidence or consequences others are unlikely to cover?
3. **Stakeholder-impact test:** Can this stakeholder experience a materially different failure or value outcome?
4. **High-risk ownership test:** Does a material accounting, identity, authorization, migration, irreversible-data, security, or external-contract risk lack a dedicated owner?
5. **Marginal-value test:** Is the expected new information worth its latency and cost?

Merge lenses that fail the first three tests. Add lenses that pass the fourth. Stop when all material risks have accountable coverage and remaining candidates fail the fifth.

Do not infer that every delivery channel needs a seat. For example, include Mobile App, API consumer, and end customer separately only when their contracts, release constraints, or failure experiences differ materially.
