#!/usr/bin/env python3
"""Cross-validate a frozen meeting-plan snapshot and its panel-output v1.2 result."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_meeting_plan import validate as validate_meeting_plan
from validate_panel_output import validate as validate_panel_output


def bundle_errors(
    meeting_plan: dict[str, Any], panel_output: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    if panel_output.get("schema_version") != "1.2":
        return ["bundle validation requires panel-output schema_version 1.2"]

    meeting = meeting_plan["meeting"]
    reference = panel_output["meeting"]
    rounds = {entry["round_id"]: entry for entry in meeting_plan["rounds"]}
    plans = {
        entry["plan_revision_id"]: entry
        for entry in meeting_plan["plan_revisions"]
    }
    role_revisions = {
        entry["role_revision_id"]: entry
        for entry in meeting_plan["role_revisions"]
    }
    risks = {
        entry["risk_surface_id"]: entry
        for entry in meeting_plan["risk_surfaces"]
    }

    if reference["meeting_id"] != meeting["meeting_id"]:
        errors.append("panel result references a different meeting")
    round_entry = rounds.get(reference["round_id"])
    if round_entry is None:
        return errors + ["panel result references an unknown meeting round"]
    if round_entry["state"] != "completed":
        errors.append("panel result is attached to a round that is not completed")
    if round_entry["panel_run_id"] != panel_output["run"]["run_id"]:
        errors.append("panel run_id does not match the completed meeting round")
    if round_entry["close_gate"] != panel_output["gate"]["state"]:
        errors.append("panel gate does not match the meeting round close gate")
    if round_entry["mode"] != panel_output["run"]["mode"]:
        errors.append("panel mode does not match the meeting round mode")
    if reference["plan_revision_id"] != round_entry["frozen_plan_revision_id"]:
        errors.append("panel result does not reference the round's frozen plan revision")
    if reference["frozen_plan_digest"] != round_entry["frozen_plan_digest"]:
        errors.append("panel result does not reference the round's frozen plan digest")

    for field in ("objective", "scope", "non_goals", "authorities", "baseline"):
        if panel_output["run"][field] != meeting[field]:
            errors.append(f"panel run {field} differs from the meeting authority snapshot")

    frozen = plans.get(reference["plan_revision_id"])
    if frozen is None:
        return errors + ["panel result references an unknown frozen plan revision"]
    if frozen["digest"] != reference["frozen_plan_digest"]:
        errors.append("panel frozen_plan_digest does not match canonical plan content")
    if frozen["round_id"] != reference["round_id"]:
        errors.append("frozen plan belongs to another meeting round")

    bindings = {
        entry["role_id"]: entry for entry in frozen["role_bindings"]
    }
    attempts_by_role: dict[str, list[dict[str, Any]]] = {
        role_id: [] for role_id in bindings
    }
    perspective_by_id = {
        entry["perspective_id"]: entry for entry in panel_output["perspectives"]
    }
    for perspective in panel_output["perspectives"]:
        perspective_id = perspective["perspective_id"]
        role_id = perspective["role_id"]
        binding = bindings.get(role_id)
        if binding is None:
            errors.append(
                f"perspective {perspective_id} executes role {role_id} outside the frozen slate"
            )
            continue
        attempts_by_role[role_id].append(perspective)
        if perspective["role_revision_id"] != binding["role_revision_id"]:
            errors.append(
                f"perspective {perspective_id} does not use the frozen role revision"
            )
            continue
        role = role_revisions[binding["role_revision_id"]]
        if perspective["name"] != role["name"]:
            errors.append(f"perspective {perspective_id} name drifted from the frozen role")
        if perspective["lens"] != role["lens_question"]:
            errors.append(f"perspective {perspective_id} lens drifted from the frozen role")
        if perspective["selection_reason"] != role["selection_reason"]:
            errors.append(
                f"perspective {perspective_id} selection reason drifted from the frozen role"
            )
        expected_stage = round_entry["stage"]
        if perspective.get("stage") != expected_stage:
            errors.append(
                f"perspective {perspective_id} stage differs from the meeting round"
            )

    missing_roles = sorted(
        role_id for role_id, attempts in attempts_by_role.items() if not attempts
    )
    if missing_roles:
        errors.append(f"frozen roles have no execution attempt: {missing_roles!r}")
    for role_id, attempts in attempts_by_role.items():
        if len(attempts) <= 1:
            continue
        attempt_ids = {entry["perspective_id"] for entry in attempts}
        replacement_targets = {
            entry["replacement_perspective_id"]
            for entry in attempts
            if entry["replacement_perspective_id"] in attempt_ids
        }
        roots = attempt_ids - replacement_targets
        if len(roots) != 1:
            errors.append(f"role {role_id} attempts do not form one replacement chain")
            continue
        visited: set[str] = set()
        current_id: str | None = next(iter(roots))
        while current_id is not None and current_id not in visited:
            visited.add(current_id)
            current = perspective_by_id[current_id]
            target = current["replacement_perspective_id"]
            current_id = target if target in attempt_ids else None
        if visited != attempt_ids:
            errors.append(f"role {role_id} attempts do not form one replacement chain")

    for item in panel_output["items"]:
        perspective = perspective_by_id.get(item["perspective_id"])
        if perspective is None:
            continue
        binding = bindings.get(perspective["role_id"])
        if binding is None:
            continue
        role = role_revisions[binding["role_revision_id"]]
        unowned = sorted(set(item["risk_surface_ids"]) - set(role["risk_surface_ids"]))
        if unowned:
            errors.append(
                f"item {item['item_id']} claims risks not owned by its frozen role: {unowned!r}"
            )

    planned_coverage = {
        entry["risk_surface_id"]: entry for entry in frozen["coverage"]
    }
    actual_coverage = {
        entry["risk_surface_id"]: entry for entry in panel_output["coverage"]
    }
    if set(actual_coverage) != set(planned_coverage):
        errors.append("panel coverage does not match the frozen risk-surface plan")
    for risk_id, planned in planned_coverage.items():
        actual = actual_coverage.get(risk_id)
        if actual is None:
            continue
        risk = risks[risk_id]
        if actual["risk_surface"] != risk["name"]:
            errors.append(f"coverage {risk_id} label differs from the meeting plan")
        if actual["critical"] != risk["critical"]:
            errors.append(f"coverage {risk_id} criticality differs from the meeting plan")
        if set(actual["planned_role_ids"]) != set(planned["role_ids"]):
            errors.append(f"coverage {risk_id} planned roles differ from the frozen plan")
        for item_id in actual["evidence_item_ids"]:
            item = next(
                (entry for entry in panel_output["items"] if entry["item_id"] == item_id),
                None,
            )
            if item is None:
                continue
            perspective = perspective_by_id.get(item["perspective_id"])
            if perspective is not None and perspective["role_id"] not in planned["role_ids"]:
                errors.append(
                    f"coverage {risk_id} uses evidence from role {perspective['role_id']} "
                    "outside the frozen coverage plan"
                )
        if (
            panel_output["gate"]["state"] == "go"
            and risk["critical"]
            and planned["status"] == "uncovered"
        ):
            errors.append(f"GO cannot recover a critical risk uncovered in the frozen plan: {risk_id}")

    frozen_events = [
        event
        for event in meeting_plan["events"]
        if event["round_id"] == round_entry["round_id"]
        and event["type"] == "role_slate_frozen"
    ]
    if not any(
        event["plan_revision_id"] == frozen["plan_revision_id"]
        for event in frozen_events
    ):
        errors.append("no freeze event binds the exact plan revision used by the result")
    if not any(
        event["round_id"] == round_entry["round_id"]
        and event["type"] == "result_ready"
        for event in meeting_plan["events"]
    ):
        errors.append("completed round has no result_ready event")

    return errors


def validate_bundle(meeting_plan_path: Path, panel_output_path: Path) -> list[str]:
    errors = [
        f"meeting-plan: {error}"
        for error in validate_meeting_plan(meeting_plan_path)
    ]
    errors.extend(
        f"panel-output: {error}"
        for error in validate_panel_output(panel_output_path)
    )
    if errors:
        return errors
    meeting_plan = json.loads(meeting_plan_path.read_text(encoding="utf-8"))
    panel_output = json.loads(panel_output_path.read_text(encoding="utf-8"))
    return bundle_errors(meeting_plan, panel_output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("meeting_plan", type=Path)
    parser.add_argument("panel_output", type=Path)
    args = parser.parse_args()

    meeting_plan_path = args.meeting_plan.resolve()
    panel_output_path = args.panel_output.resolve()
    errors = validate_bundle(meeting_plan_path, panel_output_path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid bundle: {args.meeting_plan} + {args.panel_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
