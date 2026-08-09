from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import install_skill  # noqa: E402


def snapshot(root: Path) -> dict[str, tuple[str, bytes | str]]:
    result: dict[str, tuple[str, bytes | str]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", b"")
        else:
            result[relative] = ("file", path.read_bytes())
    return result


class InstallSkillTest(unittest.TestCase):
    def target(self, directory: str, parent: str = "skills") -> Path:
        target_parent = Path(directory) / parent
        target_parent.mkdir()
        return target_parent / install_skill.SKILL_NAME

    def run_install(self, target: Path, platform: str = "codex") -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            result = install_skill.main(
                ["--platform", platform, "--target", os.fspath(target)],
                repository_validator=lambda: None,
            )
        self.assertEqual(result, 0)

    def assert_manifest_matches(self, target: Path, platform: str) -> None:
        for relative in install_skill.runtime_files(platform):
            self.assertEqual((target / relative).read_bytes(), (ROOT / relative).read_bytes())

    def test_successful_install_preserves_unrelated_file_and_check_skips_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            target.mkdir()
            unrelated = target / "local-notes.txt"
            unrelated.write_text("keep me", encoding="utf-8")
            validations: list[str] = []

            with contextlib.redirect_stdout(io.StringIO()):
                result = install_skill.main(
                    ["--platform", "codex", "--target", os.fspath(target)],
                    repository_validator=lambda: validations.append("passed"),
                )

            self.assertEqual(result, 0)
            self.assertEqual(validations, ["passed"])
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep me")
            self.assert_manifest_matches(target, "codex")
            with contextlib.redirect_stdout(io.StringIO()):
                result = install_skill.main(
                    ["--platform", "codex", "--target", os.fspath(target), "--check"],
                    repository_validator=lambda: self.fail("--check ran the repository gate"),
                )
            self.assertEqual(result, 0)

    def test_dry_run_does_not_validate_or_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = install_skill.main(
                    ["--platform", "codex", "--target", os.fspath(target), "--dry-run"],
                    repository_validator=lambda: self.fail("--dry-run ran the repository gate"),
                )

            self.assertEqual(result, 0)
            self.assertFalse(target.exists())
            self.assertIn("agents/openai.yaml", output.getvalue())

    def test_repository_gate_failure_leaves_target_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            target.mkdir()
            marker = target / "existing.txt"
            marker.write_text("original", encoding="utf-8")
            before = snapshot(target)

            def fail_gate() -> None:
                raise RuntimeError("release validation failed")

            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, "release validation failed"):
                    install_skill.main(
                        ["--platform", "codex", "--target", os.fspath(target)],
                        repository_validator=fail_gate,
                    )

            self.assertEqual(snapshot(target), before)

    def test_staging_failure_leaves_existing_target_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            self.run_install(target)
            (target / "SKILL.md").write_text("older installed version", encoding="utf-8")
            (target / "unrelated.txt").write_text("preserved", encoding="utf-8")
            before = snapshot(target)

            with mock.patch.object(
                install_skill,
                "_copy_runtime_files",
                side_effect=OSError("simulated staging failure"),
            ):
                with self.assertRaisesRegex(OSError, "simulated staging failure"):
                    self.run_install(target)

            self.assertEqual(snapshot(target), before)
            self.assertEqual(
                list(target.parent.glob(f".{install_skill.SKILL_NAME}.staging-*")),
                [],
            )

    def test_commit_failure_rolls_back_without_mixed_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            self.run_install(target)
            (target / "SKILL.md").write_text("older installed version", encoding="utf-8")
            (target / "unrelated.txt").write_text("preserved", encoding="utf-8")
            before = snapshot(target)
            real_replace = install_skill._replace_path
            calls = 0

            def fail_second_replace(source: Path, destination: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("simulated commit failure")
                real_replace(source, destination)

            with mock.patch.object(install_skill, "_replace_path", side_effect=fail_second_replace):
                with self.assertRaisesRegex(OSError, "simulated commit failure"):
                    self.run_install(target)

            self.assertEqual(snapshot(target), before)
            self.assertEqual(
                list(target.parent.glob(f".{install_skill.SKILL_NAME}.staging-*")),
                [],
            )

    def test_top_level_destination_symlink_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            outside = Path(directory) / "outside"
            outside.mkdir()
            try:
                target.symlink_to(outside, target_is_directory=True)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"directory symlinks unavailable: {error}")

            with self.assertRaisesRegex(install_skill.UnsafeDestinationError, "symlink"):
                install_skill.main(
                    ["--platform", "codex", "--target", os.fspath(target)],
                    repository_validator=lambda: self.fail("unsafe target reached repository gate"),
                )
            self.assertEqual(list(outside.iterdir()), [])

    def test_nested_directory_and_file_symlinks_are_refused_without_following(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            target.mkdir()
            outside = Path(directory) / "outside"
            outside.mkdir()
            try:
                (target / "references").symlink_to(outside, target_is_directory=True)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"directory symlinks unavailable: {error}")

            with self.assertRaisesRegex(install_skill.UnsafeDestinationError, "symlink"):
                self.run_install(target)
            self.assertEqual(list(outside.iterdir()), [])

            (target / "references").unlink()
            secret = outside / "secret.txt"
            secret.write_text("do not overwrite", encoding="utf-8")
            (target / "SKILL.md").symlink_to(secret)
            with self.assertRaisesRegex(install_skill.UnsafeDestinationError, "symlink"):
                install_skill.main(
                    ["--platform", "codex", "--target", os.fspath(target), "--check"],
                    repository_validator=lambda: self.fail("--check reached repository gate"),
                )
            self.assertEqual(secret.read_text(encoding="utf-8"), "do not overwrite")

    def test_platform_file_selection_matches_each_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            codex_target = self.target(directory, "codex-skills")
            claude_target = self.target(directory, "claude-skills")

            self.run_install(codex_target, "codex")
            self.run_install(claude_target, "claude-code")

            self.assert_manifest_matches(codex_target, "codex")
            self.assert_manifest_matches(claude_target, "claude-code")
            self.assertTrue((codex_target / "agents" / "openai.yaml").is_file())
            self.assertFalse((claude_target / "agents" / "openai.yaml").exists())
            expected_claude_files = {
                relative.as_posix() for relative in install_skill.runtime_files("claude-code")
            }
            actual_claude_files = {
                path.relative_to(claude_target).as_posix()
                for path in claude_target.rglob("*")
                if path.is_file()
            }
            self.assertEqual(actual_claude_files, expected_claude_files)

    def test_cross_platform_target_reuse_is_rejected_for_install_and_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = self.target(directory)
            self.run_install(target, "codex")
            before = snapshot(target)

            for mode in ([], ["--check"]):
                with self.subTest(mode=mode), self.assertRaisesRegex(
                    install_skill.PlatformConflictError,
                    "different platform",
                ):
                    install_skill.main(
                        [
                            "--platform",
                            "claude-code",
                            "--target",
                            os.fspath(target),
                            *mode,
                        ],
                        repository_validator=lambda: self.fail(
                            "platform conflict reached repository gate"
                        ),
                    )

            self.assertEqual(snapshot(target), before)


if __name__ == "__main__":
    unittest.main()
