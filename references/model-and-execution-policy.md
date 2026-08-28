# Model, Reasoning, and Execution Policy

Use this policy after selecting lenses. Model choice follows risk and task shape; it does not determine which perspectives are needed.

## Precedence

Apply in this order:

1. Explicit user model/agent requirements.
2. Applicable system, repository instruction files, and named-agent constraints.
3. Available model capabilities, context, tools, and concurrency.
4. The task-shape matrix below.
5. Latency and cost after capability is sufficient.

Never change persistent global subagent defaults for one run. Use per-invocation overrides only when allowed, and announce them when active instructions require it.

## Task-shape matrix

| Lens work | Model capability | Reasoning effort | Typical use |
| --- | --- | --- | --- |
| Deterministic lookup or bounded evidence extraction with exact paths/checks | Fastest model known to be reliable for the artifact/tool | Low or medium | Locate a contract clause, enumerate consumers, run a fixed check |
| Bounded single-domain review with clear authority | Current default capable model | Medium | UX operations pass, API contract completeness |
| Ambiguous cross-module design or trade-off analysis | Strong reasoning model | High | Boundaries, state machines, migrations, distributed failure |
| Conflicting evidence or high-consequence accounting, identity, authorization, security, privacy, irreversible data, or external commitments | Strongest available appropriate model | High or highest allowed by active rules | Adversarial review and disconfirming evidence |

If model capability is unknown, keep the current default rather than guessing an override. Increase reasoning only when ambiguity, consequence, or evidence conflict justifies it. Do not create artificial model diversity; independent lens questions and contexts provide the relevant diversity.

## Override decision record

For each override, retain a short public operational reason:

```text
perspective:
default_was_insufficient_because:
selected_model_or_named_agent:
reasoning_effort:
latency_cost_effect:
notification_required: yes | no
```

Do not expose private reasoning. The reason should be suitable for an activity log.

## Slot calculation and waves

Inspect live agent state when tooling supports it. Count the main session as occupied and reserve it for moderation. Let `child_capacity` be the number of child slots currently available to this session, not the platform's advertised total.

- If `child_capacity > 0`, take the next `child_capacity` required lenses in priority order, spawn them with fresh contexts, wait for completion/failure, then start the next wave.
- If `child_capacity = 0` because other useful work is active, wait or run main-session preparation; do not silently remove lenses.
- If child agents are unavailable as a capability, use the documented single-session fallback and mark execution degraded.
- Never let an unfinished low-priority panelist occupy the only path to an authority-critical lens when it can be interrupted or deferred safely under active instructions.

Do not pass a prior wave's findings into a later independent wave. Reuse only the original authority packet, except between full-cycle stages where accepted public artifacts intentionally become new authority.

## Timeouts and retries

Set or infer a bounded wait appropriate to task cost. A timeout is a failed execution event, not a negative finding.

- Record `failed` with `failure.code=timeout`.
- Retry the same lens at most once when the failure appears transient and remaining time/cost justifies it.
- Give a replacement a fresh context, the same frozen `role_id`, `role_revision_id`, lens question, and no prior findings.
- If recovery fails, mark coverage partial/uncovered and apply the gate rules; do not replace the lens with an easier nearby role.
