from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class ToyTrainResult:
    output_dir: Path
    metrics_path: Path
    weights_path: Path
    initial_loss: float
    final_loss: float
    steps: int
    samples: int


def _read_jsonl(path: Path, *, split: str, max_samples: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("split") != split:
                continue
            rows.append(row)
            if len(rows) >= max_samples:
                break
    if not rows:
        raise ValueError(f"No rows found for split={split!r} in {path}")
    return rows


def _image_array(path: Path, mode: str, size: int) -> np.ndarray:
    image = Image.open(path).convert(mode)
    resample = Image.Resampling.BILINEAR if mode != "L" else Image.Resampling.NEAREST
    image = image.resize((size, size), resample)
    array = np.asarray(image, dtype=np.float32) / 255.0
    if array.ndim == 2:
        array = array[..., None]
    return array


def _controls(row: dict[str, Any], size: int) -> np.ndarray:
    controls = row.get("controls") or {}
    angle = float(controls.get("angle_deg") or 0.0) / 360.0
    elevation = float(controls.get("elevation_deg") or 0.0) / 90.0
    softness = float(controls.get("softness_raw") or 0.0) / 3.0
    values = np.array([angle, elevation, softness], dtype=np.float32)
    return np.broadcast_to(values, (size, size, values.shape[0]))


def _load_training_arrays(
    *,
    dataset_root: Path,
    manifest: Path,
    split: str,
    max_samples: int,
    size: int,
    pixels_per_sample: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    rng = np.random.default_rng(seed)
    rows = _read_jsonl(manifest, split=split, max_samples=max_samples)

    features: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    weights: list[np.ndarray] = []

    for row in rows:
        paths = row["paths"]
        composite = _image_array(dataset_root / paths["composite"], "RGB", size)
        mask = _image_array(dataset_root / paths["object_mask"], "L", size)
        depth = _image_array(dataset_root / paths["depth"], "L", size)
        normal = _image_array(dataset_root / paths["normal"], "RGB", size)

        object_rgb = composite * mask
        outside = 1.0 - mask
        controls = _controls(row, size)
        bias = np.ones((size, size, 1), dtype=np.float32)
        x = np.concatenate([object_rgb, mask, depth, normal, controls, bias], axis=-1)
        y = composite
        w = outside

        flat_count = size * size
        take = min(pixels_per_sample, flat_count)
        indices = rng.choice(flat_count, size=take, replace=False)
        features.append(x.reshape(flat_count, -1)[indices])
        targets.append(y.reshape(flat_count, 3)[indices])
        weights.append(w.reshape(flat_count, 1)[indices])

    return (
        np.concatenate(features, axis=0),
        np.concatenate(targets, axis=0),
        np.concatenate(weights, axis=0),
        len(rows),
    )


def _maybe_wandb(mode: str, project: str, run_name: str) -> Any | None:
    if mode == "disabled":
        return None
    try:
        import wandb  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "wandb is not installed. Install it or run with --wandb-mode disabled."
        ) from exc
    return wandb.init(project=project, name=run_name, mode=mode)


def train_toy_pixel_baseline(
    *,
    dataset_root: Path,
    manifest: Path,
    output_dir: Path,
    split: str = "train",
    max_samples: int = 8,
    size: int = 128,
    pixels_per_sample: int = 4096,
    steps: int = 200,
    learning_rate: float = 0.05,
    seed: int = 7,
    wandb_mode: str = "disabled",
    wandb_project: str = "shadowgen-training",
) -> ToyTrainResult:
    if size <= 0 or steps <= 0 or max_samples <= 0:
        raise ValueError("size, steps, and max_samples must be positive")

    output_dir.mkdir(parents=True, exist_ok=True)
    x, y, w, sample_count = _load_training_arrays(
        dataset_root=dataset_root,
        manifest=manifest,
        split=split,
        max_samples=max_samples,
        size=size,
        pixels_per_sample=pixels_per_sample,
        seed=seed,
    )

    rng = np.random.default_rng(seed)
    weights = rng.normal(0.0, 0.02, size=(x.shape[1], 3)).astype(np.float32)
    velocity = np.zeros_like(weights)
    metrics: list[dict[str, float | int]] = []

    run = _maybe_wandb(
        wandb_mode,
        project=wandb_project,
        run_name=f"toy-pixel-overfit-{int(time.time())}",
    )

    initial_loss = math.nan
    final_loss = math.nan
    denom = float(np.maximum(w.sum() * 3.0, 1.0))
    for step in range(1, steps + 1):
        pred = np.clip(x @ weights, 0.0, 1.0)
        err = (pred - y) * w
        loss = float(np.sum(err * err) / denom)
        grad = (x.T @ (2.0 * err / denom)).astype(np.float32)
        velocity = 0.9 * velocity + grad
        weights -= learning_rate * velocity

        if step == 1:
            initial_loss = loss
        final_loss = loss
        if step == 1 or step == steps or step % max(1, steps // 10) == 0:
            item = {"step": step, "loss": loss}
            metrics.append(item)
            if run is not None:
                run.log(item)

    if run is not None:
        run.finish()

    metrics_path = output_dir / "metrics.json"
    weights_path = output_dir / "weights.npz"
    metrics_path.write_text(
        json.dumps(
            {
                "baseline": "toy_pixel_masked_linear",
                "manifest": str(manifest).replace("\\", "/"),
                "dataset_root": str(dataset_root).replace("\\", "/"),
                "split": split,
                "samples": sample_count,
                "size": size,
                "pixels_per_sample": pixels_per_sample,
                "steps": steps,
                "learning_rate": learning_rate,
                "initial_loss": initial_loss,
                "final_loss": final_loss,
                "loss_region": "outside_object_mask",
                "history": metrics,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    np.savez_compressed(weights_path, weights=weights)

    return ToyTrainResult(
        output_dir=output_dir,
        metrics_path=metrics_path,
        weights_path=weights_path,
        initial_loss=initial_loss,
        final_loss=final_loss,
        steps=steps,
        samples=sample_count,
    )
