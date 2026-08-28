#!/usr/bin/env python3
"""Validate the public boss-led meeting control-plane contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "meeting-plan.schema.json"
DEFAULT_ENUM_LOCK = REPO_ROOT / "schemas" / "stable-meeting-plan-enums.v1.json"
EXECUTION_STATES = {
    "frozen",
    "queued",
    "independent_opening",
    "deliberating",
    "verifying",
    "adjudicating",
    "completed",
}
ROLE_MUTATION_ACTIONS = {
    "regenerate_roles",
    "edit_role",
    "add_role",
    "remove_role",
    "merge_roles",
    "split_role",
    "reset_role_to_generated",
    "preview_import",
    "apply_import",
    "confirm_and_start",
}
BLOCKING_WARNING_CODES = {
    "AUTHORITY_SCOPE_EXPANSION",
    "MODERATOR_IMPERSONATION",
    "FORCED_CONCLUSION",
    "PEER_PRIVATE_ACCESS",
    "PRIVATE_REASONING_REQUEST",
    "UNPARSABLE_IMPORT",
    "LIVE_EXTERNAL_EXECUTION",
    "IMPORT_TOO_LARGE",
}
RESERVED_CONVENER_ROLE_IDS = {
    "role-main",
    "role-moderator",
    "role-boss",
    "role-convener",
}
PROHIBITED_KEYS = {
    "chain_of_thought",
    "hidden_reasoning",
    "private_reasoning",
    "raw_panelist_report",
    "raw_transcript",
    "scratch_work",
    "thought_trace",
}
ENUM_PATHS = {
    "schema_version": ("properties", "schema_version", "enum"),
    "complexity.range": (
        "$defs",
        "complexityProfile",
        "properties",
        "range",
        "enum",
    ),
    "meeting.status": ("$defs", "meeting", "properties", "status", "enum"),
    "round.mode": ("$defs", "round", "properties", "mode", "enum"),
    "stage": ("$defs", "stage", "enum"),
    "round.state": ("$defs", "round", "properties", "state", "enum"),
    "round.close_gate": ("$defs", "round", "properties", "close_gate", "enum"),
    "round.allowed_actions": (
        "$defs",
        "round",
        "properties",
        "allowed_actions",
        "items",
        "enum",
    ),
    "attention.code": ("$defs", "attention", "properties", "code", "enum"),
    "handoff.disposition": (
        "$defs",
        "handoffItem",
        "properties",
        "disposition",
        "enum",
    ),
    "role.source": ("$defs", "roleRevision", "properties", "source", "enum"),
    "provenance.kind": ("$defs", "provenance", "properties", "kind", "enum"),
    "plan.operation": ("$defs", "planRevision", "properties", "operation", "enum"),
    "plan.created_by": ("$defs", "planRevision", "properties", "created_by", "enum"),
    "coverage.status": ("$defs", "coveragePlan", "properties", "status", "enum"),
    "warning.code": ("$defs", "warning", "properties", "code", "enum"),
    "warning.severity": ("$defs", "warning", "properties", "severity", "enum"),
    "source.origin": ("$defs", "sourceArtifact", "properties", "origin", "enum"),
    "source.retention": ("$defs", "sourceArtifact", "properties", "retention", "enum"),
    "import.operation": ("$defs", "importPreview", "properties", "operation", "enum"),
    "import.status": ("$defs", "importPreview", "properties", "status", "enum"),
    "field_change.disposition": (
        "$defs",
        "fieldChange",
        "properties",
        "disposition",
        "enum",
    ),
    "event.type": ("$defs", "event", "properties", "type", "enum"),
}


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _walk_keys(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield key, child_path
            yield from _walk_keys(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_keys(child, f"{path}[{index}]")


def _schema_value(schema: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = schema
    for part in path:
        value = value[part]
    return value


def _version_tuple(value: Any) -> tuple[int, int] | None:
    if not isinstance(value, str):
        return None
    parts = value.split(".")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        return None
    return int(parts[0]), int(parts[1])


def stable_enum_errors(
    schema: dict[str, Any], enum_lock: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    locked_enums = enum_lock.get("enums", {})
    additions = enum_lock.get("additions", {})
    locked_version = enum_lock.get("locked_through_schema_version")
    locked_tuple = _version_tuple(locked_version)
    schema_major = enum_lock.get("schema_major")

    if set(locked_enums) != set(ENUM_PATHS):
        return ["meeting enum lock and schema paths differ"]
    if sorted(set(additions) - set(ENUM_PATHS)):
        errors.append("meeting enum additions use unknown paths")
    try:
        actual = {
            name: _schema_value(schema, path) for name, path in ENUM_PATHS.items()
        }
    except (KeyError, TypeError):
        return ["meeting schema is missing a stable enum path"]

    supported_versions = actual["schema_version"]
    if schema_major != 1 or locked_tuple is None:
        errors.append("meeting enum lock version metadata is invalid")
    if locked_version not in supported_versions:
        errors.append("meeting schema omits its locked baseline version")

    for name, baseline in locked_enums.items():
        expected = list(baseline)
        seen: list[Any] = []
        for addition in additions.get(name, []):
            if not isinstance(addition, dict) or set(addition) != {"value", "introduced_in"}:
                errors.append(f"meeting enum addition for {name} has invalid metadata")
                continue
            value = addition["value"]
            introduced = addition["introduced_in"]
            introduced_tuple = _version_tuple(introduced)
            if value in baseline or value in seen:
                errors.append(f"meeting enum addition for {name} duplicates {value!r}")
            seen.append(value)
            if (
                introduced_tuple is None
                or introduced_tuple[0] != schema_major
                or (locked_tuple is not None and introduced_tuple <= locked_tuple)
                or introduced not in supported_versions
            ):
                errors.append(
                    f"meeting enum addition {name}={value!r} has invalid introduced_in"
                )
            expected.append(value)
        if actual[name] != expected:
            errors.append(
                f"meeting schema enum {name} differs from stable lock: "
                f"expected {expected!r}, got {actual[name]!r}"
            )
    return errors


def canonical_digest(value: dict[str, Any], *, omit_key: str = "digest") -> str:
    """Return the normative SHA-256 of a JSON object with its digest field omitted."""

    material = {key: child for key, child in value.items() if key != omit_key}
    encoded = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def raw_text_digest(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _index(
    entries: list[dict[str, Any]], key: str, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    values = [entry[key] for entry in entries]
    for duplicate in sorted(_duplicates(values)):
        errors.append(f"duplicate {label}: {duplicate}")
    return {entry[key]: entry for entry in entries}


def _plan_operation_errors(
    previous: dict[str, Any],
    current: dict[str, Any],
    role_by_revision: dict[str, dict[str, Any]],
) -> list[str]:
    """Verify that a revision's declared role operation matches its public diff."""

    errors: list[str] = []
    plan_id = current["plan_revision_id"]
    operation = current["operation"]
    previous_bindings = {
        entry["role_id"]: entry for entry in previous["role_bindings"]
    }
    current_bindings = {
        entry["role_id"]: entry for entry in current["role_bindings"]
    }
    previous_roles = set(previous_bindings)
    current_roles = set(current_bindings)
    added = current_roles - previous_roles
    removed = previous_roles - current_roles
    changed = {
        role_id
        for role_id in previous_roles & current_roles
        if previous_bindings[role_id]["role_revision_id"]
        != current_bindings[role_id]["role_revision_id"]
    }
    complexity_changed = previous.get("complexity_profile") != current.get(
        "complexity_profile"
    )
    if set(current["removed_role_ids"]) != removed:
        errors.append(
            f"plan {plan_id} removed_role_ids do not match its parent diff"
        )

    def sources(role_ids: set[str]) -> set[str | None]:
        return {
            role_by_revision.get(
                current_bindings[role_id]["role_revision_id"], {}
            ).get("source")
            for role_id in role_ids
        }

    if operation == "generate":
        errors.append(f"plan {plan_id} cannot use generate after revision 1")
    elif operation == "regenerate":
        if not (added or removed or changed or complexity_changed):
            errors.append(
                f"plan {plan_id} regenerate operation has no role or complexity diff"
            )
        if sources(added | changed) - {"main_generated"}:
            errors.append(
                f"plan {plan_id} regenerated role changes are not main-generated"
            )
    elif operation == "edit":
        if added or removed or not changed:
            errors.append(f"plan {plan_id} edit operation has an invalid role diff")
        if sources(changed) - {"user_edited"}:
            errors.append(f"plan {plan_id} edit operation does not bind edited roles")
    elif operation == "add":
        if not added or removed or changed:
            errors.append(f"plan {plan_id} add operation has an invalid role diff")
        if sources(added) - {"user_added"}:
            errors.append(f"plan {plan_id} add operation does not bind user-added roles")
    elif operation == "remove":
        if not removed or added or changed:
            errors.append(f"plan {plan_id} remove operation has an invalid role diff")
    elif operation == "merge":
        if len(removed) < 2 or not added or changed:
            errors.append(f"plan {plan_id} merge operation has an invalid role diff")
        if sources(added) - {"merged"}:
            errors.append(f"plan {plan_id} merge operation does not bind merged roles")
        removed_revisions = {
            previous_bindings[role_id]["role_revision_id"] for role_id in removed
        }
        for role_id in added:
            role = role_by_revision.get(
                current_bindings[role_id]["role_revision_id"], {}
            )
            if not removed_revisions.issubset(
                set(role.get("derived_from_role_revision_ids", []))
            ):
                errors.append(
                    f"plan {plan_id} merged role {role_id} does not cite all removed parents"
                )
    elif operation == "split":
        if len(removed) != 1 or len(added) < 2 or changed:
            errors.append(f"plan {plan_id} split operation has an invalid role diff")
        if sources(added) - {"split"}:
            errors.append(f"plan {plan_id} split operation does not bind split roles")
        if removed:
            source_revision = previous_bindings[next(iter(removed))][
                "role_revision_id"
            ]
            for role_id in added:
                role = role_by_revision.get(
                    current_bindings[role_id]["role_revision_id"], {}
                )
                if source_revision not in role.get(
                    "derived_from_role_revision_ids", []
                ):
                    errors.append(
                        f"plan {plan_id} split role {role_id} does not cite its source parent"
                    )
    elif operation == "reset":
        if added or removed or not changed:
            errors.append(f"plan {plan_id} reset operation has an invalid role diff")
        if sources(changed) - {"main_generated"}:
            errors.append(
                f"plan {plan_id} reset operation does not rebind main-generated roles"
            )
    elif operation == "import_add":
        if not added or removed or changed:
            errors.append(f"plan {plan_id} import_add has an invalid role diff")
        if sources(added) - {"imported"}:
            errors.append(f"plan {plan_id} import_add does not bind imported roles")
    elif operation in {"import_replace", "import_merge"}:
        if added or removed or not changed:
            errors.append(f"plan {plan_id} {operation} has an invalid role diff")
        if sources(changed) - {"imported"}:
            errors.append(f"plan {plan_id} {operation} does not bind imported roles")
    return errors


