#!/usr/bin/env python3
"""Run deterministic repository, metadata, schema, and eval-suite checks."""

from __future__ import annotations

import json
import hashlib
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

from jsonschema import Draft202012Validator, FormatChecker

from validate_meeting_bundle import validate_bundle
from validate_meeting_plan import validate as validate_meeting_plan
from validate_panel_output import validate as validate_panel_output
from render_eval_prompt import render_conversation
from package_plugin import PLUGIN_NAME, build as build_plugin, load_manifest


ROOT = Path(__file__).resolve().parents[1]
CORE_RUNTIME_FILES = [
    "SKILL.md",
    "adapters/codex.md",
    "adapters/claude-code.md",
    "references/modes-and-selection.md",
    "references/panelist-protocol.md",
    "references/authority-and-fallback.md",
    "references/model-and-execution-policy.md",
    "references/meeting-lifecycle.md",
    "references/role-definition-and-import.md",
    "references/meeting-plan-contract.md",
    "references/panel-output-contract.md",
    "schemas/meeting-plan.schema.json",
    "schemas/stable-meeting-plan-enums.v1.json",
    "schemas/panel-output.schema.json",
    "schemas/stable-enums.v1.json",
    "scripts/validate_meeting_plan.py",
    "scripts/validate_panel_output.py",
    "scripts/validate_meeting_bundle.py",
]
HOST_RUNTIME_FILES = {
    "codex": ["agents/openai.yaml"],
    "claude-code": [],
}
EVAL_HARNESS_FILES = [
    "scripts/render_eval_prompt.py",
    "evals/archive_public_turns.py",
    "evals/run_codex_forward.py",
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
    "meeting",
    "role_review",
    "role_import",
    "external_prompt",
    "freeze",
    "routing",
    "recovery",
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
    "references/meeting-lifecycle.md",
    "references/role-definition-and-import.md",
    "references/meeting-plan-contract.md",
    "references/panel-output-contract.md",
    "schemas/meeting-plan.schema.json",
    "schemas/stable-meeting-plan-enums.v1.json",
    "schemas/panel-output.schema.json",
    "schemas/eval-artifact.schema.json",
    "schemas/eval-result.schema.json",
    "schemas/stable-enums.v1.json",
    "scripts/validate_meeting_plan.py",
    "scripts/validate_panel_output.py",
    "scripts/validate_meeting_bundle.py",
    "evals/cases.json",
    "evals/results/codex-2026-08-10.json",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "LICENSE",
    "CLAUDE.md",
    "packaging/plugin.json",
    "scripts/package_plugin.py",
    "submission/listing.json",
    "submission/test-cases.json",
    "submission/local-smoke-2026-08-31.json",
    "submission/privacy-policy.md",
    "submission/privacy-policy.zh-TW.md",
    "submission/terms-of-use.md",
    "submission/terms-of-use.zh-TW.md",
    "submission/support.md",
    "submission/support.zh-TW.md",
    "brand/README.md",
    "brand/complex-enough-mark.svg",
    "brand/complex-enough-mark-dark.svg",
    "brand/complex-enough-mark-monochrome.svg",
    "brand/complex-enough-lockup.svg",
    "packaging/assets/composer-icon.png",
    "packaging/assets/logo.png",
    "packaging/assets/logo-dark.png",
    "site/index.html",
    "site/en/index.html",
    "site/en/privacy/index.html",
    "site/en/terms/index.html",
    "site/en/support/index.html",
    "site/en/brand/index.html",
    "site/zh-TW/index.html",
    "site/zh-TW/privacy/index.html",
    "site/zh-TW/terms/index.html",
    "site/zh-TW/support/index.html",
    "site/zh-TW/brand/index.html",
    "site/assets/css/site.css",
    "site/assets/brand/mark.svg",
    "site/404.html",
    "site/robots.txt",
    "site/sitemap.xml",
    "site/.nojekyll",
    ".github/workflows/pages.yml",
    "docs/github-pages-and-dns-plan.zh-TW.md",
    "docs/official-plugin-submission-readiness.zh-TW.md",
]

PUBLIC_PUBLISHER = "Huan Min Wei"
PUBLIC_CONTACT = "support@complexenough.com"
PUBLIC_BASE_URL = "https://complexenough.com/en/"
PUBLIC_REPOSITORY_URL = "https://github.com/complex-enough/complex-enough"

