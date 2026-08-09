# Codex Adapter

Use this adapter only in Codex hosts.

## Authority and repository context

- Read applicable global and repository `AGENTS.md` instructions before repository-backed work.
- Treat the collaboration tree and current working directory as shared state. Panelists must be read-only unless the moderator assigns non-overlapping ownership.
- Follow the host's approval, sandbox, destructive-action, and branch rules. The panel never expands them.

## Fresh independent contexts

- Spawn each panelist with a new context; use `fork_turns: "none"` when the host exposes that control.
- Put the complete task-local authority packet and unique lens in the initial message.
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
- Use `orchestration.execution=waves` when more than one child wave was required.
- Codex UI metadata lives in `agents/openai.yaml`; it does not alter the stable public result schema.
