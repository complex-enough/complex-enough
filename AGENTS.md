# Repository instructions

- Treat this repository as the source of truth for the productized skill. Do not modify unrelated repositories, especially `senova-lumina`, from work scoped here.
- Keep portable runtime instructions in `SKILL.md`, `adapters/`, `references/`, and `schemas/`; keep Codex UI metadata in `agents/`. Keep maintainer/eval material outside the installed runtime manifest.
- Preserve the `1.x` public contract: do not remove or rename fields or enum values without a major schema version. Additive fields/enums require a minor schema version and compatibility tests.
- Keep panel outputs public and auditable. Never add hidden chain-of-thought, raw internal transcripts, or private scratch-work fields.
- Use neutral fixtures and fresh contexts for forward tests. Do not expose eval assertions, prior outputs, or intended fixes to evaluated agents.
- Inspect branch, status, diff, and existing work before editing. Preserve unrelated dirty changes.
- Run Skill Creator validation and `python3 scripts/validate_repo.py` before release or global installation.
- Install to a host skill directory only after the repository worktree passes validation and that host's behavioral status is stated honestly. Do not configure a remote, change visibility, choose a license, or push unless explicitly authorized.
