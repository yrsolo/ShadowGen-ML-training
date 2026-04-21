# Open Questions

Status: active questions before model training implementation.

## Dataset

- Which exact folder under `\\riper\datasets` contains the ShadowGen training
  composites and masks?
- Are image/mask filenames already paired deterministically?
- Are masks binary, soft alpha, or mixed?
- Does the composite always use a clean white background?
- Can the target shadow be separated reliably as non-object pixels, or does it
  need additional background normalization?
- Are there labels for light angle, elevation, softness, or reflection?

## Model

- Which large pretrained diffusion backbone should be first: FLUX-like,
  SD3-like, or another model?
- Is the first product baseline LoRA-only, ControlNet-style, or Control-LoRA?
- Should the model predict a shadow layer, a ready white-background composite,
  or both through an adapter?
- What is the minimum acceptable inference quality at the 11 GB target?

## Data Versioning

- What is the first named dataset version?
- Is the file count low enough for direct DVC tracking?
- Which DVC remote should be used first?

## Evaluation

- What fixed validation set should be used for qualitative panels?
- Which failure cases matter most: thin structures, contact shadows, low
  elevation, soft penumbra, or unusual object shapes?
- What acceptance threshold is enough to move from toy/pipeline smoke to large
  pretrained adaptation?
