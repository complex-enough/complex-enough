from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_meeting_bundle import bundle_errors, validate_bundle  # noqa: E402


class MeetingBundleValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.meeting_path = ROOT / "tests" / "fixtures" / "meeting-plan-v1.0.json"
        self.output_path = ROOT / "tests" / "fixtures" / "output-v1.2.json"
        self.meeting = json.loads(self.meeting_path.read_text(encoding="utf-8"))
        self.output = json.loads(self.output_path.read_text(encoding="utf-8"))

    def test_v12_bundle_fixture_is_valid(self) -> None:
        self.assertEqual(validate_bundle(self.meeting_path, self.output_path), [])

    def test_result_must_bind_the_exact_frozen_digest(self) -> None:
        output = copy.deepcopy(self.output)
        output["meeting"]["frozen_plan_digest"] = "sha256:" + "f" * 64
        self.assertIn(
            "panel result does not reference the round's frozen plan digest",
            bundle_errors(self.meeting, output),
        )

    def test_attempt_must_use_the_frozen_role_revision(self) -> None:
        output = copy.deepcopy(self.output)
        output["perspectives"][1]["role_revision_id"] = "rolerev-operations-001"
        self.assertIn(
            "perspective P2 does not use the frozen role revision",
            bundle_errors(self.meeting, output),
        )

    def test_every_frozen_role_requires_an_attempt(self) -> None:
        output = copy.deepcopy(self.output)
        output["perspectives"] = [output["perspectives"][0]]
        self.assertIn(
            "frozen roles have no execution attempt: ['role-operations']",
            bundle_errors(self.meeting, output),
        )

    def test_multiple_attempts_must_form_one_replacement_chain(self) -> None:
        output = copy.deepcopy(self.output)
        duplicate = copy.deepcopy(output["perspectives"][1])
        duplicate["perspective_id"] = "P3"
        output["perspectives"].append(duplicate)
        self.assertIn(
            "role role-operations attempts do not form one replacement chain",
            bundle_errors(self.meeting, output),
        )

    def test_item_cannot_claim_a_risk_outside_its_role(self) -> None:
        output = copy.deepcopy(self.output)
        output["items"][0]["risk_surface_ids"] = ["risk-operations"]
        self.assertTrue(
            any(
                "claims risks not owned by its frozen role" in error
                for error in bundle_errors(self.meeting, output)
            )
        )

    def test_actual_coverage_cannot_reassign_planned_ownership(self) -> None:
        output = copy.deepcopy(self.output)
        output["coverage"][1]["planned_role_ids"] = ["role-product"]
        errors = bundle_errors(self.meeting, output)
        self.assertIn(
            "coverage risk-operations planned roles differ from the frozen plan",
            errors,
        )

    def test_bundle_rejects_legacy_result_without_meeting_provenance(self) -> None:
        output = copy.deepcopy(self.output)
        output["schema_version"] = "1.1"
        self.assertEqual(
            bundle_errors(self.meeting, output),
            ["bundle validation requires panel-output schema_version 1.2"],
        )


if __name__ == "__main__":
    unittest.main()
