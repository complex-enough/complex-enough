from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RuntimeMeetingContractTest(unittest.TestCase):
    def test_exact_current_slate_confirmation_is_one_action_warning_acknowledgement(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        lifecycle = (ROOT / "references" / "meeting-lifecycle.md").read_text(
            encoding="utf-8"
        )
        import_contract = (
            ROOT / "references" / "role-definition-and-import.md"
        ).read_text(encoding="utf-8")

        self.assertIn("exact currently displayed slate", skill)
        self.assertIn("do not require a second warning-only chat turn", lifecycle)
        self.assertIn("one-action confirmation", import_contract)

    def test_one_action_acknowledgement_preserves_safety_limits(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract = (ROOT / "references" / "meeting-plan-contract.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Blocking conflicts can never be acknowledged away", skill)
        self.assertIn("still forbids a later review `GO`", skill)
        self.assertIn("Ambiguous or stale start requests do not acknowledge warnings", contract)

    def test_one_action_acknowledgement_does_not_change_confirmed_digest(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        lifecycle = (ROOT / "references" / "meeting-lifecycle.md").read_text(
            encoding="utf-8"
        )
        contract = (ROOT / "references" / "meeting-plan-contract.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("must already bind that visible warning set", skill)
        self.assertIn("freeze the identical displayed revision and digest", skill)
        self.assertIn("Do not change the displayed revision or digest", lifecycle)
        self.assertIn("does not claim that a user confirmation event has already occurred", contract)
        self.assertIn("never mutate or recompute the plan", contract)

    def test_role_review_is_a_hard_user_turn_barrier(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        lifecycle = (ROOT / "references" / "meeting-lifecycle.md").read_text(
            encoding="utf-8"
        )
        contract = (ROOT / "references" / "meeting-plan-contract.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("hard conversation-turn barrier", skill)
        self.assertIn("final response of the current assistant turn", skill)
        self.assertIn("Only a subsequent user-authored turn", lifecycle)
        self.assertIn("`awaiting_role_review` is a hard chat-turn barrier", contract)

    def test_host_adapters_forbid_commentary_confirmation_and_same_turn_dispatch(self) -> None:
        codex = (ROOT / "adapters" / "codex.md").read_text(encoding="utf-8")
        claude = (ROOT / "adapters" / "claude-code.md").read_text(encoding="utf-8")

        self.assertIn("Commentary is not a checkpoint", codex)
        self.assertIn("subsequent user-authored turn", codex)
        self.assertIn("autonomous continuation is not a confirmation checkpoint", claude)
        self.assertIn("subsequent user-authored turn", claude)

    def test_every_applied_mutation_receipt_recomputes_derived_seat_counts(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        lifecycle = (ROOT / "references" / "meeting-lifecycle.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Each applied receipt", skill)
        self.assertIn("derived from active role bindings", skill)
        self.assertIn("`unchanged` alone is not a derived count display", skill)
        self.assertIn("applied revision's per-affiliation seat counts", lifecycle)
        self.assertIn("rather than independent headcount state", lifecycle)
        self.assertIn("enumerate every label and numeric count", lifecycle)

    def test_text_completion_keeps_exact_execution_and_role_evidence_provenance(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        lifecycle = (ROOT / "references" / "meeting-lifecycle.md").read_text(
            encoding="utf-8"
        )
        protocol = (ROOT / "references" / "panelist-protocol.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("exact frozen `plan_revision_id` and digest", skill)
        self.assertIn("executed `role_revision_id` values", skill)
        self.assertIn("public completion must remain auditable", lifecycle)
        self.assertIn("Every completed same-department role", lifecycle)
        self.assertIn("its `role_revision_id`", protocol)

    def test_public_evidence_ledger_prevents_same_department_evidence_erasure(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        lifecycle = (ROOT / "references" / "meeting-lifecycle.md").read_text(
            encoding="utf-8"
        )
        protocol = (ROOT / "references" / "panelist-protocol.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("public evidence ledger", skill)
        self.assertIn("`no_material_finding`", skill)
        self.assertIn("role-execution table alone is not evidence provenance", skill)
        self.assertIn("synthesis references those item IDs", lifecycle)
        self.assertIn("role-execution table alone cannot prove", protocol)


if __name__ == "__main__":
    unittest.main()
