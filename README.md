# Complex Enough

**The right perspectives. No more.**

[Website](https://complexenough.com/en/) · [繁體中文](https://complexenough.com/zh-TW/) · [Privacy](https://complexenough.com/en/privacy/) · [Terms](https://complexenough.com/en/terms/) · [Support](https://complexenough.com/en/support/)

Complex Enough is agent-led planning quality control for autonomous software development. It is designed for situations where the user has only a goal or partial domain knowledge and expects an AI agent to drive the design. The user remains the boss, owning goals, scope, and consequential decisions; Main acts as the meeting manager.

The public plugin brand is **Complex Enough**. The contained skill, local marketplace plugin, and stable technical identifier remain `orchestrate-multi-perspective-panel`; existing invocation names, schemas, installation paths, and `1.x` contracts do not change with the brand. The official-directory submission ZIP uses the shorter wrapper identifier `complex-enough` so the required combined `plugin-name:skill-name` stays within the Platform limit; this does not rename the contained skill.

## Install

### OpenAI Plugins Directory (recommended)

Complex Enough v1.1.1 is published in OpenAI's universal Plugins Directory shared by ChatGPT and Codex. In a supported interface, open **Plugins**, search for **Complex Enough**, install it, and start a new chat or session before use.

### GitHub release marketplace (alternative)

Use the local marketplace when the universal directory is unavailable in the current host or account, or when you need a tag-pinned copy for local testing. Do not enable it beside the official-directory plugin or a same-name personal skill.

Clone the release and build its local marketplace:

```bash
git clone --depth 1 --branch v1.1.1 https://github.com/complex-enough/complex-enough.git
cd complex-enough
python3 -m pip install -r requirements-dev.txt
python3 scripts/package_plugin.py --replace
codex plugin marketplace add ./build/marketplace
codex plugin add orchestrate-multi-perspective-panel@complex-enough-releases
```

Start a new thread after installation. In the ChatGPT desktop app, this local copy appears under **Complex Enough Releases** and is separate from the public-directory listing. See OpenAI's [plugin marketplace documentation](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli).

### Codex personal skill

If the plugin surface is unavailable, install the same portable runtime as a personal Codex skill from the cloned release:

```bash
python3 scripts/install_skill.py \
  --platform codex \
  --target ~/.codex/skills/orchestrate-multi-perspective-panel
```

Restart Codex after installation. Do not keep this personal copy enabled beside the plugin, because same-name discovery may select either source.

## Product scope

### 1. Suitable situations and boundaries

Use Complex Enough when a plan has genuinely different user consequences, authority, evidence, state transitions, or human/system handoffs, especially when missing one of those perspectives could propagate a false assumption into later delivery work. The user does not need to know every stakeholder or solution detail in advance: Main maps the missing lenses and proposes the smallest sufficient slate for review.

Keep simple, single-actor, locally reversible work in an ordinary session. Selective routing is part of the product, not a failure to use it.

### 2. Difference from direct agent design

Multi-agent discussion is easy to start and easy to overdo. Fixed panels tend to invite the same architect, security, frontend, and backend roles regardless of the task; informal debates can also hide minority evidence behind consensus.

A direct design session usually lets one agent fill missing details from one working perspective. Complex Enough inserts a selective quality gate before the plan becomes the source for specs and code:

```text
direct session:  goal or partial knowledge -> one agent fills gaps -> Plan -> Spec -> Implementation
Complex Enough: goal or partial knowledge -> selective routing -> user-reviewed independent lenses
                -> evidence-based synthesis -> user-confirmed Plan -> Spec -> Implementation
```

This skill treats meeting formation as part of the decision:

- Main first checks whether independent perspectives are likely to change the result.
- Main generates complete role definitions; users do not have to author the panel themselves.
- The user may accept the proposal, edit it, change participation, or import role-positioning text produced by another ChatGPT or Claude session.
- The accepted slate is frozen before execution, so the meeting cannot silently change underneath the user.
- Main resolves claims by authority and evidence, not votes or department weights.
- When the requested task includes a user-facing workflow, its design must cover realistic uncertainty, correction, and handoff paths instead of only the happy path.

This is not an implementation-task dispatcher. Task-parallel workflows divide work after a direction exists; this skill forms stakeholder and evidence lenses before plan/spec, exposes the complete role slate for user adjustment, and hands the validated synthesis back to the normal delivery workflow.

Controlled evaluations directly measure the upstream Plan, where a broader six-task comparison observed about `5.0%` relative mean planning-score uplift. A better Plan is expected to reduce ambiguity passed into Spec and Implementation, but that downstream effect has not yet been measured and is not claimed as a percentage.

### 3. Planned extension: visible user learning

The current skills-only release returns structured public claims, evidence, conflicts, decisions, and a synthesis. A planned GUI will make that deliberation easier to follow so users can learn domain knowledge and understand why tradeoffs exist, ask Main for clarification, and request an added or split perspective for a newly confirmed round before the final Plan is locked.

Here, “learning” means the human user learns from the public decision process. It does not mean model training, permanent agent memory, hidden chain-of-thought, or access to raw private transcripts. This GUI is roadmap work and is not included in the current skills-only 1.1.1 release.

## How it works

```text
request
  -> Main checks meeting value and selects a mode
  -> Main maps users, decisions, evidence, handoffs, and failure consequences
  -> Main generates a complete role slate and complexity range
  -> user accepts, adjusts, or imports external role-positioning text
  -> the exact accepted revision is frozen
  -> roles open independently in fresh contexts
  -> Main challenges and verifies consequential claims
  -> one public synthesis, evidence ledger, and readiness result
```

The role-review turn is a real checkpoint. The skill shows the finished proposal and waits; it does not generate roles and start the meeting in the same assistant turn.

### Example

For a public appointment-change flow, Main might propose:

- a public customer who needs to understand the current booking and recover from an uncertain submit;
- a CMS operator who handles exceptions and must see the authoritative state;
- an appointment-domain owner who defines change windows, conflicts, and business rules.

The user can accept that slate as generated, ask Main to split or merge a role, remove an unnecessary seat, or paste an externally authored persona prompt for normalization. Technical implementation roles are added only when they own different evidence or consequences; they are not mandatory simply because software will eventually be built.

## When to use it

Use the skill when a task benefits from genuinely different lenses, for example:

- several users or operators have different goals, permissions, or failure consequences;
- a decision or state crosses a team, system, or human handoff;
- stale or conflicting truth can cause real harm;
- materially different evidence or authority must be reconciled;
- the user explicitly asks for a panel, meeting, adversarial review, or cross-functional judgment.

Keep the task in an ordinary session when one actor is using a mature, locally reversible pattern with no material handoff, authority split, or independent evidence need. If the user explicitly requests a meeting anyway, the skill honors that request with the smallest legitimate `lightweight` slate and discloses the likely low marginal value.

## Role and department model

The executable model has two levels:

```text
human user / boss (goals, scope, consequential decisions)
  -> Main / manager (meeting formation, moderation, synthesis)
       -> role A
       -> role B
       -> role C
```

`department` is a descriptive affiliation, not an aggregation layer. Main may select two roles from the same profession when they own different questions or evidence. There is no department leader result, compound department/role weighting, or extra vote for additional seats. This preserves useful evidence from a secondary seat instead of letting a leader collapse it into one departmental opinion.

Main also proposes the participation count through the concrete role slate. Users adjust participation by adding, splitting, merging, or removing roles; there is no separate headcount value that can drift from the people actually invited.

Main is accountable for the meeting process and evidence-based synthesis, not for silently taking product authority from the user. Product direction, scope changes, external commitments, major cost, and accepted high-consequence risk remain real user decisions.

## Design safeguards

### Selective routing

Task size is not used as a shortcut for meeting value. Routing is based on distinct consequences, handoffs, authority, evidence, reversibility, and stale-state harm. An implicitly selected low-value case returns to the ordinary Main workflow without creating meeting state.

### Actual-user perspectives

For user-facing design, simulated customer or operator roles first state their goals, information needs, likely misunderstandings, and unacceptable outcomes without seeing a proposed interface. They later critique bounded public UI/UX claims. These roles are useful design lenses, but are not a substitute for real user research.

### Minimum recovery closure

Each selected user surface must retain a safe answer for the relevant recovery conditions:

- the result of submit/save is unknown;
- the user returns or changes a selection;
- visible state is stale, replaced, or expired;
- a committed action needs correction, undo, or an existing human handoff;
- the user needs to know the current authoritative truth, its owner, the safe next action, and the success signal.

This is a synthesis requirement, not a reason to invite frontend, backend, architecture, or security roles by default.

## Modes

| Mode | Purpose |
| --- | --- |
| `ideate` | Preserve meaningfully different framings and propose the smallest useful experiments without forcing a winner. |
| `design` | Make user flows, responsibilities, states, contracts, recovery, migration, and operations concrete. |
| `converge` | Adjudicate a finite option set by authority, evidence, reversibility, compatibility, and cost. |
| `review` | Verify an artifact or runtime state and return prioritized findings plus a `GO`/`NO_GO` gate. |
| `full_cycle` | Run all four stages, generating and confirming a fresh role slate at every stage boundary. |

Use the narrowest sufficient mode; `full_cycle` is not the default.

## Maintainer installation from a repository checkout

Install the development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Preview a Codex personal-skill installation:

```bash
python3 scripts/install_skill.py \
  --platform codex \
  --target ~/.codex/skills/orchestrate-multi-perspective-panel \
  --dry-run
```

Install or update it:

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

The installer validates the repository, copies only the runtime manifest, rejects unsafe or cross-platform targets, performs an atomic swap, and rolls back a failed commit. It does not modify persistent model settings or delete unrelated target files.

Claude Code can use the same portable core with a separate target after Claude-specific forward validation:

```bash
python3 scripts/install_skill.py \
  --platform claude-code \
  --target ~/.claude/skills/orchestrate-multi-perspective-panel
```

## Use

Ask for the skill explicitly:

```text
$orchestrate-multi-perspective-panel help me design a public appointment-change flow.
```

Or ask naturally for a panel, independent perspectives, stakeholder lenses, adversarial review, or synthesized cross-functional judgment. Main will either explain why an ordinary session is sufficient or present the complete proposed slate for review.

## Platform and distribution status

| Target | Current status |
| --- | --- |
| Codex personal skill | Supported; current-runtime behavioral gate passed. |
| Claude Code skill | Structurally compatible; host-specific behavioral forward tests remain required. |
| GUI/API consumer | `meeting-plan` v1.1 and `panel-output` v1.2 contracts are ready; GUI remains separate roadmap work after the skills-only release. |
| OpenAI project-owned Skills API | OpenAI supports directory or zip uploads and immutable versions; this repository has not yet claimed an API-hosted release. |
| OpenAI universal plugin directory | Complex Enough v1.1.1 was approved and publisher-released on 2026-09-03. |
| Legacy `openai/skills` catalog | Deprecated by OpenAI in favor of plugins. |
| Plugin bundle | Packaged as v1.1.1; the local marketplace keeps `orchestrate-multi-perspective-panel`, while the official submission wrapper uses `complex-enough` and contains the same canonical skill bytes. |

The Skills API and a curated library or plugin marketplace are different distribution channels. Publishing this repository does not automatically place it in an official catalog.

### Official directory publication

OpenAI's current publication path accepts a **skills-only plugin**; an MCP server and custom UI are optional. The official flow is documented in [Build skills](https://developers.openai.com/plugins/build/skills), [Package your plugin](https://developers.openai.com/plugins/build/plugins), and [Submit plugins](https://developers.openai.com/plugins/deploy/submission).

The v1.1.1 skills-only submission was approved and published through the OpenAI Platform on 2026-09-03.

This repository retains the core skill, explicit trigger boundaries, supporting resources, public contracts, validation, behavioral evidence, metadata, changelog, Apache-2.0 license, reproducible skills-only packaging, final bilingual policy content, brand assets, static public website, and portal-oriented test cases. Build the local marketplace and submission ZIP with:

```bash
python3 scripts/package_plugin.py --replace
```

Local package discovery and selective-routing smoke checks are recorded in [submission/local-smoke-2026-08-31.json](submission/local-smoke-2026-08-31.json). The verified individual identity, public website and policy URLs, portal listing, availability, release notes, attestations, approval, and publisher-initiated publication are recorded in [submission/listing.json](submission/listing.json) and the [送審與發布紀錄](docs/official-plugin-submission-readiness.zh-TW.md).

The existing 26-case eval suite remains the product evidence base, and [submission/test-cases.json](submission/test-cases.json) preserves the five-positive/three-negative portal-oriented cases. Directory publication adds a supported distribution path; it does not replace those evaluations or prove downstream implementation outcomes. GUI development remains separate roadmap work and was not part of the published skills-only release.

For local development, do not leave an older same-name personal skill beside the plugin: host discovery may select either source. Update the personal installation to the same bytes with `scripts/install_skill.py --check`, or remove the duplicate before testing the packaged plugin.

## Public contracts and privacy

`meeting-plan` v1.1 records the editable role proposal, complexity profile, copy-on-write adjustments and imports, coverage, warnings, and frozen revision. `panel-output` v1.2 records the closed-round result, role/risk provenance, evidence, adjudication, degradation, gate, and summary. Legacy same-major inputs remain supported as documented.

Both contracts exclude hidden chain-of-thought, private scratch work, raw internal messages, and panelist transcripts. Normal results also exclude raw imported role prompts. See [meeting-plan contract](references/meeting-plan-contract.md) and [panel-output contract](references/panel-output-contract.md).

## Current validation evidence

The primary public result keeps all six selective plan-only tasks: `+0.222/5`, or about `5.0%` relative to Control, with Treatment scoring higher in 5 of 6 tasks. The batch deliberately included B1, a simple, single-actor and reversible negative-applicability case, and did not remove its `-0.167` result. Within the same batch, the higher meeting-value B4–B6 cases averaged `+0.403/5`, compared with `+0.146/5` for B2–B3—about `2.8x` the observed score-delta magnitude. This is descriptive scenario segmentation, not a claim that quality became 2.8 times higher.

A separate focused three-task compact-panel comparison improved `+0.514/5` (about `12.5%` relative to its Control; 3 of 3 tasks). These are directional planning results, not a universal outcome guarantee. See the [concise quality evidence summary](docs/evaluations/complex-enough-quality-evidence-summary.zh-TW.md) for calculation boundaries and publication-safe wording.

| Host | Result |
| --- | --- |
| Codex | `GO`: 26/26 isolated cases, 59 public turns, and 120/120 assertions passed by three fresh blind public-output graders. |
| Claude Code | Structural compatibility only; no host behavioral `GO` is claimed. |

The current scorecard is [evals/results/codex-2026-08-31.json](evals/results/codex-2026-08-31.json). Cases use neutral fixtures and fresh contexts; assertions, future turns, prior outputs, and intended fixes are not exposed to evaluated agents. Versioned artifacts contain public Main-session responses only, never raw panelist reports or private reasoning. See [evals/README.md](evals/README.md).

## Develop and validate

Run the Skill Creator structural validator:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

Run repository, schema compatibility, semantic, metadata, and eval-coverage checks:

```bash
python3 scripts/validate_repo.py
```

Validate public meeting artifacts directly:

```bash
python3 scripts/validate_meeting_plan.py path/to/meeting-plan.json
python3 scripts/validate_panel_output.py path/to/panel-output.json
python3 scripts/validate_meeting_bundle.py path/to/meeting-plan.json path/to/panel-output.json
```

Before contributing, preserve the public `1.x` compatibility contract, keep runtime files separate from maintainer/eval material, use neutral fresh-context forward tests, and run both release validators. See [CHANGELOG.md](CHANGELOG.md) for version history.

## Repository map

```text
SKILL.md                              Portable runtime workflow and routing
agents/openai.yaml                    Codex skill UI metadata
adapters/                             Host capability and execution mappings
references/                           Runtime protocols and public contracts
schemas/                              Versioned meeting-plan and panel-output schemas
scripts/                              Validators, eval renderer, and safe installer
packaging/                            Canonical manifest and packaged listing images
brand/                                Canonical SVG logo sources and usage guidance
site/                                 Bilingual static website and public policy pages
submission/                           Portal listing, tests, policies, and readiness records
tests/                                Contract, compatibility, and semantic tests
evals/                                Neutral cases and versioned public evidence
docs/                                 Design decisions and evaluation reports
```

The installer copies only the runtime files. Repository documentation, tests, and evaluation material are not included in the installed skill manifest.

## Design and evaluation documents

- [Complex Enough 品質成效摘要](docs/evaluations/complex-enough-quality-evidence-summary.zh-TW.md)
- [多視角編排邏輯現況評估與發展建議](docs/current-multi-perspective-logic-assessment.zh-TW.md)
- [老闆召集式多視角會議核心設計](docs/boss-led-meeting-core-design.zh-TW.md)
- [Meeting core Plan-only 六案盲評](docs/evaluations/meeting-core-plan-only-batch6.zh-TW.md)
- [Meeting core 使用者驗證 Plan Pilot](docs/evaluations/meeting-core-user-validated-plan-pilot.zh-TW.md)
- [Meeting core 規劃品質對照評估](docs/evaluations/meeting-core-quality-comparison.zh-TW.md) ([English](docs/evaluations/meeting-core-quality-comparison.md))
- [Meeting core 3–4 人 compact panel 品質評估](docs/evaluations/meeting-core-compact-panel-comparison.zh-TW.md)
- [Meeting core 後續控制實驗](docs/evaluations/meeting-core-follow-up-experiments.zh-TW.md)
- [OpenAI 官方 Plugin 送審準備紀錄](docs/official-plugin-submission-readiness.zh-TW.md)
- [GitHub Pages 與 DNS 發布計畫](docs/github-pages-and-dns-plan.zh-TW.md)

## License

Copyright 2026 [Huan Min Wei](https://complexenough.com/en/) and contributors.

Licensed under Apache-2.0. See [LICENSE](LICENSE).
