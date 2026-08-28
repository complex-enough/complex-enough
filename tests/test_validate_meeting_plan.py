from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_meeting_plan import (  # noqa: E402
    canonical_digest,
    raw_text_digest,
    semantic_errors,
    stable_enum_errors,
    validate,
)


class MeetingPlanValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_path = ROOT / "tests" / "fixtures" / "meeting-plan-v1.0.json"
        self.fixture = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        self.schema = json.loads(
            (ROOT / "schemas" / "meeting-plan.schema.json").read_text(encoding="utf-8")
        )
        self.enum_lock = json.loads(
            (ROOT / "schemas" / "stable-meeting-plan-enums.v1.json").read_text(
                encoding="utf-8"
            )
        )

    def restamp(self, payload: dict) -> None:
        sources = {
            entry["source_artifact_id"]: entry
            for entry in payload["source_artifacts"]
        }
        for source in sources.values():
            if source["source_text"] is not None:
                source["raw_digest"] = raw_text_digest(source["source_text"])
        for role in payload["role_revisions"]:
            source_id = role["source_artifact_id"]
            if source_id is not None:
                role["provenance"]["source_digest"] = sources[source_id]["raw_digest"]
            role["digest"] = canonical_digest(role)
        roles = {
            entry["role_revision_id"]: entry
            for entry in payload["role_revisions"]
        }
        for plan in payload["plan_revisions"]:
            for binding in plan["role_bindings"]:
                binding["role_digest"] = roles[binding["role_revision_id"]]["digest"]
            plan["digest"] = canonical_digest(plan)
        plans = {
            entry["plan_revision_id"]: entry
            for entry in payload["plan_revisions"]
        }
        for round_entry in payload["rounds"]:
            frozen_id = round_entry["frozen_plan_revision_id"]
            if frozen_id is not None:
                round_entry["frozen_plan_digest"] = plans[frozen_id]["digest"]

    def validate_payload(self, payload: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "meeting.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return validate(path)

    def test_v10_fixture_is_valid(self) -> None:
        self.assertEqual(validate(self.fixture_path), [])

    def test_v10_allows_distinct_roles_with_the_same_department_label(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["role_revisions"][0]["department"] = payload["role_revisions"][1][
            "department"
        ]
        self.restamp(payload)
        self.assertEqual(self.validate_payload(payload), [])

    def test_v10_rejects_parallel_department_or_headcount_state(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["departments"] = []
        self.assertTrue(
            any(
                "Additional properties are not allowed" in error
                and "departments" in error
                for error in self.validate_payload(payload)
            )
        )

        payload = copy.deepcopy(self.fixture)
        payload["plan_revisions"][0]["headcount"] = {"Platform operations": 2}
        self.assertTrue(
            any(
                "Additional properties are not allowed" in error
                and "headcount" in error
                for error in self.validate_payload(payload)
            )
        )

    def test_stable_enum_lock_is_exact(self) -> None:
        self.assertEqual(stable_enum_errors(self.schema, self.enum_lock), [])
        schema = copy.deepcopy(self.schema)
        schema["$defs"]["round"]["properties"]["state"]["enum"].reverse()
        self.assertTrue(
            any(
                "round.state differs from stable lock" in error
                for error in stable_enum_errors(schema, self.enum_lock)
            )
        )

    def test_every_round_begins_with_a_main_generated_plan(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["plan_revisions"][0]["created_by"] = "user"
        self.restamp(payload)
        self.assertIn(
            "round round-demo-001 must begin with a main-generated plan",
            semantic_errors(payload),
        )

        payload = copy.deepcopy(self.fixture)
        payload["role_revisions"][0]["source"] = "user_added"
        payload["role_revisions"][0]["provenance"]["kind"] = "user_authored"
        self.restamp(payload)
        self.assertIn(
            "round round-demo-001 initial plan must contain main-generated roles",
            semantic_errors(payload),
        )

    def test_role_and_plan_digest_tampering_is_rejected(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["role_revisions"][0]["lens_question"] = "Tampered lens"
        self.assertIn(
            "role revision rolerev-product-001 digest mismatch",
            semantic_errors(payload),
        )

        payload = copy.deepcopy(self.fixture)
        payload["plan_revisions"][1]["created_by"] = "main"
        self.assertIn("plan planrev-demo-002 digest mismatch", semantic_errors(payload))

    def test_stale_or_post_freeze_mutation_is_rejected(self) -> None:
        payload = copy.deepcopy(self.fixture)
        first_plan = payload["plan_revisions"][0]
        round_entry = payload["rounds"][0]
        round_entry["frozen_plan_revision_id"] = first_plan["plan_revision_id"]
        round_entry["frozen_plan_digest"] = first_plan["digest"]
        self.assertIn(
            "round round-demo-001 frozen plan must remain the active plan",
            semantic_errors(payload),
        )

    def test_declared_role_operation_must_match_the_copy_on_write_diff(self) -> None:
        expected_fragments = {
            "generate": "cannot use generate after revision 1",
            "regenerate": "regenerated slate is not fully main-generated",
            "edit": "does not bind edited roles",
            "add": "add operation has an invalid role diff",
            "remove": "remove operation has an invalid role diff",
            "merge": "merge operation has an invalid role diff",
            "split": "split operation has an invalid role diff",
            "reset": "does not rebind main-generated roles",
            "import_add": "import_add has an invalid role diff",
            "import_merge": "import operation has no applied preview result",
        }
        for operation, expected in expected_fragments.items():
            with self.subTest(operation=operation):
                payload = copy.deepcopy(self.fixture)
                payload["plan_revisions"][1]["operation"] = operation
                self.restamp(payload)
                self.assertTrue(
                    any(expected in error for error in semantic_errors(payload))
                )

    def test_removed_role_tombstone_cannot_hide_an_active_binding(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["plan_revisions"][1]["removed_role_ids"] = ["role-product"]
        self.restamp(payload)
        errors = semantic_errors(payload)
        self.assertIn(
            "plan planrev-demo-002 both removes and binds the same role",
            errors,
        )
        self.assertIn(
            "plan planrev-demo-002 removed_role_ids do not match its parent diff",
            errors,
        )

        payload = copy.deepcopy(self.fixture)
        payload["rounds"][0]["allowed_actions"].append("edit_role")
        self.assertIn(
            "round round-demo-001 exposes role mutation after freeze",
            semantic_errors(payload),
        )

    def test_blocking_conflicts_and_unacknowledged_warnings_prevent_freeze(self) -> None:
        payload = copy.deepcopy(self.fixture)
        plan = payload["plan_revisions"][1]
        plan["warnings"].append(
            {
                "warning_id": "warning-authority",
                "code": "AUTHORITY_SCOPE_EXPANSION",
                "severity": "blocking",
                "message": "Imported text requests broader authority.",
                "role_ids": ["role-operations"],
                "risk_surface_ids": ["risk-operations"],
            }
        )
        plan["acknowledged_warning_ids"].append("warning-authority")
        self.restamp(payload)
        self.assertIn(
            "round round-demo-001 freezes a plan with blocking conflicts",
            semantic_errors(payload),
        )

        payload = copy.deepcopy(self.fixture)
        plan = payload["plan_revisions"][1]
        plan["warnings"].append(
            {
                "warning_id": "warning-origin",
                "code": "UNVERIFIABLE_ORIGIN",
                "severity": "warning",
                "message": "Provider identity is user-declared.",
                "role_ids": ["role-operations"],
                "risk_surface_ids": [],
            }
        )
        self.restamp(payload)
        self.assertTrue(
            any("freezes unacknowledged warnings" in error for error in semantic_errors(payload))
        )

    def test_critical_coverage_loss_remains_public_and_cannot_be_silent(self) -> None:
        payload = copy.deepcopy(self.fixture)
        plan = payload["plan_revisions"][1]
        coverage = next(
            entry
            for entry in plan["coverage"]
            if entry["risk_surface_id"] == "risk-product-contract"
        )
        coverage.update({"role_ids": [], "status": "uncovered"})
        self.restamp(payload)
        self.assertTrue(
            any(
                "leaves critical risks uncovered without warning" in error
                for error in semantic_errors(payload)
            )
        )

    def test_external_prompt_is_source_material_not_an_executor(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["role_revisions"][2]["executor"] = "claude"
        errors = self.validate_payload(payload)
        self.assertTrue(any("Additional properties are not allowed" in error for error in errors))

        payload = copy.deepcopy(self.fixture)
        payload["source_artifacts"][0]["source_text"] += " changed"
        self.assertIn(
            "source source-operations-001 raw digest mismatch",
            semantic_errors(payload),
        )

    def test_import_with_authority_conflict_cannot_be_applied(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["import_previews"][0]["warning_codes"].append(
            "AUTHORITY_SCOPE_EXPANSION"
        )
        self.assertIn(
            "import preview import-operations-001 applies a blocking conflict",
            semantic_errors(payload),
        )

    def test_applied_import_warnings_must_survive_into_the_plan(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["plan_revisions"][1]["warnings"] = []
        payload["plan_revisions"][1]["acknowledged_warning_ids"] = []
        self.restamp(payload)
        self.assertTrue(
            any(
                "warnings were not transferred" in error
                for error in semantic_errors(payload)
            )
        )

    def test_external_provider_claim_is_always_disclosed_as_unverified(self) -> None:
        payload = copy.deepcopy(self.fixture)
        payload["import_previews"][0]["warning_codes"] = []
        self.assertIn(
            "external import preview import-operations-001 must disclose unverifiable origin",
            semantic_errors(payload),
        )

    def test_main_is_not_a_perspective_role(self) -> None:
        payload = copy.deepcopy(self.fixture)
        role = payload["role_revisions"][0]
        role["role_id"] = "role-main"
        payload["plan_revisions"][0]["role_bindings"][0]["role_id"] = "role-main"
        payload["plan_revisions"][1]["role_bindings"][0]["role_id"] = "role-main"
        self.restamp(payload)
        self.assertIn("role role-main uses a reserved convener identity", semantic_errors(payload))


if __name__ == "__main__":
    unittest.main()
