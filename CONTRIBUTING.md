# Contributing

Contributions that improve the skill's meeting selection, role definition, evidence handling, portability, contracts, or validation are welcome.

## Before opening a change

- Keep the root `SKILL.md` and its runtime manifest as the canonical source. Do not commit generated files under `build/`.
- Preserve the public `1.x` contract. Removing or renaming fields or enum values requires a major version; additive fields or enum values require a minor schema version and compatibility tests.
- Keep public output auditable without adding chain-of-thought, private scratch work, raw internal transcripts, or private panelist reports.
- Use neutral fixtures and fresh contexts for behavioral tests. Do not expose assertions, intended fixes, future turns, or prior outputs to evaluated agents.
- Keep unrelated changes out of the pull request.

## Validate locally

Install development dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

Run the structural and repository release gates:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
python3 scripts/validate_repo.py
```

Build the skills-only plugin and validate the generated plugin when the Plugin Creator skill is available:

```bash
python3 scripts/package_plugin.py --replace
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  build/marketplace/plugins/orchestrate-multi-perspective-panel
```

Describe the user-visible effect, tests performed, compatibility impact, and any remaining host-specific limitation in the pull request.
