#!/usr/bin/env python3
"""Validate a public panel output against the v1 schema and semantic rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "panel-output.schema.json"
DEFAULT_ENUM_LOCK = REPO_ROOT / "schemas" / "stable-enums.v1.json"
STAGES = ("ideate", "design", "converge", "review")
ENUM_PATHS = {
    "schema_version": ("properties", "schema_version", "enum"),
    "run.mode": ("$defs", "run", "properties", "mode", "enum"),
    "stage": ("$defs", "stage", "enum"),
    "perspective.status": ("$defs", "perspective", "properties", "status", "enum"),
    "perspective.executor": ("$defs", "perspective", "properties", "executor", "enum"),
    "failure.code": ("$defs", "failure", "properties", "code", "enum"),
    "item.kind": ("$defs", "item", "properties", "kind", "enum"),
    "item.severity": ("$defs", "item", "properties", "severity", "enum"),
    "item.confidence": ("$defs", "item", "properties", "confidence", "enum"),
    "decision.status": ("$defs", "decision", "properties", "status", "enum"),
    "coverage.status": ("$defs", "coverage", "properties", "status", "enum"),
    "orchestration.execution": (
        "$defs",
        "orchestration",
        "properties",
        "execution",
        "enum",
    ),
    "gate.state": ("$defs", "gate", "properties", "state", "enum"),
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


def _version_tuple(value: Any) -> tuple[int, int] | None:
    if not isinstance(value, str):
        return None
    parts = value.split(".")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        return None
    return int(parts[0]), int(parts[1])


def _schema_minor_at_least(payload: dict[str, Any], minor: int) -> bool:
    version = _version_tuple(payload.get("schema_version"))
    return version is not None and version[0] == 1 and version[1] >= minor


def _schema_value(schema: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = schema
    for part in path:
        value = value[part]
    return value


def stable_enum_errors(
    schema: dict[str, Any], enum_lock: dict[str, Any]
) -> list[str]:
    """Check the frozen v1 enum baseline and versioned additive metadata."""

    errors: list[str] = []
    locked_enums = enum_lock.get("enums", {})
    additions = enum_lock.get("additions", {})
    locked_version = enum_lock.get("locked_through_schema_version")
    locked_version_tuple = _version_tuple(locked_version)

    if locked_version_tuple is None:
        errors.append("stable enum lock has invalid locked_through_schema_version")
    if set(locked_enums) != set(ENUM_PATHS):
        errors.append("stable enum lock and schema paths differ")
        return errors
    unknown_addition_paths = sorted(set(additions) - set(ENUM_PATHS))
    if unknown_addition_paths:
        errors.append(f"stable enum additions use unknown paths: {unknown_addition_paths}")

    try:
        actual = {
            name: _schema_value(schema, path) for name, path in ENUM_PATHS.items()
        }
    except (KeyError, TypeError):
        errors.append("schema is missing a stable enum path")
        return errors

    supported_versions = actual["schema_version"]
    schema_major = enum_lock.get("schema_major")
    if schema_major != 1:
        errors.append("stable enum lock schema_major must remain 1 for the v1 lock")
    supported_version_tuples = [_version_tuple(value) for value in supported_versions]
    if any(
        version is None or version[0] != schema_major
        for version in supported_version_tuples
    ):
        errors.append("schema versions do not match the stable enum lock major")
    if locked_version not in supported_versions:
        errors.append(
            f"schema does not support locked enum baseline version {locked_version!r}"
        )

    for name, baseline_values in locked_enums.items():
        expected_values = list(baseline_values)
        seen_additions: list[Any] = []
        for addition in additions.get(name, []):
            if not isinstance(addition, dict) or set(addition) != {"value", "introduced_in"}:
                errors.append(f"stable enum addition for {name} has invalid metadata")
                continue
            value = addition["value"]
            introduced_in = addition["introduced_in"]
            introduced_tuple = _version_tuple(introduced_in)
            if value in baseline_values or value in seen_additions:
                errors.append(f"stable enum addition for {name} duplicates {value!r}")
            seen_additions.append(value)
            if introduced_tuple is None:
                errors.append(
                    f"stable enum addition {name}={value!r} has invalid introduced_in"
                )
            else:
                if introduced_tuple[0] != schema_major:
                    errors.append(
                        f"stable enum addition {name}={value!r} changes schema major"
                    )
                if locked_version_tuple is not None and introduced_tuple <= locked_version_tuple:
                    errors.append(
                        f"stable enum addition {name}={value!r} must use a schema minor after {locked_version}"
                    )
                if introduced_in not in supported_versions:
                    errors.append(
                        f"stable enum addition {name}={value!r} uses unsupported schema version {introduced_in}"
                    )
            expected_values.append(value)

        if actual[name] != expected_values:
            errors.append(
                f"schema enum {name} differs from stable lock: expected {expected_values!r}, got {actual[name]!r}"
            )

    return errors


def _replacement_cycle_errors(
    perspective_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(perspective_id: str) -> None:
        state[perspective_id] = 1
        stack.append(perspective_id)
        replacement = perspective_by_id[perspective_id].get("replacement_perspective_id")
        if replacement in perspective_by_id and replacement != perspective_id:
            if state.get(replacement) == 1:
                start = stack.index(replacement)
                cycle = stack[start:] + [replacement]
                errors.append(f"replacement cycle: {' -> '.join(cycle)}")
            elif state.get(replacement, 0) == 0:
                visit(replacement)
        stack.pop()
        state[perspective_id] = 2

    for perspective_id in perspective_by_id:
        if state.get(perspective_id, 0) == 0:
            visit(perspective_id)
    return errors


def _ordered_stage_errors(
    collection_name: str, identifier_key: str, entries: list[dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    stages: list[str] = []
    for entry in entries:
        stage = entry.get("stage")
        if not stage:
            identifier = entry.get(identifier_key, "unknown")
            errors.append(f"full_cycle {collection_name} {identifier} has no stage")
        elif stage in STAGES:
            stages.append(stage)
    indexes = [STAGES.index(stage) for stage in stages]
    if indexes != sorted(indexes):
        errors.append(
            f"full_cycle {collection_name} stages are out of order: {stages!r}"
        )
    return errors


def semantic_errors(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    perspectives = payload.get("perspectives", [])
    items = payload.get("items", [])
    decisions = payload.get("decisions", [])
    coverage = payload.get("coverage", [])

    perspective_ids = [entry["perspective_id"] for entry in perspectives]
    item_ids = [entry["item_id"] for entry in items]
    decision_ids = [entry["decision_id"] for entry in decisions]

    for label, values in (
        ("perspective_id", perspective_ids),
        ("item_id", item_ids),
        ("decision_id", decision_ids),
    ):
        for duplicate in sorted(_duplicates(values)):
            errors.append(f"duplicate {label}: {duplicate}")

    perspective_set = set(perspective_ids)
    item_set = set(item_ids)
    perspective_by_id = {entry["perspective_id"]: entry for entry in perspectives}
    item_by_id = {entry["item_id"]: entry for entry in items}

    if payload.get("schema_version") == "1.2":
        meeting = payload.get("meeting", {})
        meeting_round_id = meeting.get("round_id")
        if run_mode := payload.get("run", {}).get("mode"):
            if run_mode == "full_cycle":
                errors.append(
                    "schema 1.2 is a closed-round result; full_cycle must emit one result per stage round"
                )
        role_revision_by_role: dict[str, str] = {}
        role_by_perspective: dict[str, str] = {}
        for perspective in perspectives:
            perspective_id = perspective["perspective_id"]
            role_id = perspective.get("role_id")
            role_revision_id = perspective.get("role_revision_id")
            role_by_perspective[perspective_id] = role_id
            if perspective.get("round_id") != meeting_round_id:
                errors.append(
                    f"perspective {perspective_id} does not belong to meeting round {meeting_round_id}"
                )
            prior_revision = role_revision_by_role.setdefault(role_id, role_revision_id)
            if prior_revision != role_revision_id:
                errors.append(
                    f"role {role_id} uses multiple frozen revisions in one round"
                )
        for perspective in perspectives:
            replacement_id = perspective.get("replacement_perspective_id")
            if perspective.get("status") != "replaced" or not replacement_id:
                continue
            replacement = perspective_by_id.get(replacement_id)
            if replacement is not None and (
                replacement.get("role_id") != perspective.get("role_id")
                or replacement.get("role_revision_id")
                != perspective.get("role_revision_id")
            ):
                errors.append(
                    f"replacement {replacement_id} does not preserve frozen role revision from "
                    f"{perspective['perspective_id']}"
                )

        for item in items:
            perspective = perspective_by_id.get(item["perspective_id"])
            if item.get("round_id") != meeting_round_id:
                errors.append(
                    f"item {item['item_id']} does not belong to meeting round {meeting_round_id}"
                )
            if perspective is not None and item.get("round_id") != perspective.get("round_id"):
                errors.append(
                    f"item {item['item_id']} round does not match its perspective"
                )
        for decision in decisions:
            if decision.get("round_id") != meeting_round_id:
                errors.append(
                    f"decision {decision['decision_id']} does not belong to meeting round {meeting_round_id}"
                )
            source_rounds = {
                item_by_id[item_id].get("round_id")
                for item_id in decision["source_item_ids"]
                if item_id in item_by_id
            }
            if source_rounds - {meeting_round_id}:
                errors.append(
                    f"decision {decision['decision_id']} cites an item from another round"
                )
        coverage_ids = [entry.get("risk_surface_id") for entry in coverage]
        for duplicate in sorted(_duplicates(coverage_ids)):
            errors.append(f"duplicate risk_surface_id: {duplicate}")
        for entry in coverage:
            risk_surface_id = entry.get("risk_surface_id")
            if entry.get("round_id") != meeting_round_id:
                errors.append(
                    f"coverage {risk_surface_id} does not belong to meeting round {meeting_round_id}"
                )
            planned_roles = set(entry.get("planned_role_ids", []))
            for item_id in entry["evidence_item_ids"]:
                item = item_by_id.get(item_id)
                if item is None:
                    continue
                if risk_surface_id not in item.get("risk_surface_ids", []):
                    errors.append(
                        f"coverage {risk_surface_id} cites item {item_id} that does not claim that risk surface"
                    )
                evidence_role = role_by_perspective.get(item["perspective_id"])
                if evidence_role not in planned_roles:
                    errors.append(
                        f"coverage {risk_surface_id} cites item {item_id} from unplanned role {evidence_role}"
                    )

    for item in items:
        if item["perspective_id"] not in perspective_set:
            errors.append(
                f"item {item['item_id']} references unknown perspective {item['perspective_id']}"
            )
        else:
            item_stage = item.get("stage")
            perspective_stage = perspective_by_id[item["perspective_id"]].get("stage")
            if item_stage is not None and perspective_stage is not None and item_stage != perspective_stage:
                errors.append(
                    f"item {item['item_id']} stage {item_stage} does not match perspective "
                    f"{item['perspective_id']} stage {perspective_stage}"
                )

    run_mode = payload.get("run", {}).get("mode")
    for item in items:
        item_stage = item.get("stage")
        if item["kind"] == "risk" and (run_mode == "ideate" or item_stage == "ideate"):
            if item.get("severity") is not None:
                errors.append(f"ideate risk {item['item_id']} must not use severity")

    for decision in decisions:
        known_source_items = [
            item_by_id[item_id]
            for item_id in decision["source_item_ids"]
            if item_id in item_by_id
        ]
        for item_id in decision["source_item_ids"]:
            if item_id not in item_set:
                errors.append(
                    f"decision {decision['decision_id']} references unknown item {item_id}"
                )
        decision_stage = decision.get("stage")
        if decision_stage is not None:
            if known_source_items:
                later_sources = [
                    item["item_id"]
                    for item in known_source_items
                    if item.get("stage") in STAGES
                    and STAGES.index(item["stage"]) > STAGES.index(decision_stage)
                ]
                if later_sources:
                    errors.append(
                        f"decision {decision['decision_id']} stage {decision_stage} references later-stage "
                        f"items {later_sources!r}"
                    )
            if run_mode == "full_cycle" and not any(
                item.get("stage") == decision_stage
                and perspective_by_id.get(item["perspective_id"], {}).get("status")
                == "completed"
                for item in known_source_items
            ):
                errors.append(
                    f"full_cycle decision {decision['decision_id']} stage {decision_stage} has no "
                    "same-stage source item from a completed perspective"
                )

    for entry in coverage:
        for item_id in entry["evidence_item_ids"]:
            if item_id not in item_set:
                errors.append(
                    f"coverage {entry['risk_surface']!r} references unknown item {item_id}"
                )
                continue
            item = item_by_id[item_id]
            perspective_id = item["perspective_id"]
            if not item.get("evidence"):
                errors.append(
                    f"coverage {entry['risk_surface']!r} references item {item_id} without public evidence"
                )
            if perspective_id not in perspective_by_id:
                continue
            if perspective_by_id[perspective_id]["status"] != "completed":
                errors.append(
                    f"coverage {entry['risk_surface']!r} references item {item_id} from non-completed "
                    f"perspective {perspective_id}"
                )
        if entry["status"] == "covered" and not entry["evidence_item_ids"]:
            errors.append(
                f"coverage {entry['risk_surface']!r} is covered without evidence items"
            )

    for item_id in payload.get("gate", {}).get("unresolved_item_ids", []):
        if item_id not in item_set:
            errors.append(f"gate references unknown unresolved item {item_id}")

    replacement_sources: dict[str, list[str]] = {}
    perspective_positions = {
        perspective["perspective_id"]: index
        for index, perspective in enumerate(perspectives)
    }
    for perspective in perspectives:
        perspective_id = perspective["perspective_id"]
        status = perspective["status"]
        failure = perspective.get("failure")
        replacement = perspective.get("replacement_perspective_id")
        if status in {"failed", "replaced"} and not failure:
            errors.append(
                f"perspective {perspective_id} is {status} but has no failure"
            )
        if status == "completed" and failure:
            errors.append(
                f"perspective {perspective_id} completed but still has a failure"
            )
        if status in {"completed", "failed"} and replacement:
            errors.append(
                f"perspective {perspective_id} is {status} but has a replacement"
            )
        if status == "replaced":
            if not replacement:
                errors.append(
                    f"perspective {perspective_id} is replaced without replacement_perspective_id"
                )
            elif replacement not in perspective_by_id:
                errors.append(
                    f"perspective {perspective_id} references unknown replacement {replacement}"
                )
            elif replacement == perspective_id:
                errors.append(f"perspective {perspective_id} cannot replace itself")
            else:
                target = perspective_by_id[replacement]
                replacement_sources.setdefault(replacement, []).append(perspective_id)
                if perspective_positions[replacement] <= perspective_positions[perspective_id]:
                    errors.append(
                        f"replacement perspective {replacement} must appear after {perspective_id}"
                    )
                if target.get("lens") != perspective.get("lens"):
                    errors.append(
                        f"replacement {replacement} does not preserve lens from {perspective_id}"
                    )
                if target.get("stage") != perspective.get("stage"):
                    errors.append(
                        f"replacement {replacement} does not preserve stage from {perspective_id}"
                    )

    for replacement, sources in replacement_sources.items():
        if len(sources) > 1:
            errors.append(
                f"replacement perspective {replacement} has multiple sources: {sorted(sources)!r}"
            )
    errors.extend(_replacement_cycle_errors(perspective_by_id))

    orchestration = payload.get("orchestration")
    if orchestration:
        execution = orchestration["execution"]
        degraded = orchestration["degraded"]
        waves = orchestration["waves"]
        executors = {
            perspective["perspective_id"]: perspective.get("executor")
            for perspective in perspectives
        }
        if _schema_minor_at_least(payload, 1):
            for perspective_id, executor in executors.items():
                if executor is None:
                    errors.append(
                        f"schema {payload.get('schema_version')} perspective {perspective_id} has no executor"
                    )

        if execution in {"single_session_fallback", "mixed"} and not degraded:
            errors.append(f"orchestration execution {execution} must be degraded")
        if any(
            perspective["status"] in {"failed", "replaced"}
            for perspective in perspectives
        ) and not degraded:
            errors.append("orchestration with failed or replaced perspectives must be degraded")

        executor_values = set(executors.values())
        if execution == "single_session_fallback":
            if executor_values - {"main_session"}:
                errors.append(
                    "single_session_fallback requires every perspective executor to be main_session"
                )
            if waves:
                errors.append("single_session_fallback must not declare subagent waves")
        elif execution == "mixed":
            if not {"subagent", "main_session"}.issubset(executor_values):
                errors.append("mixed execution requires subagent and main_session perspectives")
            if not waves:
                errors.append("mixed execution requires at least one subagent wave")
        else:
            if executor_values - {"subagent"}:
                errors.append(f"{execution} execution requires subagent perspectives")
            expected_wave_count = 1 if execution == "subagents" else None
            if expected_wave_count is not None and len(waves) != expected_wave_count:
                errors.append("subagents execution requires exactly one wave")
            if execution == "waves" and len(waves) < 2:
                errors.append("waves execution requires at least two waves")

        flattened_waves = [perspective_id for wave in waves for perspective_id in wave]
        for duplicate in sorted(_duplicates(flattened_waves)):
            errors.append(f"perspective {duplicate} appears in multiple orchestration waves")
        for perspective_id in flattened_waves:
            if perspective_id not in perspective_set:
                errors.append(
                    f"orchestration wave references unknown perspective {perspective_id}"
                )
            elif executors[perspective_id] != "subagent":
                errors.append(
                    f"orchestration wave includes non-subagent perspective {perspective_id}"
                )

        expected_wave_ids = {
            perspective_id
            for perspective_id, executor in executors.items()
            if executor == "subagent"
        }
        actual_wave_ids = set(flattened_waves) & perspective_set
        for perspective_id in sorted(expected_wave_ids - actual_wave_ids):
            errors.append(
                f"subagent perspective {perspective_id} is missing from orchestration waves"
            )

        wave_positions = {
            perspective_id: index
            for index, wave in enumerate(waves)
            for perspective_id in wave
        }
        for perspective in perspectives:
            replacement = perspective.get("replacement_perspective_id")
            if perspective["status"] != "replaced" or not replacement:
                continue
            if perspective["perspective_id"] in wave_positions and replacement in wave_positions:
                if wave_positions[replacement] <= wave_positions[perspective["perspective_id"]]:
                    errors.append(
                        f"replacement perspective {replacement} must run in a later wave than "
                        f"{perspective['perspective_id']}"
                    )

    if payload.get("run", {}).get("mode") == "full_cycle":
        for collection_name, identifier_key, entries in (
            ("perspective", "perspective_id", perspectives),
            ("item", "item_id", items),
            ("decision", "decision_id", decisions),
        ):
            errors.extend(_ordered_stage_errors(collection_name, identifier_key, entries))

        completed_stages = {
            perspective.get("stage")
            for perspective in perspectives
            if perspective["status"] == "completed"
        }
        missing_completed_stages = [
            stage for stage in STAGES if stage not in completed_stages
        ]
        if missing_completed_stages:
            errors.append(
                "full_cycle has no completed perspective for stages: "
                + ", ".join(missing_completed_stages)
            )
        item_stages = {item.get("stage") for item in items}
        missing_item_stages = [stage for stage in STAGES if stage not in item_stages]
        if missing_item_stages:
            errors.append(
                "full_cycle has no public item for stages: "
                + ", ".join(missing_item_stages)
            )

        if orchestration:
            wave_stages: list[str] = []
            for index, wave in enumerate(orchestration["waves"]):
                stages = {
                    perspective_by_id[perspective_id].get("stage")
                    for perspective_id in wave
                    if perspective_id in perspective_by_id
                }
                stages.discard(None)
                if len(stages) > 1:
                    errors.append(
                        f"full_cycle orchestration wave {index + 1} mixes stages: {sorted(stages)!r}"
                    )
                elif stages:
                    wave_stages.append(next(iter(stages)))
            wave_indexes = [STAGES.index(stage) for stage in wave_stages]
            if wave_indexes != sorted(wave_indexes):
                errors.append(
                    f"full_cycle orchestration waves are out of stage order: {wave_stages!r}"
                )

    if payload.get("gate", {}).get("state") == "go":
        if not perspectives:
            errors.append("gate is go without any perspective")
        if not items:
            errors.append("gate is go without any public item")
        if _schema_minor_at_least(payload, 1) and not coverage:
            errors.append("gate is go without declared risk-surface coverage")
        unresolved = set(payload["gate"]["unresolved_item_ids"])
        for item in items:
            if item.get("severity") in {"blocker", "high"}:
                errors.append(
                    f"gate is go with {item['severity']} item {item['item_id']}"
                )
        for entry in coverage:
            if entry.get("critical") and entry["status"] != "covered":
                errors.append(
                    f"gate is go with critical risk surface {entry['risk_surface']!r} marked {entry['status']}"
                )
            if entry.get("critical"):
                evidence_ids = entry["evidence_item_ids"]
                evidence_backed = bool(evidence_ids) and all(
                    item_id in item_by_id and item_by_id[item_id].get("evidence")
                    for item_id in evidence_ids
                )
                if not evidence_backed:
                    errors.append(
                        f"gate is go without evidence-backed critical risk surface {entry['risk_surface']!r}"
                    )

    for key, path in _walk_keys(payload):
        if key.lower() in PROHIBITED_KEYS:
            errors.append(f"prohibited private-reasoning field at {path}")

    return errors


def validate(payload_path: Path, schema_path: Path = DEFAULT_SCHEMA) -> list[str]:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    enum_lock = json.loads(DEFAULT_ENUM_LOCK.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [f"schema contract: {error}" for error in stable_enum_errors(schema, enum_lock)]
    errors.extend(
        f"schema {'.'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
        for error in sorted(validator.iter_errors(payload), key=lambda err: list(err.absolute_path))
    )
    if not errors:
        errors.extend(semantic_errors(payload))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    errors = validate(args.payload.resolve(), args.schema.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid: {args.payload}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
