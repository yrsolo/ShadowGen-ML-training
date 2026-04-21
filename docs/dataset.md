# Dataset Notes

Status: initial pointer only; no data is copied into this repository.

## Selected Dataset

```text
\\riper\datasets\3D\final_objaverse_v1
```

This is the current dataset for the first ShadowGen training work.

## Observed Top-Level Layout

Initial non-mutating inspection showed:

- `manifest.json`
- `eligible_models.json`
- `metadata/`
- `passes/`
- `_tmp_passes/`
- root-level `*.png` composite images

The `_tmp_passes/` directory should be treated as temporary until confirmed.

The current top-level entry count reported by `shadowgen-training
inspect-dataset` is `9476`.

## Current Training Assumption

Available supervision:

- ready composite image with shadow,
- object mask.

Initial target policy:

- treat the model output as `shadow_layer`,
- focus training/evaluation on the non-object region,
- ignore imperfect generated pixels inside the object mask because inference
  overlays the original object afterward.

## Next Inspection Questions

- How are composites paired with masks and metadata?
- Which files under `passes/` are required for training?
- Are masks binary or soft?
- Does `manifest.json` contain enough metadata to define train/validation/test
  splits?
- Are light angle, elevation, softness, or reflection labels available?
