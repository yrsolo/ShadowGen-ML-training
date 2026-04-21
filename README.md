# ShadowGen-ML-training

Training and evaluation workspace for ShadowGen shadow generation models.

This repository owns only the training-side work for the main shadow generation
model. Serving code, API integration, product orchestration, and compositor logic
live in sibling repositories.

## Responsibilities

- Dataset access checks and future dataset preparation code.
- Reproducible training and evaluation scaffolding.
- Experiment configuration and run documentation.
- Model contract compatibility checks before export.
- Text-only documentation for architecture decisions and runbooks.

## Non-responsibilities

- API request parsing or service hosting.
- Triton repository deployment.
- Object detection, segmentation, depth, normals, or final composition.
- Storing raw datasets, images, videos, checkpoints, model weights, or generated
  artifacts in Git.

## Quick Start

```powershell
uv sync
$env:SHADOWGEN_DATASET_ROOT="\\riper\datasets\3D\final_objaverse_v1"
uv run shadowgen-training doctor
uv run shadowgen-training inspect-dataset --root "\\riper\datasets\3D\final_objaverse_v1"
uv run shadowgen-training validate-config configs/project.yaml
uv run shadowgen-training build-manifest --root "\\riper\datasets\3D\final_objaverse_v1"
uv run shadowgen-training train-toy --max-samples 4 --size 64 --steps 30 --wandb-mode disabled
uv run pytest -q
```

## Current Model Status

The first serious backbone is Stable Diffusion 1.5 adapted for the ShadowGen
task. LoRA, ControlNet-style conditioning, and a Control-LoRA hybrid remain the
main adaptation candidates. A toy baseline is required first to validate the
pipeline before serious backbone work.

## Important Paths

- Model contract snapshot: `docs/contracts/shadow-v2-model-contract.md`
- Repository scope: `docs/repo-scope.md`
- Artifact policy: `docs/artifact-policy.md`
- Model direction: `docs/decisions/model-direction.md`
- Training stack: `docs/decisions/training-stack.md`
- Data versioning: `docs/decisions/data-versioning.md`
- Open questions: `docs/decisions/open-questions.md`
- Dataset notes: `docs/dataset.md`
- Local setup: `docs/runbooks/local-setup.md`
- Next model step: `docs/runbooks/next-model-step.md`
- Toy baseline: `docs/runbooks/toy-baseline.md`
- Captured discussions: `docs/discussions/`

## GitHub Policy

Only text files belong in this GitHub repository. Large or binary ML assets must
stay outside Git and be tracked later through an explicit artifact system.
