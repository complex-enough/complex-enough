#!/usr/bin/env python3
"""Install verified runtime skill files for a supported host without deletion."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "orchestrate-multi-perspective-panel"
CORE_RUNTIME_FILES = [
    Path("SKILL.md"),
    Path("adapters/codex.md"),
    Path("adapters/claude-code.md"),
    Path("references/modes-and-selection.md"),
    Path("references/panelist-protocol.md"),
    Path("references/authority-and-fallback.md"),
    Path("references/model-and-execution-policy.md"),
    Path("references/meeting-lifecycle.md"),
    Path("references/role-definition-and-import.md"),
    Path("references/meeting-plan-contract.md"),
    Path("references/panel-output-contract.md"),
    Path("schemas/meeting-plan.schema.json"),
    Path("schemas/stable-meeting-plan-enums.v1.json"),
    Path("schemas/panel-output.schema.json"),
    Path("schemas/stable-enums.v1.json"),
    Path("scripts/validate_meeting_plan.py"),
    Path("scripts/validate_panel_output.py"),
    Path("scripts/validate_meeting_bundle.py"),
]
PLATFORM_FILES = {
    "codex": [Path("agents/openai.yaml")],
    "claude-code": [],
}
ALL_PLATFORM_FILES = tuple(
    sorted(
        {relative for files in PLATFORM_FILES.values() for relative in files},
        key=os.fspath,
    )
)


class UnsafeDestinationError(ValueError):
    """Raised when an install path could redirect writes outside the target."""


class InstallTransactionError(RuntimeError):
    """Raised when automatic rollback cannot safely finish."""


class PlatformConflictError(ValueError):
    """Raised when a target contains managed files for another host."""


def _is_link_like(file_stat: os.stat_result) -> bool:
    if stat.S_ISLNK(file_stat.st_mode):
        return True
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    file_attributes = getattr(file_stat, "st_file_attributes", 0)
    return bool(reparse_flag and file_attributes & reparse_flag)


def _lstat(path: Path) -> os.stat_result | None:
    try:
        return path.lstat()
    except FileNotFoundError:
        return None


def _assert_not_link_like(path: Path) -> os.stat_result | None:
    file_stat = _lstat(path)
    if file_stat is not None and _is_link_like(file_stat):
        raise UnsafeDestinationError(f"refusing symlink or reparse-point destination: {path}")
    return file_stat


def _assert_safe_components(path: Path) -> None:
    """Reject every existing lexical component before any path is resolved."""

    for component in reversed((path, *path.parents)):
        _assert_not_link_like(component)


def _absolute_lexical(path: Path) -> Path:
    expanded = path.expanduser()
    return Path(os.path.abspath(os.fspath(expanded)))


def digest(path: Path) -> str:
    """Hash a regular file without following a final-component symlink."""

    file_stat = _assert_not_link_like(path)
    if file_stat is None or not stat.S_ISREG(file_stat.st_mode):
        raise FileNotFoundError(f"not a regular file: {path}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise UnsafeDestinationError(f"refusing non-regular file: {path}")
        result = hashlib.sha256()
        with os.fdopen(descriptor, "rb", closefd=False) as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                result.update(chunk)
        return result.hexdigest()
    finally:
        os.close(descriptor)


def validate_target(target: Path) -> Path:
    lexical = _absolute_lexical(target)
    if lexical.name != SKILL_NAME:
        raise ValueError(f"target directory must be named {SKILL_NAME}")
    _assert_safe_components(lexical)
    resolved = lexical.resolve(strict=False)
    if resolved in {Path("/"), Path.home().resolve(), ROOT}:
        raise ValueError("refusing unsafe install target")
    target_stat = _lstat(lexical)
    if target_stat is not None and not stat.S_ISDIR(target_stat.st_mode):
        raise UnsafeDestinationError(f"install target is not a directory: {lexical}")
    return lexical


def runtime_files(platform: str) -> tuple[Path, ...]:
    return tuple(CORE_RUNTIME_FILES + PLATFORM_FILES[platform])


def _assert_no_platform_conflicts(target: Path, platform: str) -> None:
    """Refuse cross-host reuse instead of retaining or deleting known managed files."""

    _validate_destination_paths(target, ALL_PLATFORM_FILES)
    expected = set(PLATFORM_FILES[platform])
    conflicts = [
        relative
        for relative in ALL_PLATFORM_FILES
        if relative not in expected and _lstat(target / relative) is not None
    ]
    if conflicts:
        rendered = ", ".join(os.fspath(relative) for relative in conflicts)
        raise PlatformConflictError(
            f"target contains managed files for a different platform: {rendered}; "
            "use a separate host-specific target"
        )


def _validate_sources(files: Sequence[Path]) -> None:
    for relative in files:
        source = ROOT / relative
        source_stat = _assert_not_link_like(source)
        if source_stat is None or not stat.S_ISREG(source_stat.st_mode):
            raise FileNotFoundError(source)


def _validate_destination_paths(target: Path, files: Sequence[Path]) -> None:
    """Reject managed paths that would traverse or overwrite link-like entries."""

    _assert_safe_components(target)
    target_stat = _lstat(target)
    if target_stat is not None and not stat.S_ISDIR(target_stat.st_mode):
        raise UnsafeDestinationError(f"install target is not a directory: {target}")
    for relative in files:
        current = target
        for index, part in enumerate(relative.parts):
            current /= part
            current_stat = _assert_not_link_like(current)
            if current_stat is None:
                continue
            is_final = index == len(relative.parts) - 1
            expected_type = stat.S_ISREG if is_final else stat.S_ISDIR
            if not expected_type(current_stat.st_mode):
                kind = "file" if is_final else "directory"
                raise UnsafeDestinationError(f"managed destination is not a {kind}: {current}")


def _mismatches(target: Path, files: Sequence[Path]) -> list[str]:
    _validate_destination_paths(target, files)
    mismatches: list[str] = []
    for relative in files:
        destination = target / relative
        destination_stat = _lstat(destination)
        if destination_stat is None or not stat.S_ISREG(destination_stat.st_mode):
            mismatches.append(str(relative))
            continue
        if digest(ROOT / relative) != digest(destination):
            mismatches.append(str(relative))
    return mismatches


def validate_repository() -> None:
    """Enforce the portable repository release gate before a real install."""

    validator = ROOT / "scripts" / "validate_repo.py"
    completed = subprocess.run(
        [sys.executable, os.fspath(validator)],
        cwd=ROOT,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"repository validation prerequisite failed with exit code {completed.returncode}; "
            "installation aborted"
        )


def _copy_runtime_files(staged_target: Path, files: Sequence[Path]) -> None:
    for relative in files:
        destination = staged_target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination, follow_symlinks=False)


def _replace_path(source: Path, destination: Path) -> None:
    os.replace(source, destination)


def _rollback_commit(
    *,
    target: Path,
    staged_root: Path,
    backup: Path,
    previous_moved: bool,
    payload_moved: bool,
) -> None:
    if payload_moved:
        failed_payload = staged_root / "failed-payload"
        _replace_path(target, failed_payload)
    if previous_moved:
        _replace_path(backup, target)


def _commit_staged_target(
    *,
    target: Path,
    staged_target: Path,
    staged_root: Path,
    files: Sequence[Path],
) -> None:
    """Swap a validated same-filesystem payload into place, rolling back on error."""

    backup = staged_root / "previous-target"
    previous_moved = False
    payload_moved = False
    try:
        if _lstat(target) is not None:
            _replace_path(target, backup)
            previous_moved = True
        _replace_path(staged_target, target)
        payload_moved = True
        mismatches = _mismatches(target, files)
        if mismatches:
            raise RuntimeError("post-install verification failed: " + ", ".join(mismatches))
    except BaseException:
        try:
            _rollback_commit(
                target=target,
                staged_root=staged_root,
                backup=backup,
                previous_moved=previous_moved,
                payload_moved=payload_moved,
            )
        except BaseException as rollback_error:
            raise InstallTransactionError(
                "installation failed and automatic rollback could not complete; "
                f"recovery data was preserved at {staged_root}"
            ) from rollback_error
        raise


def _install_transaction(target: Path, files: Sequence[Path]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    _assert_safe_components(target.parent)
    _validate_destination_paths(target, files)
    staged_root = Path(
        tempfile.mkdtemp(prefix=f".{SKILL_NAME}.staging-", dir=target.parent)
    )
    preserve_staging = False
    try:
        staged_target = staged_root / "payload"
        if _lstat(target) is not None:
            shutil.copytree(target, staged_target, symlinks=True)
        else:
            staged_target.mkdir()
        _validate_destination_paths(staged_target, files)
        _copy_runtime_files(staged_target, files)
        staged_mismatches = _mismatches(staged_target, files)
        if staged_mismatches:
            raise RuntimeError("staged install verification failed: " + ", ".join(staged_mismatches))
        _validate_destination_paths(target, files)
        _commit_staged_target(
            target=target,
            staged_target=staged_target,
            staged_root=staged_root,
            files=files,
        )
    except InstallTransactionError:
        preserve_staging = True
        raise
    finally:
        if not preserve_staging:
            shutil.rmtree(staged_root)


def install(
    *,
    target: Path,
    platform: str,
    check: bool = False,
    dry_run: bool = False,
    repository_validator: Callable[[], None] | None = None,
) -> None:
    target = validate_target(target)
    files = runtime_files(platform)
    _validate_sources(files)
    _validate_destination_paths(target, files)
    _assert_no_platform_conflicts(target, platform)

    if check:
        mismatches = _mismatches(target, files)
        if mismatches:
            raise SystemExit("skill install differs: " + ", ".join(mismatches))
        print(f"skill install verified: {target}")
        return

    for relative in files:
        print(f"{ROOT / relative} -> {target / relative}")
    if dry_run:
        return

    validator = repository_validator or validate_repository
    validator()
    _install_transaction(target, files)
    print(f"skill installed and verified: {target}")


def main(
    argv: Sequence[str] | None = None,
    *,
    repository_validator: Callable[[], None] | None = None,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--platform", choices=sorted(PLATFORM_FILES), default="codex")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify bytes without writing")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    install(
        target=args.target,
        platform=args.platform,
        check=args.check,
        dry_run=args.dry_run,
        repository_validator=repository_validator,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
