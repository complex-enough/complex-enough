# Codex Adapter

Use this adapter only in Codex hosts.

## Authority and repository context

- Read applicable global and repository `AGENTS.md` instructions before repository-backed work.
- Treat the collaboration tree and current working directory as shared state. Panelists must be read-only unless the moderator assigns non-overlapping ownership.
- Follow the host's approval, sandbox, destructive-action, and branch rules. The panel never expands them.

## Fresh independent contexts

- Do not call `spawn_agent` until the main-generated role slate has been shown to the user and the current revision/digest has been confirmed and frozen.
- Yield the role-slate checkpoint as the main session's final response and end that assistant turn. Commentary is not a checkpoint. Do not spawn, pre-spawn, queue, or run panelists in the same turn that proposes or revises roles.
- Accept freeze/start only from a subsequent user-authored turn. A role adjustment creates a new revision; deliver it as another final response and do not treat the adjustment message as permission to execute that new or a stale proposal.
- Spawn each panelist with a new context; use `fork_turns: "none"` when the host exposes that control.
- Put the complete task-local authority packet and exact frozen EffectiveRole in the initial message, including role/revision identity and digest.
- Do not use a full-history fork: it can leak moderator preferences, earlier findings, or evaluator criteria.
- Tell panelists they are not alone in the workspace, must preserve other work, and must not spawn nested agents unless explicitly authorized.

## Model and reasoning

- Keep inherited defaults unless the task-shape policy justifies an override.
- Use a named custom agent such as `luna_worker` only when its declared bounded-work scope matches. Supply a complete initial packet and a fresh context.
- Before a non-default spawn override or a named-agent choice, make any notification required by active user/repository instructions. Do not rewrite persistent global agent settings.

## Capacity and failures

- Inspect live agents before each wave when the host exposes agent status.
- Count the root/main session as occupied and reserve it for moderation.
- Use no more child agents than current free slots. Wait for a wave to complete before starting the next.
- If spawning returns a capacity error, keep the lens queued. If collaboration tools are unavailable entirely, use the declared single-session fallback and mark reduced independence.
- Treat wait expiry as an observation, not automatically as a panelist timeout; confirm agent state before recording failure or interrupting.

## Output metadata

- `perspective.executor` is `subagent` for successful child contexts and `main_session` for fallback passes.
- Retry/replacement creates a new `perspective_id` but preserves the frozen `role_id` and `role_revision_id`.
- Use `orchestration.execution=waves` when more than one child wave was required.
- In the public completion receipt, state the frozen plan revision/digest and map every planned `role_revision_id` to its executed attempt, wave, and degradation outcome; retain role-level public evidence attribution in the synthesis.
- When machine state is requested, retain the public meeting-plan snapshot across turns and bind panel-output 1.2 to its frozen revision/digest. Do not persist raw subagent messages.
- Codex UI metadata lives in `agents/openai.yaml`; it does not alter the stable public result schema.
