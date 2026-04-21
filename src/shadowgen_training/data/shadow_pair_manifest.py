from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_DATASET_VERSION = "shadow_pair_v1"


@dataclass(frozen=True)
class BuildManifestResult:
    dataset_version: str
    source_manifest: str
    output: Path
    summary_output: Path | None
    total_records: int
    written_records: int
    skipped_not_ok: int
    skipped_missing_paths: int
    split_counts: dict[str, int]


def object_split(uid: str, train_pct: int = 80, val_pct: int = 10) -> str:
    """Return a deterministic object-level split for a source object UID."""

    if train_pct <= 0 or val_pct <= 0 or train_pct + val_pct >= 100:
        raise ValueError("train_pct and val_pct must be positive and sum below 100")
    digest = hashlib.sha1(uid.encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) % 100
    if bucket < train_pct:
        return "train"
    if bucket < train_pct + val_pct:
        return "val"
    return "test"


def load_source_manifest(root: Path) -> dict[str, Any]:
    path = root / "manifest.json"
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected manifest root mapping: {path}")
    records = data.get("records")
    if not isinstance(records, list):
        raise ValueError(f"Expected manifest.records list: {path}")
    return data


def _relative_path(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("\\", "/")


def _required_paths(record: dict[str, Any]) -> dict[str, str]:
    pass_paths = record.get("pass_paths")
    if not isinstance(pass_paths, dict):
        pass_paths = {}
    paths = {
        "composite": _relative_path(record.get("preview_path")),
        "metadata": _relative_path(record.get("metadata_path")),
        "object_mask": _relative_path(pass_paths.get("object_mask")),
        "depth": _relative_path(pass_paths.get("depth_normalized")),
        "normal": _relative_path(pass_paths.get("normal")),
    }
    return {key: value for key, value in paths.items() if value}


def missing_paths(root: Path, paths: dict[str, str]) -> list[str]:
    missing: list[str] = []
    for key in ("composite", "metadata", "object_mask", "depth", "normal"):
        rel = paths.get(key)
        if not rel or not (root / rel).exists():
            missing.append(key)
    return missing


def convert_record(
    record: dict[str, Any],
    *,
    root: Path,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> dict[str, Any] | None:
    if record.get("ok") is not True:
        return None

    uid = str(record.get("uid") or record.get("sample_id") or "")
    if not uid:
        return None

    paths = _required_paths(record)
    missing = missing_paths(root, paths)
    if missing:
        return None

    render = record.get("render_params")
    if not isinstance(render, dict):
        render = {}

    key_size = render.get("key_size")
    return {
        "dataset_version": dataset_version,
        "sample_id": record.get("sample_id"),
        "split": object_split(uid),
        "source_dataset": "final_objaverse_v1",
        "uid": uid,
        "paths": paths,
        "object": {
            "category_groups": record.get("category_groups"),
            "lvis_categories": record.get("lvis_categories"),
            "license": record.get("license"),
            "file_identifier": record.get("fileIdentifier"),
            "transparent_material_detected": record.get(
                "transparent_material_detected"
            ),
        },
        "controls": {
            "angle_deg": render.get("key_azimuth_deg"),
            "elevation_deg": render.get("key_elevation_deg"),
            "softness_source": "render_params.key_size",
            "softness_raw": key_size,
            "reflection": 0.0,
            "camera_elevation_deg": render.get("camera_elevation_deg"),
            "camera_fov_deg": render.get("camera_fov_deg"),
            "object_yaw_deg": render.get("object_yaw_deg"),
        },
        "target": {
            "kind": "shadow_layer",
            "source": "composite_with_shadow",
            "loss_region": "outside_object_mask",
            "inside_object_mask_policy": "ignored",
        },
    }


def iter_converted_records(
    root: Path,
    records: Iterable[dict[str, Any]],
    *,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> Iterable[dict[str, Any]]:
    for record in records:
        converted = convert_record(record, root=root, dataset_version=dataset_version)
        if converted is not None:
            yield converted


def build_shadow_pair_manifest(
    *,
    root: Path,
    output: Path,
    summary_output: Path | None = None,
    dataset_version: str = DEFAULT_DATASET_VERSION,
    limit: int | None = None,
) -> BuildManifestResult:
    source = load_source_manifest(root)
    records = source["records"]

    output.parent.mkdir(parents=True, exist_ok=True)
    if summary_output is not None:
        summary_output.parent.mkdir(parents=True, exist_ok=True)

    total_records = 0
    written_records = 0
    skipped_not_ok = 0
    skipped_missing_paths = 0
    split_counts = {"train": 0, "val": 0, "test": 0}

    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            total_records += 1
            if record.get("ok") is not True:
                skipped_not_ok += 1
                continue
            paths = _required_paths(record)
            if missing_paths(root, paths):
                skipped_missing_paths += 1
                continue
            converted = convert_record(
                record,
                root=root,
                dataset_version=dataset_version,
            )
            if converted is None:
                skipped_missing_paths += 1
                continue
            handle.write(json.dumps(converted, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            written_records += 1
            split_counts[converted["split"]] += 1
            if limit is not None and written_records >= limit:
                break

    result = BuildManifestResult(
        dataset_version=dataset_version,
        source_manifest=str(root / "manifest.json"),
        output=output,
        summary_output=summary_output,
        total_records=total_records,
        written_records=written_records,
        skipped_not_ok=skipped_not_ok,
        skipped_missing_paths=skipped_missing_paths,
        split_counts=split_counts,
    )

    if summary_output is not None:
        summary = {
            "dataset_version": result.dataset_version,
            "source_manifest": result.source_manifest,
            "output": str(result.output).replace("\\", "/"),
            "total_records_seen": result.total_records,
            "written_records": result.written_records,
            "skipped_not_ok": result.skipped_not_ok,
            "skipped_missing_paths": result.skipped_missing_paths,
            "split_counts": result.split_counts,
            "target_policy": {
                "kind": "shadow_layer",
                "loss_region": "outside_object_mask",
                "inside_object_mask_policy": "ignored",
            },
        }
        summary_output.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return result