def semantic_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    meeting = payload["meeting"]
    rounds = payload["rounds"]
    risks = payload["risk_surfaces"]
    roles = payload["role_revisions"]
    plans = payload["plan_revisions"]
    sources = payload["source_artifacts"]
    imports = payload["import_previews"]
    events = payload["events"]
    schema_version = payload["schema_version"]

    for plan in plans:
        has_profile = "complexity_profile" in plan
        if schema_version == "1.0" and has_profile:
            errors.append(
                f"meeting-plan 1.0 plan {plan['plan_revision_id']} cannot declare complexity_profile"
            )
        if schema_version == "1.1" and not has_profile:
            errors.append(
                f"meeting-plan 1.1 plan {plan['plan_revision_id']} requires complexity_profile"
            )
        if (
            schema_version == "1.1"
            and plan["operation"] == "generate"
            and has_profile
            and plan["complexity_profile"]["user_adjusted"]
        ):
            errors.append(
                f"meeting-plan 1.1 generated plan {plan['plan_revision_id']} cannot start user_adjusted"
            )

    round_by_id = _index(rounds, "round_id", "round_id", errors)
    risk_by_id = _index(risks, "risk_surface_id", "risk_surface_id", errors)
    role_by_revision = _index(
        roles, "role_revision_id", "role_revision_id", errors
    )
    plan_by_id = _index(plans, "plan_revision_id", "plan_revision_id", errors)
    source_by_id = _index(
        sources, "source_artifact_id", "source_artifact_id", errors
    )
    _index(imports, "import_preview_id", "import_preview_id", errors)
    _index(events, "event_id", "event_id", errors)

    sequences = [entry["sequence"] for entry in rounds]
    if sequences != list(range(1, len(rounds) + 1)):
        errors.append("rounds must appear in contiguous sequence order starting at 1")

    current_round_id = meeting["current_round_id"]
    if current_round_id is not None and current_round_id not in round_by_id:
        errors.append(f"meeting references unknown current round {current_round_id}")
    if meeting["status"] == "active" and current_round_id is None:
        errors.append("active meeting requires current_round_id")

    for round_entry in rounds:
        round_id = round_entry["round_id"]
        sequence = round_entry["sequence"]
        for field in ("previous_round_id", "supersedes_round_id"):
            reference = round_entry[field]
            if reference is None:
                continue
            if reference not in round_by_id:
                errors.append(f"round {round_id} references unknown {field} {reference}")
            elif round_by_id[reference]["sequence"] >= sequence:
                errors.append(f"round {round_id} {field} must reference an earlier round")
        if sequence == 1 and round_entry["previous_round_id"] is not None:
            errors.append(f"first round {round_id} cannot have previous_round_id")
        if sequence > 1 and round_entry["previous_round_id"] is None:
            errors.append(f"round {round_id} requires previous_round_id")
        for handoff in round_entry["handoff"]:
            source_round = handoff["source_round_id"]
            if source_round not in round_by_id:
                errors.append(f"round {round_id} handoff references unknown round {source_round}")
            elif round_by_id[source_round]["sequence"] >= sequence:
                errors.append(f"round {round_id} handoff must reference an earlier round")

        mode = round_entry["mode"]
        stage = round_entry["stage"]
        if mode == "full_cycle" and stage is None:
            errors.append(f"full_cycle round {round_id} requires a stage")
        if mode != "full_cycle" and stage not in {None, mode}:
            errors.append(f"round {round_id} stage {stage} conflicts with mode {mode}")

        active_id = round_entry["active_plan_revision_id"]
        frozen_id = round_entry["frozen_plan_revision_id"]
        frozen_digest = round_entry["frozen_plan_digest"]
        state = round_entry["state"]
        actions = set(round_entry["allowed_actions"])

        if active_id is not None:
            if active_id not in plan_by_id:
                errors.append(f"round {round_id} references unknown active plan {active_id}")
            elif plan_by_id[active_id]["round_id"] != round_id:
                errors.append(f"round {round_id} active plan belongs to another round")
        if state == "awaiting_role_review":
            if active_id is None:
                errors.append(f"round {round_id} awaits review without an active plan")
            if frozen_id is not None or frozen_digest is not None:
                errors.append(f"round {round_id} awaits review but is already frozen")
            if "confirm_and_start" not in actions:
                errors.append(f"round {round_id} awaits review without confirm_and_start")
        if state == "generating_roles" and "confirm_and_start" in actions:
            errors.append(f"round {round_id} cannot confirm before roles are generated")
        if state in EXECUTION_STATES:
            if frozen_id is None or frozen_digest is None:
                errors.append(f"round {round_id} state {state} requires a frozen plan")
            if active_id != frozen_id:
                errors.append(f"round {round_id} frozen plan must remain the active plan")
            if actions & ROLE_MUTATION_ACTIONS:
                errors.append(f"round {round_id} exposes role mutation after freeze")
        if frozen_id is None and frozen_digest is not None:
            errors.append(f"round {round_id} has a frozen digest without a frozen plan")
        if frozen_id is not None:
            frozen_plan = plan_by_id.get(frozen_id)
            if frozen_plan is None:
                errors.append(f"round {round_id} references unknown frozen plan {frozen_id}")
            elif frozen_plan["round_id"] != round_id:
                errors.append(f"round {round_id} frozen plan belongs to another round")
            elif frozen_digest != frozen_plan["digest"]:
                errors.append(f"round {round_id} frozen digest does not match plan {frozen_id}")
        if state == "needs_attention" and round_entry["attention"] is None:
            errors.append(f"round {round_id} needs_attention without attention detail")
        if state not in {"needs_attention", "failed"} and round_entry["attention"] is not None:
            errors.append(f"round {round_id} has attention detail outside an attention state")
        if state == "completed":
            if round_entry["panel_run_id"] is None or round_entry["close_gate"] is None:
                errors.append(f"completed round {round_id} requires run and close gate")
        elif round_entry["close_gate"] is not None:
            errors.append(f"round {round_id} has a close gate before completion")

    risks_by_round: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for risk in risks:
        round_id = risk["round_id"]
        if round_id not in round_by_id:
            errors.append(
                f"risk surface {risk['risk_surface_id']} references unknown round {round_id}"
            )
        risks_by_round[round_id].append(risk)

    role_revisions_by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for role in roles:
        role_revision_id = role["role_revision_id"]
        role_id = role["role_id"]
        round_id = role["round_id"]
        role_revisions_by_role[role_id].append(role)
        if role_id in RESERVED_CONVENER_ROLE_IDS:
            errors.append(f"role {role_id} uses a reserved convener identity")
        if round_id not in round_by_id:
            errors.append(f"role revision {role_revision_id} references unknown round {round_id}")
        unknown_risks = sorted(set(role["risk_surface_ids"]) - set(risk_by_id))
        if unknown_risks:
            errors.append(
                f"role revision {role_revision_id} references unknown risks {unknown_risks!r}"
            )
        for risk_id in role["risk_surface_ids"]:
            if risk_id in risk_by_id and risk_by_id[risk_id]["round_id"] != round_id:
                errors.append(
                    f"role revision {role_revision_id} owns risk {risk_id} from another round"
                )
        expected_digest = canonical_digest(role)
        if role["digest"] != expected_digest:
            errors.append(f"role revision {role_revision_id} digest mismatch")

        source_artifact_id = role["source_artifact_id"]
        provenance = role["provenance"]
        if role["source"] == "main_generated":
            if source_artifact_id is not None or provenance["kind"] != "main_generated":
                errors.append(
                    f"main-generated role revision {role_revision_id} has external provenance"
                )
        elif role["source"] != "imported" and source_artifact_id is not None:
            errors.append(
                f"non-imported role revision {role_revision_id} cannot bind a source artifact"
            )
        if role["source"] == "imported":
            if source_artifact_id is None:
                errors.append(f"imported role revision {role_revision_id} has no source artifact")
            elif source_artifact_id not in source_by_id:
                errors.append(
                    f"imported role revision {role_revision_id} references unknown source"
                )
            elif source_by_id[source_artifact_id]["round_id"] != round_id:
                errors.append(
                    f"imported role revision {role_revision_id} uses a source from another round"
                )
            elif provenance["source_digest"] != source_by_id[source_artifact_id]["raw_digest"]:
                errors.append(
                    f"imported role revision {role_revision_id} provenance digest does not match its source"
                )
            if provenance["kind"] not in {"external_prompt", "user_authored"}:
                errors.append(
                    f"imported role revision {role_revision_id} has invalid provenance kind"
                )
        for parent_id in role["derived_from_role_revision_ids"]:
            parent = role_by_revision.get(parent_id)
            if parent is None:
                errors.append(f"role revision {role_revision_id} has unknown parent {parent_id}")
            elif parent["round_id"] != round_id:
                errors.append(f"role revision {role_revision_id} derives across rounds")
        parent_count = len(role["derived_from_role_revision_ids"])
        if role["source"] in {"user_edited", "split"} and parent_count < 1:
            errors.append(f"role revision {role_revision_id} requires a parent revision")
        if role["source"] == "merged" and parent_count < 2:
            errors.append(f"merged role revision {role_revision_id} requires two parents")

    for role_id, revisions in role_revisions_by_role.items():
        ordered = sorted(revisions, key=lambda entry: entry["revision"])
        expected = list(range(1, len(ordered) + 1))
        actual = [entry["revision"] for entry in ordered]
        if actual != expected:
            errors.append(f"role {role_id} revisions must be contiguous from 1")
        if len({entry["round_id"] for entry in revisions}) != 1:
            errors.append(f"role {role_id} cannot span meeting rounds")

    plans_by_round: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for plan in plans:
        plan_id = plan["plan_revision_id"]
        round_id = plan["round_id"]
        plans_by_round[round_id].append(plan)
        if round_id not in round_by_id:
            errors.append(f"plan {plan_id} references unknown round {round_id}")
        if plan["digest"] != canonical_digest(plan):
            errors.append(f"plan {plan_id} digest mismatch")

        bindings = plan["role_bindings"]
        binding_role_ids = [binding["role_id"] for binding in bindings]
        binding_revision_ids = [binding["role_revision_id"] for binding in bindings]
        for duplicate in sorted(_duplicates(binding_role_ids)):
            errors.append(f"plan {plan_id} binds role {duplicate} more than once")
        for duplicate in sorted(_duplicates(binding_revision_ids)):
            errors.append(f"plan {plan_id} binds role revision {duplicate} more than once")
        binding_by_role = {binding["role_id"]: binding for binding in bindings}
        for binding in bindings:
            revision = role_by_revision.get(binding["role_revision_id"])
            if revision is None:
                errors.append(
                    f"plan {plan_id} references unknown role revision {binding['role_revision_id']}"
                )
                continue
            if revision["role_id"] != binding["role_id"]:
                errors.append(f"plan {plan_id} role binding identity mismatch")
            if revision["round_id"] != round_id:
                errors.append(f"plan {plan_id} binds a role from another round")
            if revision["digest"] != binding["role_digest"]:
                errors.append(f"plan {plan_id} role binding digest mismatch")
        if set(plan["removed_role_ids"]) & set(binding_role_ids):
            errors.append(f"plan {plan_id} both removes and binds the same role")

        expected_risks = {
            risk["risk_surface_id"] for risk in risks_by_round.get(round_id, [])
        }
        coverage_ids = [entry["risk_surface_id"] for entry in plan["coverage"]]
        for duplicate in sorted(_duplicates(coverage_ids)):
            errors.append(f"plan {plan_id} repeats coverage for risk {duplicate}")
        if set(coverage_ids) != expected_risks:
            errors.append(f"plan {plan_id} coverage does not match its round risk surfaces")
        uncovered_critical: set[str] = set()
        for coverage in plan["coverage"]:
            risk_id = coverage["risk_surface_id"]
            for role_id in coverage["role_ids"]:
                binding = binding_by_role.get(role_id)
                if binding is None:
                    errors.append(
                        f"plan {plan_id} coverage assigns unknown active role {role_id}"
                    )
                    continue
                revision = role_by_revision.get(binding["role_revision_id"])
                if revision is not None and risk_id not in revision["risk_surface_ids"]:
                    errors.append(
                        f"plan {plan_id} assigns risk {risk_id} to role {role_id} that does not own it"
                    )
            if (
                coverage["status"] == "uncovered"
                and risk_id in risk_by_id
                and risk_by_id[risk_id]["critical"]
            ):
                uncovered_critical.add(risk_id)

        warnings = plan["warnings"]
        warning_ids = [warning["warning_id"] for warning in warnings]
        for duplicate in sorted(_duplicates(warning_ids)):
            errors.append(f"plan {plan_id} repeats warning {duplicate}")
        known_warning_ids = set(warning_ids)
        unknown_acknowledgements = sorted(
            set(plan["acknowledged_warning_ids"]) - known_warning_ids
        )
        if unknown_acknowledgements:
            errors.append(
                f"plan {plan_id} acknowledges unknown warnings {unknown_acknowledgements!r}"
            )
        for warning in warnings:
            if warning["code"] in BLOCKING_WARNING_CODES and warning["severity"] != "blocking":
                errors.append(
                    f"plan {plan_id} safety conflict {warning['code']} must be blocking"
                )
            if warning["code"] == "CRITICAL_COVERAGE_REMOVAL" and warning["severity"] != "warning":
                errors.append(
                    f"plan {plan_id} critical coverage removal must be an acknowledgeable warning"
                )
            for role_id in warning["role_ids"]:
                if role_id not in binding_by_role and role_id not in plan["removed_role_ids"]:
                    errors.append(f"plan {plan_id} warning references unknown role {role_id}")
            for risk_id in warning["risk_surface_ids"]:
                if risk_id not in expected_risks:
                    errors.append(f"plan {plan_id} warning references unknown risk {risk_id}")
        warned_critical = {
            risk_id
            for warning in warnings
            if warning["code"] == "CRITICAL_COVERAGE_REMOVAL"
            for risk_id in warning["risk_surface_ids"]
        }
        if uncovered_critical - warned_critical:
            errors.append(
                f"plan {plan_id} leaves critical risks uncovered without warning: "
                f"{sorted(uncovered_critical - warned_critical)!r}"
            )

    for round_id, round_plans in plans_by_round.items():
        ordered = sorted(round_plans, key=lambda entry: entry["revision"])
        actual = [entry["revision"] for entry in ordered]
        if actual != list(range(1, len(ordered) + 1)):
            errors.append(f"round {round_id} plan revisions must be contiguous from 1")
            continue
        first = ordered[0]
        if (
            first["parent_plan_revision_id"] is not None
            or first["operation"] != "generate"
            or first["created_by"] != "main"
        ):
            errors.append(f"round {round_id} must begin with a main-generated plan")
        if any(
            role_by_revision.get(binding["role_revision_id"], {}).get("source")
            != "main_generated"
            for binding in first["role_bindings"]
        ):
            errors.append(f"round {round_id} initial plan must contain main-generated roles")
        for previous, current in zip(ordered, ordered[1:]):
            if current["parent_plan_revision_id"] != previous["plan_revision_id"]:
                errors.append(f"round {round_id} plan revisions must form a linear history")
            errors.extend(
                _plan_operation_errors(previous, current, role_by_revision)
            )
            previous_profile = previous.get("complexity_profile")
            current_profile = current.get("complexity_profile")
            if (
                previous_profile is not None
                and current_profile is not None
                and previous_profile["range"] != current_profile["range"]
            ):
                if current["operation"] != "regenerate":
                    errors.append(
                        f"plan {current['plan_revision_id']} complexity range change requires regenerate"
                    )
                if current["created_by"] == "user" and not current_profile[
                    "user_adjusted"
                ]:
                    errors.append(
                        f"plan {current['plan_revision_id']} user-requested complexity range change requires user_adjusted"
                    )
        round_entry = round_by_id.get(round_id)
        if round_entry and round_entry["active_plan_revision_id"] != ordered[-1]["plan_revision_id"]:
            errors.append(f"round {round_id} active plan is not its latest revision")

    for source in sources:
        source_id = source["source_artifact_id"]
        if source["round_id"] not in round_by_id:
            errors.append(f"source {source_id} references unknown round")
        if source["source_text"] is not None:
            if source["raw_digest"] != raw_text_digest(source["source_text"]):
                errors.append(f"source {source_id} raw digest mismatch")
        if source["retention"] == "digest_only" and source["source_text"] is not None:
            errors.append(f"digest-only source {source_id} must omit source_text")

    for preview in imports:
        preview_id = preview["import_preview_id"]
        source = source_by_id.get(preview["source_artifact_id"])
        if source is None:
            errors.append(f"import preview {preview_id} references unknown source")
        elif source["round_id"] != preview["round_id"]:
            errors.append(f"import preview {preview_id} uses a source from another round")
        elif (
            source["origin"] == "external_prompt"
            and "UNVERIFIABLE_ORIGIN" not in preview["warning_codes"]
        ):
            errors.append(
                f"external import preview {preview_id} must disclose unverifiable origin"
            )
        if preview["round_id"] not in round_by_id:
            errors.append(f"import preview {preview_id} references unknown round")
        if preview["operation"] == "import_add" and preview["target_role_id"] is not None:
            errors.append(f"import-add preview {preview_id} must not target an existing role")
        if preview["operation"] != "import_add" and preview["target_role_id"] is None:
            errors.append(f"import preview {preview_id} requires a target role")
        if preview["target_role_id"] is not None:
            target_roles = [
                role
                for role in roles
                if role["role_id"] == preview["target_role_id"]
                and role["round_id"] == preview["round_id"]
            ]
            if not target_roles:
                errors.append(f"import preview {preview_id} targets an unknown round role")
        has_conflict = any(
            change["disposition"] == "conflicting"
            for change in preview["field_changes"]
        ) or bool(set(preview["warning_codes"]) & BLOCKING_WARNING_CODES)
        result_id = preview["result_role_revision_id"]
        if preview["status"] == "applied":
            if result_id is None or result_id not in role_by_revision:
                errors.append(f"applied import preview {preview_id} requires a result role")
            elif role_by_revision[result_id]["source_artifact_id"] != preview["source_artifact_id"]:
                errors.append(f"import preview {preview_id} result does not bind its source")
            elif role_by_revision[result_id]["round_id"] != preview["round_id"]:
                errors.append(f"import preview {preview_id} result belongs to another round")
            if has_conflict:
                errors.append(f"import preview {preview_id} applies a blocking conflict")
        elif result_id is not None:
            errors.append(f"non-applied import preview {preview_id} must not have a result role")

    applied_imports = {
        (preview["round_id"], preview["operation"], preview["result_role_revision_id"])
        for preview in imports
        if preview["status"] == "applied"
        and preview["result_role_revision_id"] is not None
    }
    for preview in imports:
        if preview["status"] != "applied" or preview["result_role_revision_id"] is None:
            continue
        matching_plans = [
            plan
            for plan in plans
            if plan["round_id"] == preview["round_id"]
            and plan["operation"] == preview["operation"]
            and preview["result_role_revision_id"]
            in {
                binding["role_revision_id"]
                for binding in plan["role_bindings"]
            }
        ]
        if not matching_plans:
            continue
        warning_codes = {
            warning["code"]
            for plan in matching_plans
            for warning in plan["warnings"]
        }
        missing_warning_codes = sorted(
            set(preview["warning_codes"]) - warning_codes
        )
        if missing_warning_codes:
            errors.append(
                f"import preview {preview['import_preview_id']} warnings were not transferred "
                f"to its plan revision: {missing_warning_codes!r}"
            )
    for plan in plans:
        if plan["operation"] not in {"import_add", "import_replace", "import_merge"}:
            continue
        bound_revisions = {
            binding["role_revision_id"] for binding in plan["role_bindings"]
        }
        if not any(
            (plan["round_id"], plan["operation"], revision_id) in applied_imports
            for revision_id in bound_revisions
        ):
            errors.append(
                f"plan {plan['plan_revision_id']} import operation has no applied preview result"
            )

    event_sequences = [event["sequence"] for event in events]
    if event_sequences and event_sequences != list(range(1, len(events) + 1)):
        errors.append("events must appear in contiguous sequence order starting at 1")
    events_by_round: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        event_id = event["event_id"]
        if event["meeting_id"] != meeting["meeting_id"]:
            errors.append(f"event {event_id} belongs to another meeting")
        round_entry = round_by_id.get(event["round_id"])
        if round_entry is None:
            errors.append(f"event {event_id} references unknown round")
        elif event["state_version"] > round_entry["state_version"]:
            errors.append(f"event {event_id} exceeds its round state version")
        events_by_round[event["round_id"]].append(event)
        plan_id = event["plan_revision_id"]
        role_revision_id = event["role_revision_id"]
        if plan_id is not None and plan_id not in plan_by_id:
            errors.append(f"event {event_id} references unknown plan")
        elif plan_id is not None and plan_by_id[plan_id]["round_id"] != event["round_id"]:
            errors.append(f"event {event_id} references a plan from another round")
        if role_revision_id is not None and role_revision_id not in role_by_revision:
            errors.append(f"event {event_id} references unknown role revision")
        elif (
            role_revision_id is not None
            and role_by_revision[role_revision_id]["round_id"] != event["round_id"]
        ):
            errors.append(f"event {event_id} references a role from another round")

    for round_entry in rounds:
        round_id = round_entry["round_id"]
        types = [event["type"] for event in events_by_round.get(round_id, [])]
        if round_entry["active_plan_revision_id"] is not None and "roles_generated" not in types:
            errors.append(f"round {round_id} has a plan without roles_generated event")
        if round_entry["frozen_plan_revision_id"] is not None and "role_slate_frozen" not in types:
            errors.append(f"round {round_id} is frozen without role_slate_frozen event")
        if "role_slate_frozen" in types and "roles_generated" in types:
            if types.index("role_slate_frozen") <= types.index("roles_generated"):
                errors.append(f"round {round_id} froze roles before generation")

        freeze_events = [
            event
            for event in events_by_round.get(round_id, [])
            if event["type"] == "role_slate_frozen"
        ]
        if freeze_events and not any(
            event["plan_revision_id"] == round_entry["frozen_plan_revision_id"]
            for event in freeze_events
        ):
            errors.append(f"round {round_id} freeze event does not bind its frozen plan")

        frozen_id = round_entry["frozen_plan_revision_id"]
        if frozen_id is not None and frozen_id in plan_by_id:
            frozen = plan_by_id[frozen_id]
            warning_ids = {warning["warning_id"] for warning in frozen["warnings"]}
            acknowledged = set(frozen["acknowledged_warning_ids"])
            blocking = {
                warning["warning_id"]
                for warning in frozen["warnings"]
                if warning["severity"] == "blocking"
            }
            if blocking:
                errors.append(f"round {round_id} freezes a plan with blocking conflicts")
            missing_ack = warning_ids - acknowledged
            if missing_ack:
                errors.append(
                    f"round {round_id} freezes unacknowledged warnings {sorted(missing_ack)!r}"
                )

    for key, path in _walk_keys(payload):
        if key.lower() in PROHIBITED_KEYS:
            errors.append(f"prohibited private-reasoning field at {path}")

    return errors


