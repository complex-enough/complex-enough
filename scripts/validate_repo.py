#!/usr/bin/env python3
"""Run deterministic repository, metadata, schema, and eval-suite checks."""

from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from jsonschema import Draft202012Validator, FormatChecker

from validate_panel_output import validate
from render_eval_prompt import render_prompt


ROOT = Path(__file__).resolve().parents[1]
CORE_RUNTIME_FILES = [
    "SKILL.md",
    "adapters/codex.md",
    "adapters/claude-code.md",
    "references/modes-and-selection.md",
    "references/panelist-protocol.md",
    "references/authority-and-fallback.md",
    "references/model-and-execution-policy.md",
    "references/panel-output-contract.md",
    "schemas/panel-output.schema.json",
    "schemas/stable-enums.v1.json",
]
HOST_RUNTIME_FILES = {
    "codex": ["agents/openai.yaml"],
    "claude-code": [],
}
EVAL_HARNESS_FILES = [
    "scripts/render_eval_prompt.py",
    "schemas/eval-result.schema.json",
    "schemas/eval-artifact.schema.json",
]
REQUIRED_CASE_TAGS = {
    "ideate",
    "design",
    "converge",
    "review",
    "mobile",
    "api",
    "customer",
    "accounting",
    "identity",
    "permission",
    "conflict",
    "runtime_evidence",
    "slots",
    "timeout",
    "unavailable",
    "gui",
    "concise",
    "full_cycle",
    "trigger",
    "platform",
    "portable",
}
REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "adapters/codex.md",
    "adapters/claude-code.md",
    "references/modes-and-selection.md",
    "references/panelist-protocol.md",
    "references/authority-and-fallback.md",
    "references/model-and-execution-policy.md",
    "references/panel-output-contract.md",
    "schemas/panel-output.schema.json",
    "schemas/eval-artifact.schema.json",
    "schemas/eval-result.schema.json",
    "schemas/stable-enums.v1.json",
    "evals/cases.json",
    "evals/results/codex-2026-08-10.json",
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "CLAUDE.md",
]


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_skill() -> None:
    skill_path = ROOT / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    if len(text.splitlines()) >= 500:
        fail("SKILL.md must stay below 500 lines")
    if not text.startswith("---\n"):
        fail("SKILL.md frontmatter is missing")
    _, frontmatter, _ = text.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    if set(metadata) != {"name", "description"}:
        fail("SKILL.md frontmatter must contain only name and description")
    if metadata["name"] != "orchestrate-multi-perspective-panel":
        fail("unexpected skill name")
    description = metadata["description"]
    if len(description) > 1024:
        fail("trigger description exceeds cross-platform 1024-character limit")
    for phrase in ("Use when", "Do not use"):
        if phrase not in description:
            fail(f"trigger description must include {phrase!r}")


def validate_openai_yaml() -> None:
    payload = yaml.safe_load((ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    interface = payload["interface"]
    if not 25 <= len(interface["short_description"]) <= 64:
        fail("short_description must be 25-64 characters")
    if "$orchestrate-multi-perspective-panel" not in interface["default_prompt"]:
        fail("default_prompt must name the skill")


def validate_evals() -> None:
    suite = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    if suite.get("target_platforms") != ["codex", "claude-code"]:
        fail("eval suite must declare Codex and Claude Code targets")
    cases = suite["cases"]
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)):
        fail("eval case ids must be unique")
    tags = {tag for case in cases for tag in case["tags"]}
    missing = REQUIRED_CASE_TAGS - tags
    if missing:
        fail(f"eval suite missing required tags: {sorted(missing)}")
    for case in cases:
        if not case["assertions"]:
            fail(f"eval case {case['id']} has no assertions")
        for relative in case["fixtures"]:
            fixture = ROOT / "evals" / relative
            if not fixture.is_file():
                fail(f"eval case {case['id']} missing fixture {relative}")


