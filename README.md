# Orchestrate Multi-Perspective Panel

An Agent Skill for boss-led multi-perspective meetings. Main selects the departments needed for each round, generates their complete roles, lets the user accept or adjust the finished proposal, freezes the exact slate, and then runs independent internal perspectives. It supports product ideation, architecture/product design, option convergence, readiness review, full-cycle orchestration, and versioned public contracts for future GUI/API consumers.

The panel is not a fixed roster and is not a voting mechanism. External ChatGPT/Claude prompts can be imported as role-authoring material, but external providers never become meeting executors. The moderator verifies consequential evidence, adjudicates conflicts, and owns the final output and any authorized edits.

Maintainer docs:

- [多視角編排邏輯現況評估與發展建議](docs/current-multi-perspective-logic-assessment.zh-TW.md)
- [老闆召集式多視角會議核心設計](docs/boss-led-meeting-core-design.zh-TW.md) — meeting-core design and GUI entry contract
- [Meeting core planning quality comparison](docs/evaluations/meeting-core-quality-comparison.md) — ordinary-session versus meeting-skill blind comparison

## Architecture

```text
SKILL.md                              Runtime workflow and routing
agents/openai.yaml                    Codex UI metadata and default prompt
adapters/codex.md                     Codex context, agent, slot, and model mapping
adapters/claude-code.md               Claude Code context, agent, and permission mapping
references/modes-and-selection.md     Distinct mode behavior and lens selection
references/panelist-protocol.md       Independent task and public response protocol
references/authority-and-fallback.md  Repository, scope, branch, wave, and failure rules
references/model-and-execution-policy.md  Model/reasoning tiers, slot math, and retries
references/meeting-lifecycle.md         Role generation, review/freeze, meeting phases, and handoff
references/role-definition-and-import.md  Effective roles and external prompt normalization
references/meeting-plan-contract.md     Editable control-plane contract and canonical digests
references/panel-output-contract.md   Versioned GUI/API contract guidance
schemas/meeting-plan.schema.json       Meeting/round/role revision public control state
schemas/panel-output.schema.json      Draft 2020-12 normative public schema
schemas/stable-*.v1.json              Automated v1 wire-enum compatibility locks
evals/                                Repeatable cases, neutral fixtures, and result summaries
scripts/                              Validation, prompt rendering, and safe global install
tests/                                Schema compatibility and semantic invariant tests
```

`SKILL.md` and the core references are platform-neutral. Thin adapters map host-specific instruction files, subagent tools, permissions, model routing, concurrency, and install paths. Repository docs, eval artifacts, and tests support maintainers; the installer copies only runtime files.

## Platform support

| Host | Packaging | Behavioral status |
| --- | --- | --- |
| Codex | `SKILL.md`, references/schemas/scripts, Codex adapter, `agents/openai.yaml` | Current range-calibrated runtime passes deterministic/structural validation; fresh behavioral release scorecard pending |
| Claude Code | Same core plus Claude Code adapter; no OpenAI UI metadata required | Structurally compatible; behavioral forward tests still required in a Claude runtime |
| GUI/API | `meeting-plan` v1.1 plus `panel-output` v1.2; no GUI runtime dependency | Control/result contracts implemented; GUI implementation deferred |

## Dynamic perspective selection

For each task, the moderator maps delivery surfaces, stakeholders, failure modes, irreversible decisions, evidence gaps, and cost. Before splitting seats it publishes a `lightweight`, `standard`, or `critical` complexity range. The range controls role granularity, not risk acceptance or a fixed headcount: lightweight work combines ordinary architecture/security/reliability duties into a capable generalist, standard work splits only evidence-distinct lenses, and critical work uses dedicated specialists for high-consequence evidence that cannot safely be combined.

A lens is included only when it asks a distinct material question, brings distinct evidence, or owns a material stakeholder consequence. Overlapping roles are merged. User-facing design also distinguishes actual customer/operator lenses from professional proxies: selected user roles state unanchored task needs first, then critique bounded public UI/UX claims. These are explicitly simulated lenses, not a substitute for real user research.

The model stays two-level: a MeetingRound directly binds professional perspective roles. `department` is only a descriptive affiliation label, so main may generate multiple roles from one profession when they own distinct questions or evidence. There is no Department entity, leader-mediated department result, or compound weighting layer. This avoids weight distortion and preserves a secondary seat's evidence instead of letting a department lead collapse it into one position; extra same-department seats still never count as extra votes.

Main also proposes each profession's seat count by generating the concrete roles. Users may ask for more or fewer seats, which becomes copy-on-write add/split/remove/merge operations with coverage deltas. The displayed count is always derived from active role bindings; there is no second `headcount` source that can drift from the executable slate.

Main converts the selected lenses into a complete role slate and waits for user review before execution. The user can accept immediately, adjust roles, or import externally authored role-positioning text. There is no default, minimum, or maximum panel size. Insufficient concurrency creates waves, not omitted lenses.

## Modes

