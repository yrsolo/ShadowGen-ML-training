# Toy Baseline

This baseline is a pipeline smoke test, not the product model.

It validates:

- `shadow_pair_v1` manifest loading,
- composite/mask/depth/normal image reads,
- masked non-object loss,
- ignored object-mask region policy,
- optional W&B logging.

## Build Manifest

```powershell
uv run shadowgen-training build-manifest `
  --root "\\riper\datasets\3D\final_objaverse_v1" `
  --output manifests/shadow_pair_v1.jsonl `
  --summary manifests/shadow_pair_v1.summary.json
```

## Run Toy Overfit

Outputs go to ignored `outputs/`.

```powershell
uv run shadowgen-training train-toy `
  --root "\\riper\datasets\3D\final_objaverse_v1" `
  --manifest manifests/shadow_pair_v1.jsonl `
  --output-dir outputs/toy_pixel_overfit `
  --max-samples 8 `
  --steps 200 `
  --wandb-mode disabled
```

Use `--wandb-mode offline` or `--wandb-mode online` after `wandb` is installed
and configured.

## Smoke Result

Validated on 2026-04-21 with:

```powershell
uv run shadowgen-training train-toy `
  --root "\\riper\datasets\3D\final_objaverse_v1" `
  --manifest manifests/shadow_pair_v1.jsonl `
  --output-dir outputs/toy_pixel_smoke `
  --max-samples 4 `
  --size 64 `
  --pixels-per-sample 1024 `
  --steps 30 `
  --wandb-mode disabled
```

Result:

- samples: `4`
- steps: `30`
- initial loss: `0.47687230`
- final loss: `0.02357174`
