#!/usr/bin/env python3
"""Build a deterministic skills-only plugin from the canonical skill source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path

import install_skill


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_NAME = install_skill.SKILL_NAME
PLUGIN_MANIFEST = ROOT / "packaging" / "plugin.json"
PLUGIN_ASSET_ROOT = ROOT / "packaging" / "assets"
DEFAULT_OUTPUT_ROOT = ROOT / "build"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)
DIRECTORY_TEXT_LIMITS = {
    "displayName": 30,
    "shortDescription": 30,
    "longDescription": 4000,
    "developerName": 80,
}
DIRECTORY_URL_FIELDS = {
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
}
DIRECTORY_ASSET_FIELDS = {
    "composerIcon",
    "logo",
    "logoDark",
}


class PackagingError(ValueError):
    """Raised when a plugin bundle cannot be built safely or consistently."""


def load_manifest(path: Path = PLUGIN_MANIFEST) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("name") != PLUGIN_NAME:
        raise PackagingError("plugin manifest name must match the canonical skill name")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise PackagingError("plugin manifest version must be strict semantic versioning")
    if manifest.get("skills") != "./skills/":
        raise PackagingError("skills-only plugin manifest must use ./skills/")
    author = manifest.get("author", {})
    if not isinstance(author.get("name"), str) or not author["name"].strip():
        raise PackagingError("plugin manifest requires author.name")
    if not isinstance(author.get("url"), str) or not author["url"].startswith("https://"):
        raise PackagingError("plugin manifest requires an absolute HTTPS author.url")
    if not isinstance(author.get("email"), str) or not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", author["email"]
    ):
        raise PackagingError("plugin manifest requires a public author.email")
    for field in ("homepage", "repository"):
        if not isinstance(manifest.get(field), str) or not manifest[field].startswith("https://"):
            raise PackagingError(f"plugin manifest requires an absolute HTTPS {field}")
    interface = manifest.get("interface")
    required_interface = {
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
        "capabilities",
        "defaultPrompt",
    }
    if not isinstance(interface, dict) or required_interface - set(interface):
        missing = sorted(required_interface - set(interface or {}))
        raise PackagingError(f"plugin manifest missing interface fields: {missing}")
    for field, maximum in DIRECTORY_TEXT_LIMITS.items():
        value = interface[field]
        if not isinstance(value, str) or not value.strip():
            raise PackagingError(f"interface.{field} must be a nonempty string")
        if len(value) > maximum:
            raise PackagingError(
                f"interface.{field} must be at most {maximum} characters"
            )
    for field in ("displayName", "shortDescription", "developerName"):
        if "\n" in interface[field] or "\r" in interface[field]:
            raise PackagingError(f"interface.{field} must be a single line")
    if interface["developerName"] != author["name"]:
        raise PackagingError("interface.developerName must match author.name")
    for field in DIRECTORY_URL_FIELDS:
        value = interface.get(field)
        if not isinstance(value, str) or not value.startswith("https://"):
            raise PackagingError(f"interface.{field} must be an absolute HTTPS URL")
    for field in DIRECTORY_ASSET_FIELDS:
        value = interface.get(field)
        if not isinstance(value, str) or not re.fullmatch(r"\./assets/[A-Za-z0-9._-]+", value):
            raise PackagingError(f"interface.{field} must point to a plugin asset")
        source = ROOT / "packaging" / value.removeprefix("./")
        if not source.is_file() or source.is_symlink():
            raise PackagingError(f"interface.{field} asset is missing or unsafe")
    prompts = interface["defaultPrompt"]
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
        raise PackagingError("plugin manifest requires one to three starter prompts")
    if any(not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 128 for prompt in prompts):
        raise PackagingError("starter prompts must be nonempty strings of at most 128 characters")
    return manifest


def _assert_safe_output_root(output_root: Path) -> Path:
    absolute = Path(os.path.abspath(os.fspath(output_root.expanduser())))
    if absolute in {Path("/"), Path.home().resolve(), ROOT}:
        raise PackagingError("refusing unsafe plugin output root")
    if ROOT not in absolute.parents:
        raise PackagingError("plugin output root must stay inside the repository")
    return absolute


def _copy_runtime(plugin_root: Path) -> None:
    skill_root = plugin_root / "skills" / PLUGIN_NAME
    for relative in install_skill.runtime_files("codex"):
        source = ROOT / relative
        if not source.is_file() or source.is_symlink():
            raise PackagingError(f"runtime source is missing or unsafe: {relative}")
        destination = skill_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)
    shutil.copy2(ROOT / "LICENSE", skill_root / "LICENSE.txt", follow_symlinks=False)


def _copy_plugin_assets(plugin_root: Path, manifest: dict) -> None:
    copied: set[Path] = set()
    for field in sorted(DIRECTORY_ASSET_FIELDS):
        relative = Path(manifest["interface"][field].removeprefix("./"))
        if relative in copied:
            continue
        source = ROOT / "packaging" / relative
        destination = plugin_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)
        copied.add(relative)


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def _marketplace(category: str) -> dict:
    return {
        "name": "complex-enough-releases",
        "interface": {"displayName": "Complex Enough Releases"},
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": {"source": "local", "path": f"./plugins/{PLUGIN_NAME}"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": category,
            }
        ],
    }


def _zip_mode(path: Path) -> int:
    mode = path.stat().st_mode
    return 0o755 if mode & stat.S_IXUSR else 0o644


def _write_reproducible_zip(plugin_root: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sorted(path for path in plugin_root.rglob("*") if path.is_file()):
            relative = source.relative_to(plugin_root).as_posix()
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (_zip_mode(source) & 0xFFFF) << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(output_root: Path = DEFAULT_OUTPUT_ROOT, *, replace: bool = False) -> dict[str, Path | str]:
    output_root = _assert_safe_output_root(output_root)
    manifest = load_manifest()
    if output_root.exists() and not replace:
        raise PackagingError(f"output already exists: {output_root}; pass --replace to rebuild it")

    output_root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".plugin-build-", dir=output_root.parent) as directory:
        staged_root = Path(directory) / output_root.name
        marketplace_root = staged_root / "marketplace"
        plugin_root = marketplace_root / "plugins" / PLUGIN_NAME
        _write_json(plugin_root / ".codex-plugin" / "plugin.json", manifest)
        _copy_runtime(plugin_root)
        _copy_plugin_assets(plugin_root, manifest)
        shutil.copy2(ROOT / "LICENSE", plugin_root / "LICENSE", follow_symlinks=False)
        marketplace_path = marketplace_root / ".agents" / "plugins" / "marketplace.json"
        _write_json(marketplace_path, _marketplace(manifest["interface"]["category"]))

        archive = staged_root / "submission" / f"{PLUGIN_NAME}-{manifest['version']}.zip"
        _write_reproducible_zip(plugin_root, archive)
        digest = sha256(archive)
        (archive.parent / f"{archive.name}.sha256").write_text(
            f"{digest}  {archive.name}\n", encoding="utf-8"
        )

        if output_root.exists():
            shutil.rmtree(output_root)
        staged_root.rename(output_root)

    return {
        "plugin_root": output_root / "marketplace" / "plugins" / PLUGIN_NAME,
        "marketplace": output_root / "marketplace" / ".agents" / "plugins" / "marketplace.json",
        "archive": output_root / "submission" / f"{PLUGIN_NAME}-{manifest['version']}.zip",
        "sha256": digest,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="generated build root inside this repository (default: build)",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="replace an existing generated output root",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build(args.output_root, replace=args.replace)
    except (OSError, PackagingError, json.JSONDecodeError) as error:
        print(f"plugin packaging failed: {error}", file=sys.stderr)
        return 1
    for key in ("plugin_root", "marketplace", "archive", "sha256"):
        print(f"{key}: {result[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
