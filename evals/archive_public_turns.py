#!/usr/bin/env python3
"""Archive exact public assistant finals captured by an isolated eval runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_repo import _contains_prohibited_private_output_marker  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("turn_files", nargs="+", type=Path)
    args = parser.parse_args()

    if args.output.exists():
        parser.error(f"refusing to overwrite existing archive: {args.output}")

    outputs = [path.read_text(encoding="utf-8") for path in args.turn_files]
    if any(not output.strip() for output in outputs):
        parser.error("every captured public turn must be nonempty")
    if any(_contains_prohibited_private_output_marker(output) for output in outputs):
        parser.error("captured output contains a prohibited private-output identifier")

    payload = {"case_id": args.case_id, "assistant_outputs": outputs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    json.loads(args.output.read_text(encoding="utf-8"))
    print(f"archived {args.case_id}: {len(outputs)} turn(s) -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
