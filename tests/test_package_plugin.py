from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("package_plugin", SCRIPTS / "package_plugin.py")
assert SPEC and SPEC.loader
package_plugin = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package_plugin)


class PackagePluginTest(unittest.TestCase):
    def test_manifest_enforces_final_directory_text_limits(self) -> None:
        source = json.loads(package_plugin.PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        cases = {
            "displayName": 30,
            "shortDescription": 30,
            "longDescription": 4000,
            "developerName": 80,
        }
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            manifest_path = Path(directory) / "plugin.json"
            for field, maximum in cases.items():
                with self.subTest(field=field):
                    manifest = json.loads(json.dumps(source))
                    manifest["interface"][field] = "x" * (maximum + 1)
                    if field == "developerName":
                        manifest["author"]["name"] = manifest["interface"][field]
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    with self.assertRaisesRegex(
                        package_plugin.PackagingError,
                        f"interface\\.{field} must be at most {maximum} characters",
                    ):
                        package_plugin.load_manifest(manifest_path)

    def test_build_contains_exact_runtime_and_submission_archive(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory) / "build"
            result = package_plugin.build(output)
            plugin_root = Path(result["plugin_root"])
            skill_root = plugin_root / "skills" / package_plugin.PLUGIN_NAME

            expected_runtime = {
                relative.as_posix()
                for relative in package_plugin.install_skill.runtime_files("codex")
            }
            actual_runtime = {
                path.relative_to(skill_root).as_posix()
                for path in skill_root.rglob("*")
                if path.is_file() and path.name != "LICENSE.txt"
            }
            self.assertEqual(actual_runtime, expected_runtime)
            self.assertEqual((skill_root / "SKILL.md").read_bytes(), (ROOT / "SKILL.md").read_bytes())
            manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
            self.assertTrue(manifest_path.is_file())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["author"]["name"], "Huan Min Wei")
            self.assertEqual(manifest["author"]["email"], "support@complexenough.com")
            self.assertEqual(manifest["author"]["url"], "https://complexenough.com/en/")
            self.assertEqual(
                manifest["repository"],
                "https://github.com/complex-enough/complex-enough",
            )
            self.assertEqual(manifest["interface"]["developerName"], manifest["author"]["name"])
            self.assertEqual(manifest["interface"]["displayName"], "Complex Enough")
            self.assertEqual(
                manifest["interface"]["shortDescription"],
                "Agent-led plan quality control",
            )

            archive = Path(result["archive"])
            with zipfile.ZipFile(archive) as bundle:
                names = set(bundle.namelist())
            self.assertIn(".codex-plugin/plugin.json", names)
            self.assertIn(f"skills/{package_plugin.PLUGIN_NAME}/SKILL.md", names)
            self.assertIn("assets/composer-icon.png", names)
            self.assertIn("assets/logo.png", names)
            self.assertIn("assets/logo-dark.png", names)
            self.assertNotIn("README.md", names)
            self.assertFalse(any(name.startswith("evals/") or name.startswith("tests/") for name in names))

    def test_build_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            first = package_plugin.build(Path(directory) / "first")
            second = package_plugin.build(Path(directory) / "second")
            self.assertEqual(first["sha256"], second["sha256"])
            self.assertEqual(Path(first["archive"]).read_bytes(), Path(second["archive"]).read_bytes())

    def test_existing_output_requires_explicit_replace(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            output = Path(directory) / "build"
            package_plugin.build(output)
            with self.assertRaisesRegex(package_plugin.PackagingError, "--replace"):
                package_plugin.build(output)
            replaced = package_plugin.build(output, replace=True)
            self.assertTrue(Path(replaced["archive"]).is_file())

    def test_marketplace_points_to_generated_plugin(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            result = package_plugin.build(Path(directory) / "build")
            marketplace = json.loads(Path(result["marketplace"]).read_text(encoding="utf-8"))
            self.assertEqual(
                Path(result["marketplace"]).relative_to(Path(result["plugin_root"]).parents[1]).as_posix(),
                ".agents/plugins/marketplace.json",
            )
            entry = marketplace["plugins"][0]
            self.assertEqual(entry["name"], package_plugin.PLUGIN_NAME)
            self.assertEqual(entry["source"]["path"], f"./plugins/{package_plugin.PLUGIN_NAME}")
            self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
            self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
            self.assertEqual(
                entry["category"],
                package_plugin.load_manifest()["interface"]["category"],
            )


if __name__ == "__main__":
    unittest.main()
