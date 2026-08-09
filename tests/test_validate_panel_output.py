from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_panel_output import (  # noqa: E402
    semantic_errors,
    stable_enum_errors,
    validate,
)


class PanelOutputValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.v10_path = ROOT / "tests" / "fixtures" / "output-v1.0.json"
        self.v11_path = ROOT / "tests" / "fixtures" / "output-v1.1.json"
        self.v11 = json.loads(self.v11_path.read_text(encoding="utf-8"))
        self.schema = json.loads(
            (ROOT / "schemas" / "panel-output.schema.json").read_text(encoding="utf-8")
        )
        self.enum_lock = json.loads(
            (ROOT / "schemas" / "stable-enums.v1.json").read_text(encoding="utf-8")
        )

    def validate_payload(self, payload: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate(path)

    def full_cycle_payload(self) -> dict:
        payload = copy.deepcopy(self.v11)
        payload["run"]["mode"] = "full_cycle"
        payload["orchestration"] = {
            "execution": "waves",
            "degraded": False,
            "waves": [["P1"], ["P2"], ["P3"], ["P4"]],
            "notes": [],
        }
        perspective_template = copy.deepcopy(self.v11["perspectives"][1])
        payload["perspectives"] = []
        payload["items"] = []
        item_template = copy.deepcopy(self.v11["items"][0])
        for index, stage in enumerate(("ideate", "design", "converge", "review"), 1):
            perspective = copy.deepcopy(perspective_template)
            perspective.update(
                {
                    "perspective_id": f"P{index}",
                    "name": f"{stage.title()} perspective",
                    "lens": f"{stage} decision surface",
                    "selection_reason": f"Own the {stage} stage evidence",
                    "stage": stage,
                }
            )
            payload["perspectives"].append(perspective)

            item = copy.deepcopy(item_template)
            item.update(
                {
                    "item_id": f"I{index}",
                    "perspective_id": f"P{index}",
                    "stage": stage,
                    "kind": "idea",
                    "severity": None,
                    "statement": f"Public {stage} artifact.",
                }
            )
            payload["items"].append(item)
        payload["decisions"] = []
        payload["coverage"][0]["evidence_item_ids"] = ["I4"]
        payload["gate"]["unresolved_item_ids"] = []
        payload["gate"]["state"] = "revise"
        return payload

    def test_v10_compatibility_fixture_is_valid(self) -> None:
        self.assertEqual(validate(self.v10_path), [])

    def test_v11_fixture_is_valid(self) -> None:
        self.assertEqual(validate(self.v11_path), [])

    def test_duplicate_ids_are_rejected(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["perspectives"].append(copy.deepcopy(payload["perspectives"][1]))
        self.assertIn("duplicate perspective_id: P2", semantic_errors(payload))

    def test_unknown_item_reference_is_rejected(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["decisions"][0]["source_item_ids"] = ["I404"]
        self.assertIn(
            "decision D1 references unknown item I404",
            semantic_errors(payload),
        )

    def test_go_with_blocker_is_rejected_even_if_unresolved_list_is_cleared(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["gate"]["state"] = "go"
        payload["gate"]["unresolved_item_ids"] = []
        errors = semantic_errors(payload)
        self.assertIn("gate is go with blocker item I1", errors)

    def test_go_with_partial_critical_coverage_is_rejected(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["gate"]["state"] = "go"
        payload["gate"]["unresolved_item_ids"] = []
        payload["coverage"][0]["status"] = "partially_covered"
        errors = semantic_errors(payload)
        self.assertTrue(any("critical risk surface" in error for error in errors))

    def test_covered_requires_public_evidence(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["coverage"][0]["evidence_item_ids"] = []
        self.assertIn(
            "coverage 'refund posting authorization' is covered without evidence items",
            semantic_errors(payload),
        )
        self.assertTrue(
            any("is too short" in error for error in self.validate_payload(payload))
        )

        payload = copy.deepcopy(self.v11)
        payload["items"][0]["kind"] = "option"
        payload["items"][0]["severity"] = None
        payload["items"][0]["evidence"] = []
        self.assertIn(
            "coverage 'refund posting authorization' references item I1 without public evidence",
            self.validate_payload(payload),
        )

    def test_go_requires_evidence_backed_critical_coverage(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["gate"]["state"] = "go"
        payload["gate"]["unresolved_item_ids"] = []
        payload["coverage"][0]["evidence_item_ids"] = []
        self.assertIn(
            "gate is go without evidence-backed critical risk surface 'refund posting authorization'",
            semantic_errors(payload),
        )

    def test_go_rejects_vacuous_panel_items_and_coverage(self) -> None:
        base = copy.deepcopy(self.v11)
        base["gate"]["state"] = "go"
        base["gate"]["unresolved_item_ids"] = []

        for field, expected in (
            ("perspectives", "gate is go without any perspective"),
            ("items", "gate is go without any public item"),
            ("coverage", "gate is go without declared risk-surface coverage"),
        ):
            payload = copy.deepcopy(base)
            payload[field] = []
            self.assertIn(expected, semantic_errors(payload))
            self.assertIn(expected, self.validate_payload(payload), field)

    def test_non_go_v10_empty_collections_remain_compatible(self) -> None:
        payload = json.loads(self.v10_path.read_text(encoding="utf-8"))
        payload["perspectives"] = []
        payload["items"] = []
        self.assertEqual(self.validate_payload(payload), [])

    def test_legacy_v10_go_remains_valid_without_v11_coverage(self) -> None:
        payload = json.loads(self.v10_path.read_text(encoding="utf-8"))
        payload["gate"].update(
            {
                "state": "go",
                "rationale": "Legacy producer reports readiness.",
                "unresolved_item_ids": [],
            }
        )
        self.assertEqual(self.validate_payload(payload), [])

    def test_v11_shape_cannot_be_down_labeled_as_v10(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["schema_version"] = "1.0"
        errors = self.validate_payload(payload)
        self.assertTrue(any("False schema does not allow" in error for error in errors))

    def test_evidence_backed_covered_surface_is_valid(self) -> None:
        errors = semantic_errors(self.v11)
        self.assertFalse(any("coverage" in error or "evidence-backed" in error for error in errors))

    def test_ideate_risk_must_not_use_severity(self) -> None:
        payload = json.loads(self.v10_path.read_text(encoding="utf-8"))
        payload["items"][0]["kind"] = "risk"
        payload["items"][0]["severity"] = "high"
        payload["items"][0]["evidence"] = [
            {"source": "user request", "locator": None, "observation": "Assumption is untested."}
        ]
        self.assertIn("ideate risk I1 must not use severity", semantic_errors(payload))

    def test_ideate_risk_with_null_severity_is_schema_valid(self) -> None:
        payload = json.loads(self.v10_path.read_text(encoding="utf-8"))
        payload["items"][0]["kind"] = "risk"
        payload["items"][0]["evidence"] = [
            {"source": "user request", "locator": None, "observation": "Assumption is untested."}
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            errors = validate(path)
        self.assertEqual(errors, [])

    def test_private_reasoning_field_is_rejected(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["summary"]["chain_of_thought"] = "private trace"
        errors = semantic_errors(payload)
        self.assertTrue(any("prohibited private-reasoning field" in error for error in errors))

    def test_v11_requires_orchestration_and_coverage(self) -> None:
        payload = copy.deepcopy(self.v11)
        del payload["orchestration"]
        del payload["coverage"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            errors = validate(path)
        self.assertTrue(any("orchestration" in error for error in errors))
        self.assertTrue(any("coverage" in error for error in errors))

    def test_full_cycle_requires_stage_provenance(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["run"]["mode"] = "full_cycle"
        del payload["items"][0]["stage"]
        errors = semantic_errors(payload)
        self.assertIn("full_cycle item I1 has no stage", errors)

    def test_item_stage_must_match_owning_perspective(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["items"][0]["stage"] = "design"
        self.assertIn(
            "item I1 stage design does not match perspective P2 stage review",
            semantic_errors(payload),
        )

    def test_full_cycle_decision_requires_same_stage_source(self) -> None:
        payload = self.full_cycle_payload()
        payload["decisions"] = [
            {
                "decision_id": "D1",
                "source_item_ids": ["I1"],
                "stage": "review",
                "status": "accepted",
                "rationale": "Use an earlier idea as the only purported review evidence.",
                "resulting_change": "Proceed.",
            }
        ]
        self.assertIn(
            "full_cycle decision D1 stage review has no same-stage source item from a completed perspective",
            semantic_errors(payload),
        )

        payload["decisions"][0]["source_item_ids"] = []
        self.assertIn(
            "full_cycle decision D1 stage review has no same-stage source item from a completed perspective",
            semantic_errors(payload),
        )

    def test_full_cycle_decision_cannot_source_only_failed_perspective(self) -> None:
        payload = self.full_cycle_payload()
        payload["perspectives"][1].update(
            {
                "status": "failed",
                "failure": {
                    "code": "timeout",
                    "message": "Design attempt timed out after partial material.",
                    "retry_count": 1,
                },
            }
        )
        completed_design = copy.deepcopy(payload["perspectives"][1])
        completed_design.update(
            {
                "perspective_id": "P5",
                "name": "Completed design perspective",
                "status": "completed",
                "failure": None,
            }
        )
        payload["perspectives"].insert(2, completed_design)
        payload["orchestration"].update(
            {
                "degraded": True,
                "waves": [["P1"], ["P2"], ["P5"], ["P3"], ["P4"]],
            }
        )
        payload["decisions"] = [
            {
                "decision_id": "D1",
                "source_item_ids": ["I2"],
                "stage": "design",
                "status": "accepted",
                "rationale": "Accept partial material from the failed attempt.",
                "resulting_change": "Proceed.",
            }
        ]
        self.assertIn(
            "full_cycle decision D1 stage design has no same-stage source item from a completed perspective",
            semantic_errors(payload),
        )

    def test_full_cycle_proves_all_four_stages_in_order(self) -> None:
        payload = self.full_cycle_payload()
        self.assertEqual(self.validate_payload(payload), [])

        missing = copy.deepcopy(payload)
        missing["perspectives"][1]["stage"] = "ideate"
        self.assertTrue(
            any(
                "no completed perspective for stages: design" in error
                for error in semantic_errors(missing)
            )
        )

        missing_item = copy.deepcopy(payload)
        missing_item["items"][1]["stage"] = "ideate"
        self.assertTrue(
            any(
                "no public item for stages: design" in error
                for error in semantic_errors(missing_item)
            )
        )

        out_of_order = copy.deepcopy(payload)
        out_of_order["perspectives"][1], out_of_order["perspectives"][2] = (
            out_of_order["perspectives"][2],
            out_of_order["perspectives"][1],
        )
        self.assertTrue(
            any(
                "full_cycle perspective stages are out of order" in error
                for error in semantic_errors(out_of_order)
            )
        )

        mixed_wave = copy.deepcopy(payload)
        mixed_wave["orchestration"]["waves"] = [["P1", "P2"], ["P3"], ["P4"]]
        self.assertTrue(
            any(
                "full_cycle orchestration wave 1 mixes stages" in error
                for error in semantic_errors(mixed_wave)
            )
        )

    def test_single_session_fallback_is_degraded_main_session_only(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["orchestration"].update(
            {"execution": "single_session_fallback", "degraded": True, "waves": []}
        )
        for perspective in payload["perspectives"]:
            perspective["executor"] = "main_session"
        self.assertEqual(semantic_errors(payload), [])

        not_degraded = copy.deepcopy(payload)
        not_degraded["orchestration"]["degraded"] = False
        self.assertIn(
            "orchestration execution single_session_fallback must be degraded",
            semantic_errors(not_degraded),
        )

        subagent = copy.deepcopy(payload)
        subagent["perspectives"][0]["executor"] = "subagent"
        self.assertIn(
            "single_session_fallback requires every perspective executor to be main_session",
            semantic_errors(subagent),
        )

    def test_mixed_execution_requires_both_executors_and_degradation(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["orchestration"].update(
            {"execution": "mixed", "degraded": True, "waves": [["P1"]]}
        )
        payload["perspectives"][1]["executor"] = "main_session"
        self.assertEqual(semantic_errors(payload), [])

        only_subagents = copy.deepcopy(self.v11)
        only_subagents["orchestration"]["execution"] = "mixed"
        self.assertIn(
            "mixed execution requires subagent and main_session perspectives",
            semantic_errors(only_subagents),
        )

        payload["orchestration"]["degraded"] = False
        self.assertIn(
            "orchestration execution mixed must be degraded",
            semantic_errors(payload),
        )

    def test_v11_perspective_requires_executor(self) -> None:
        payload = copy.deepcopy(self.v11)
        del payload["perspectives"][0]["executor"]
        self.assertIn("schema 1.1 perspective P1 has no executor", semantic_errors(payload))
        self.assertTrue(
            any("executor" in error for error in self.validate_payload(payload))
        )

    def test_waves_reference_each_subagent_exactly_once(self) -> None:
        self.assertEqual(semantic_errors(self.v11), [])

        unknown = copy.deepcopy(self.v11)
        unknown["orchestration"]["waves"][1] = ["P404"]
        unknown_errors = semantic_errors(unknown)
        self.assertIn(
            "orchestration wave references unknown perspective P404", unknown_errors
        )
        self.assertIn(
            "subagent perspective P2 is missing from orchestration waves", unknown_errors
        )

        duplicate = copy.deepcopy(self.v11)
        duplicate["orchestration"]["waves"][1].insert(0, "P1")
        self.assertIn(
            "perspective P1 appears in multiple orchestration waves",
            semantic_errors(duplicate),
        )

        main_in_wave = copy.deepcopy(self.v11)
        main_in_wave["orchestration"].update(
            {"execution": "mixed", "waves": [["P1", "P2"]]}
        )
        main_in_wave["perspectives"][1]["executor"] = "main_session"
        self.assertIn(
            "orchestration wave includes non-subagent perspective P2",
            semantic_errors(main_in_wave),
        )

    def test_execution_mode_matches_wave_cardinality_and_failure_state(self) -> None:
        one_wave = copy.deepcopy(self.v11)
        one_wave["perspectives"][0].update(
            {
                "status": "completed",
                "failure": None,
                "replacement_perspective_id": None,
            }
        )
        one_wave["orchestration"]["degraded"] = False
        one_wave["orchestration"].update(
            {"execution": "subagents", "waves": [["P1", "P2"]]}
        )
        self.assertEqual(semantic_errors(one_wave), [])

        two_subagent_waves = copy.deepcopy(one_wave)
        two_subagent_waves["orchestration"]["waves"] = [["P1"], ["P2"]]
        self.assertIn(
            "subagents execution requires exactly one wave",
            semantic_errors(two_subagent_waves),
        )

        one_declared_wave = copy.deepcopy(self.v11)
        one_declared_wave["orchestration"]["waves"] = [["P1", "P2"]]
        self.assertIn(
            "waves execution requires at least two waves",
            semantic_errors(one_declared_wave),
        )

        not_degraded = copy.deepcopy(self.v11)
        not_degraded["orchestration"]["degraded"] = False
        self.assertIn(
            "orchestration with failed or replaced perspectives must be degraded",
            semantic_errors(not_degraded),
        )

    def test_replacement_status_model_and_graph_are_unambiguous(self) -> None:
        self.assertEqual(semantic_errors(self.v11), [])

        failed_with_replacement = copy.deepcopy(self.v11)
        failed_with_replacement["perspectives"][0]["status"] = "failed"
        self.assertIn(
            "perspective P1 is failed but has a replacement",
            semantic_errors(failed_with_replacement),
        )
        self.assertTrue(
            any(
                "is not of type 'null'" in error
                for error in self.validate_payload(failed_with_replacement)
            )
        )

        self_link = copy.deepcopy(self.v11)
        self_link["perspectives"][0]["replacement_perspective_id"] = "P1"
        self.assertIn("perspective P1 cannot replace itself", semantic_errors(self_link))

        cycle = copy.deepcopy(self.v11)
        cycle["perspectives"][1].update(
            {
                "status": "replaced",
                "failure": {
                    "code": "timeout",
                    "message": "Replacement also timed out",
                    "retry_count": 1,
                },
                "replacement_perspective_id": "P1",
            }
        )
        self.assertTrue(
            any("replacement cycle: P1 -> P2 -> P1" in error for error in semantic_errors(cycle))
        )

        changed_lens = copy.deepcopy(self.v11)
        changed_lens["perspectives"][1]["lens"] = "A different question"
        self.assertIn(
            "replacement P2 does not preserve lens from P1",
            semantic_errors(changed_lens),
        )

        changed_stage = copy.deepcopy(self.v11)
        changed_stage["perspectives"][1]["stage"] = "design"
        self.assertIn(
            "replacement P2 does not preserve stage from P1",
            semantic_errors(changed_stage),
        )

        shared_target = copy.deepcopy(self.v11)
        extra_source = copy.deepcopy(shared_target["perspectives"][0])
        extra_source["perspective_id"] = "P3"
        shared_target["perspectives"].append(extra_source)
        shared_target["orchestration"]["waves"][0].append("P3")
        self.assertIn(
            "replacement perspective P2 has multiple sources: ['P1', 'P3']",
            semantic_errors(shared_target),
        )

    def test_replacement_runs_later_and_failed_attempt_cannot_back_coverage(self) -> None:
        earlier = copy.deepcopy(self.v11)
        earlier["orchestration"]["waves"] = [["P2"], ["P1"]]
        self.assertIn(
            "replacement perspective P2 must run in a later wave than P1",
            semantic_errors(earlier),
        )

        failed = copy.deepcopy(self.v11)
        failed["perspectives"][1].update(
            {
                "status": "failed",
                "failure": {
                    "code": "timeout",
                    "message": "Replacement also timed out",
                    "retry_count": 1,
                },
            }
        )
        failed["gate"]["state"] = "go"
        failed["gate"]["unresolved_item_ids"] = []
        self.assertIn(
            "coverage 'refund posting authorization' references item I1 from non-completed perspective P2",
            semantic_errors(failed),
        )

    def test_cross_executor_replacement_must_appear_later(self) -> None:
        payload = copy.deepcopy(self.v11)
        payload["perspectives"][1]["executor"] = "main_session"
        payload["orchestration"].update(
            {"execution": "mixed", "degraded": True, "waves": [["P1"]]}
        )
        payload["perspectives"].reverse()
        self.assertIn(
            "replacement perspective P2 must appear after P1",
            semantic_errors(payload),
        )

    def test_public_schema_id_is_platform_neutral(self) -> None:
        schema_id = self.schema["$id"]
        self.assertEqual(
            schema_id,
            "urn:orchestrate-multi-perspective-panel:schema:panel-output:v1",
        )
        self.assertNotIn("codex", schema_id.lower())
        self.assertNotIn("claude", schema_id.lower())

    def test_stable_enum_lock_is_exact(self) -> None:
        self.assertEqual(stable_enum_errors(self.schema, self.enum_lock), [])

        wrong_major = copy.deepcopy(self.enum_lock)
        wrong_major["schema_major"] = 2
        self.assertIn(
            "stable enum lock schema_major must remain 1 for the v1 lock",
            stable_enum_errors(self.schema, wrong_major),
        )

        reordered = copy.deepcopy(self.schema)
        reordered["$defs"]["item"]["properties"]["kind"]["enum"].reverse()
        self.assertTrue(
            any(
                "schema enum item.kind differs from stable lock" in error
                for error in stable_enum_errors(reordered, self.enum_lock)
            )
        )

    def test_enum_addition_requires_new_minor_and_lock_metadata(self) -> None:
        unrecorded_schema = copy.deepcopy(self.schema)
        unrecorded_schema["$defs"]["item"]["properties"]["kind"]["enum"].append(
            "constraint"
        )
        self.assertTrue(
            any(
                "schema enum item.kind differs from stable lock" in error
                for error in stable_enum_errors(unrecorded_schema, self.enum_lock)
            )
        )

        same_minor_lock = copy.deepcopy(self.enum_lock)
        same_minor_lock["additions"] = {
            "item.kind": [{"value": "constraint", "introduced_in": "1.1"}]
        }
        self.assertTrue(
            any(
                "must use a schema minor after 1.1" in error
                for error in stable_enum_errors(unrecorded_schema, same_minor_lock)
            )
        )

        additive_schema = copy.deepcopy(unrecorded_schema)
        additive_schema["properties"]["schema_version"]["enum"].append("1.2")
        additive_lock = copy.deepcopy(self.enum_lock)
        additive_lock["additions"] = {
            "schema_version": [{"value": "1.2", "introduced_in": "1.2"}],
            "item.kind": [{"value": "constraint", "introduced_in": "1.2"}],
        }
        self.assertEqual(stable_enum_errors(additive_schema, additive_lock), [])


if __name__ == "__main__":
    unittest.main()
