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
$env:SHADOWGEN_DATASET_ROOT="\\riper\datasets"
uv run shadowgen-training doctor
uv run shadowgen-training inspect-dataset --root "\\riper\datasets"
uv run shadowgen-training validate-config configs/project.yaml
uv run pytest -q
```

## Current Model Status

The first production model is expected to be diffusion-based and may use LoRA,
ControlNet, or a hybrid conditioning approach. The exact architecture is not
selected in this repository scaffold. Configuration intentionally records the
contract and candidates without hard-coding a training pipeline.

## Important Paths

- Model contract snapshot: `docs/contracts/shadow-v2-model-contract.md`
- Repository scope: `docs/repo-scope.md`
- Artifact policy: `docs/artifact-policy.md`
- Model direction: `docs/decisions/model-direction.md`
- Training stack: `docs/decisions/training-stack.md`
- Data versioning: `docs/decisions/data-versioning.md`
- Open questions: `docs/decisions/open-questions.md`
- Local setup: `docs/runbooks/local-setup.md`
- Next model step: `docs/runbooks/next-model-step.md`
- Captured discussions: `docs/discussions/`

## GitHub Policy

Only text files belong in this GitHub repository. Large or binary ML assets must
stay outside Git and be tracked later through an explicit artifact system.
