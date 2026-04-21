# Training Stack

Status: accepted direction for the next implementation phase.

Source context:

- `docs/discussions/2026-04-21-training-pipeline-chatgpt-share.md`
- User decisions on 2026-04-21.

## Core Stack

- Python package managed with `uv`.
- PyTorch-based training.
- Hugging Face Diffusers/Accelerate as the likely large-model training base.
- Config-driven experiments; Hydra/OmegaConf remains a strong candidate for the
  next scaffold expansion.
- W&B is the selected experiment tracker.
- DVC is selected for dataset versioning, with rollout details still to be
  finalized after dataset inspection.

## W&B Policy

W&B should be the primary experiment tracking interface because this project is
also a portfolio project and visual comparison matters.

Expected W&B usage:

- run configs and hyperparameters,
- scalar metrics,
- GPU/system metrics,
- qualitative image panels,
- fixed validation subsets,
- links or metadata for dataset versions,
- model/version notes without committing weights to GitHub.

W&B artifacts may be useful later, but the repository policy remains unchanged:
do not commit W&B run directories, generated images, checkpoints, or model
weights to Git.

## Experiment Naming

Use stable names that communicate model family, data version, and purpose.

Examples:

- `toy-cond-diffusion-overfit-v0`
- `large-lora-shadow-v0`
- `control-lora-shadow-v0`
- `shadow-pair-v1-smoke`

## Baseline Sequence

Recommended sequence:

1. Dataset inspection and manifest.
2. Shadow target extraction prototype from composite plus object mask.
3. Fixed qualitative validation panel.
4. Toy/small overfit smoke to prove the pipeline.
5. Stable Diffusion 1.5 adaptation baseline.

The toy model is intentionally a pipeline test, not the product model.

## Validation Focus

Validation should show whether the model learned useful shadow behavior, not
only whether pixel loss decreases.

Required qualitative views:

- input object/composite,
- object mask,
- derived shadow target,
- model output,
- composite preview with original object overlaid,
- failure cases.

When control labels become available, add sweeps for:

- light angle,
- elevation,
- softness,
- reflection.