PROHIBITED_PRIVATE_OUTPUT_IDENTIFIERS = (
    "chain_of_thought",
    "hidden_reasoning",
    "private_reasoning",
    "raw_panelist_report",
    "raw_transcript",
    "scratch_work",
    "thought_trace",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def _contains_prohibited_private_output_marker(output: str) -> bool:
    """Detect exact private-output identifiers without rejecting public error codes.

    Public safety responses may contain longer stable codes such as
    ``PRIVATE_REASONING_REQUEST``. Treating prohibited identifiers as arbitrary
    substrings would reject the audit evidence that the unsafe request was
    blocked. Underscore-aware token boundaries still reject the private field
    identifiers themselves.
    """
    lowered_output = output.lower()
    return any(
        re.search(
            rf"(?<![a-z0-9_]){re.escape(marker)}(?![a-z0-9_])",
            lowered_output,
        )
        for marker in PROHIBITED_PRIVATE_OUTPUT_IDENTIFIERS
    )


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
        followups = case.get("followups", [])
        if not isinstance(followups, list) or not all(
            isinstance(turn, str) and turn.strip() for turn in followups
        ):
            fail(f"eval case {case['id']} has invalid followups")
        if case["mode"] is not None and not followups:
            fail(f"meeting eval case {case['id']} has no confirmation followup")
        for relative in case["fixtures"]:
            fixture = ROOT / "evals" / relative
            if not fixture.is_file():
                fail(f"eval case {case['id']} missing fixture {relative}")


def validate_submission_materials() -> None:
    manifest = load_manifest()
    listing = json.loads((ROOT / "submission" / "listing.json").read_text(encoding="utf-8"))
    test_suite = json.loads(
        (ROOT / "submission" / "test-cases.json").read_text(encoding="utf-8")
    )
    smoke = json.loads(
        (ROOT / "submission" / "local-smoke-2026-08-31.json").read_text(
            encoding="utf-8"
        )
    )

    if listing.get("record_type") != "internal_openai_plugin_submission_readiness":
        fail("submission listing must identify its internal readiness record type")
    if listing.get("submission_type") != "skills_only":
        fail("submission listing must remain skills_only until scope changes explicitly")
    if listing.get("status") not in {"awaiting_publisher_inputs", "ready_to_submit"}:
        fail("submission listing has an unknown readiness status")
    plugin = listing.get("plugin", {})
    if plugin.get("name") != PLUGIN_NAME or plugin.get("version") != manifest["version"]:
        fail("submission listing and plugin manifest identity/version differ")
    listing_interface_fields = {
        "display_name": "displayName",
        "short_description": "shortDescription",
        "long_description": "longDescription",
    }
    for listing_field, manifest_field in listing_interface_fields.items():
        if plugin.get(listing_field) != manifest["interface"][manifest_field]:
            fail(
                f"submission listing {listing_field} and plugin manifest "
                f"{manifest_field} differ"
            )
    if plugin.get("starter_prompts") != manifest["interface"]["defaultPrompt"]:
        fail("submission listing and plugin manifest starter prompts differ")

    publisher_inputs = listing.get("publisher_inputs", {})
    if publisher_inputs.get("publisher_display_name") != manifest["author"]["name"]:
        fail("submission publisher display name and plugin manifest author differ")
    if publisher_inputs.get("publisher_profile_url") != manifest["author"]["url"]:
        fail("submission publisher profile URL and plugin manifest author URL differ")
    if publisher_inputs.get("publisher_type") != "individual":
        fail("submission publisher type must match the confirmed individual application")
    expected_public_inputs = {
        "publisher_display_name": PUBLIC_PUBLISHER,
        "publisher_profile_url": PUBLIC_BASE_URL,
        "public_repository_url": PUBLIC_REPOSITORY_URL,
        "website_url": PUBLIC_BASE_URL,
        "support_url": PUBLIC_BASE_URL + "support/",
        "privacy_policy_url": PUBLIC_BASE_URL + "privacy/",
        "terms_url": PUBLIC_BASE_URL + "terms/",
    }
    for field, expected in expected_public_inputs.items():
        if publisher_inputs.get(field) != expected:
            fail(f"submission publisher input {field} differs from the public surface")
    if listing["status"] == "ready_to_submit" and any(
        value is None or value == "" for value in publisher_inputs.values()
    ):
        fail("ready_to_submit requires every publisher-owned input")

    cases = test_suite.get("cases")
    if not isinstance(cases, list):
        fail("submission test cases must be a list")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)) or any(not isinstance(case_id, str) for case_id in ids):
        fail("submission test case ids must be unique strings")
    counts = {
        kind: sum(case.get("kind") == kind for case in cases)
        for kind in ("positive", "negative")
    }
    if counts != {"positive": 5, "negative": 3}:
        fail(f"submission suite must contain five positive and three negative cases: {counts}")
    for case in cases:
        turns = case.get("turns")
        expected = case.get("expected_behavior")
        if not isinstance(turns, list) or not turns or not all(
            isinstance(turn, str) and turn.strip() for turn in turns
        ):
            fail(f"submission case {case.get('id')} has invalid turns")
        if not isinstance(expected, list) or not expected or not all(
            isinstance(item, str) and item.strip() for item in expected
        ):
            fail(f"submission case {case.get('id')} has invalid expected behavior")

    if smoke.get("record_type") != "local_plugin_discovery_smoke":
        fail("local plugin smoke has an unknown record type")
    smoke_plugin = smoke.get("plugin", {})
    if (
        smoke_plugin.get("name") != PLUGIN_NAME
        or smoke_plugin.get("version") != manifest["version"]
    ):
        fail("local plugin smoke and manifest identity/version differ")
    if smoke.get("overall") not in {"pass", "pass_with_observations"}:
        fail("local plugin smoke must state a passing overall result")
    scored_attempts = [
        attempt
        for attempt in smoke.get("attempts", [])
        if attempt.get("result") == "pass"
    ]
    if not any(attempt.get("id", "").startswith("positive-") for attempt in scored_attempts):
        fail("local plugin smoke has no passing positive routing attempt")
    if not any(attempt.get("id", "").startswith("negative-") for attempt in scored_attempts):
        fail("local plugin smoke has no passing negative routing attempt")

    with tempfile.TemporaryDirectory(prefix="plugin-validation-", dir=ROOT) as directory:
        first = build_plugin(Path(directory) / "first")
        second = build_plugin(Path(directory) / "second")
        if first["sha256"] != second["sha256"]:
            fail("skills-only plugin bundle is not reproducible")
        if smoke_plugin.get("current_bundle_sha256") != "sha256:" + first["sha256"]:
            fail("current local plugin bundle digest differs from the reproducible build")
        tested_bundle = smoke_plugin.get("tested_bundle_sha256")
        if not isinstance(tested_bundle, str) or not tested_bundle.startswith("sha256:"):
            fail("local plugin smoke must retain the behaviorally tested bundle digest")
        repository_skill_digest = "sha256:" + hashlib.sha256(
            (ROOT / "SKILL.md").read_bytes()
        ).hexdigest()
        if (
            smoke.get("runtime_source_check", {}).get("repository_skill_sha256")
            != repository_skill_digest
        ):
            fail("local smoke runtime digest differs from the current canonical skill")
        if tested_bundle != smoke_plugin["current_bundle_sha256"]:
            update = smoke.get("current_bundle_update", {})
            if (
                update.get("classification") != "metadata_only"
                or update.get("runtime_skill_bytes_changed") is not False
                or not update.get("behavioral_claim")
            ):
                fail("bundle digest changed without an explicit metadata-only smoke boundary")
        if not Path(first["archive"]).is_file():
            fail("skills-only plugin archive was not generated")