def validate_payload(
    payload: dict[str, Any],
    schema: dict[str, Any],
    enum_lock: dict[str, Any],
) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"schema contract: {error}"
        for error in stable_enum_errors(schema, enum_lock)
    ]
    errors.extend(
        f"schema {'.'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
        for error in sorted(
            validator.iter_errors(payload), key=lambda entry: list(entry.absolute_path)
        )
    )
    if not errors:
        errors.extend(semantic_errors(payload))
    return errors


def validate(
    payload_path: Path,
    schema_path: Path = DEFAULT_SCHEMA,
    enum_lock_path: Path = DEFAULT_ENUM_LOCK,
) -> list[str]:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    enum_lock = json.loads(enum_lock_path.read_text(encoding="utf-8"))
    return validate_payload(payload, schema, enum_lock)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--enum-lock", type=Path, default=DEFAULT_ENUM_LOCK)
    parser.add_argument(
        "--print-computed-digests",
        action="store_true",
        help="print normative role, plan, and retained-source digests",
    )
    args = parser.parse_args()

    payload_path = args.payload.resolve()
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    if args.print_computed_digests:
        computed = {
            "role_revisions": {
                entry["role_revision_id"]: canonical_digest(entry)
                for entry in payload.get("role_revisions", [])
            },
            "plan_revisions": {
                entry["plan_revision_id"]: canonical_digest(entry)
                for entry in payload.get("plan_revisions", [])
            },
            "source_artifacts": {
                entry["source_artifact_id"]: (
                    raw_text_digest(entry["source_text"])
                    if entry.get("source_text") is not None
                    else entry.get("raw_digest")
                )
                for entry in payload.get("source_artifacts", [])
            },
        }
        print(json.dumps(computed, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    errors = validate(payload_path, args.schema.resolve(), args.enum_lock.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid: {args.payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
