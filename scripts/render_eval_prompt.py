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


def render_conversation(
    case: dict, host: str, skill_path: Path | None
) -> list[str]:
    """Render the exact user turns without exposing assertions or evaluator notes."""

    initial = render_prompt(case, host, skill_path)
    followups = case.get("followups", [])
    if not isinstance(followups, list) or not all(
        isinstance(turn, str) and turn.strip() for turn in followups
    ):
        raise ValueError("case followups must be non-empty strings")
    return [initial, *followups]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case_id")
    parser.add_argument("--host", choices=["codex", "claude-code"], required=True)
    parser.add_argument("--skill-path", type=Path)
    parser.add_argument(
        "--turn",
        type=int,
        default=0,
        help="zero-based user turn to render",
    )
    parser.add_argument(
        "--conversation-json",
        action="store_true",
        help="render every user turn as a JSON array",
    )
    args = parser.parse_args()

    suite = json.loads((REPO_ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    case = next((entry for entry in suite["cases"] if entry["id"] == args.case_id), None)
    if case is None:
        parser.error(f"unknown case_id: {args.case_id}")

    try:
        turns = render_conversation(case, args.host, args.skill_path)
        if args.conversation_json:
            print(json.dumps(turns, ensure_ascii=False, indent=2))
        elif args.turn < 0 or args.turn >= len(turns):
            parser.error(
                f"turn {args.turn} is out of range for {len(turns)}-turn conversation"
            )
        else:
            print(turns[args.turn])
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