def runtime_revision(host: str) -> str:
    digest = hashlib.sha256()
    for relative in CORE_RUNTIME_FILES + HOST_RUNTIME_FILES[host]:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((ROOT / relative).read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def eval_suite_revision(
    suite: dict,
    fixture_root: Path | None = None,
    repository_root: Path | None = None,
) -> str:
    """Bind an eval result to every suite field and, when available, fixture bytes."""
    digest = hashlib.sha256()
    digest.update(
        json.dumps(suite, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    )
    if fixture_root is not None:
        fixture_paths = sorted(
            {
                relative
                for case in suite["cases"]
                for relative in case.get("fixtures", [])
            }
        )
        for relative in fixture_paths:
            digest.update(b"\0")
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update((fixture_root / relative).read_bytes())
    if repository_root is not None:
        for relative in EVAL_HARNESS_FILES:
            digest.update(b"\0")
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update((repository_root / relative).read_bytes())
    return "sha256:" + digest.hexdigest()


def _parsed_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        fail("eval timestamps must include a timezone")
    return parsed


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact_file:
        for chunk in iter(lambda: artifact_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def validate_eval_artifact(
    *,
    result_path: Path,
    result_case: dict,
    case_definition: dict,
    expected_host: str,
    expected_runtime_revision: str,
    expected_suite_revision: str,
    result_executed_at: datetime,
) -> None:
    relative = result_case.get("artifact_path")
    expected_digest = result_case.get("artifact_sha256")
    run_id = result_case.get("run_id")
    if not relative or not expected_digest or not run_id:
        fail(f"passing behavioral case {result_case['case_id']} has no captured artifact")

    eval_root = result_path.parent.parent.resolve()
    artifact_path = (eval_root / relative).resolve()
    try:
        artifact_path.relative_to(eval_root)
    except ValueError:
        fail(f"eval artifact escapes eval root: {relative}")
    if not artifact_path.is_file() or artifact_path.is_symlink():
        fail(f"missing or unsafe eval artifact: {relative}")
    if _sha256_file(artifact_path) != expected_digest:
        fail(f"eval artifact digest mismatch for {result_case['case_id']}")

    artifact_schema = json.loads(
        (ROOT / "schemas" / "eval-artifact.schema.json").read_text(encoding="utf-8")
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact_errors = sorted(
        Draft202012Validator(
            artifact_schema, format_checker=FormatChecker()
        ).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if artifact_errors:
        rendered = "; ".join(error.message for error in artifact_errors)
        fail(f"invalid eval artifact {relative}: {rendered}")
    expected_fields = {
        "case_id": result_case["case_id"],
        "host": expected_host,
        "run_id": run_id,
        "execution": result_case["execution"],
        "runtime_revision": expected_runtime_revision,
        "suite_revision": expected_suite_revision,
    }
    for field, expected in expected_fields.items():
        if artifact[field] != expected:
            fail(
                f"eval artifact {relative} has {field}={artifact[field]!r}, expected {expected!r}"
            )

    artifact_executed_at = _parsed_datetime(artifact["executed_at"])
    if artifact_executed_at > result_executed_at:
        fail(
            f"eval artifact {relative} was executed after its enclosing scorecard execution"
        )

    skill_path = Path(artifact["skill_path"]) if artifact["skill_path"] else None
    rendered_prompt = render_prompt(case_definition, expected_host, skill_path)
    prompt_digest = "sha256:" + hashlib.sha256(
        rendered_prompt.encode("utf-8")
    ).hexdigest()
    if artifact["prompt_sha256"] != prompt_digest:
        fail(f"eval artifact prompt digest mismatch for {result_case['case_id']}")

    prohibited_markers = (
        "chain_of_thought",
        "hidden_reasoning",
        "private_reasoning",
        "raw_panelist_report",
        "raw_transcript",
        "scratch_work",
        "thought_trace",
    )
    lowered_output = artifact["output"].lower()
    if any(marker in lowered_output for marker in prohibited_markers):
        fail(f"eval artifact {relative} contains a prohibited private-output marker")


def validate_eval_result(
    result_path: Path,
    suite: dict,
    schema: dict,
    expected_runtime_revisions: dict[str, str],
    expected_suite_revision: str | None = None,
) -> None:
    case_definitions = {case["id"]: case for case in suite["cases"]}
    known_case_ids = set(case_definitions)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    result = json.loads(result_path.read_text(encoding="utf-8"))
    errors = sorted(validator.iter_errors(result), key=lambda error: list(error.path))
    if errors:
        rendered = "; ".join(error.message for error in errors)
        fail(f"invalid eval result {result_path.name}: {rendered}")
    filename_hosts = {
        "codex-": "codex",
        "claude-code-": "claude-code",
        "static-only-": "static-only",
    }
    expected_host = next(
        (host for prefix, host in filename_hosts.items() if result_path.name.startswith(prefix)),
        None,
    )
    if expected_host is None:
        fail(f"eval result {result_path.name} must use a host-prefixed filename")
    if result["environment"]["host"] != expected_host:
        fail(f"eval result {result_path.name} claims the wrong host")
    if result["suite_version"] != suite["suite_version"]:
        fail(f"eval result {result_path.name} does not match the current suite version")
    expected_suite_revision = expected_suite_revision or eval_suite_revision(suite)
    if result["suite_revision"] != expected_suite_revision:
        fail(f"eval result {result_path.name} does not match the current suite revision")
    executed_at = _parsed_datetime(result["executed_at"])
    verified_at = _parsed_datetime(result["verified_at"])
    if verified_at < executed_at:
        fail(f"eval result {result_path.name} was verified before it was executed")
    now = datetime.now(timezone.utc)
    if executed_at.astimezone(timezone.utc) > now or verified_at.astimezone(timezone.utc) > now:
        fail(f"eval result {result_path.name} has a future timestamp")
    filename_date_match = re.match(
        r"^(?:codex|claude-code|static-only)-(\d{4}-\d{2}-\d{2})\.json$",
        result_path.name,
    )
    if not filename_date_match or executed_at.date().isoformat() != filename_date_match.group(1):
        fail(f"eval result {result_path.name} execution date does not match its filename")
    if expected_host in expected_runtime_revisions:
        if result["skill_revision"] != expected_runtime_revisions[expected_host]:
            fail(f"eval result {result_path.name} does not match the current runtime revision")
    result_case_ids = [case["case_id"] for case in result["cases"]]
    if len(result_case_ids) != len(set(result_case_ids)):
        fail(f"eval result {result_path.name} has duplicate case ids")
    unknown = set(result_case_ids) - known_case_ids
    if unknown:
        fail(f"eval result {result_path.name} has unknown case ids: {sorted(unknown)}")
    for result_case in result["cases"]:
        expected_assertions = case_definitions[result_case["case_id"]]["assertions"]
        scored_assertions = [item["assertion"] for item in result_case["assertions"]]
        if scored_assertions != expected_assertions:
            fail(f"eval result {result_path.name} does not score every assertion for {result_case['case_id']}")
        assertion_statuses = [item["status"] for item in result_case["assertions"]]
        expected_status = (
            "fail"
            if "fail" in assertion_statuses
            else "pass"
            if assertion_statuses and set(assertion_statuses) == {"pass"}
            else "not_run"
        )
        if result_case["status"] != expected_status:
            fail(f"eval result {result_path.name} has inconsistent status for {result_case['case_id']}")
        if result_case["status"] == "not_run" and result_case["execution"] != "not_run":
            fail(f"eval result {result_path.name} must mark unrun case execution for {result_case['case_id']}")
        if result_case["status"] != "not_run" and result_case["execution"] == "not_run":
            fail(f"eval result {result_path.name} cannot pass an unrun case {result_case['case_id']}")
        if expected_host in expected_runtime_revisions and result_case["status"] == "pass":
            if result_case["execution"] not in {"forward", "simulated_failure"}:
                fail(
                    f"behavioral eval result {result_path.name} uses non-behavioral execution "
                    f"for passing case {result_case['case_id']}"
                )
            if result_case["execution"] == "simulated_failure":
                capability = case_definitions[result_case["case_id"]]["capability"]
                if capability not in {"panelist_timeout", "subagents_unavailable"}:
                    fail(
                        f"eval result {result_path.name} simulates failure for unsupported case "
                        f"{result_case['case_id']}"
                    )
            validate_eval_artifact(
                result_path=result_path,
                result_case=result_case,
                case_definition=case_definitions[result_case["case_id"]],
                expected_host=expected_host,
                expected_runtime_revision=expected_runtime_revisions[expected_host],
                expected_suite_revision=expected_suite_revision,
                result_executed_at=executed_at,
            )
    failure_capabilities = {"panelist_timeout", "subagents_unavailable"}
    simulated_failure = any(
        case["execution"] == "simulated_failure" for case in result["cases"]
    )
    real_failure = any(
        case_definitions[case["case_id"]].get("capability") in failure_capabilities
        and case["execution"] == "forward"
        for case in result["cases"]
    )
    expected_failure_injection = (
        "mixed"
        if simulated_failure and real_failure
        else "simulated"
        if simulated_failure
        else "real"
        if real_failure
        else "none"
    )
    if result["environment"]["failure_injection"] != expected_failure_injection:
        fail(
            f"eval result {result_path.name} has failure_injection "
            f"{result['environment']['failure_injection']}, expected {expected_failure_injection}"
        )
    if expected_host in expected_runtime_revisions and set(result_case_ids) != known_case_ids:
        missing = known_case_ids - set(result_case_ids)
        fail(f"behavioral eval result {result_path.name} is missing cases: {sorted(missing)}")
    if expected_host in expected_runtime_revisions:
        expected_gate = "GO" if all(case["status"] == "pass" for case in result["cases"]) else "NO_GO"
        if result["gate"] != expected_gate:
            fail(f"eval result {result_path.name} has gate {result['gate']}, expected {expected_gate}")
    elif result["gate"] != "NO_GO":
        fail(f"static-only eval result {result_path.name} cannot claim GO")


def validate_eval_results() -> None:
    suite = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas" / "eval-result.schema.json").read_text(encoding="utf-8"))
    expected_revisions = {host: runtime_revision(host) for host in HOST_RUNTIME_FILES}
    expected_suite_revision = eval_suite_revision(suite, ROOT / "evals", ROOT)
    for result_path in sorted((ROOT / "evals" / "results").glob("*.json")):
        validate_eval_result(
            result_path,
            suite,
            schema,
            expected_revisions,
            expected_suite_revision,
        )


def validate_release_gate(result_path: Path) -> None:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("environment", {}).get("host") != "codex" or result.get("gate") != "GO":
        fail(f"required Codex release scorecard is not GO: {result_path.name}")


def validate_stable_enums() -> None:
    schema = json.loads((ROOT / "schemas" / "panel-output.schema.json").read_text(encoding="utf-8"))
    locked = json.loads((ROOT / "schemas" / "stable-enums.v1.json").read_text(encoding="utf-8"))["enums"]
    actual = {
        "schema_version": schema["properties"]["schema_version"]["enum"],
        "run.mode": schema["$defs"]["run"]["properties"]["mode"]["enum"],
        "stage": schema["$defs"]["stage"]["enum"],
        "perspective.status": schema["$defs"]["perspective"]["properties"]["status"]["enum"],
        "perspective.executor": schema["$defs"]["perspective"]["properties"]["executor"]["enum"],
        "failure.code": schema["$defs"]["failure"]["properties"]["code"]["enum"],
        "item.kind": schema["$defs"]["item"]["properties"]["kind"]["enum"],
        "item.severity": schema["$defs"]["item"]["properties"]["severity"]["enum"],
        "item.confidence": schema["$defs"]["item"]["properties"]["confidence"]["enum"],
        "decision.status": schema["$defs"]["decision"]["properties"]["status"]["enum"],
        "coverage.status": schema["$defs"]["coverage"]["properties"]["status"]["enum"],
        "orchestration.execution": schema["$defs"]["orchestration"]["properties"]["execution"]["enum"],
        "gate.state": schema["$defs"]["gate"]["properties"]["state"]["enum"],
    }
    if set(actual) != set(locked):
        fail("stable enum lock and schema paths differ")
    for name, required_values in locked.items():
        missing = [value for value in required_values if value not in actual[name]]
        if missing:
            fail(f"schema removed stable {name} values: {missing}")


def main() -> int:
    try:
        for relative in REQUIRED_FILES:
            if not (ROOT / relative).is_file():
                fail(f"missing required file: {relative}")
        validate_skill()
        validate_openai_yaml()
        validate_evals()
        validate_eval_results()
        validate_release_gate(ROOT / "evals" / "results" / "codex-2026-08-10.json")
        validate_stable_enums()
        Draft202012Validator.check_schema(
            json.loads((ROOT / "schemas" / "panel-output.schema.json").read_text(encoding="utf-8"))
        )
        Draft202012Validator.check_schema(
            json.loads((ROOT / "schemas" / "eval-result.schema.json").read_text(encoding="utf-8"))
        )
        Draft202012Validator.check_schema(
            json.loads((ROOT / "schemas" / "eval-artifact.schema.json").read_text(encoding="utf-8"))
        )
        for fixture in (
            ROOT / "tests" / "fixtures" / "output-v1.0.json",
            ROOT / "tests" / "fixtures" / "output-v1.1.json",
        ):
            errors = validate(fixture)
            if errors:
                fail(f"invalid contract fixture {fixture.name}: {'; '.join(errors)}")
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=ROOT,
            check=False,
        )
        if completed.returncode:
            fail("unit tests failed")
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    print("repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
