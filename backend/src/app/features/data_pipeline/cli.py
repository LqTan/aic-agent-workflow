"""CLI entry point for the data pipeline.

Usage::

    uv run python -m app.features.data_pipeline.cli scan \
        --data-root ./data

    uv run python -m app.features.data_pipeline.cli prepare-data \
        --data-root ./data [--collection-output ./data/collection.json]

    uv run python -m app.features.data_pipeline.cli validate \
        --manifest ./data/manifest.csv
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .manifest import build_collection, build_manifest, validate_manifest
from .scanner import scan_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.features.data_pipeline.cli",
        description="Prepare the AIC dataset manifest for the search engine.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser(
        "scan", help="Inspect dataset layout and report missing sources."
    )
    scan.add_argument("--data-root", type=Path, default=Path("./data"))
    scan.add_argument(
        "--deep",
        action="store_true",
        help="Also validate per-video keyframe/feature counts.",
    )

    prepare = subparsers.add_parser(
        "prepare-data",
        help="Generate manifest.csv (+ validate + collection.json).",
    )
    prepare.add_argument("--data-root", type=Path, default=Path("./data"))
    prepare.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Override manifest output path (default <data-root>/manifest.csv).",
    )
    prepare.add_argument(
        "--collection-output",
        type=Path,
        default=None,
        help="Override collection.json output path.",
    )
    prepare.add_argument(
        "--skip-collection",
        action="store_true",
        help="Skip emitting collection.json.",
    )

    validate = subparsers.add_parser("validate", help="Validate an existing manifest.")
    validate.add_argument(
        "--manifest",
        type=Path,
        default=Path("./data/manifest.csv"),
    )
    validate.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Override data root used to resolve image paths.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "scan":
        report = scan_dataset(args.data_root, deep=args.deep)
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return 0 if report.valid else 2
    if args.command == "prepare-data":
        manifest_info = build_manifest(args.data_root, output_path=args.manifest)
        validation = validate_manifest(manifest_info["output"], data_root=args.data_root)
        if not validation["valid"]:
            print(json.dumps({"manifest": manifest_info, "validation": validation}, indent=2))
            print("VALIDATION FAILED — fix the manifest before building the index.", file=sys.stderr)
            return 1
        if not args.skip_collection:
            build_collection(
                manifest_info["output"],
                output_path=args.collection_output,
            )
        print(
            json.dumps(
                {"manifest": manifest_info, "validation": validation},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    if args.command == "validate":
        result = validate_manifest(args.manifest, data_root=args.data_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["valid"] else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
