# Orchestrate Multi-Perspective Panel

An Agent Skill for assembling independent perspectives dynamically, preserving divergence when appropriate, and returning one evidence-based synthesis. It supports product ideation, architecture/product design, option convergence, readiness review, full-cycle orchestration, and a stable public contract for future GUI/API consumers.

The panel is not a fixed roster and is not a voting mechanism. The moderator selects lenses from material risk surfaces, gives each panelist a fresh context, verifies consequential evidence, adjudicates conflicts, and owns the final output and any authorized edits.

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
references/panel-output-contract.md   Versioned GUI/API contract guidance
schemas/panel-output.schema.json      Draft 2020-12 normative public schema
schemas/stable-enums.v1.json          Automated v1 wire-enum compatibility lock
evals/                                Repeatable cases, neutral fixtures, and result summaries
scripts/                              Validation, prompt rendering, and safe global install
tests/                                Schema compatibility and semantic invariant tests
```

`SKILL.md` and the core references are platform-neutral. Thin adapters map host-specific instruction files, subagent tools, permissions, model routing, concurrency, and install paths. Repository docs, eval artifacts, and tests support maintainers; the installer copies only runtime files.

## Platform support

| Host | Packaging | Behavioral status |
| --- | --- | --- |
| Codex | `SKILL.md`, references/schemas, Codex adapter, `agents/openai.yaml` | Forward-tested in this release |
| Claude Code | Same core plus Claude Code adapter; no OpenAI UI metadata required | Structurally compatible; behavioral forward tests still required in a Claude runtime |
| GUI/API | Stable JSON Schema only; no agent runtime dependency | Contract ready, implementation deferred |

## Dynamic perspective selection

For each task, the moderator maps delivery surfaces, stakeholders, failure modes, irreversible decisions, evidence gaps, and cost. A lens is included only when it asks a distinct material question, brings distinct evidence, or owns a material stakeholder consequence. Overlapping roles are merged; high-risk accounting, identity, authorization, migration, security, irreversible-data, and external-contract concerns receive dedicated ownership when material.

There is no default, minimum, or maximum panel size. Insufficient concurrency creates waves, not omitted lenses.

## Modes

- `ideate` preserves different framings and proposes smallest experiments without picking a winner.
- `design` makes responsibilities, ownership, contracts, states, UX, failure recovery, migration, and operations concrete.
- `converge` adjudicates a finite decision set by authority, evidence, reversibility, compatibility, and cost.
- `review` requires locatable evidence, prioritizes findings, and produces a moderator `GO`/`NO_GO` gate.
- `full_cycle` runs all four stages, closes public stage artifacts, and reselects fresh lenses at every boundary.

## Public GUI/API contract

The current public schema is `1.1`, additive to the original `1.0` shape. It includes perspectives, evidence-backed items, adjudicated decisions, risk-surface coverage, orchestration degradation, gate, and concise summary. It explicitly excludes hidden chain-of-thought, private scratch work, raw internal messages, and panelist transcripts.

Consumers should reject unknown major versions, ignore unknown fields, and render unknown enum values with a safe fallback. See [references/panel-output-contract.md](references/panel-output-contract.md) and [schemas/panel-output.schema.json](schemas/panel-output.schema.json).

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

Validate a GUI payload directly:

```bash
python3 scripts/validate_panel_output.py path/to/panel-output.json
```

## Forward evals

`evals/cases.json` contains neutral user requests, capability conditions, and evaluator assertions. Fixtures contain only task authority, not intended answers. Render a contamination-resistant agent prompt with:

```bash
python3 scripts/render_eval_prompt.py ideate-pure-product \
  --host codex \
  --skill-path /path/to/isolated/skill
```

Trigger cases omit `--skill-path` and render only the natural user request plus fixture, so discovery is observed without being named or primed. Run each behavioral case in a fresh agent context. Do not pass assertions or prior results to the evaluated agent. Version only the final public moderator response as a digest-bound artifact; never persist raw panelist reports or private reasoning. See [evals/README.md](evals/README.md).

The Codex `1.0.0` scorecard is [evals/results/codex-2026-08-10.json](evals/results/codex-2026-08-10.json): all 17 cases passed, including real one-child-slot waves, simulated same-lens timeout fallback, actual unavailable-subagent fallback, unprimed positive/negative trigger discovery, full-cycle reselection, and schema-valid GUI output. Every passing case is bound to its captured public artifact, exact rendered-prompt digest, runtime/suite revisions, run ID, and artifact digest. Claude Code remains structural-only until its separate host scorecard passes.

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
