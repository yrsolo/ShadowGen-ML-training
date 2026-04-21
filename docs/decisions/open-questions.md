# Open Questions

Status: active questions before model training implementation.

## Dataset

- Are image/mask filenames already paired deterministically?
- Are masks binary, soft alpha, or mixed?
- Does the composite always use a clean white background?
- Can the target shadow be separated reliably as non-object pixels, or does it
  need additional background normalization?
- Are there labels for light angle, elevation, softness, or reflection?

## Model

- Is the first product baseline LoRA-only, ControlNet-style, or Control-LoRA?
- What is the minimum acceptable inference quality at the 11 GB target?
- What threshold means direction fidelity is bad enough to add a v2 coarse
  projected-shadow prior?

## Data Versioning

- What is the first named dataset version?
- Is the file count low enough for direct DVC tracking?
- What local/NAS path should be used as the first DVC remote?

## Evaluation

- What fixed validation set should be used for qualitative panels?
- Which failure cases matter most: thin structures, contact shadows, low
  elevation, soft penumbra, or unusual object shapes?
- What acceptance threshold is enough to move from toy/pipeline smoke to large
  pretrained adaptation?
