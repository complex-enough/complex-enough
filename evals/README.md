# Forward evals

The suite separates neutral task inputs from evaluator assertions so an evaluated agent cannot reconstruct the expected answer from its prompt.

## Procedure

1. Validate the repository.
2. Copy only runtime skill files to an isolated temporary skill directory.
3. Render one case with `scripts/render_eval_prompt.py --host <host>`. Non-trigger cases also require the isolated `--skill-path`; trigger cases intentionally reject that argument and render only the natural user request plus fixture, with no discovery priming.
4. Start a fresh agent context and provide only turn 0. After each public assistant response, send the next rendered `--turn N` message in the same context. Never provide future user turns early: the eval must observe that role generation pauses before execution.
5. Capture every public main-session assistant response for the conversation in `evals/artifacts/<case-id>.json`; do not capture raw panelist reports, private agent messages, or private reasoning. The artifact `output` may concatenate these public responses with clear turn boundaries.
6. Bind the artifact's run ID, prompt digest, runtime/suite revisions, and file digest into the host scorecard, then score it against the case assertions.
7. Do not expose prior outputs or diagnoses to later agents.
8. After the final iteration, write one aggregate result file per host conforming to `schemas/eval-result.schema.json` and validate every artifact against `schemas/eval-artifact.schema.json`.

`executed_at` records when the forward cases completed. `verified_at` records the later time, if any, when the same public evidence was rechecked against the exact `skill_revision`. The result also carries `suite_revision`, a SHA-256 over the full suite definition, every referenced fixture byte, prompt renderer, and eval schemas; changing any of those inputs invalidates the scorecard. Each artifact is additionally bound to the exact rendered conversation and captured public output by SHA-256. `prompt_sha256` hashes the canonical JSON array of all rendered user turns, not only turn 0.

The artifact wrapper `run_id` identifies the evaluation execution. A machine-readable panel output may also contain its own public `run.run_id`, which identifies that panel-contract payload; the two namespaces are intentionally independent and are each preserved inside the artifact digest.

Capability cases (`one_child_slot`, `panelist_timeout`, `subagents_unavailable`) must use the stated harness condition when the platform can enforce it. If the condition is simulated in the task packet, use `execution: simulated_failure` and do not claim transport-level fault injection. The aggregate `failure_injection` value must agree with the real/simulated failure-capability executions.

## Scoring

Score every assertion as `pass`, `fail`, or `not_run`. A case passes only when every required assertion passes. Record concrete, concise public evidence from the output; placeholder evidence and an unnamed runner are invalid. Do not persist hidden reasoning or raw panelist transcripts.

The suite gate is:

- `GO`: all required static checks pass, every critical behavioral case passes, GUI output validates, and no unresolved trigger/scope/anchoring defect remains.
- `NO_GO`: any critical case fails or a required capability case is neither executed nor explicitly recorded as simulated/limited.

Captured public moderator outputs are versioned as release evidence. Raw panelist outputs, transcripts, and private reasoning remain excluded. Evaluated agents must not inspect existing artifacts, so versioned evidence does not become prompt context or anchoring input.

Multi-turn cases must demonstrate observable lifecycle order:

1. main generates a complete default role slate;
2. no perspective executes before the role-review followup;
3. adjustments/imports create a new public revision and coverage diff;
4. stale or conflicting confirmation does not dispatch;
5. the final public result binds the confirmed frozen role revision/digest when machine output is requested.

Codex and Claude Code must be scored separately. A passing Codex run plus Claude structural compatibility is not a Claude behavioral pass.

## Current versus historical scorecards

`scripts/validate_repo.py` classifies a scorecard by `suite_version`:

- A current-suite scorecard must match the exact current suite digest, runtime digest, complete case set, rendered-conversation digests, artifact digests, and gate semantics.
- An older semantic suite version is historical evidence only. Its result/artifact schemas, file digests, sealed metadata, timestamps, public-output restrictions, case status, and gate consistency are still checked, but it cannot satisfy the current release gate.
- An equal-version result with a stale digest, or a result claiming a future/newer suite version, fails validation instead of being treated as history.

Historical prompt bytes are not reconstructed from the changing current harness. Their stored prompt digest remains part of the sealed artifact, while only a fresh current-suite run can establish behavioral release evidence. Repository promotion requires at least one fully validated current Codex `GO` scorecard.

The [results/codex-2026-08-28.json](results/codex-2026-08-28.json) scorecard is sealed historical evidence for the preceding meeting-core runtime: 21/21 isolated cases, 49 captured public turns, and 95/95 assertions passed three fresh blind public-output graders. The 2026-08-29 role-complexity runtime change requires a new exact-runtime scorecard before release. The older 2026-08-10 scorecard also remains historical only.

Example non-trigger run:

```bash
python3 scripts/render_eval_prompt.py design-cross-module \
  --host codex \
  --skill-path /tmp/isolated/orchestrate-multi-perspective-panel
```

Render a later turn or inspect the neutral conversation packet:

```bash
python3 scripts/render_eval_prompt.py meeting-role-operations \
  --host codex \
  --skill-path /tmp/isolated/orchestrate-multi-perspective-panel \
  --turn 1

python3 scripts/render_eval_prompt.py meeting-role-operations \
  --host codex \
  --skill-path /tmp/isolated/orchestrate-multi-perspective-panel \
  --conversation-json
```

Example discovery-boundary run (no explicit skill path by design):

```bash
python3 scripts/render_eval_prompt.py trigger-negative-routine-review --host codex
```