def validate_public_surface() -> None:
    manifest = load_manifest()
    if manifest["author"] != {
        "name": PUBLIC_PUBLISHER,
        "email": PUBLIC_CONTACT,
        "url": PUBLIC_BASE_URL,
    }:
        fail("plugin author metadata differs from the confirmed public publisher")
    if manifest.get("repository") != PUBLIC_REPOSITORY_URL:
        fail("plugin repository URL differs from the Organization repository")
    interface = manifest["interface"]
    expected_urls = {
        "websiteURL": PUBLIC_BASE_URL,
        "privacyPolicyURL": PUBLIC_BASE_URL + "privacy/",
        "termsOfServiceURL": PUBLIC_BASE_URL + "terms/",
    }
    for field, expected in expected_urls.items():
        if interface.get(field) != expected:
            fail(f"plugin interface {field} differs from the public surface")

    policy_paths = [
        ROOT / "submission" / "privacy-policy.md",
        ROOT / "submission" / "privacy-policy.zh-TW.md",
        ROOT / "submission" / "terms-of-use.md",
        ROOT / "submission" / "terms-of-use.zh-TW.md",
        ROOT / "submission" / "support.md",
        ROOT / "submission" / "support.zh-TW.md",
    ]
    for path in policy_paths:
        content = path.read_text(encoding="utf-8")
        if PUBLIC_PUBLISHER not in content or PUBLIC_CONTACT not in content:
            fail(f"public policy identity/contact is incomplete: {path.name}")
        if "not for publication" in content.lower() or "[verified publisher" in content.lower():
            fail(f"public policy still contains draft language: {path.name}")

    for path in (ROOT / "site").rglob("*.html"):
        content = path.read_text(encoding="utf-8")
        lowered = content.lower()
        if "http://" in lowered:
            fail(f"public site contains an insecure URL: {path.relative_to(ROOT)}")
        if re.search(r"<script\s+[^>]*src=", lowered):
            fail(f"public site must not load external scripts: {path.relative_to(ROOT)}")
        if any(marker in lowered for marker in ("google-analytics", "googletagmanager", "segment.io", "facebook.net")):
            fail(f"public site contains analytics/tracking code: {path.relative_to(ROOT)}")

    legacy_personal_alias = "dryada" + "70749"
    tracked_public_text = subprocess.run(
        ["git", "grep", "-n", "-I", legacy_personal_alias, "--", ":(exclude)evals/results/**"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked_public_text.returncode == 0:
        fail("current public repository content still identifies the legacy personal alias")
    if tracked_public_text.returncode not in {0, 1}:
        fail("could not scan current public repository content for legacy identity")


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


def _semantic_version(value: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value)
    if not match:
        fail(f"eval suite version is not semantic x.y.z: {value!r}")
    return tuple(int(part) for part in match.groups())


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
    rendered_prompt = json.dumps(
        render_conversation(case_definition, expected_host, skill_path),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    prompt_digest = "sha256:" + hashlib.sha256(
        rendered_prompt.encode("utf-8")
    ).hexdigest()
    if artifact["prompt_sha256"] != prompt_digest:
        fail(f"eval artifact prompt digest mismatch for {result_case['case_id']}")

    if _contains_prohibited_private_output_marker(artifact["output"]):
        fail(f"eval artifact {relative} contains a prohibited private-output marker")


def validate_historical_eval_artifact(
    *,
    result_path: Path,
    result_case: dict,
    expected_host: str,
    expected_runtime_revision: str,
    expected_suite_revision: str,
    result_executed_at: datetime,
) -> None:
    """Verify archived artifact integrity without treating it as current evidence.

    Historical suite and prompt bytes are not release authority for the current
    candidate. The artifact remains useful as an auditable record, so retain the
    digest, schema, metadata, timestamp, and public-output checks that can be
    verified from the sealed scorecard itself.
    """
    relative = result_case.get("artifact_path")
    expected_digest = result_case.get("artifact_sha256")
    run_id = result_case.get("run_id")
    if not relative or not expected_digest or not run_id:
        fail(f"passing historical case {result_case['case_id']} has no captured artifact")

    eval_root = result_path.parent.parent.resolve()
    artifact_path = (eval_root / relative).resolve()
    try:
        artifact_path.relative_to(eval_root)
    except ValueError:
        fail(f"historical eval artifact escapes eval root: {relative}")
    if not artifact_path.is_file() or artifact_path.is_symlink():
        fail(f"missing or unsafe historical eval artifact: {relative}")
    if _sha256_file(artifact_path) != expected_digest:
        fail(f"historical eval artifact digest mismatch for {result_case['case_id']}")

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
        fail(f"invalid historical eval artifact {relative}: {rendered}")
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
                f"historical eval artifact {relative} has "
                f"{field}={artifact[field]!r}, expected {expected!r}"
            )
    if _parsed_datetime(artifact["executed_at"]) > result_executed_at:
        fail(
            f"historical eval artifact {relative} was executed after its "
            "enclosing scorecard execution"
        )

    if _contains_prohibited_private_output_marker(artifact["output"]):
        fail(f"historical eval artifact {relative} contains a prohibited private-output marker")


def validate_historical_eval_result(
    result_path: Path,
    schema: dict,
    current_suite_version: str,
) -> None:
    """Validate archived evidence while explicitly excluding it from release."""
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    result = json.loads(result_path.read_text(encoding="utf-8"))
    errors = sorted(validator.iter_errors(result), key=lambda error: list(error.path))
    if errors:
        rendered = "; ".join(error.message for error in errors)
        fail(f"invalid historical eval result {result_path.name}: {rendered}")
    if result["suite_version"] == current_suite_version:
        fail(f"eval result {result_path.name} is current, not historical")
    if _semantic_version(result["suite_version"]) >= _semantic_version(current_suite_version):
        fail(
            f"eval result {result_path.name} claims non-historical suite version "
            f"{result['suite_version']}"
        )

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
        fail(f"historical eval result {result_path.name} must use a host-prefixed filename")
    if result["environment"]["host"] != expected_host:
        fail(f"historical eval result {result_path.name} claims the wrong host")

    executed_at = _parsed_datetime(result["executed_at"])
    verified_at = _parsed_datetime(result["verified_at"])
    if verified_at < executed_at:
        fail(f"historical eval result {result_path.name} was verified before it was executed")
    now = datetime.now(timezone.utc)
    if executed_at.astimezone(timezone.utc) > now or verified_at.astimezone(timezone.utc) > now:
        fail(f"historical eval result {result_path.name} has a future timestamp")
    filename_date_match = re.match(
        r"^(?:codex|claude-code|static-only)-(\d{4}-\d{2}-\d{2})\.json$",
        result_path.name,
    )
    if not filename_date_match or executed_at.date().isoformat() != filename_date_match.group(1):
        fail(
            f"historical eval result {result_path.name} execution date "
            "does not match its filename"
        )

    result_case_ids = [case["case_id"] for case in result["cases"]]
    if len(result_case_ids) != len(set(result_case_ids)):
        fail(f"historical eval result {result_path.name} has duplicate case ids")
    for result_case in result["cases"]:
        assertion_statuses = [item["status"] for item in result_case["assertions"]]
        expected_status = (
            "fail"
            if "fail" in assertion_statuses
            else "pass"
            if assertion_statuses and set(assertion_statuses) == {"pass"}
            else "not_run"
        )
        if result_case["status"] != expected_status:
            fail(
                f"historical eval result {result_path.name} has inconsistent status "
                f"for {result_case['case_id']}"
            )
        if result_case["status"] == "not_run" and result_case["execution"] != "not_run":
            fail(
                f"historical eval result {result_path.name} must mark unrun case "
                f"execution for {result_case['case_id']}"
            )
        if result_case["status"] != "not_run" and result_case["execution"] == "not_run":
            fail(
                f"historical eval result {result_path.name} cannot pass an unrun case "
                f"{result_case['case_id']}"
            )
        if expected_host in {"codex", "claude-code"} and result_case["status"] == "pass":
            if result_case["execution"] not in {"forward", "simulated_failure"}:
                fail(
                    f"historical behavioral eval result {result_path.name} uses "
                    f"non-behavioral execution for {result_case['case_id']}"
                )
            validate_historical_eval_artifact(
                result_path=result_path,
                result_case=result_case,
                expected_host=expected_host,
                expected_runtime_revision=result["skill_revision"],
                expected_suite_revision=result["suite_revision"],
                result_executed_at=executed_at,
            )

    simulated_failure = any(
        case["execution"] == "simulated_failure" for case in result["cases"]
    )
    declared_failure_injection = result["environment"]["failure_injection"]
    if simulated_failure and declared_failure_injection not in {"simulated", "mixed"}:
        fail(
            f"historical eval result {result_path.name} does not disclose its "
            "simulated failure execution"
        )
    if not simulated_failure and declared_failure_injection in {"simulated", "mixed"}:
        fail(
            f"historical eval result {result_path.name} declares simulated failure "
            "without a simulated execution"
        )

    if expected_host in {"codex", "claude-code"}:
        expected_gate = (
            "GO" if all(case["status"] == "pass" for case in result["cases"]) else "NO_GO"
        )
        if result["gate"] != expected_gate:
            fail(
                f"historical eval result {result_path.name} has gate "
                f"{result['gate']}, expected {expected_gate}"
            )
    elif result["gate"] != "NO_GO":
        fail(f"historical static-only eval result {result_path.name} cannot claim GO")


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


def validate_eval_results() -> list[Path]:
    suite = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas" / "eval-result.schema.json").read_text(encoding="utf-8"))
    expected_revisions = {host: runtime_revision(host) for host in HOST_RUNTIME_FILES}
    expected_suite_revision = eval_suite_revision(suite, ROOT / "evals", ROOT)
    current_results: list[Path] = []
    for result_path in sorted((ROOT / "evals" / "results").glob("*.json")):
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if not isinstance(result, dict):
            fail(f"invalid eval result {result_path.name}: root must be an object")
        if result.get("suite_version") == suite["suite_version"]:
            validate_eval_result(
                result_path,
                suite,
                schema,
                expected_revisions,
                expected_suite_revision,
            )
            current_results.append(result_path)
        else:
            validate_historical_eval_result(
                result_path,
                schema,
                suite["suite_version"],
            )
    return current_results


def validate_release_gate(
    result_path: Path,
    suite: dict | None = None,
    schema: dict | None = None,
    expected_runtime_revisions: dict[str, str] | None = None,
    expected_suite_revision: str | None = None,
) -> None:
    if not result_path.is_file():
        fail(f"missing required Codex release scorecard: {result_path.name}")
    if suite is None:
        suite = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    if schema is None:
        schema = json.loads(
            (ROOT / "schemas" / "eval-result.schema.json").read_text(encoding="utf-8")
        )
    if expected_runtime_revisions is None:
        expected_runtime_revisions = {
            host: runtime_revision(host) for host in HOST_RUNTIME_FILES
        }
    if expected_suite_revision is None:
        expected_suite_revision = eval_suite_revision(suite, ROOT / "evals", ROOT)
    validate_eval_result(
        result_path,
        suite,
        schema,
        expected_runtime_revisions,
        expected_suite_revision,
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result.get("environment", {}).get("host") != "codex" or result.get("gate") != "GO":
        fail(f"required Codex release scorecard is not GO: {result_path.name}")


def validate_current_release_gate(current_results: list[Path]) -> None:
    codex_go_results = []
    for result_path in current_results:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("environment", {}).get("host") == "codex" and result.get("gate") == "GO":
            codex_go_results.append(result_path)
    if not codex_go_results:
        fail("no current Codex GO scorecard exists for the meeting-core runtime")
    validate_release_gate(max(codex_go_results, key=lambda path: path.name))


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
        validate_submission_materials()
        validate_public_surface()
        current_results = validate_eval_results()
        validate_stable_enums()
        Draft202012Validator.check_schema(
            json.loads((ROOT / "schemas" / "meeting-plan.schema.json").read_text(encoding="utf-8"))
        )
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
            ROOT / "tests" / "fixtures" / "output-v1.2.json",
        ):
            errors = validate_panel_output(fixture)
            if errors:
                fail(f"invalid contract fixture {fixture.name}: {'; '.join(errors)}")
        meeting_fixture = ROOT / "tests" / "fixtures" / "meeting-plan-v1.0.json"
        meeting_errors = validate_meeting_plan(meeting_fixture)
        if meeting_errors:
            fail(
                "invalid contract fixture meeting-plan-v1.0.json: "
                + "; ".join(meeting_errors)
            )
        bundle_errors = validate_bundle(
            meeting_fixture,
            ROOT / "tests" / "fixtures" / "output-v1.2.json",
        )
        if bundle_errors:
            fail("invalid meeting bundle fixture: " + "; ".join(bundle_errors))
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            cwd=ROOT,
            check=False,
        )
        if completed.returncode:
            fail("unit tests failed")
        validate_current_release_gate(current_results)
    except (AssertionError, KeyError, TypeError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    print("repository validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
