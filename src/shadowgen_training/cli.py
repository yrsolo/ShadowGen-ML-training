from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml


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
