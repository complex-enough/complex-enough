from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_repo import (  # noqa: E402
    eval_suite_revision,
    validate_historical_eval_result,
    validate_eval_result,
    validate_release_gate,
)
from render_eval_prompt import render_conversation  # noqa: E402


class EvalResultValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads((ROOT / "schemas" / "eval-result.schema.json").read_text())
        cls.revision = "sha256:" + "a" * 64
        cls.suite = {
            "suite_version": "1.0.0",
            "cases": [{
                "id": "case-1",
                "mode": "review",
                "request": "Review the supplied artifact.",
                "tags": [],
                "fixtures": [],
                "capability": "subagents_available",
                "assertions": ["assertion-1"],
            }],
        }

    def payload(self) -> dict:
        return {
            "suite_version": "1.0.0",
            "suite_revision": eval_suite_revision(self.suite),
            "skill_revision": self.revision,
            "executed_at": "2026-08-09T12:00:00+08:00",
            "verified_at": "2026-08-09T13:00:00+08:00",
            "environment": {
                "host": "codex",
                "forward_runner": "fresh isolated contexts",
                "failure_injection": "none",
            },
            "cases": [{
                "case_id": "case-1",
                "execution": "forward",
                "status": "pass",
                "artifact_path": None,
                "artifact_sha256": None,
                "run_id": None,
                "assertions": [{
                    "assertion": "assertion-1",
                    "status": "pass",
                    "evidence": "observable output",
                }],
                "notes": "",
            }],
            "gate": "GO",
        }

    def validate_payload(
        self,
        filename: str,
        payload: dict,
        suite: dict | None = None,
        capture_artifacts: bool = True,
        artifact_mutator: Callable[[dict], None] | None = None,
        tamper_after_hash: bool = False,
    ) -> None:
        suite = suite or self.suite
        with tempfile.TemporaryDirectory() as directory:
            eval_root = Path(directory)
            path = eval_root / "results" / filename
            path.parent.mkdir()
            artifact_root = eval_root / "artifacts"
            artifact_root.mkdir()
            case_definitions = {case["id"]: case for case in suite["cases"]}
            host = payload["environment"]["host"]
            if capture_artifacts and host in {"codex", "claude-code"}:
                for result_case in payload["cases"]:
                    if result_case["status"] != "pass":
                        continue
                    case = case_definitions[result_case["case_id"]]
                    run_id = f"test-{result_case['case_id']}"
                    skill_path = ROOT if "trigger" not in case["tags"] else None
                    prompt = json.dumps(
                        render_conversation(case, host, skill_path),
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    artifact = {
                        "artifact_version": "1.0",
                        "case_id": result_case["case_id"],
                        "host": host,
                        "run_id": run_id,
                        "executed_at": payload["executed_at"],
                        "execution": result_case["execution"],
                        "runtime_revision": payload["skill_revision"],
                        "suite_revision": payload["suite_revision"],
                        "skill_path": str(skill_path) if skill_path else None,
                        "prompt_sha256": "sha256:"
                        + hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                        "output": "Captured public moderator response for test validation.",
                    }
                    if artifact_mutator:
                        artifact_mutator(artifact)
                    artifact_path = artifact_root / f"{result_case['case_id']}.json"
                    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
                    result_case["artifact_path"] = f"artifacts/{artifact_path.name}"
                    result_case["artifact_sha256"] = "sha256:" + hashlib.sha256(
                        artifact_path.read_bytes()
                    ).hexdigest()
                    result_case["run_id"] = run_id
                    if tamper_after_hash:
                        artifact_path.write_text(
                            artifact_path.read_text(encoding="utf-8") + "\n",
                            encoding="utf-8",
                        )
            path.write_text(json.dumps(payload), encoding="utf-8")
            validate_eval_result(path, suite, self.schema, {"codex": self.revision})

    def test_valid_codex_result_is_bound_to_filename_suite_and_revision(self) -> None:
        self.validate_payload("codex-2026-08-09.json", self.payload())

    def test_captured_artifact_digest_and_prompt_are_bound(self) -> None:
        with self.assertRaisesRegex(AssertionError, "artifact digest mismatch"):
            self.validate_payload(
                "codex-2026-08-09.json",
                self.payload(),
                tamper_after_hash=True,
            )

        with self.assertRaisesRegex(AssertionError, "prompt digest mismatch"):
            self.validate_payload(
                "codex-2026-08-09.json",
                self.payload(),
                artifact_mutator=lambda artifact: artifact.update(
                    {"prompt_sha256": "sha256:" + "b" * 64}
                ),
            )

    def test_captured_artifact_cannot_postdate_scorecard_execution(self) -> None:
        with self.assertRaisesRegex(AssertionError, "after its enclosing scorecard"):
            self.validate_payload(
                "codex-2026-08-09.json",
                self.payload(),
                artifact_mutator=lambda artifact: artifact.update(
                    {"executed_at": "2026-08-09T14:00:00+08:00"}
                ),
            )

    def test_private_output_marker_scan_uses_exact_identifier_boundaries(self) -> None:
        self.validate_payload(
            "codex-2026-08-09.json",
            self.payload(),
            artifact_mutator=lambda artifact: artifact.update(
                {
                    "output": (
                        "The import rejected `PRIVATE_REASONING_REQUEST` and "
                        "did not expose private reasoning."
                    )
                }
            ),
        )

        with self.assertRaisesRegex(AssertionError, "prohibited private-output marker"):
            self.validate_payload(
                "codex-2026-08-09.json",
                self.payload(),
                artifact_mutator=lambda artifact: artifact.update(
                    {"output": "Leaked field: `private_reasoning`."}
                ),
            )

    def test_codex_filename_cannot_claim_static_host(self) -> None:
        payload = self.payload()
        payload["environment"]["host"] = "static-only"
        with self.assertRaisesRegex(AssertionError, "wrong host"):
            self.validate_payload("codex-2026-08-09.json", payload)

    def test_static_only_result_cannot_claim_go(self) -> None:
        payload = self.payload()
        payload["environment"]["host"] = "static-only"
        with self.assertRaisesRegex(AssertionError, "cannot claim GO"):
            self.validate_payload("static-only-2026-08-09.json", payload)

    def test_stale_suite_or_runtime_revision_is_rejected(self) -> None:
        for field, value, message in (
            ("suite_version", "0.9.0", "suite version"),
            ("skill_revision", "sha256:" + "b" * 64, "runtime revision"),
        ):
            with self.subTest(field=field):
                payload = self.payload()
                payload[field] = value
                with self.assertRaisesRegex(AssertionError, message):
                    self.validate_payload("codex-2026-08-09.json", payload)

        payload = self.payload()
        payload["suite_revision"] = "sha256:" + "b" * 64
        with self.assertRaisesRegex(AssertionError, "suite revision"):
            self.validate_payload("codex-2026-08-09.json", payload)

    def test_suite_revision_binds_requests_modes_capabilities_and_fixture_bytes(self) -> None:
        baseline = self.payload()
        for field, value in (
            ("request", "A changed request."),
            ("mode", "design"),
            ("capability", "panelist_timeout"),
            ("fixtures", ["fixtures/changed.md"]),
        ):
            with self.subTest(field=field):
                suite = copy.deepcopy(self.suite)
                suite["cases"][0][field] = value
                with self.assertRaisesRegex(AssertionError, "suite revision"):
                    self.validate_payload(
                        "codex-2026-08-09.json",
                        baseline,
                        suite,
                        capture_artifacts=False,
                    )

        suite = copy.deepcopy(self.suite)
        suite["cases"][0]["fixtures"] = ["fixtures/input.md"]
        with tempfile.TemporaryDirectory() as directory:
            fixture_root = Path(directory)
            fixture = fixture_root / "fixtures" / "input.md"
            fixture.parent.mkdir()
            fixture.write_text("original authority", encoding="utf-8")
            original = eval_suite_revision(suite, fixture_root)
            fixture.write_text("changed authority", encoding="utf-8")
            self.assertNotEqual(original, eval_suite_revision(suite, fixture_root))

    def test_timestamps_runner_and_evidence_are_not_vacuous(self) -> None:
        ancient = self.payload()
        ancient["executed_at"] = "2000-01-01T00:00:00+00:00"
        with self.assertRaisesRegex(AssertionError, "execution date"):
            self.validate_payload("codex-2026-08-09.json", ancient)

        reversed_times = self.payload()
        reversed_times["verified_at"] = "2026-08-09T11:00:00+08:00"
        with self.assertRaisesRegex(AssertionError, "verified before"):
            self.validate_payload("codex-2026-08-09.json", reversed_times)

        for mutate in ("runner", "evidence"):
            with self.subTest(mutate=mutate):
                payload = self.payload()
                if mutate == "runner":
                    payload["environment"]["forward_runner"] = ""
                else:
                    payload["cases"][0]["assertions"][0]["evidence"] = "x"
                with self.assertRaisesRegex(AssertionError, "invalid eval result"):
                    self.validate_payload("codex-2026-08-09.json", payload)

    def test_failure_injection_matches_failure_case_execution(self) -> None:
        suite = copy.deepcopy(self.suite)
        suite["cases"][0]["capability"] = "panelist_timeout"
        for execution in ("simulated_failure", "forward"):
            with self.subTest(execution=execution):
                payload = self.payload()
                payload["suite_revision"] = eval_suite_revision(suite)
                payload["cases"][0]["execution"] = execution
                payload["environment"]["failure_injection"] = "none"
                with self.assertRaisesRegex(AssertionError, "failure_injection"):
                    self.validate_payload("codex-2026-08-09.json", payload, suite)

    def test_empty_cases_are_rejected_by_schema(self) -> None:
        payload = self.payload()
        payload["cases"] = []
        with self.assertRaisesRegex(AssertionError, "invalid eval result"):
            self.validate_payload("codex-2026-08-09.json", payload)

    def test_go_cannot_use_static_execution_or_empty_evidence(self) -> None:
        static_payload = self.payload()
        static_payload["cases"][0]["execution"] = "static"
        with self.assertRaisesRegex(AssertionError, "non-behavioral execution"):
            self.validate_payload("codex-2026-08-09.json", static_payload)

        empty_evidence = self.payload()
        empty_evidence["cases"][0]["assertions"][0]["evidence"] = ""
        with self.assertRaisesRegex(AssertionError, "invalid eval result"):
            self.validate_payload("codex-2026-08-09.json", empty_evidence)

    def test_incomplete_behavioral_result_is_rejected(self) -> None:
        suite = copy.deepcopy(self.suite)
        suite["cases"].append({
            "id": "case-2",
            "mode": "review",
            "request": "Review another artifact.",
            "fixtures": [],
            "capability": "subagents_available",
            "assertions": ["assertion-2"],
        })
        payload = self.payload()
        payload["suite_revision"] = eval_suite_revision(suite)
        with self.assertRaisesRegex(AssertionError, "missing cases"):
            self.validate_payload("codex-2026-08-09.json", payload, suite)

    def test_required_release_scorecard_must_be_codex_go(self) -> None:
        for host in ("codex", "static-only"):
            with self.subTest(host=host), tempfile.TemporaryDirectory() as directory:
                payload = self.payload()
                payload["environment"]["host"] = host
                payload["cases"][0]["status"] = "fail"
                payload["cases"][0]["assertions"][0]["status"] = "fail"
                payload["gate"] = "NO_GO"
                path = Path(directory) / f"{host}-2026-08-09.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(AssertionError, "not GO"):
                    validate_release_gate(
                        path,
                        self.suite,
                        self.schema,
                        {"codex": self.revision},
                        eval_suite_revision(self.suite),
                    )

    def test_historical_scorecard_keeps_integrity_but_cannot_be_current(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            eval_root = Path(directory)
            results_root = eval_root / "results"
            artifacts_root = eval_root / "artifacts"
            results_root.mkdir()
            artifacts_root.mkdir()
            payload = self.payload()
            run_id = "historical-case-1"
            artifact = {
                "artifact_version": "1.0",
                "case_id": "case-1",
                "host": "codex",
                "run_id": run_id,
                "executed_at": payload["executed_at"],
                "execution": "forward",
                "runtime_revision": payload["skill_revision"],
                "suite_revision": payload["suite_revision"],
                "skill_path": None,
                "prompt_sha256": "sha256:" + "c" * 64,
                "output": "Archived public moderator output retained as historical evidence.",
            }
            artifact_path = artifacts_root / "case-1.json"
            artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
            payload["cases"][0]["artifact_path"] = "artifacts/case-1.json"
            payload["cases"][0]["artifact_sha256"] = "sha256:" + hashlib.sha256(
                artifact_path.read_bytes()
            ).hexdigest()
            payload["cases"][0]["run_id"] = run_id
            result_path = results_root / "codex-2026-08-09.json"
            result_path.write_text(json.dumps(payload), encoding="utf-8")

            validate_historical_eval_result(result_path, self.schema, "2.0.0")
            with self.assertRaisesRegex(AssertionError, "current suite version"):
                validate_release_gate(
                    result_path,
                    {**self.suite, "suite_version": "2.0.0"},
                    self.schema,
                    {"codex": self.revision},
                )

            artifact_path.write_text(
                artifact_path.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(AssertionError, "historical eval artifact digest mismatch"):
                validate_historical_eval_result(result_path, self.schema, "2.0.0")


if __name__ == "__main__":
    unittest.main()
