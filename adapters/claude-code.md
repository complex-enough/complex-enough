# Claude Code Adapter

Use this adapter only in Claude Code hosts. The core `SKILL.md`, references, schemas, and eval fixtures are platform-neutral; this file maps them to Claude Code execution.

## Authority and repository context

- Read applicable `CLAUDE.md` files and any repository-defined authority documents before repository-backed work.
- Respect Claude Code permission/tool policies. A panel does not grant write, network, shell, or bypass authority.
- Most panelists should be read-only because subagents share repository state. Do not use an isolated worktree when the review must observe the current dirty worktree: an isolated checkout can have a different baseline.

## Fresh independent contexts

- Do not invoke Agent/subagent execution until Claude has shown the complete main-generated role slate and the user has confirmed the current revision/digest.
- Show the complete slate as the final response and end that assistant turn. Commentary or autonomous continuation is not a confirmation checkpoint, and no Agent/subagent may be pre-spawned, queued, or run in the proposal turn.
- Accept freeze/start only from a subsequent user-authored turn. Treat role adjustment/import as a new immutable draft revision, then yield the updated complete slate as another final response and wait again before freeze.
- Use the Agent/subagent capability so every panelist receives its own context window.
- Give each subagent the same task-local authority packet, one exact frozen EffectiveRole with role/revision identity, and no peer findings or moderator preference.
- Prefer a general-purpose or explicitly read-only custom subagent whose tool restrictions match the lens.
- Do not use a fork of the current conversation as a substitute for a clean panelist context when it would carry anchoring material.
- Prevent nested delegation for panelists unless the moderator explicitly designed and budgeted it.

## Model, effort, and permissions

- Keep `inherit`/session defaults unless the task-shape policy justifies a model or effort override.
- Use faster models for bounded evidence extraction and stronger models for ambiguous/high-consequence lenses, subject to the configured allowlist.
- Apply per-invocation or subagent-definition overrides rather than changing global settings for one panel.
- For review, restrict tools to the read/search/test surface needed by the lens. For design/ideate/converge without repository evidence, no write capability is needed.

## Capacity and failures

- Respect the session's configured concurrent subagent limit; do not hardcode a platform default.
- Start only the lenses that fit, wait for completion/failure, and run later lenses as fresh waves.
- A concurrency error queues the lens; it does not justify dropping it or retrying immediately while capacity is unchanged.
- If the Agent capability is denied or unavailable, use explicit main-session lens passes and disclose that they are not independent subagent validation.
- Retry/replacement changes the attempt identity only; preserve the frozen role revision and do not substitute a nearby role.
- In the public completion receipt, state the frozen plan revision/digest and map every planned role revision to its executed attempt, wave, and degradation outcome; retain role-level public evidence attribution in the synthesis.

## Packaging and validation

- Personal skills live under `~/.claude/skills/<skill-name>/`; project skills live under `.claude/skills/<skill-name>/`.
- `SKILL.md` and referenced runtime files are shared with Codex. Claude Code ignores `agents/openai.yaml`, so the Claude installer does not need to copy it.
- Validate behavior with fresh Claude Code sessions before claiming Claude runtime support. Structural compatibility alone is not a behavioral pass.
- When machine state is requested, bind the closed-round panel-output 1.2 result to the confirmed meeting-plan revision/digest and exclude raw imported prompts from the result.
