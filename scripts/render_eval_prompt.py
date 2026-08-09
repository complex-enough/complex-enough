#!/usr/bin/env python3
"""Render an eval prompt without leaking assertions or expected answers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def render_prompt(case: dict, host: str, skill_path: Path | None) -> str:
    is_trigger_case = "trigger" in case["tags"]
    sections: list[str] = []
    if is_trigger_case:
        if skill_path is not None:
            raise ValueError("trigger cases must use installed discovery without --skill-path")
    else:
        if skill_path is None:
            raise ValueError("non-trigger cases require --skill-path")
        sections.append(
            f"Run this as a {host} behavioral evaluation. Apply only the Agent Skill runtime at "
            f"{skill_path.resolve()} and the supplied fixtures as task authority. Do not inspect eval "
            "assertions, unrelated repositories, or prior run results. Do not modify files or external systems."
        )

    sections.append("User request:\n" + case["request"])
    if case["fixtures"]:
        fixture_sections = ["Supplied fixtures:"]
        for relative in case["fixtures"]:
            fixture_path = (REPO_ROOT / "evals" / relative).resolve()
            fixture_sections.append(
                f"--- {Path(relative).name} ---\n\n{fixture_path.read_text(encoding='utf-8').rstrip()}"
            )
        sections.append("\n\n".join(fixture_sections))
    if not is_trigger_case:
        sections.append("Return exactly the response you would give the user.")
    return "\n\n".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("--host", choices=["codex", "claude-code"], required=True)
    parser.add_argument("--skill-path", type=Path)
    args = parser.parse_args()

    suite = json.loads((REPO_ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    case = next((entry for entry in suite["cases"] if entry["id"] == args.case_id), None)
    if case is None:
        parser.error(f"unknown case_id: {args.case_id}")

    try:
        print(render_prompt(case, args.host, args.skill_path))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
