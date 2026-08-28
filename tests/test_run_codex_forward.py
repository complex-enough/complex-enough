from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))

from run_codex_forward import (  # noqa: E402
    ForwardRunError,
    initial_command,
    parse_jsonl_events,
    resume_command,
    select_cases,
    validate_public_archive,
    write_public_archive,
)


class CodexForwardRunnerTest(unittest.TestCase):
    def test_jsonl_parser_keeps_only_operational_metadata(self) -> None:
        stream = "\n".join(
            [
                json.dumps({"type": "thread.started", "thread_id": "thread-123"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {"type": "agent_message", "text": "private raw report"},
                    }
                ),
                json.dumps({"type": "turn.completed"}),
            ]
        )
        thread_id, event_types, diagnostic = parse_jsonl_events(stream)
        self.assertEqual(thread_id, "thread-123")
        self.assertEqual(
            event_types,
            ("thread.started", "item.completed", "turn.completed"),
        )
        self.assertEqual(diagnostic, "")

    def test_commands_keep_future_followups_out_of_initial_turn(self) -> None:
        initial = initial_command(
            codex_bin="codex",
            workspace=Path("/tmp/work"),
            output_file=Path("/tmp/turn0"),
            prompt="initial neutral request",
        )
        followup = resume_command(
            codex_bin="codex",
            thread_id="thread-123",
            output_file=Path("/tmp/turn1"),
            prompt="confirm current slate",
        )
        self.assertIn("initial neutral request", initial)
        self.assertNotIn("confirm current slate", initial)
        self.assertIn("confirm current slate", followup)
        self.assertIn("thread-123", followup)
        self.assertIn("read-only", initial)

    def test_select_cases_preserves_suite_or_requested_order(self) -> None:
        cases = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
        self.assertEqual(
            [case["id"] for case in select_cases(cases, [], "b")],
            ["b", "c"],
        )
        self.assertEqual(
            [case["id"] for case in select_cases(cases, ["c", "a"], None)],
            ["c", "a"],
        )
        with self.assertRaisesRegex(ForwardRunError, "unknown case"):
            select_cases(cases, ["missing"], None)

    def test_public_archive_is_exact_and_refuses_private_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "case.json"
            outputs = ["proposal final\n", "synthesis final\n"]
            write_public_archive(archive, "case", outputs)
            payload = json.loads(archive.read_text(encoding="utf-8"))
            self.assertEqual(payload["assistant_outputs"], outputs)
            validate_public_archive(archive, "case", 2)

            private_archive = Path(directory) / "private.json"
            private_archive.write_text(
                json.dumps(
                    {
                        "case_id": "private",
                        "assistant_outputs": ["chain_of_thought: no"],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ForwardRunError, "private-output"):
                validate_public_archive(private_archive, "private", 1)

    def test_public_archive_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "case.json"
            write_public_archive(archive, "case", ["first final"])
            with self.assertRaisesRegex(ForwardRunError, "overwrite"):
                write_public_archive(archive, "case", ["second final"])


if __name__ == "__main__":
    unittest.main()
