#!/usr/bin/env python3
"""Run neutral multi-turn Codex forward cases in isolated CLI sessions.

This maintainer harness deliberately keeps Codex JSONL events ephemeral.  Only
the direct public final written by ``codex exec -o`` is archived as release
evidence; raw reasoning, tool events, and nested-agent reports are discarded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_eval_prompt import render_conversation  # noqa: E402
from validate_repo import (  # noqa: E402
    CORE_RUNTIME_FILES,
    HOST_RUNTIME_FILES,
    _contains_prohibited_private_output_marker,
    eval_suite_revision,
)


SKILL_NAME = "orchestrate-multi-perspective-panel"
DEFAULT_TIMEOUT_SECONDS = 3600


class ForwardRunError(RuntimeError):
    """Raised when a case cannot produce trustworthy public-turn evidence."""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    thread_id: str | None
    event_types: tuple[str, ...]
    diagnostic: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def runtime_revision_at(skill_path: Path, host: str = "codex") -> str:
    digest = hashlib.sha256()
    for relative in CORE_RUNTIME_FILES + HOST_RUNTIME_FILES[host]:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((skill_path / relative).read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def parse_jsonl_events(stream: str) -> tuple[str | None, tuple[str, ...], str]:
    """Extract only operational metadata, never agent-message payloads."""

    thread_id: str | None = None
    event_types: list[str] = []
    diagnostic = ""
    for line in stream.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_type = event.get("type")
        if isinstance(event_type, str):
            event_types.append(event_type)
        if event_type == "thread.started" and isinstance(event.get("thread_id"), str):
            thread_id = event["thread_id"]
        if event_type in {"error", "turn.failed"}:
            candidate = event.get("message") or event.get("error") or event_type
            diagnostic = str(candidate)[:500]
    return thread_id, tuple(event_types), diagnostic


def run_codex_command(
    command: Sequence[str], *, cwd: Path, timeout_seconds: int
) -> CommandResult:
    try:
        completed = subprocess.run(
            list(command),
            cwd=cwd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as error:
        raise ForwardRunError(
            f"Codex turn exceeded {timeout_seconds}s and was terminated"
        ) from error

    thread_id, event_types, diagnostic = parse_jsonl_events(completed.stdout)
    if not diagnostic and completed.returncode:
        diagnostic = completed.stderr.strip()[-500:]
    return CommandResult(
        returncode=completed.returncode,
        thread_id=thread_id,
        event_types=event_types,
        diagnostic=diagnostic,
    )


def initial_command(
    *, codex_bin: str, workspace: Path, output_file: Path, prompt: str
) -> list[str]:
    return [
        codex_bin,
        "exec",
        "--json",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        os.fspath(workspace),
        "-o",
        os.fspath(output_file),
        prompt,
    ]


def resume_command(
    *, codex_bin: str, thread_id: str, output_file: Path, prompt: str
) -> list[str]:
    return [
        codex_bin,
        "exec",
        "resume",
        "--json",
        "--skip-git-repo-check",
        "-o",
        os.fspath(output_file),
        thread_id,
        prompt,
    ]


def copy_runtime(source: Path, destination: Path) -> None:
    if destination.exists():
        raise ForwardRunError(f"refusing to replace staged runtime: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, symlinks=False)


def read_public_final(path: Path) -> str:
    if not path.is_file():
        raise ForwardRunError(f"Codex did not write a public final: {path}")
    output = path.read_text(encoding="utf-8")
    if not output.strip():
        raise ForwardRunError(f"Codex wrote an empty public final: {path}")
    if _contains_prohibited_private_output_marker(output):
        raise ForwardRunError("public final contains a prohibited private-output identifier")
    return output


def validate_public_archive(path: Path, case_id: str, expected_turns: int) -> None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ForwardRunError(f"invalid existing public archive: {path}") from error
    if set(payload) != {"case_id", "assistant_outputs"}:
        raise ForwardRunError(f"unexpected public archive fields: {path}")
    if payload["case_id"] != case_id:
        raise ForwardRunError(f"public archive case mismatch: {path}")
    outputs = payload["assistant_outputs"]
    if not isinstance(outputs, list) or len(outputs) != expected_turns:
        raise ForwardRunError(f"public archive turn count mismatch: {path}")
    for output in outputs:
        if not isinstance(output, str) or not output.strip():
            raise ForwardRunError(f"public archive contains an empty turn: {path}")
        if _contains_prohibited_private_output_marker(output):
            raise ForwardRunError(f"public archive contains private-output marker: {path}")


def write_public_archive(path: Path, case_id: str, outputs: Sequence[str]) -> None:
    if path.exists():
        raise ForwardRunError(f"refusing to overwrite public archive: {path}")
    payload = {"case_id": case_id, "assistant_outputs": list(outputs)}
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    validate_public_archive(path, case_id, len(outputs))


def select_cases(
    cases: Sequence[dict], requested: Sequence[str], start_at: str | None
) -> list[dict]:
    by_id = {case["id"]: case for case in cases}
    if requested:
        missing = [case_id for case_id in requested if case_id not in by_id]
        if missing:
            raise ForwardRunError("unknown case id(s): " + ", ".join(missing))
        return [by_id[case_id] for case_id in requested]
    selected = list(cases)
    if start_at is not None:
        if start_at not in by_id:
            raise ForwardRunError(f"unknown --start-at case: {start_at}")
        offset = next(index for index, case in enumerate(selected) if case["id"] == start_at)
        selected = selected[offset:]
    return selected


def update_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def run_case(
    *,
    case: dict,
    candidate_source: Path,
    expected_runtime_revision: str,
    work_root: Path,
    output_dir: Path,
    codex_bin: str,
    timeout_seconds: int,
) -> int:
    case_id = case["id"]
    case_root = work_root / "cases" / case_id / f"attempt-{uuid.uuid4().hex}"
    workspace = case_root / "workspace"
    capture_dir = case_root / "captured-public-turns"
    workspace.mkdir(parents=True, exist_ok=False)
    capture_dir.mkdir(parents=True, exist_ok=False)

    is_trigger_case = "trigger" in case["tags"]
    if is_trigger_case:
        staged_skill = workspace / ".agents" / "skills" / SKILL_NAME
        copy_runtime(candidate_source, staged_skill)
        skill_path_for_prompt: Path | None = None
    else:
        staged_skill = case_root / "runtime" / SKILL_NAME
        copy_runtime(candidate_source, staged_skill)
        skill_path_for_prompt = staged_skill

    staged_revision = runtime_revision_at(staged_skill)
    if staged_revision != expected_runtime_revision:
        raise ForwardRunError(
            f"staged runtime changed for {case_id}: {staged_revision}"
        )

    conversation = render_conversation(case, "codex", skill_path_for_prompt)
    outputs: list[str] = []
    thread_id: str | None = None
    for turn_index, prompt in enumerate(conversation):
        turn_file = capture_dir / f"turn-{turn_index}.txt"
        print(
            f"  turn {turn_index + 1}/{len(conversation)} starting",
            flush=True,
        )
        started = time.monotonic()
        if turn_index == 0:
            command = initial_command(
                codex_bin=codex_bin,
                workspace=workspace,
                output_file=turn_file,
                prompt=prompt,
            )
        else:
            if thread_id is None:
                raise ForwardRunError(f"missing thread id before turn {turn_index}")
            command = resume_command(
                codex_bin=codex_bin,
                thread_id=thread_id,
                output_file=turn_file,
                prompt=prompt,
            )
        result = run_codex_command(
            command,
            cwd=workspace,
            timeout_seconds=timeout_seconds,
        )
        if result.returncode:
            detail = result.diagnostic or f"exit {result.returncode}"
            raise ForwardRunError(f"Codex turn {turn_index} failed: {detail}")
        if turn_index == 0:
            thread_id = result.thread_id
            if thread_id is None:
                raise ForwardRunError("initial Codex turn emitted no thread.started id")
        outputs.append(read_public_final(turn_file))
        elapsed = time.monotonic() - started
        print(f"  turn {turn_index + 1} completed in {elapsed:.1f}s", flush=True)

    if runtime_revision_at(staged_skill) != expected_runtime_revision:
        raise ForwardRunError(f"runtime bytes changed during {case_id}")
    archive = output_dir / f"{case_id}.json"
    write_public_archive(archive, case_id, outputs)
    return len(outputs)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-path", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--expected-runtime-revision", required=True)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--start-at")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="skip cases that already have a valid complete public-turn archive",
    )
    args = parser.parse_args(argv)

    candidate_source = args.skill_path.resolve()
    if candidate_source.name != SKILL_NAME or not (candidate_source / "SKILL.md").is_file():
        parser.error(f"invalid candidate skill directory: {candidate_source}")
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    resolved_work_root = args.work_root.resolve()
    try:
        resolved_work_root.relative_to(ROOT)
    except ValueError:
        pass
    else:
        parser.error("--work-root must be outside the repository so raw CLI events stay untracked")
    actual_runtime_revision = runtime_revision_at(candidate_source)
    if actual_runtime_revision != args.expected_runtime_revision:
        parser.error(
            "candidate runtime revision mismatch: "
            f"expected {args.expected_runtime_revision}, got {actual_runtime_revision}"
        )

    suite = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    suite_revision = eval_suite_revision(suite, ROOT / "evals", ROOT)
    try:
        selected = select_cases(suite["cases"], args.case, args.start_at)
    except ForwardRunError as error:
        parser.error(str(error))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    resolved_work_root.mkdir(parents=True, exist_ok=True)
    state_path = args.output_dir.parent / "runner-state.json"
    state = {
        "runner_version": "1.0",
        "started_at": utc_now(),
        "updated_at": utc_now(),
        "host": "codex",
        "runtime_revision": actual_runtime_revision,
        "suite_revision": suite_revision,
        "selected_case_ids": [case["id"] for case in selected],
        "cases": {},
    }
    update_state(state_path, state)

    failures = 0
    total = len(selected)
    for index, case in enumerate(selected, start=1):
        case_id = case["id"]
        archive = args.output_dir / f"{case_id}.json"
        expected_turns = 1 + len(case.get("followups", []))
        print(f"[{index}/{total}] {case_id}", flush=True)
        if archive.exists() and args.resume:
            try:
                validate_public_archive(archive, case_id, expected_turns)
            except ForwardRunError as error:
                state["cases"][case_id] = {
                    "status": "failed",
                    "updated_at": utc_now(),
                    "diagnostic": str(error),
                }
                failures += 1
                print(f"  invalid existing archive: {error}", flush=True)
            else:
                state["cases"][case_id] = {
                    "status": "skipped_valid",
                    "turns": expected_turns,
                    "updated_at": utc_now(),
                }
                print("  skipped valid archive", flush=True)
            state["updated_at"] = utc_now()
            update_state(state_path, state)
            continue
        if archive.exists():
            state["cases"][case_id] = {
                "status": "failed",
                "updated_at": utc_now(),
                "diagnostic": "archive already exists; use --resume or a new output directory",
            }
            failures += 1
            state["updated_at"] = utc_now()
            update_state(state_path, state)
            print("  failed: archive already exists", flush=True)
            continue

        try:
            turns = run_case(
                case=case,
                candidate_source=candidate_source,
                expected_runtime_revision=actual_runtime_revision,
                work_root=resolved_work_root,
                output_dir=args.output_dir,
                codex_bin=args.codex_bin,
                timeout_seconds=args.timeout_seconds,
            )
        except (ForwardRunError, OSError) as error:
            failures += 1
            state["cases"][case_id] = {
                "status": "failed",
                "updated_at": utc_now(),
                "diagnostic": str(error),
            }
            print(f"  failed: {error}", flush=True)
        else:
            state["cases"][case_id] = {
                "status": "completed",
                "turns": turns,
                "updated_at": utc_now(),
            }
            print(f"  archived {turns} public turn(s)", flush=True)
        state["updated_at"] = utc_now()
        update_state(state_path, state)

    state["finished_at"] = utc_now()
    state["updated_at"] = utc_now()
    state["failure_count"] = failures
    update_state(state_path, state)
    print(f"batch complete: {total - failures}/{total} cases archived", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
