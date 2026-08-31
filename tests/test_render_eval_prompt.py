from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_eval_prompt import render_conversation, render_prompt  # noqa: E402


class RenderEvalPromptTest(unittest.TestCase):
    def test_negative_trigger_is_natural_user_request_without_discovery_priming(self) -> None:
        case = {
            "tags": ["trigger", "negative"],
            "request": "Review a tiny function.",
            "fixtures": [],
        }
        rendered = render_prompt(case, "codex", None)
        self.assertEqual(rendered, "User request:\nReview a tiny function.")
        self.assertNotIn("orchestrate-multi-perspective-panel", rendered)
        self.assertNotIn("Apply only the Agent Skill", rendered)
        self.assertNotIn("discovery", rendered.lower())
        self.assertNotIn("skill", rendered.lower())
        self.assertNotIn("codex", rendered.lower())

    def test_trigger_case_rejects_explicit_skill_path(self) -> None:
        case = {"tags": ["trigger"], "request": "Use independent perspectives.", "fixtures": []}
        with self.assertRaisesRegex(ValueError, "without --skill-path"):
            render_prompt(case, "codex", Path("/tmp/skill"))

    def test_non_trigger_case_requires_skill_path(self) -> None:
        case = {"tags": ["review"], "request": "Review it.", "fixtures": []}
        with self.assertRaisesRegex(ValueError, "require --skill-path"):
            render_prompt(case, "claude-code", None)

    def test_non_trigger_prompt_is_host_neutral_and_scoped(self) -> None:
        case = {"tags": ["design"], "request": "Design it.", "fixtures": []}
        rendered = render_prompt(case, "claude-code", Path("/tmp/portable-skill"))
        self.assertIn("claude-code behavioral evaluation", rendered)
        self.assertIn("/tmp/portable-skill", rendered)
        self.assertNotIn("Use the Codex skill", rendered)

    def test_multi_turn_conversation_keeps_followups_separate(self) -> None:
        case = {
            "tags": ["meeting"],
            "request": "Generate the meeting roles.",
            "fixtures": [],
            "followups": [
                "Edit the operations role and show the new slate.",
                "Use the current slate and start.",
            ],
        }
        turns = render_conversation(case, "codex", Path("/tmp/portable-skill"))
        self.assertEqual(len(turns), 3)
        self.assertIn("Generate the meeting roles", turns[0])
        self.assertEqual(turns[1], case["followups"][0])
        self.assertNotIn(case["followups"][1], turns[0])

    def test_followups_must_be_nonempty_strings(self) -> None:
        case = {
            "tags": ["meeting"],
            "request": "Generate roles.",
            "fixtures": [],
            "followups": [""],
        }
        with self.assertRaisesRegex(ValueError, "followups"):
            render_conversation(case, "codex", Path("/tmp/portable-skill"))

    def test_full_cycle_resolves_product_gate_before_confirming_review_slate(self) -> None:
        suite = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        case = next(
            item for item in suite["cases"] if item["id"] == "full-cycle-reselect-lenses"
        )

        self.assertEqual(len(case["followups"]), 5)
        self.assertIn("choose C3-A", case["followups"][-2])
        self.assertIn("Generate the fresh readiness-review role slate", case["followups"][-2])
        self.assertIn("final review stage", case["followups"][-1])


if __name__ == "__main__":
    unittest.main()
