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

## Source Manifest

`manifest.json` contains:

- `dataset_name`: `final_objaverse_v1`
- `resolution`: `768`
- `records`: `9889`
- `failures`: `12`
- `pass_layout`:
  - `passes/depth_normalized/<sample_id>.png`
  - `passes/normal/<sample_id>.png`
  - `passes/object_mask/<sample_id>.png`

Each record includes:

- `sample_id`
- source object `uid`
- `preview_path`
- `metadata_path`
- `pass_paths`
- `render_params`
- category and license metadata

Render params include useful control labels:

- `key_azimuth_deg` -> initial `angle_deg`
- `key_elevation_deg` -> initial `elevation_deg`
- `key_size` -> raw softness source, not yet normalized

## Current Training Assumption

Available supervision:

- ready composite image with shadow,
- object mask.

Initial target policy:

- treat the model output as `shadow_layer`,
- focus training/evaluation on the non-object region,
- ignore imperfect generated pixels inside the object mask because inference
  overlays the original object afterward.

## Derived Manifest

The first derived manifest is:

```text
manifests/shadow_pair_v1.jsonl
```

It stores relative paths and metadata only. It does not copy dataset images into
the repository.

Current build summary:

- source records seen: `9889`
- written complete records: `9797`
- skipped records with missing required paths: `92`
- split counts:
  - train: `7920`
  - val: `912`
  - test: `965`

Splits are deterministic and object-level based on source `uid`.

## Next Inspection Questions

- How are composites paired with masks and metadata?
- Which files under `passes/` are required for training?
- Are masks binary or soft?
- Does `manifest.json` contain enough metadata to define train/validation/test
  splits?
- Are light angle, elevation, softness, or reflection labels available?
