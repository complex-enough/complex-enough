from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_eval_prompt import render_prompt  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