- `ideate` preserves different framings and proposes smallest experiments without picking a winner.
- `design` makes responsibilities, ownership, contracts, states, UX, failure recovery, migration, and operations concrete.
- `converge` adjudicates a finite decision set by authority, evidence, reversibility, compatibility, and cost.
- `review` requires locatable evidence, prioritizes findings, and produces a moderator `GO`/`NO_GO` gate.
- `full_cycle` runs all four stages, closes public stage artifacts, and regenerates a user-confirmed role slate at every boundary.

## Public GUI/API contract

`meeting-plan` v1.1 records the editable main-generated role proposal, digest-bound complexity profile, copy-on-write adjustments/imports, planned coverage, warnings, frozen revision/digest, lifecycle, and public events. Meeting-plan v1.0 remains valid legacy input without the complexity profile. `panel-output` v1.2 remains the closed-round result and adds immutable meeting/round/role/risk provenance to the v1.1 evidence, adjudication, coverage, degradation, gate, and summary shape. Panel-output v1.0/v1.1 remain valid legacy results.

Both contracts explicitly exclude hidden chain-of-thought, private scratch work, raw internal messages, and panelist transcripts. Normal panel results also exclude raw imported role prompts. Consumers should reject unknown major versions, ignore unknown same-major additions, and render unknown enum values with a safe fallback. See [references/meeting-plan-contract.md](references/meeting-plan-contract.md) and [references/panel-output-contract.md](references/panel-output-contract.md).

## Install or update the skill

Prerequisites for development validation:

```bash
python3 -m pip install -r requirements-dev.txt
```

Preview or install the Codex personal skill:

```bash
python3 scripts/install_skill.py \
  --platform codex \
  --target ~/.codex/skills/orchestrate-multi-perspective-panel \
  --dry-run
```

Install or update without deleting unrelated target files:

```bash
python3 scripts/install_skill.py \
  --platform codex \
  --target ~/.codex/skills/orchestrate-multi-perspective-panel
```

Verify the installed bytes later:

```bash
python3 scripts/install_skill.py \
  --platform codex \
  --target ~/.codex/skills/orchestrate-multi-perspective-panel \
  --check
```

Install the same portable core for Claude Code after running Claude-specific forward tests:

```bash
python3 scripts/install_skill.py \
  --platform claude-code \
  --target ~/.claude/skills/orchestrate-multi-perspective-panel
```

Before a real install, the installer runs the repository release gate. It rejects managed-path symlinks/reparse points and cross-platform target reuse, stages and verifies the complete target on the same filesystem, atomically swaps it into place, and rolls back a failed commit. It does not modify persistent model settings or delete unrelated target files. Use separate Codex and Claude targets.

## Validate

Run the Skill Creator structural validator:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Run repository, schema compatibility, semantic, metadata, and eval-coverage checks:

```bash
python3 scripts/validate_repo.py
```

Validate meeting state, a closed result, or their frozen-provenance bundle directly:

```bash
python3 scripts/validate_meeting_plan.py path/to/meeting-plan.json
python3 scripts/validate_panel_output.py path/to/panel-output.json
python3 scripts/validate_meeting_bundle.py path/to/meeting-plan.json path/to/panel-output.json
```

## Forward evals

`evals/cases.json` contains neutral multi-turn user requests, capability conditions, and evaluator assertions. Fixtures contain only task authority, not intended answers. Render turn 0 of a contamination-resistant conversation with:

```bash
python3 scripts/render_eval_prompt.py ideate-pure-product \
  --host codex \
  --skill-path /path/to/isolated/skill
```

Trigger cases omit `--skill-path` and render only the natural user request plus fixture, so discovery is observed without being named or primed. Send later `--turn N` messages only after the prior public response. Run each case in a fresh context; do not pass assertions, future turns, prior results, or intended fixes. Version only public main-session responses as a digest-bound artifact; never persist raw panelist reports or private reasoning. See [evals/README.md](evals/README.md).

The Codex `1.0.0` scorecard at [evals/results/codex-2026-08-10.json](evals/results/codex-2026-08-10.json) remains historical evidence for the pre-meeting runtime. The `1.1.0` [2026-08-28 Codex scorecard](evals/results/codex-2026-08-28.json) is historical evidence for the preceding boss-led meeting runtime: all 21 isolated multi-turn cases and all 95 assertions passed fresh blind public-output grading. The 2026-08-29 complexity-range change modifies runtime bytes, so it requires a fresh bound scorecard before release or global installation. Claude Code remains structural-only until its separate host scorecard passes.

Repository validation keeps the historical scorecard integrity-checked but excludes it from release. A release `GO` is accepted only after full revalidation against the current suite digest, current runtime digest, complete current case set, and bound public artifacts.

## Local Git and remote setup

This repository is designed to work without a configured remote. A maintainer can add one later:

```bash
git remote add origin <repository-url>
git push -u origin main
```

Remote owner and visibility are intentionally not assumed by the skill or installer.

## Platform references

- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Claude Code: Create custom subagents](https://code.claude.com/docs/en/sub-agents)

## License

Licensed under Apache-2.0. See [LICENSE](LICENSE).
