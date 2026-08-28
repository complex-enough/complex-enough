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
2. Classify handoff items as `carry_forward`, `deferred`, `excluded`, or `needs_user_decision`.
3. Open a new meeting round, recompute risk surfaces, and generate a complete new role slate.
4. Let the user accept or adjust that finished proposal, then freeze it before dispatch.
5. Start new panelists with fresh contexts and stage-specific instructions.
6. Do not expose prior raw panelist reports; provide only the authority packet and accepted public artifacts.
7. Stop when authorization ends or a genuine decision gate blocks the next stage.

The role-slate checkpoint occurs in every mode, not only `full_cycle`. It confirms who will execute the current round; it is not a vote and is not a `needs_user_decision` product escalation.

## Perspective selection algorithm

Build a table internally with these columns:

| Risk surface | Decision question | Needed evidence | Candidate lens | Distinct from | Criticality | Cost |
| --- | --- | --- | --- | --- | --- | --- |

Before turning candidate lenses into seats, choose one role-splitting complexity range:

| Range | Use when | Role-granularity behavior |
| --- | --- | --- |
| `lightweight` | The change is bounded, locally reversible, low-coupling, and has no high-consequence authority, data, financial, safety, migration, public-contract, or operating-risk trigger. One or few actual user surfaces may still exist. | Prefer a domain/product/implementation generalist plus only evidence-distinct user or specialist lenses. Architecture, security, privacy, reliability, testing, and rollout remain explicit duties on a capable generalist unless one requires distinct evidence. |
| `standard` | Multiple actual user surfaces, shared state, concurrency, or an external integration creates material coordination risk, but failures remain recoverable and no critical trigger requires separately accountable specialist evidence. | Split actual-user lenses when their goals, permissions, or failure consequences differ. Add professional seats only for distinct questions/evidence; keep generic architecture/security/reliability checklists combined where practical. |
| `critical` | A material financial/accounting, identity/authorization, sensitive or regulated data, irreversible-data/migration, safety, external/public contract, or high-consequence reliability/security failure needs specialist evidence or authority. Conflicting authority can also trigger this range. | Give every triggered critical surface a dedicated accountable specialist when another role cannot produce the required evidence. Still merge unrelated or overlapping roles and do not create a fixed roster. |

These are calibration ranges, not panel-size buckets. Do not define a minimum, maximum, or fixed role list for any range. A single critical trigger can justify `critical`; several ordinary surfaces do not. Conversely, the mere presence of data, an API, authentication, architecture, or security hygiene does not create a dedicated specialist seat. State the selected range and concise evidence-backed reasons in the role proposal. The user may request another range; recompute risks, granularity, coverage, and the whole slate rather than changing a scalar label while keeping contradictory roles.

For each risk, distinguish **ownership** from a **dedicated seat**. Every material risk needs an owner. A dedicated specialist is warranted only when its question, evidence source, authority, or consequence is materially distinct and the range supports that split. This keeps a lightweight CSV import from automatically receiving separate architecture and security seats while still requiring safe parsing, authorization, and recovery duties.

Use these tests:

1. **Distinct-question test:** Would this lens ask a question no selected lens owns?
2. **Distinct-evidence test:** Can this lens inspect evidence or consequences others are unlikely to cover?
3. **Stakeholder-impact test:** Can this stakeholder experience a materially different failure or value outcome?
4. **High-risk ownership test:** Does a material accounting, identity, authorization, migration, irreversible-data, security, privacy, safety, reliability, or external-contract risk lack explicit ownership, and does its evidence/consequence require a dedicated specialist under the selected range?
5. **Marginal-value test:** Is the expected new information worth its latency and cost?

Merge lenses that fail the first three tests. Assign every fourth-test risk, but create a separate seat only when generalist ownership would leave a distinct evidence or authority gap. Stop when all material risks have accountable coverage and remaining candidates fail the fifth.

## Actual-user lenses

Do not treat a product, UX, architecture, or operations professional as actual-user evidence. For user-facing `design` work:

1. Identify actual customer/operator surfaces whose goals, permissions, information, or failure consequences differ materially.
2. Merge surfaces when the same task and consequence can be represented by one lens; never add one seat merely because another UI channel exists.
3. In each selected user lens's independent opening, request goals, necessary information, likely misunderstandings, unacceptable failures, and minimum success conditions without showing proposed UI.
4. After professional openings, main normalizes only the relevant public UI/UX claims and evidence locators into a bounded packet.
5. Ask the same frozen user role to critique understandability, operability, false-success cues, unsafe shortcuts, and recovery. Do not send raw reports.

Label these as simulated actual-user lenses. They can expose task-model and operability gaps, but they do not prove prevalence, accessibility performance, or real user preference; preserve genuine research as a follow-up when material.

After selection, main converts every chosen lens into a complete RoleDefinition and presents the whole main-generated slate. User customization happens only after that proposal exists. A prior-round role has no automatic seat in the next round.

Treat `department` as a professional-affiliation label, not a grouping entity, leader-mediated reporting layer, or weight layer. A profession may contribute several roles in the same round when each passes the distinct-question or distinct-evidence tests—for example, two Engineering roles may separately own inventory integrity and event-delivery recovery. Keep their `role_id`, lens, evidence duties, risk ownership, and public provenance distinct. Never add same-department seats merely to create apparent consensus; multiple seats deepen coverage and do not multiply decision authority. Do not pre-collapse their results into a department position: a secondary seat's reproducible evidence must reach main even when a nominal lead or same-department majority disagrees.

Do not infer that every delivery channel needs a seat. For example, include Mobile App, API consumer, and end customer separately only when their contracts, release constraints, or failure experiences differ materially.
