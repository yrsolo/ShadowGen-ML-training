from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

from shadowgen_training.data.shadow_pair_manifest import (
    DEFAULT_DATASET_VERSION,
    build_shadow_pair_manifest,
)
from shadowgen_training.toy.pixel_baseline import train_toy_pixel_baseline


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_ROOT = r"\\riper\datasets\3D\final_objaverse_v1"

REQUIRED_DIRS = (
    "configs",
    "docs",
    "src/shadowgen_training",
    "tests",
)

REQUIRED_GITIGNORE_PATTERNS = (
    "data/",
    "datasets/",
    "outputs/",
    "runs/",
    "checkpoints/",
    "wandb/",
    "mlruns/",
    ".playwright-cli/",
    "*.png",
    "*.jpg",
    "*.webp",
    "*.pt",
    "*.pth",
    "*.ckpt",
    "*.safetensors",
    "*.onnx",
    "*.engine",
    "*.plan",
    "*.npy",
    "*.npz",
)


class CliError(RuntimeError):
    """User-facing CLI error."""


def _repo_path(path: str) -> Path:
    return REPO_ROOT / path


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise CliError(f"Config file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise CliError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise CliError(f"Config root must be a mapping: {path}")
    return data


def _validate_project_config(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    project = data.get("project")
    data_section = data.get("data")
    model = data.get("model")
    artifacts = data.get("artifacts")

    if not isinstance(project, dict):
        errors.append("missing mapping: project")
    elif project.get("contract_variant") != "v2-diff":
        errors.append("project.contract_variant must be v2-diff")

    if not isinstance(data_section, dict):
        errors.append("missing mapping: data")
    else:
        if data_section.get("dataset_root_env") != "SHADOWGEN_DATASET_ROOT":
            errors.append("data.dataset_root_env must be SHADOWGEN_DATASET_ROOT")
        if data_section.get("copy_raw_data_into_repo") is not False:
            errors.append("data.copy_raw_data_into_repo must be false")
        if data_section.get("git_tracked_data") is not False:
            errors.append("data.git_tracked_data must be false")

    if not isinstance(model, dict):
        errors.append("missing mapping: model")
    else:
        if model.get("family") != "stable_diffusion":
            errors.append("model.family must be stable_diffusion")
        if model.get("architecture") != "sd1.5":
            errors.append("model.architecture must be sd1.5")
        if model.get("toy_baseline_required_for_pipeline_smoke") is not True:
            errors.append("model.toy_baseline_required_for_pipeline_smoke must be true")
        candidates = model.get("candidates")
        if not isinstance(candidates, list) or "stable_diffusion_1_5" not in candidates:
            errors.append("model.candidates must include stable_diffusion_1_5")
        contract = model.get("contract")
        if not isinstance(contract, dict):
            errors.append("missing mapping: model.contract")
        else:
            if contract.get("stage_key") != "shadow_generator":
                errors.append("model.contract.stage_key must be shadow_generator")
            if contract.get("model_variant") != "v2-diff":
                errors.append("model.contract.model_variant must be v2-diff")

    if not isinstance(artifacts, dict):
        errors.append("missing mapping: artifacts")
    elif artifacts.get("commit_large_artifacts_to_git") is not False:
        errors.append("artifacts.commit_large_artifacts_to_git must be false")

    return errors


def command_doctor(_args: argparse.Namespace) -> int:
    print("ShadowGen training doctor")
    print(f"python: {sys.version.split()[0]}")

    uv_path = shutil.which("uv")
    print(f"uv: {uv_path or 'not found'}")

    dataset_root = os.environ.get("SHADOWGEN_DATASET_ROOT", DEFAULT_DATASET_ROOT)
    dataset_path = Path(dataset_root)
    print(f"dataset_root: {dataset_root}")
    print(f"dataset_accessible: {dataset_path.exists()}")

    missing_dirs = [path for path in REQUIRED_DIRS if not _repo_path(path).exists()]
    if missing_dirs:
        raise CliError(f"Missing required directories: {', '.join(missing_dirs)}")
    print("required_dirs: ok")

    gitignore = _repo_path(".gitignore")
    gitignore_text = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    missing_patterns = [
        pattern for pattern in REQUIRED_GITIGNORE_PATTERNS if pattern not in gitignore_text
    ]
    if missing_patterns:
        raise CliError(
            "Missing artifact safety patterns in .gitignore: "
            + ", ".join(missing_patterns)
        )
    print("artifact_policy: ok")

    return 0


def command_inspect_dataset(args: argparse.Namespace) -> int:
    root = Path(args.root or os.environ.get("SHADOWGEN_DATASET_ROOT", DEFAULT_DATASET_ROOT))
    print(f"dataset_root: {root}")
    if not root.exists():
        raise CliError(f"Dataset root is not accessible: {root}")
    if not root.is_dir():
        raise CliError(f"Dataset root is not a directory: {root}")

    children = sorted(root.iterdir(), key=lambda item: item.name.lower())
    print(f"top_level_entries: {len(children)}")
    for child in children[:20]:
        kind = "dir" if child.is_dir() else "file"
        print(f"- {kind}: {child.name}")
    if len(children) > 20:
        print(f"... {len(children) - 20} more entries not shown")
    return 0


def command_validate_config(args: argparse.Namespace) -> int:
    path = Path(args.config)
    if not path.is_absolute():
        path = REPO_ROOT / path
    data = _load_yaml(path)
    errors = _validate_project_config(data)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"config_valid: {path}")
    return 0


def command_build_manifest(args: argparse.Namespace) -> int:
    root = Path(args.root or os.environ.get("SHADOWGEN_DATASET_ROOT", DEFAULT_DATASET_ROOT))
    output = Path(args.output)
    summary_output = Path(args.summary) if args.summary else None
    result = build_shadow_pair_manifest(
        root=root,
        output=output,
        summary_output=summary_output,
        dataset_version=args.dataset_version,
        limit=args.limit,
    )
    print(f"dataset_version: {result.dataset_version}")
    print(f"source_manifest: {result.source_manifest}")
    print(f"output: {result.output}")
    if result.summary_output is not None:
        print(f"summary: {result.summary_output}")
    print(f"records_seen: {result.total_records}")
    print(f"records_written: {result.written_records}")
    print(f"skipped_not_ok: {result.skipped_not_ok}")
    print(f"skipped_missing_paths: {result.skipped_missing_paths}")
    print(f"split_counts: {result.split_counts}")
    return 0


def command_train_toy(args: argparse.Namespace) -> int:
    root = Path(args.root or os.environ.get("SHADOWGEN_DATASET_ROOT", DEFAULT_DATASET_ROOT))
    result = train_toy_pixel_baseline(
        dataset_root=root,
        manifest=Path(args.manifest),
        output_dir=Path(args.output_dir),
        split=args.split,
        max_samples=args.max_samples,
        size=args.size,
        pixels_per_sample=args.pixels_per_sample,
        steps=args.steps,
        learning_rate=args.learning_rate,
        seed=args.seed,
        wandb_mode=args.wandb_mode,
        wandb_project=args.wandb_project,
    )
    print(f"toy_baseline: {result.output_dir}")
    print(f"metrics: {result.metrics_path}")
    print(f"weights: {result.weights_path}")
    print(f"samples: {result.samples}")
    print(f"steps: {result.steps}")
    print(f"initial_loss: {result.initial_loss:.8f}")
    print(f"final_loss: {result.final_loss:.8f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shadowgen-training")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check local training workspace setup.")
    doctor.set_defaults(func=command_doctor)

    inspect_dataset = subparsers.add_parser(
        "inspect-dataset",
        help="Check top-level dataset root accessibility without indexing data.",
    )
    inspect_dataset.add_argument("--root", default=None, help="Dataset root path.")
    inspect_dataset.set_defaults(func=command_inspect_dataset)

    validate_config = subparsers.add_parser(
        "validate-config",
        help="Validate the project YAML configuration.",
    )
    validate_config.add_argument("config", help="Path to YAML config.")
    validate_config.set_defaults(func=command_validate_config)

    build_manifest = subparsers.add_parser(
        "build-manifest",
        help="Build the text-only shadow_pair_v1 JSONL manifest.",
    )
    build_manifest.add_argument("--root", default=None, help="Dataset root path.")
    build_manifest.add_argument(
        "--output",
        default="manifests/shadow_pair_v1.jsonl",
        help="Output JSONL manifest path.",
    )
    build_manifest.add_argument(
        "--summary",
        default="manifests/shadow_pair_v1.summary.json",
        help="Output summary JSON path.",
    )
    build_manifest.add_argument(
        "--dataset-version",
        default=DEFAULT_DATASET_VERSION,
        help="Dataset version name to write into records.",
    )
    build_manifest.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional record limit for debugging.",
    )
    build_manifest.set_defaults(func=command_build_manifest)

    train_toy = subparsers.add_parser(
        "train-toy",
        help="Run a small masked pixel baseline to smoke-test the pipeline.",
    )
    train_toy.add_argument("--root", default=None, help="Dataset root path.")
    train_toy.add_argument(
        "--manifest",
        default="manifests/shadow_pair_v1.jsonl",
        help="JSONL manifest path.",
    )
    train_toy.add_argument(
        "--output-dir",
        default="outputs/toy_pixel_overfit",
        help="Ignored output directory for toy metrics and weights.",
    )
    train_toy.add_argument("--split", default="train", choices=["train", "val", "test"])
    train_toy.add_argument("--max-samples", type=int, default=8)
    train_toy.add_argument("--size", type=int, default=128)
    train_toy.add_argument("--pixels-per-sample", type=int, default=4096)
    train_toy.add_argument("--steps", type=int, default=200)
    train_toy.add_argument("--learning-rate", type=float, default=0.05)
    train_toy.add_argument("--seed", type=int, default=7)
    train_toy.add_argument(
        "--wandb-mode",
        default="disabled",
        choices=["disabled", "offline", "online"],
        help="W&B mode for toy logging.",
    )
    train_toy.add_argument("--wandb-project", default="shadowgen-training")
    train_toy.set_defaults(func=command_train_toy)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
